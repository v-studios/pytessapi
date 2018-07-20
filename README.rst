=======================================================
 PyTessAPI: Trying Python wrappers for Tesseract's API
=======================================================

https://github.com/tesseract-ocr/tesseract/wiki/AddOns#tesseract-wrappers
lists API wrappers including:

* tesserocr
* tesserwrap
* python-tesseract-sip


Build Tesseract-4.0-beta from source
====================================

Ensure you have “icu” installed; on mac, “brew install icu4c”; on
linux maybe install libicu-devel?

Ensure we have no remaining tesseracts and install hand-built tesseract::

  brew uninstall tesseract

Checkout tesseract from github and get onto the most recent “beta”
tag. Then config (with icu's location) and build::

  ./autogen.sh
  LDFLAGS=-L/usr/local/opt/icu4c/lib CPPFLAGS=-I/usr/local/opt/icu4c/include ./configure
  make
  sudo make install

This installs tesseract to /usr/local/bin/, data to
/usr/local/share/tessdata, and libraries to /usr/local/lib/, and
includes to /usr/local/include/tesseract/.

We're running 4.0.0-beta-3::

  $ tesseract -v
  tesseract 4.0.0-beta.3-180-gab1f
   leptonica-1.76.0
    libjpeg 9c : libpng 1.6.34 : libtiff 4.0.9 : zlib 1.2.11
   Found AVX2
   Found AVX
   Found SSE

Build tesserocr
===============

Use python3 virtualenv::

  pip install tesserocr
  ...
    tesserocr.cpp:635:10: fatal error: 'tesseract/osdetect.h' file not found
    #include "tesseract/osdetect.h"
             ^~~~~~~~~~~~~~~~~~~~~~

Fix it by copying the file from tesseract source to the system
includes::

  cp ./tesseract/src/ccmain/osdetect.h /usr/local/include/tesseract/

Now pip install works.

Run tesserocr with fixed locale
===============================

If I try to use it, we get an error::

  $ python
  >>> import tesserocr
  !strcmp(locale, "C"):Error:Assert failed:in file baseapi.cpp, line 191
  Abort trap: 6

This is a new breakage in tesseract: https://github.com/tesseract-ocr/tesseract/issues/1670

I see my locale::

  $ locale
  LANG="en_US.UTF-8"
  LC_COLLATE="en_US.UTF-8"
  LC_CTYPE="en_US.UTF-8"
  LC_MESSAGES="en_US.UTF-8"
  LC_MONETARY="en_US.UTF-8"
  LC_NUMERIC="en_US.UTF-8"
  LC_TIME="en_US.UTF-8"
  LC_ALL="en_US.UTF-8"

I can fix this for a run by first setting one of the locale variables::

  export LC_ALL=C

and now I can import tessocr. Better to do it in python only::

  
>>> import locale
>>> locale.setlocale(locale.LC_ALL, "C")
'C'
>>> import tesserocr

This may break UTF: https://github.com/sirfz/tesserocr/issues/122

No languages?
-------------

why not::
  import tesserocr
  print(tesserocr.get_languages())
  ('/usr/local/share/tessdata/', [])

My /usr/local/sahre/tessdata/ is mostly from June 19, do I need to download it separately from tess-4?
See https://github.com/tesseract-ocr/tessdata/blob/master/README.md

I clone the repo and copy::

  git clone git@github.com:tesseract-ocr/tessdata.git
  cp -r tessdata/* /usr/local/share/tessdata/

And now I can find languages::

  print(tesserocr.get_languages())
  ('/usr/local/share/tessdata/', ['ori', 'por', 'snd', 'srp', 'hin', 'chi_sim', 'spa', 'uzb_cyrl', 'mar', 'swa', 'ces', 'urd', 'fry', 'nep', 'cat', 'mya', 'lit', 'dan', 'mlt', 'enm', 'bod', 'ltz', 'tir', 'gla', 'tgl', 'tha', 'fas', 'hrv', 'ukr', 'lao', 'ben', 'eus', 'fao', 'div', 'eng', 'dzo', 'nld', 'hye', 'vie', 'ita', 'kir', 'jpn_vert', 'pus', 'yor', 'msa', 'kor_vert', 'heb', 'bre', 'slv', 'cos', 'kaz', 'fin', 'yid', 'deu', 'ton', 'bul', 'khm', 'ell', 'cym', 'kor', 'slk_frak', 'lav', 'mkd', 'script/Thaana', 'script/Cherokee', 'script/Hangul_vert', 'script/Hangul', 'script/Armenian', 'script/Tamil', 'script/Telugu', 'script/Kannada', 'script/Sinhala', 'script/Khmer', 'script/Devanagari', 'script/HanS', 'script/Cyrillic', 'script/Syriac', 'script/Gurmukhi', 'script/HanS_vert', 'script/Gujarati', 'script/Ethiopic', 'script/Thai', 'script/Oriya', 'script/HanT_vert', 'script/Tibetan', 'script/Malayalam', 'script/Greek', 'script/Japanese', 'script/Arabic', 'script/Latin', 'script/Lao', 'script/HanT', 'script/Japanese_vert', 'script/Myanmar', 'script/Hebrew', 'script/Fraktur', 'script/Bengali', 'script/Georgian', 'script/Vietnamese', 'script/Canadian_Aboriginal', 'glg', 'sin', 'syr', 'rus', 'kat', 'frk', 'kur', 'bos', 'ind', 'swe', 'est', 'iku', 'sqi', 'nor', 'fil', 'pol', 'oci', 'sun', 'tam', 'mal', 'slk', 'que', 'chi_sim_vert', 'jav', 'srp_latn', 'osd', 'afr', 'hat', 'gle', 'ron', 'kan', 'uig', 'lat', 'ita_old', 'frm', 'equ', 'tgk', 'kat_old', 'spa_old', 'uzb', 'dan_frak', 'hun', 'aze_cyrl', 'isl', 'grc', 'aze', 'asm', 'pan', 'chi_tra_vert', 'epo', 'chi_tra', 'tel', 'deu_frak', 'mon', 'mri', 'amh', 'chr', 'guj', 'ara', 'kur_ara', 'san', 'tat', 'fra', 'tur', 'jpn', 'ceb', 'bel'])

And now I can use the API to extract text per the example on tesserocr's GitHub page::

  from tesserocr import PyTessBaseAPI
  api = PyTessBaseAPI()
  api.SetImageFile('Brobo_Gearbox_with_Old_Pump.png')
  print(api.GetUTF8Text())
  print(api.AllWordConfidences())

Running with ScrollView
=======================

We can display ScrollView by doing in Python::

    image = Image.open('nike.png')
    api = PyTessBaseAPI()
    api.SetVariable("textord_show_tables", "true")
    api.SetVariable("textord_tablefind_recognize_tables", "true")
    api.SetImage(image)  # set image after variables to get ScrollView to work

 but we need to set a path before we invoke for ScrollView JARs to be found::

   export SCROLLVIEW_PATH=./scrollview/


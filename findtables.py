#!/usr/bin/env python
"""For a given image, iterate over the blocks and find ones that are tables."""

import locale
locale.setlocale(locale.LC_ALL, "C")  # MUST come before import of tesserocr
from pprint import pprint as pprint

from PIL import Image
from tesserocr import PT, PyTessBaseAPI, RIL, iterate_level

# PT is a 'type' so make a textual mapping
# Isn't there an easier, built-in way to do this??
PT_NAME = {
    PT.UNKNOWN:         'UNKNOWN',
    PT.FLOWING_TEXT:    'FLOWING_TEXT',
    PT.HEADING_TEXT:    'HEADING_TEXT',
    PT.PULLOUT_TEXT:    'PULLOUT_TEXT',
    PT.EQUATION:        'EQUATION',
    PT.INLINE_EQUATION: 'INLINE_EQUATION',
    PT.TABLE:           'TABLE',
    PT.VERTICAL_TEXT:   'VERTICAL_TEXT',
    PT.CAPTION_TEXT:    'CAPTION_TEXT',
    PT.FLOWING_IMAGE:   'FLOWING_IMAGE',
    PT.HEADING_IMAGE:   'HEADING_IMAGE',
    PT.PULLOUT_IMAGE:   'PULLOUT_IMAGE',
    PT.HORZ_LINE:       'HORZ_LINE',
    PT.VERT_LINE:       'VERT_LINE',
    PT.NOISE:           'NOISE',
    PT.COUNT:           'COUNT',
}

# AnalyseLayout:
# - https://zdenop.github.io/tesseract-doc/group___advanced_a_p_i.html#gaaac2abf8505c89afb8466dc3cff2c666
# GetComponentImages:
# - https://zdenop.github.io/tesseract-doc/group___advanced_a_p_i.html#ga56369b1654400ef97e581bb65749ec3d
# GetConnectedComponents:
# - https://zdenop.github.io/tesseract-doc/group___advanced_a_p_i.html#gaf2b4f88c53457fa5153dc80f5a60e152
# GetIterator:
# - https://zdenop.github.io/tesseract-doc/group___advanced_a_p_i.html#ga52eee8b9a4f147c26e4b64c16b46bc04
# GetRegions:
# - https://zdenop.github.io/tesseract-doc/group___advanced_a_p_i.html#gafdd23f73100c54cff18ecfa14efa0379
# Recognize:
# - https://zdenop.github.io/tesseract-doc/group___advanced_a_p_i.html#ga0e4065c20b142d69a2324ee0c74ae0b0

def main():
    """Show the blocks."""
    api = PyTessBaseAPI()
    api.SetVariable("textord_tablefind_recognize_tables", "true")
    # This launches ScrollView so ensure SCROLLVIEW_PATH points to our
    # ./scrollview/ dir with ScrollView.jar and piccolo2d-*-3.0.jar files
    # api.SetVariable("textord_show_tables", "true")  # launches ScrollView

    # Must set image after variables to get ScrollView to work
    image = Image.open('packinglist.png')
    api.SetImage(image)
    api.Recognize()             # what's this do?
    # api.AnalyseLayout()         # causes nullptr in iterator

    level = RIL.BLOCK           # BLOCK PARA SYMBOL TEXTLINE WORD
    riter = api.GetIterator()

    for r in iterate_level(riter, level):
        print('### blocktype={}={} conf={} txt:\n{}'.format(
            r.BlockType(), PT_NAME[r.BlockType()], int(r.Confidence(level)), r.GetUTF8Text(level)))

    # C++ code
    # tesseract::PageIterator *ri = api->GetIterator();
    #       if (ri != 0) {
    #           do {
    #                     cout<<ri->BlockType()<<endl;
    #           } while (ri->Next(tesseract::RIL_BLOCK));
    #       }

    # riter = api.GetIterator()
    # #import pdb; pdb.set_trace()
    # while riter:
    #     print('riter blocktype:', riter.BlockType())
    #     riter = riter.Next(RIL.BLOCK)

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""For a given image, iterate over the blocks and find ones that are tables."""

import locale
locale.setlocale(locale.LC_ALL, "C")  # MUST come before import of tesserocr
from pprint import pprint as pprint

from PIL import Image
from tesserocr import PyTessBaseAPI, RIL


def main():
    """Show the blocks."""
    image = Image.open('nike.png')
    api = PyTessBaseAPI()
    # This launches ScrollView so ensure SCROLLVIEW_PATH points to our
    # ./scrollview/ dir with ScrollView.jar and piccolo2d-*-3.0.jar files
    # api.SetVariable("textord_show_tables", "true")
    api.SetVariable("textord_tablefind_recognize_tables", "true")

    # Must set image after variables to get ScrollView to work
    api.SetImage(image)

    boxes = api.GetComponentImages(RIL.BLOCK, True)
    pprint(boxes)

    # C++ code
    # tesseract::PageIterator *ri = api->GetIterator();
    #       if (ri != 0) {
    #           do {
    #                     cout<<ri->BlockType()<<endl;
    #           } while (ri->Next(tesseract::RIL_BLOCK));
    #       }

    riter = api.GetIterator()
    #import pdb; pdb.set_trace()
    while riter:
        print('riter blocktype:', riter.BlockType())
        riter = riter.Next(RIL.BLOCK)

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""For a given image, iterate over the blocks and find ones that are tables."""

import argparse
import locale

from PIL import Image

locale.setlocale(locale.LC_ALL, "C")  # MUST come before import of tesserocr

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


def main(args):
    """Show the blocks and extracted text."""

    with PyTessBaseAPI(psm=args.psm) as api:
        api.SetImageFile(args.filepath)

        # Set variables to find blocks, show info -- version and default in comments
        # api.SetVariable('textord_dump_table_images', 'true')         # 302: 0, not in 400
        api.SetVariable('textord_tabfind_find_tables', 'true')         # 400: 1
        api.SetVariable('textord_tablefind_recognize_tables', 'true')  # 400: 0
        api.SetVariable('textord_tablefind_show_mark', 'true')         # 400: 0
        api.SetVariable('textord_tablefind_show_stats', 'true')        # 400: 0

        if args.scrollview:
            # This launches ScrollView so ensure SCROLLVIEW_PATH points to our
            # ./scrollview/ dir with ScrollView.jar and piccolo2d-*-3.0.jar files
            api.SetVariable("textord_show_tables", "true")  # launches ScrollView

        api.Recognize()             # what's this do?
        # api.AnalyseLayout()         # causes nullptr in iterator

        level = RIL.BLOCK           # BLOCK, PARA, SYMBOL, TEXTLINE, WORD
        riter = api.GetIterator()
        for r in iterate_level(riter, level):
            if args.tablesonly is False or PT_NAME[r.BlockType()] == 'TABLE':
                print('### blocktype={}={} confidence={} txt:\n{}'.format(
                    r.BlockType(), PT_NAME[r.BlockType()],
                    int(r.Confidence(level)), r.GetUTF8Text(level)))
                import pdb; pdb.set_trace()

        if args.scrollview:
            input('Type something to exit scrollview:')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Try to find tables in a scan; '
                                     'only seems to work with PSM 0-3')
    parser.add_argument('-f', '--filepath', dest='filepath',
                        default='sample-doc-with-table-300ppi.png',
                        help='path to the PNG, TIF or PDF scanned page')
    parser.add_argument('-p', '--psm', dest='psm',
                        default=3, type=int,
                        help='Page Segmentation Mode (default 3)')
    parser.add_argument('-t', '--tables-only', dest='tablesonly',
                        default=False, action='store_true',
                        help='Display only table info, not non-TABLE blocks')
    parser.add_argument('-s', '--scrollview', dest='scrollview',
                        default=False, action='store_true',
                        help='Enable ScrollView display (set SCROLLVIEW_PATH=scrollview)')
    args = parser.parse_args()
    main(args)

# Tesseract API docs
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

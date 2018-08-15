#!/usr/bin/env python
"""For a given image, iterate over the blocks and find ones that are tables."""

import argparse
from collections import namedtuple
import locale

locale.setlocale(locale.LC_ALL, "C")  # MUST come before import of tesserocr

from tesserocr import PT, PyTessBaseAPI, RIL, iterate_level

LEVEL = RIL.BLOCK           # BLOCK, PARA, SYMBOL, TEXTLINE, WORD
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

    BoxXYXY = namedtuple('BoxXYXY', ['xtop', 'ytop', 'xbot', 'ybot'])
    # BoxXYWH = namedtuple('BoxXYWH', ['x', 'y', 'w', 'h'])

    # First pass through API: find TABLEs
    print('# Finding tables...')
    tables = []
    with PyTessBaseAPI(psm=args.psm) as api:
        api.SetImageFile(args.filepath)

        # Set variables to find blocks, show info -- version and default in comments
        # Ensure SCROLLVIEW_PATH points to our ./scrollview/ dir with jars
        api.SetVariable('textord_tabfind_find_tables', 'true')         # 400: 1
        api.SetVariable('textord_tablefind_recognize_tables', 'true')  # 400: 0
        # api.SetVariable('textord_tablefind_show_mark', 'true')         # 400: 0
        # api.SetVariable('textord_tablefind_show_stats', 'true')        # 400: 0
        if args.scrollview:
            api.SetVariable("textord_show_tables", "true")  # launches ScrollView

        api.Recognize()
        riter = api.GetIterator()
        for r in iterate_level(riter, LEVEL):
            if r.BlockType() == PT.TABLE:
                tables.append(BoxXYXY(*r.BoundingBox(LEVEL)))
            if args.tablesonly is False or r.BlockType() == PT.TABLE:
                print('### blocktype={}={} confidence={} bbox={} txt:\n{}'.format(
                    r.BlockType(), PT_NAME[r.BlockType()],
                    int(r.Confidence(LEVEL)), r.BoundingBox(LEVEL), r.GetUTF8Text(LEVEL)))

    # Second pass through API: get LINEs in the TABLEs, read cells
    print('# Finding cells in each table...')
    for table in tables:
        print('# table={}'.format(table))
        with PyTessBaseAPI(psm=args.psm) as api:
            horz_lines = []
            vert_lines = []
            width = table.xbot - table.xtop
            height = table.ybot - table.ytop
            api.SetImageFile(args.filepath)
            api.SetRectangle(table.xtop, table.ytop, width, height)
            api.Recognize()
            riter = api.GetIterator()
            for r in iterate_level(riter, LEVEL):
                if r.BlockType() == PT.HORZ_LINE:
                    horz_lines.append(BoxXYXY(*r.BoundingBox(LEVEL)))
                if r.BlockType() == PT.VERT_LINE:
                    vert_lines.append(BoxXYXY(*r.BoundingBox(LEVEL)))
            print('horz_lines={}'.format(horz_lines))
            print('vert_lines={}'.format(vert_lines))
            # Get X and Y list for TABLE and HLINE and VLINE respectively, sort each
            ys = [table.ytop, table.ybot]
            xs = [table.xtop, table.xbot]
            for hline in horz_lines:
                ys.append(round((hline.ytop + hline.ybot) / 2))
            ys.sort()
            for vline in vert_lines:
                xs.append(round((vline.xtop + vline.xbot) / 2))
            xs.sort()
            print('ys={}'.format(ys))
            print('xs={}'.format(xs))
            # Iterate over pairs of lines and x-coords to get text in each cell
            table_xmin = xs[0]
            table_xmax = xs[-1]
            for ymin, ymax in zip(ys[:-1], ys[1:]):
                # Set the rectangle, then get the text inside
                width = table_xmax - table_xmin
                height = ymax - ymin
                api.SetRectangle(table_xmin, ymin, width, height)
                line = api.GetUTF8Text().strip().replace('\n\n', '\n')
                print('\n### LINE ({:>4}, {:>4}, {:>4}, {:>4}) w={:>4} h={:>4}:\n{}'.format(
                    table_xmin, ymin, table_xmax, ymax, width, height, line))
                # Interestingly, on non-header row, the cell text is \n-separated; can't depend on it tho
                for xmin, xmax in zip(xs[:-1], xs[1:]):
                    width = xmax - xmin
                    height = ymax - ymin
                    api.SetRectangle(xmin, ymin, width, height)
                    cell = api.GetUTF8Text().strip()
                    print('### CELL ({:>4}, {:>4}, {:>4}, {:>4}) w={:>4} h={:>4}: {}'.format(
                        xmin, ymin, xmax, ymax, width, height, cell))




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

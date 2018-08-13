#!/usr/bin/env python3
"""Test getting a block, then iterating over it with second iterator."""

import locale
locale.setlocale(locale.LC_ALL, "C")  # MUST come before import of tesserocr

from tesserocr import PT, PyTessBaseAPI, RIL, iterate_level


with PyTessBaseAPI() as api:
    api.SetImageFile('sample-doc-with-table-300ppi.png')
    api.SetVariable('textord_tabfind_find_tables', 'true')
    api.SetVariable('textord_tablefind_recognize_tables', 'true')
    api.Recognize()             # what's this do?
    level = RIL.BLOCK
    riter = api.GetIterator()
    for r in iterate_level(riter, level):
        print(r.BlockType())
        if r.BlockType() == PT.TABLE:
            bbox = r.BoundingBox(level)
            print('TABLE: {}'.format(bbox))

    print('Second iterator...')
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    # Setting the rect causes this GetIterator to return None
    api.SetRectangle(bbox[0], bbox[1], width, height)
    riter2 = api.GetIterator()
    if riter2 is None:
        raise RuntimeError('Second iterator is None')
    print('riter2=', riter2)
    for r2 in iterate_level(riter2, level):
        print(r2.BlockType())


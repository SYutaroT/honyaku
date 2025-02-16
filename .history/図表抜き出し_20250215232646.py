import sys
import os

from pdfrw import PdfReader, PdfWriter
from pdfrw.findobjs import trivial_xobjs, wrap_object, find_objects
from pdfrw.objects import PdfDict, PdfArray, PdfName

arxiv_id = "1506.02640"
file_path = f"data/paper_pdf/{arxiv_id}.pdf"
out_path = f"data/paper_summary/{arxiv_id}.pdf"

WIDTH = 8.5 * 72
MARGIN = 0.5*72

pdf = PdfReader(file_path)
objects = []
for xobj in list(find_objects(pdf.pages)):
    if xobj.Type==PdfName.XObject and xobj.Subtype == PdfName.Form:
        if '/PTEX.FileName' in xobj:
            wrapped = wrap_object(xobj, WIDTH, MARGIN)
            objects.append(wrapped)

if not objects:
    raise IndexError("No XObjects found")
writer = PdfWriter(out_path)
writer.addpages(objects)
writer.write()
from pdfrw import PdfReader
from pdfrw.findobjs import find_objects
filename = 'suiteki.pdf'
pdf = PdfReader(filename)
print(list(find_objects(pdf.pages)))

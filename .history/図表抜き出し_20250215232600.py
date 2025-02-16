from pdfrw import PdfReader
from pdfrw.findobjs import find_objects
filename = 'suiteki.pdf'
pdf = PdfReader(ile_pafth)
print(list(find_objects(pdf.pages)))
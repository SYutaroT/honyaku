from pdfrw import PdfReader
from pdfrw.findobjs import find_objects



pdf = PdfReader(file_path)
print(list(find_objects(pdf.pages)))
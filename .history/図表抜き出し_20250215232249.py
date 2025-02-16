import fitz
import os

filename = 'suiteki.pdf'
dir_name = filename.split(".")[0]
img_dir = os.path.join(os.getcwd(),dir_name)

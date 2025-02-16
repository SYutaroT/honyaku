import fitz
import os

filename = 'suiteki.pdf'
dir_name = filename.split(".")[0]
img_dir = os.path.join(os.getcwd(), dir_name)
if os.path.isdir(img_dir) == False:
    os.mkdir(img_dir)


# PRG3：PDFファイルを読み込む
doc = fitz.open(filename)

# PRG4：画像情報を格納するリストを作成
images = []

# PRG5：１ページずつ画像データを取得
for page in range(len(doc)):
    images.append(doc[page].get_images())

# PRG6：ページ内の画像情報を順番に処理
for pageNo, image in enumerate(images):
    # PRG7：ページ内の画像情報を処理する
    if image != []:
        for i in range(len(image)):
            # PRG8：画像情報の取得
            xref = image[i][0]
            smask = image[i][1]
            if image[i][8] == 'FlateDecode':
                ext = 'png'
            elif image[i][8] == 'DCTDecode':
                ext = 'jpeg'

            # PRG9：マスク情報の取得と画像の再構築
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])
            if smask > 0:
                mask = fitz.Pixmap(doc.extract_image(smask)["image"])
                pix = fitz.Pixmap(pix, 0)
                pix = fitz.Pixmap(pix, mask)

            # PRG10：画像を保存
            img_name = os.path.join(img_dir, f'image{pageNo+1}_{i}.{ext}')
            pix.save(img_name)

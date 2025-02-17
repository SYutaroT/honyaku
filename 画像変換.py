from PIL import Image
import os


def convert_png_to_eps(input_png, output_eps):
    # 画像を開く
    img = Image.open(input_png)

    # EPS形式で保存
    img.save(output_eps, format="EPS")


# 変換する画像のパス
input_png = "C:\\Users\\sachy\\Desktop\\翻訳\\honyaku\\Img\\image_1.png"
output_eps = "C:\\Users\\sachy\\Desktop\翻訳\\Transed\Img\\A droplet-based electricity generator with high instantaneous power density\\image_1.eps"
print(os.path.dirname(os.path.dirname(__file__)+"Transed+\\Img")
      )
script_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(os.path.dirname(script_dir), "Transed")
print(img_dir)

# PNG → EPS に変換
convert_png_to_eps(input_png, output_eps)
print(f"変換完了: {output_eps}")

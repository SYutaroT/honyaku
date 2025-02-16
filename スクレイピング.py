from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# 画像を保存するディレクトリ
dir_name = "Img"
img_dir = os.path.join(os.getcwd(), dir_name)
if not os.path.isdir(img_dir):
    os.mkdir(img_dir)

url = "https://www.nature.com/articles/s41586-020-1985-6"


def Nature():
    # Seleniumのセットアップ
    options = Options()
    options.add_argument("--headless")  # ヘッドレスモード（ブラウザを表示しない）

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    driver.get(url)

    # JavaScriptが実行された後のHTMLを取得
    html = driver.page_source
    driver.quit()

    # BeautifulSoupで解析
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []

    # すべての<source>タグを取得し、srcsetの値のみをリストに格納
    for source in soup.find_all("source"):
        if "srcset" in source.attrs:
            image_urls.append("https:" + source["srcset"])

    # 一番上の要素を除外
    return image_urls[1:]  # 最初の不要な画像を削除


def download_images(image_urls, save_dir):
    for i, img_url in enumerate(image_urls):
        # クエリパラメータを除いたURLのファイル名を取得
        img_name = f"image_{i+1}.png"  # 画像ファイル名を作成
        img_path = os.path.join(save_dir, img_name)

        # 画像をダウンロード
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            with open(img_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"ダウンロード完了: {img_path}")
        else:
            print(f"ダウンロード失敗: {img_url}")


# 実行
filtered_image_urls = Nature()
download_images(filtered_image_urls, img_dir)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import sys

# UTF-8に変更
sys.stdout.reconfigure(encoding='utf-8')

# Natureの論文URL
url = "https://www.nature.com/articles/s41586-020-1985-6"

# HTTPリクエストを送信
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)

# レスポンスのステータスを確認
if response.status_code == 200:
    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(response.text, "html.parser")

    # タイトルを取得
    title = soup.find("title").text
    print(f"論文タイトル: {title}")

    # 要旨（Abstract）の取得
    abstract_section = soup.find("div", class_="c-article-section__content")
    if abstract_section:
        abstract_text = abstract_section.get_text(strip=True)
        print(f"要旨: {abstract_text}")
    else:
        print("要旨が見つかりませんでした。")

else:
    print("ページを取得できませんでした。")

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
print(soup.prettify())

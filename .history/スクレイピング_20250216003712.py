from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


url = "https://www.nature.com/articles/s41586-020-1985-6"
# Seleniumのセットアップ
options = Options()
options.add_argument("--headless")  # ヘッQドレスモード（ブラウザを表示しない）

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)
driver.get(url)

# JavaScriptが実行された後のHTMLを取得
html = driver.page_source
driver.quit()

# BeautifulSoupで解析
soup = BeautifulSoup(html, "html.parser")
print(soup.prettify())

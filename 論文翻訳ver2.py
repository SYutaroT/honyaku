import json
import re
import deepl
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import API_Libla
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape
import subprocess
import os
import PyPDF2
import subprocess
import PySimpleGUI as sg
import requests
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
#!----------------------------------------------------------------関数


def choose_file():  # GUI ファイル選択
    layout = [
        [sg.Text('ファイルを選択してください')],
        [sg.Input(), sg.FileBrowse()],
        [sg.OK(), sg.Cancel()]
    ]

    # ウィンドウの作成
    window = sg.Window('ファイル選択', layout)

    # イベントループ
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
        elif event == 'OK':
            file_path = values[0]  # 選択されたファイルのパス
            window.close()
            return file_path

    window.close()
    return None


def run_command(command):
    try:
        subprocess.run(command, check=True)
        print("sucsess")
    except subprocess.CalledProcessError as e:
        print(f"error: {e}")


def main():
    # コマンドの設定
    command = ["nougat", selected_file, "-o", "output_directory"]

    # コマンドの実行
    run_command(command)


def extract_paragraphs_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        print(pdf_path)
        reader = PyPDF2.PdfReader(file)
        paragraphs = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                paragraphs.extend(text.split('\n\n'))  # 段落を分割
        return paragraphs


def generate_stringsQJ():
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ['QJ' + a + b + c for a in alphabet for b in alphabet for c in alphabet]


def generate_stringsQE():
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ['QE' + a + b + c for a in alphabet for b in alphabet for c in alphabet]


def extract_math_and_text(file_path, input_text_file):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 数式の抽出
    extracted_math = re.findall(r'\\\[.*?\\\]', content)
    extracted_math2 = re.findall(r'\\\(.*?\\\)', content)

    # 数式をプレースホルダーで置き換え
    string_gen1 = generate_stringsQJ()
    string_gen2 = generate_stringsQE()
    replaced_strings1 = []
    replaced_strings2 = []

    for i, math_expr in enumerate(extracted_math):
        replacement = string_gen1[i]
        content = content.replace(math_expr, replacement, 1)
        replaced_strings1.append(replacement)

    for i, math_expr in enumerate(extracted_math2):
        replacement = string_gen2[i]
        content = content.replace(math_expr, replacement, 1)
        replaced_strings2.append(replacement)

    # 段落に分割

    paragraphs = content.split('\n\n')

    if paragraphs[0] == "[MISSING_PAGE_EMPTY:1]":
        paragraphs = extract_paragraphs_from_pdf(input_text_file)

    return extracted_math, paragraphs, extracted_math2, replaced_strings1, replaced_strings2


def translate_paragraphs(paragraphs, api_key, glossary_id, source_lang="EN", target_lang="JA"):
    translated_paragraphs = []
    references_started = False  # REFERENCESセクションが始まったかどうかを追跡するフラグ

    # DeepL APIのエンドポイント
    url = "https://api.deepl.com/v2/translate"

    for paragraph in paragraphs:
        # REFERENCESセクションが始まったかどうかをチェック
        if "REFERENCES" in paragraph.upper():
            references_started = True
            continue  # REFERENCESセクションの内容はスキップ

        # REFERENCESセクションが始まっていない、または終了した後の段落のみ翻訳
        if not references_started or paragraph.strip():  # 空白の段落は無視
            data = {
                'auth_key': api_key,
                'text': paragraph,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'glossary_id': glossary_id
            }
            response = requests.post(url, data=data)
            print("Request data:", data)  # デバッグ情報
            print("Response status:", response.status_code)  # レスポンスステータス
            print("Response content:", response.text)  # レスポンス内容
            if response.status_code == 200:
                result = response.json()
                translated_text = result['translations'][0]['text']
                translated_paragraphs.append(translated_text + "\n")
            else:
                print("error:", response.text)
                translated_paragraphs.append(paragraph + "\n")

    return translated_paragraphs


def save_text_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for paragraph in text:
            file.write(paragraph)


def create_pdf_with_wrapping(input_file_path, output_pdf_path, font_name='IPAexGothic', font_path="C:/Users/sachy/Desktop/翻訳/GenShinGothic-ExtraLight.ttf"):
    # フォントの登録
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    # PDFドキュメントの作成
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    story = []

    # スタイルの設定
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = font_name
    style.fontSize = 12
    style.leading = 15  # 行間の設定

    # テキストファイルの読み込み
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            escaped_line = escape(line.strip())  # HTMLタグをエスケープ
            paragraph = Paragraph(escaped_line, style)
            story.append(paragraph)

    # PDFの保存
    doc.build(story)


def replace_math_symbols(paragraphs, extracted_math, replaced_strings1):
    for i, math_expr in enumerate(extracted_math):
        replacement = replaced_strings1[i]
        # 識別子を含むプレースホルダーを特定
        identifier = replacement[-3:]
        for j, paragraph in enumerate(paragraphs):
            # 識別子を含むプレースホルダーを探す
            if identifier in paragraph:
                # プレースホルダー（識別子を含む）を元の数式に置き換える
                paragraphs[j] = paragraph.replace(replacement, math_expr, 1)
    return paragraphs


def replace_math_symbols2(paragraphs, extracted_math, replaced_strings1):
    for i, math_expr in enumerate(extracted_math):
        replacement = replaced_strings1[i]
        # 識別子を含むプレースホルダーを特定
        identifier = replacement[-3:]
        for j, paragraph in enumerate(paragraphs):
            # 識別子を含むプレースホルダーを探す
            if identifier in paragraph:
                # プレースホルダー（識別子を含む）を元の数式に置き換える
                paragraphs[j] = paragraph.replace(replacement, math_expr, 1)
    return paragraphs


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def save_as_latex(paragraphs, output_tex_path, img__dir):
    with open(output_tex_path, 'w', encoding='utf-8') as file:
        # LaTeXドキュメントの開始
        file.write('\\documentclass[a4paper,11pt]{jsarticle}\n')
        file.write('\\usepackage{amsmath,amsfonts}\n')
        file.write('\\usepackage{bm}\n')
        file.write('\\usepackage{ascmac}\n')
        file.write('\\usepackage{amssymb}\n')
        file.write('\\usepackage{amsmath, amsthm}\n')
        file.write('\\usepackage{listings}\n')
        file.write('\\usepackage{xcolor}\n')
        file.write('\\usepackage[dvipdfmx]{graphicx}\n')
        file.write('\\usepackage{subcaption}\n')
        file.write('\\usepackage{footnote}\n')
        file.write('\\usepackage{dsfont}\n')
        file.write('\\usepackage{stmaryrd}\n')

        file.write('\\begin{document}\n')
        # 段落の追加
        for paragraph in paragraphs:
            file.write(paragraph + '\n')
        file.write('\\newpage\n')
        file.write('\\section*{画像一覧}\n')

        # 画像を取得（拡張子フィルタ）
        image_files = [f for f in os.listdir(
            img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            file.write('画像が見つかりませんでした。\n')
        else:
            for i, image in enumerate(image_files):
                # 画像の拡張子を .eps に変換
                eps_image = os.path.splitext(image)[0] + ".eps"
                print(img_dir)
                print(eps_image)
                image_path = os.path.relpath(os.path.join(
                    img_dir, eps_image), img__dir).replace("\\", "/")

                print(image_path)
                file.write('\\begin{figure}[h]\n')
                file.write('\\centering\n')
                file.write(f'\\includegraphics[scale=0.5]{{{image_path}}}\n')
                file.write('\\caption{}\n')
                file.write('\\label{}\n')
                file.write('\\end{figure}\n')

        # LaTeXドキュメントの終了
        file.write('\\end{document}\n')


def convert_markdown_to_latex(paragraphs):
    converted_paragraphs = []
    for paragraph in paragraphs:
        if paragraph.startswith('#####'):
            # Abstract
            paragraph = paragraph.replace('#####', '')
            paragraph = '\\begin{abstract}\n' + '\n\\end{abstract}'
        elif paragraph.startswith('###'):
            # Subsection
            paragraph = paragraph.replace('###', '')
            paragraph = '\\subsection{' + paragraph + '}'
        elif paragraph.startswith('##'):
            # Section
            paragraph = paragraph.replace('##', '')
            paragraph = '\\section{' + paragraph + '}'
        elif paragraph.startswith('#'):
            # Title
            paragraph = paragraph.replace('#', '')
            paragraph = '\\title{' + paragraph + '}\maketitle'
        converted_paragraphs.append(paragraph)
    return converted_paragraphs


def get_paper_url(title):
    """
    CrossRef API を使って論文タイトルから DOI を取得し、論文URLを返す
    """
    base_url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 1}  # 1件のみ取得
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "message" in data and "items" in data["message"] and len(data["message"]["items"]) > 0:
            first_result = data["message"]["items"][0]  # 最初の検索結果
            actual_url = first_result.get("URL")  # "URL" フィールドを取得
            if actual_url:
                return actual_url  # Nature などの直接の論文URL
    return "論文URLが見つかりませんでした。"


def Nature(url):
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


def download_images(image_urls, save_dir, Img_dir):
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
            print(img_path)
            print(Img_dir+os.path.basename(img_path))
            convert_png_to_eps(img_path, Img_dir+"\\" +
                               os.path.basename(img_path))
        else:
            print(f"ダウンロード失敗: {img_url}")


def convert_png_to_eps(input_png, output_eps):
    # 画像を開く
    img = Image.open(input_png)
    output_eps = os.path.splitext(output_eps)[0] + ".eps"
    # EPS形式で保存
    img.save(output_eps, format="EPS")


#!処理
glasspath = os.path.dirname(__file__)+"\\MyGlossary.csv"
print(glasspath)
# selected_file = choose_file()
selected_file = "C:\\Users\\sachy\\Downloads\\A droplet-based electricity generator with high instantaneous power density.pdf"

file_name_with_extension = os.path.basename(selected_file)


input_file = os.path.splitext(file_name_with_extension)[0]
input_text_file = input_file+'.pdf'
# print(input_text_file)
file_path = 'output_directory/'+input_file+'.mmd'
api_key = API_Libla.Deple  # DeepL APIキー
glossary_id = API_Libla.glossary_id  # 辞書のID
pdfmetrics.registerFont(TTFont(
    'IPAexGothic',  os.path.dirname(__file__)+"\\GenShinGothic-ExtraLight.ttf"))
output_file_path = input_file+'.txt'


if __name__ == "__main__":
    main()

extracted_math, paragraphs, extracted_math2, replaced_strings1, replaced_strings2 = extract_math_and_text(
    file_path, input_text_file)


# translated_paragraphs = translate_paragraphs(paragraphs, api_key, glossary_id)
translated_paragraphs = paragraphs

paragraphs = replace_math_symbols(
    translated_paragraphs, extracted_math, replaced_strings1)
paragraphs = replace_math_symbols2(
    paragraphs, extracted_math2, replaced_strings2)
paragraphs = [p.replace('$', ' \$ ') for p in paragraphs]
paragraphs = [p.replace('%', ' \% ') for p in paragraphs]
paragraphs = [p.replace('&', ' and ') for p in paragraphs]
# print(paragraphs)
input_text_file = input_file+'.txt'
output_directory = 'Transed'
create_directory_if_not_exists(output_directory)
output_tex_file = os.path.join(
    output_directory, 'translated_' + input_file + '.tex')
translated_paragraphs = convert_markdown_to_latex(paragraphs)
translated_paragraphs = [p.replace('#', '') for p in translated_paragraphs]

paper_url = get_paper_url(input_file)
filtered_image_urls = Nature(paper_url)
safe_input_file = re.sub(r'[\\/*?:"<>|]', "", input_file)

dir_name = os.path.join("Img", safe_input_file)
img_dir = os.path.join(os.getcwd(), dir_name)

# 親フォルダも作成できるように変更
os.makedirs(img_dir, exist_ok=True)

download_images(filtered_image_urls, img_dir, os.path.dirname(
    os.path.dirname(__file__))+"\\Transed\\Img\\"+input_file)

script_dir = os.path.dirname(os.path.abspath(__file__))
save_as_latex(translated_paragraphs, output_tex_file,
              os.path.join(os.path.dirname(script_dir)))

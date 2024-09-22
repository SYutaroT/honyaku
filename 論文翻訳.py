import json
import re
import deepl
import sys
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

myfile = os.getcwd()
print(myfile)


def choose_file():  # ファイル選択ダイアログのレイアウト

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
            file_path = values[0]
            window.close()
            return file_path

    window.close()
    return None


# ----------------------------------------------------------------辞書
csv = myfile+"/MyGlossary.csv"  # 辞書csv
glasspath = fr"{csv}"  # 拡張子を除去

# ----------------------------------------------------------------ファイル選択
selected_file = choose_file()  # ファイルの選択
print(selected_file)
file_name_with_extension = os.path.basename(selected_file)
input_file = os.path.splitext(file_name_with_extension)[0]
input_text_file = input_file+'.pdf'
print(input_text_file)
file_path = 'output_directory/'+input_file+'.mmd'
api_key = API_Libla.Deple  # DeepL APIキー
ttf = myfile+"/GenShinGothic-ExtraLight.ttf"  # フォント
pdfmetrics.registerFont(TTFont(
    'IPAexGothic',  ttf))
output_file_path = input_file+'.txt'
glossary_id = API_Libla.Glossary


def run_command(command):  # プロセスが成功したかどうかの確認
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
        # print(pdf_path)
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


def extract_math_and_text(file_path, input_text_file):  # PDFから数式を抽出
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 数式の抽出(数式を2種類に分ける)
    extracted_math = re.findall(r'\\\[.*?\\\]', content)
    extracted_math2 = re.findall(r'\\\(.*?\\\)', content)

    # 2種の数式をそれぞれのルールに基づいて代替文字に置き換え
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


def translate_paragraphs(paragraphs, api_key, glossary_id, source_lang="EN", target_lang="JA"):  # 段落ごとにDeepleAPIで翻訳
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
            # print("Request data:", data)  # デバッグ情報
            # print("Response status:", response.status_code)  # レスポンスステータス
            # print("Response content:", response.text)  # レスポンス内容
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


def create_pdf_with_wrapping(input_file_path, output_pdf_path, font_name='IPAexGothic', font_path=myfile+"/GenShinGothic-ExtraLight.ttf"):
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


def save_as_latex(paragraphs, output_tex_path):
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


# メイン処理
if __name__ == "__main__":
    main()
extracted_math, paragraphs, extracted_math2, replaced_strings1, replaced_strings2 = extract_math_and_text(
    file_path, input_text_file)

paragraphs = [p.replace('_', '') for p in paragraphs]
translated_paragraphs = translate_paragraphs(paragraphs, api_key, glossary_id)
# translated_paragraphs = paragraphs
paragraphs = [p.replace('&', ' and ') for p in paragraphs]
paragraphs = replace_math_symbols(
    translated_paragraphs, extracted_math, replaced_strings1)
paragraphs = replace_math_symbols2(
    paragraphs, extracted_math2, replaced_strings2)
paragraphs = [p.replace('$', ' \$ ') for p in paragraphs]

input_text_file = input_file+'.txt'
output_directory = 'Transed'
create_directory_if_not_exists(output_directory)
output_tex_file = os.path.join(
    output_directory, 'translated_' + input_file + '.tex')
translated_paragraphs = convert_markdown_to_latex(paragraphs)
translated_paragraphs = [p.replace('#', '') for p in translated_paragraphs]
save_as_latex(translated_paragraphs, output_tex_file)

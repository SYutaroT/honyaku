
from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()
# DeepL API URL
url = 'https://api.deepl.com/v2/glossaries'

# APIキーの設定 (実際のAPIキーに置き換えてください)
api_key = os.getenv("Deple")

# リクエストヘッダ
headers = {
    'Authorization': f'DeepL-Auth-Key {api_key}',
    'Content-Type': 'application/json'
}

# 用語集データ
entries = [
    "QJAAA,QJAAA",
    "QJAAB,QJAAB",
    "QJAAC,QJAAC",
    "QJAAD,QJAAD",
    "QJAAE,QJAAE",
    "QJAAF,QJAAF",
    "QJAAG,QJAAG",
    "QJAAH,QJAAH",
    "QJAAI,QJAAI",
    "QJAAJ,QJAAJ",
    "QJAAK,QJAAK",
    "QJAAL,QJAAL",
    "QJAAM,QJAAM",
    "QJAAN,QJAAN",
    "QJAAO,QJAAO",
    "QJAAP,QJAAP",
    "QJAAQ,QJAAQ",
    "QJAAR,QJAAR",
    "QJAAS,QJAAS",
    "QJAAT,QJAAT",
    "QJAAU,QJAAU",
    "QJAAV,QJAAV",
    "QJAAW,QJAAW",
    "QJAAX,QJAAX",
    "QJAAY,QJAAY",
    "QJAAZ,QJAAZ",
    "QJABA,QJABA",
    "QJABB,QJABB",
    "QJABC,QJABC",
    "QJABD,QJABD",
    "QJABE,QJABE",
    "QJABF,QJABF",
    "QJABG,QJABG",
    "QJABH,QJABH",
    "QJABI,QJABI",
    "QJABJ,QJABJ",
    "QJABK,QJABK",
    "QJABL,QJABL",
    "QJABM,QJABM",
    "QJABN,QJABN",
    "QJABO,QJABO",
    "QJABP,QJABP",
    "QJABQ,QJABQ",
    "QJABR,QJABR",
    "QJABS,QJABS",
    "QJABT,QJABT",
    "QJABU,QJABU",
    "QJABV,QJABV",
    "QJABW,QJABW",
    "QJABX,QJABX",
    "QJABY,QJABY",
    "QJABZ,QJABZ",
    "QJACA,QJACA",
    "QJACB,QJACB",
    "QJACC,QJACC",
    "QJACD,QJACD",
    "QJACE,QJACE",
    "QJACF,QJACF",
    "QJACG,QJACG",
    "QJACH,QJACH",
    "QJACI,QJACI",
    "QJACJ,QJACJ",
    "QJACK,QJACK",
    "QJACL,QJACL",
    "QJACM,QJACM",
    "QJACN,QJACN",
    "QJACO,QJACO",
    "QJACP,QJACP",
    "QJACQ,QJACQ",
    "QJACR,QJACR",
    "QJACS,QJACS",
    "QJACT,QJACT",
    "QJACU,QJACU",
    "QJACV,QJACV",
    "QJACW,QJACW",
    "QJACX,QJACX",
    "QJACY,QJACY",
    "QJACZ,QJACZ",
    "QJADA,QJADA",
    "QJADB,QJADB",
    "QJADC,QJADC",
    "QJADD,QJADD",
    "QJADE,QJADE",
    "QJADF,QJADF",
    "QJADG,QJADG",
    "QJADH,QJADH",
    "QJADI,QJADI",
    "QJADJ,QJADJ",
    "QJADK,QJADK",
    "QJADL,QJADL",
    "QJADM,QJADM",
    "QJADN,QJADN",
    "QJADO,QJADO",
    "QJADP,QJADP",
    "QJADQ,QJADQ",
    "QJADR,QJADR",
    "QJADS,QJADS",
    "QJADT,QJADT",
    "QJADU,QJADU",
    "QJADV,QJADV",
    "QJADW,QJADW",
    "QJADX,QJADX",
    "QJADY,QJADY",
    "QJADZ,QJADZ",
    "QEAAA,QEAAA",
    "QEAAB,QEAAB",
    "QEAAC,QEAAC",
    "QEAAD,QEAAD",
    "QEAAE,QEAAE",
    "QEAAF,QEAAF",
    "QEAAG,QEAAG",
    "QEAAH,QEAAH",
    "QEAAI,QEAAI",
    "QEAAJ,QEAAJ",
    "QEAAK,QEAAK",
    "QEAAL,QEAAL",
    "QEAAM,QEAAM",
    "QEAAN,QEAAN",
    "QEAAO,QEAAO",
    "QEAAP,QEAAP",
    "QEAAQ,QEAAQ",
    "QEAAR,QEAAR",
    "QEAAS,QEAAS",
    "QEAAT,QEAAT",
    "QEAAU,QEAAU",
    "QEAAV,QEAAV",
    "QEAAW,QEAAW",
    "QEAAX,QEAAX",
    "QEAAY,QEAAY",
    "QEAAZ,QEAAZ",
    "QEABA,QEABA",
    "QEABB,QEABB",
    "QEABC,QEABC",
    "QEABD,QEABD",
    "QEABE,QEABE",
    "QEABF,QEABF",
    "QEABG,QEABG",
    "QEABH,QEABH",
    "QEABI,QEABI",
    "QEABJ,QEABJ",
    "QEABK,QEABK",
    "QEABL,QEABL",
    "QEABM,QEABM",
    "QEABN,QEABN",
    "QEABO,QEABO",
    "QEABP,QEABP",
    "QEABQ,QEABQ",
    "QEABR,QEABR",
    "QEABS,QEABS",
    "QEABT,QEABT",
    "QEABU,QEABU",
    "QEABV,QEABV",
    "QEABW,QEABW",
    "QEABX,QEABX",
    "QEABY,QEABY",
    "QEABZ,QEABZ",
    "QEACA,QEACA",
    "QEACB,QEACB",
    "QEACC,QEACC",
    "QEACD,QEACD",
    "QEACE,QEACE",
    "QEACF,QEACF",
    "QEACG,QEACG",
    "QEACH,QEACH",
    "QEACI,QEACI",
    "QEACJ,QEACJ",
    "QEACK,QEACK",
    "QEACL,QEACL",
    "QEACM,QEACM",
    "QEACN,QEACN",
    "QEACO,QEACO",
    "QEACP,QEACP",
    "QEACQ,QEACQ",
    "QEACR,QEACR",
    "QEACS,QEACS",
    "QEACT,QEACT",
    "QEACU,QEACU",
    "QEACV,QEACV",
    "QEACW,QEACW",
    "QEACX,QEACX",
    "QEACY,QEACY",
    "QEACZ,QEACZ",
]
entries_str = "\n".join(entries)
data = {
    "name": "My Glossary",
    "source_lang": "en",
    "target_lang": "ja",
    "entries": entries_str,
    "entries_format": "csv"
}

# リクエストの送信
response = requests.post(url, headers=headers, data=json.dumps(data))

# レスポンスの確認
if response.status_code == 200:
    print("sucsess")
    print(response.json())
else:
    print("Error")
    print(f"state: {response.status_code}")
    print(f"response: {response.text}")

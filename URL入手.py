import requests

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
            doi = first_result.get("DOI")
            if doi:
                return f"https://doi.org/{doi}"  # DOIからURLを生成
    return "論文URLが見つかりませんでした。"

# 実行
paper_title = "A droplet-based electricity generator with high instantaneous power density"
paper_url = get_paper_url(paper_title)
print(f"論文URL: {paper_url}")

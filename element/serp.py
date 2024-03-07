import json
from serpapi import GoogleSearch
# import human_jp

serpapi_key = "" #serpAPIのキーを設定

def google_scholar_search(query, json_path):
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": serpapi_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results["organic_results"]

    # positionが0の結果のみを抽出
    position_0_results = [result for result in organic_results if result.get('position', -1) == 0]

    # すべての結果をリストにまとめる
    all_results = []

    for result in position_0_results:
        # 必要な情報を抽出して新しい辞書にまとめる
        new_result = {
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet"),
            "resources": [{"file_format": res.get("file_format"), "link": res.get("link")} for res in result.get("resources", [])],
            "cited_by": result.get("inline_links", {}).get("cited_by", {}).get("total")
        }
        all_results.append(new_result)

    if all_results:
        print(f"Query: {query}\nPosition 0 Results: {all_results}\n")

        # 既存のJSONファイルを読み込む
        existing_data = []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                print(existing_data)
        except json.decoder.JSONDecodeError:
            # ファイルが空または有効なJSONデータを含まない場合の処理
            pass

        # 既存のデータに新しいデータを結合する
        existing_data.extend(all_results)

        # 結果をJSONファイルに保存する（上書き保存）
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
    else:
        print(f"Query: {query}\nPosition 0 Results not found\n")

def delete_json(json_path):

    # 空のJSONデータを用意
    empty_data = []

    # 空のJSONデータをファイルに書き込んで上書きする
    with open(json_path, "w") as json_file:
        json.dump(empty_data, json_file)

    print("JSONファイルの中身を空にしました。")


if __name__ == "__main__":
    json_path = './data/exp/json/google_scholar_results_B2.json'
    delete_json(json_path)
    queries = [
        "SupportVectorMachineを用いた文書の重要文節抽出",
        "統計的手法に基づくWebページからのヘッドライン生成",
        "コーパスから自動抽出した表現パターンを用いる日本語文生成",
        "濃縮還元型文要約モデルの検討"
    ]
    for query in queries:
        google_scholar_search(query, json_path)

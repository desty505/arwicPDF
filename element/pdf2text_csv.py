import PyPDF2
import fitz  # PyMuPDF
import MeCab
import ipadic
import csv

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text += page.get_text()

    # 改行文字とスペースを削除
    text = text.replace("\n", "").replace(" ", "")

    return text

def pdf_to_csv(pdf_path, csv_path):
    text = extract_text_from_pdf(pdf_path)
    ppp=0
    # MeCabを初期化
    mecab = MeCab.Tagger(ipadic.MECAB_ARGS)
    
    a= []
    analyzed_text = set()  # 重複を防ぐためにsetを使用
    mecab_text = mecab.parse(text)
    # print(mecab_text)
    for word_info in mecab_text.split("\n"):
        if word_info == "EOS":
            continue
        # タブを検出して分割
        parts = word_info.split('\t')
        # print(parts)
        if len(parts) > 1:  # 要素数が1以上の場合のみ処理
            word = parts[0]
            info = parts[1]
            # print(info)
            pos = info.split(",")[0]
            if pos in ["名詞", "未知語"]:
                a.append(word)
                # すでに同じ単語が存在しない場合に追加
                if word not in analyzed_text:
                    analyzed_text.add(word)
                    
    # PDF内での座標とページ数を取得
    pdf_doc = fitz.open(pdf_path)
    page_info = []
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        for word in analyzed_text:
            for rect in page.search_for(word):
                x, y, x1, y1 = rect.x0, rect.y0, rect.x1, rect.y1
                width = x1 - x
                height = y1 - y
                page_info.append((word, (x, y, width, height), page_num + 1))
    
    # 結果をCSVファイルに書き出し
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Word", "X", "Y", "Width", "Height", "Page"])
        for word, bbox, page_num in page_info:
            x, y, width, height = bbox
            csv_writer.writerow([word, x, y, width, height, page_num])

if __name__ == "__main__":
    pdf_path = "../visualization_of_relation/data/sample/sample.pdf"
    csv_path = "../visualization_of_relation/data/word/pdf2text_PyMuPDF_a.csv"
    pdf_to_csv(pdf_path, csv_path)

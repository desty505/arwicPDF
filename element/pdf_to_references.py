from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdfminer.layout import LTPage
import re
import langid
import csv

def get_page_height(pdf_path):
    for page_layout in extract_pages(pdf_path):
        if isinstance(page_layout, LTPage):
            return page_layout.height  # 最初のページの高さのみを取得

    # PDFが空またはページが見つからない場合は、適切なエラー処理を行う
    raise ValueError("PDFにページが見つかりませんでした")


def extract_text_in_y_range(pdf_path, y_start, y_end):
    extracted_text = ''
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                _, y, _, _ = element.bbox  # Y座標のみを取得
                if y_start <= y <= y_end:
                    extracted_text += element.get_text()

    return extracted_text

def extract_references_in_range(pdf_path, y_start, y_end):
    text_in_y_range = extract_text_in_y_range(pdf_path, y_start, y_end)

    # 参考文献セクションの開始を検出
    references = []
    in_references_section = False
    reference_keywords = ['文献', '参考文献', 'reference', 'references']

    for line in text_in_y_range.split('\n'):
        line_processed = ''.join(line.lower().split())  # スペースを削除して小文字に変換した文字列を取得

        # キーワードが見つかったら参考文献セクションとして扱う
        if any(keyword in line_processed for keyword in reference_keywords) and line_processed in reference_keywords:
            in_references_section = True
            continue

        if in_references_section:
            references.append(line)

    return '\n'.join(references)

def is_english(text):
    language, confidence = langid.classify(text)
    return language == 'en'

def remove_newlines(text):
    processed_text = ""
    is_prev_english = False  # 直前のセグメントが英語かどうかを示すフラグ

    start_idx = 0
    for i in range(len(text)):
        segment = text[start_idx:i + 1]

        # 改行文字が出現した場合
        if text[i] == '\n':
            # 直前のセグメントがハイフンで終わる英語の場合、改行文字を削除
            if is_prev_english and text[i - 1] == '-':
                processed_text += text[start_idx:i - 1]  # ハイフンを除いて追加
            # 直前のセグメントが英語の場合、改行文字をスペースに置き換える
            elif is_prev_english:
                processed_text += text[start_idx:i] + ' '
            else:
                processed_text += text[start_idx:i]
            start_idx = i + 1  # 次のセグメントの開始位置を更新
            is_prev_english = False  # フラグをリセット

        # テキストの末尾に到達した場合
        if i == len(text) - 1:
            # 直前のセグメントがハイフンで終わる英語の場合、改行文字を削除
            if is_prev_english and text[i] == '-':
                processed_text += text[start_idx:i]  # ハイフンを除いて追加
            # 直前のセグメントが英語の場合、改行文字をスペースに置き換える
            elif is_prev_english:
                processed_text += text[start_idx:i + 1] + ' '
            else:
                processed_text += text[start_idx:]

        # テキストが英語かどうかを判定
        if is_english(segment):
            is_prev_english = True
        else:
            is_prev_english = False

    return processed_text


def remove_empty_lines(input_text):
    lines = input_text.split('\n')  # テキストを行に分割

    # 空の行を削除
    non_empty_lines = [line for line in lines if line.strip() != '']

    # 改行文字を使ってテキストに戻す
    cleaned_text = '\n'.join(non_empty_lines)
    
    return cleaned_text

def extract_text_until_language(text):
    # ひらがな、カタカナ、漢字、英語の文字が最初に出現する位置を探す正規表現
    match = re.search(r'[ぁ-んァ-ン一-龯a-zA-Z]', text)

    if match:
        first_language_index = match.start()
        extracted_text = text[:first_language_index]
        return extracted_text
    else:
        # ひらがな、カタカナ、漢字、英語の文字が見つからない場合、元のテキストを返す
        return text

def extract_list(text, pattern):
    """
    テキストを与えられたパターンに基づいて分割し、パターンに一致する部分をリスト化する関数
    """
    # テキストをパターンに基づいて分割
    pattern_sections = re.split(pattern, text)

    # パターンに一致する部分を削除してリスト化
    result = [section for section in pattern_sections if section and not re.match(pattern, section)]

    return result

def patterning_text(text):
    """
    テキスト内の各文字を処理する関数
    数字の場合は `\d+` に置き換え、それ以外の場合はその文字の前に `\` を付ける
    """
    processed_text = ''

    for char in text:
        if char.isdigit():
            processed_text += r'\d+'
        else:
            processed_text += '\\' + char

    return processed_text

def pick_pattern(text):
    """
    箇条書きパターンを取り出す関数
    ひらがな、カタカナ、漢字、英語の文字が最初に出現する位置を探す正規表現
    """
    match = re.search(r'[ぁ-んァ-ン一-龠a-zA-Z]', text)

    if match:
        first_language_index = match.start()
        extracted_text = text[:first_language_index]
        return extracted_text
    else:
        # ひらがな、カタカナ、漢字、英語の文字が見つからない場合、元のテキストを返す
        return text

def make_reference_list(text):
    text = str(text)  # 必要に応じて文字列に変換

    pattern_text = pick_pattern(text)
    pattern = patterning_text(pattern_text)

    result = extract_list(text, pattern)

    return result

def pick_reference_list(pdf_path):
    # pdfの高さを取得
    height = get_page_height(pdf_path)
    remove_area = height * 0.055
    min_area = remove_area
    max_area = height - remove_area

    # pdfから参考文献を抽出
    references = extract_references_in_range(pdf_path, min_area, max_area)
    
    # 空の行を削除
    no_empty_references = remove_empty_lines(references)

    # 改行を削除
    cleaned_references = remove_newlines(no_empty_references)

    # 文献ごとにリスト化
    result = make_reference_list(cleaned_references)

    return result

def save_to_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        for item in data:
            csv_writer.writerow([item])

if __name__ == "__main__":
    # PDFファイルのパスを指定して参考文献を抽出
    pdf_path = './data/sample/sample.pdf'
    result = pick_reference_list(pdf_path)

    print(result)

    # CSVファイルに出力
    csv_file_path = './data/output/references.csv'
    save_to_csv(csv_file_path, result)
    print(f"結果を {csv_file_path} に保存しました")

    # text="一[1]"
    # pick = pick_pattern(text)
    # print(pick)
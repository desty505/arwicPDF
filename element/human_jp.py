import MeCab
import re
import csv

def remove_specific_names(text):
    tagger = MeCab.Tagger('ここにパスおを設定 README.mdを参照')

    parsed_text = tagger.parse(text)
    
    cleaned_text = ''
    
    lines = parsed_text.split('\n')
    for line in lines:
        if '固有名詞' not in line or '人名' not in line:
            word = line.split('\t')[0]
            if word != 'EOS':
                cleaned_text += word
    
    return cleaned_text

# 英語のテキストから人名を抽出して削除する関数
def remove_english_names(text):
    # テキストをトークン化し、品詞タグ付け
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    
    # 人名（固有名詞）を除外して残りの単語を抽出
    filtered_words = [word for word, tag in tagged_words if tag != 'NNP' and tag != 'NNPS']
    
    # 単語をスペースで結合して新しいテキストを作成
    cleaned_text = ' '.join(filtered_words)
    return cleaned_text

def extract_string(text):
    pattern = "([^,:.\s-]+)"
    matches = re.findall(pattern, text)

    filtered_list = [item for item in matches if not all(c.isdigit() or c == '-' for c in item)]

    # print(filtered_list)

    # スペースで結合して最初の要素を取得
    extracted_string = ' '.join(matches)  # 6つの単語を抽出する例

    return extracted_string

# def extract_longest_words(text):
#     words = re.findall(r'\S+', text)  # スペースで区切られた単語を抽出
#     words.sort(key=len, reverse=True)  # 文字数の大きい順にソート

#     top_three_words = words[:2]  # 文字数の大きい上位3つの単語を取得
#     concatenated_string = ' '.join(top_three_words)  # 上位3つの単語をスペースで連結して1つの文字列にする

#     return concatenated_string  # 1つの文字列として返す

def extract_longest_words(text):
    words = re.findall(r'\S+', text)  # スペースで区切られた単語を抽出
    if not words or len(words) < 2:
        return None

    # 要素とそのインデックスのペアのリストを作成
    indexed_strings = list(enumerate(words))

    # 文字列の長さに基づいて降順でソート
    sorted_strings = sorted(indexed_strings, key=lambda x: len(x[1]), reverse=True)

    # 上位2つの要素のインデックスを取得
    n1, n2 = sorted_strings[0][0], sorted_strings[1][0]

    # n1 と n2 のうち小さいほうのインデックスを出力
    smallest_index = min(n1, n2)

    return words[smallest_index]

def process_csv_file(file_path):
    cleaned_text3_list = []  # cleaned_text3 を格納するためのリスト

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > 0:
                # CSVファイルの各行からテキストを取得
                text = row[0].replace(" ", "")
                # print(text)
                # 各処理関数を適用
                cleaned_text = remove_specific_names(text)
                cleaned_text2 = extract_string(cleaned_text)
                cleaned_text3 = extract_longest_words(cleaned_text2)

                # cleaned_text3 をリストに追加
                cleaned_text3_list.append(cleaned_text3)

    return cleaned_text3_list

# japanese_text = "黒橋禎夫: 情報の信頼性評価に関する基盤技術の研究開発,人工知能学会誌, Vol.23, No.6, pp.783-790, 2008ù"

# cleaned_text = remove_specific_names(japanese_text)
# print(cleaned_text)
# cleaned_text2 = extract_string(cleaned_text)
# print(cleaned_text2)  # 人名と思われる固有名詞を削除したテキストを出力
# cleaned_text3 = extract_longest_words(cleaned_text2)
# print(cleaned_text3)

if __name__ == "__main__":
    # CSVファイルのパスを指定して処理を実行
    csv_file_path = './data/output/references.csv'  # 実際のファイルパスに置き換えてください
    result_list = process_csv_file(csv_file_path)

    # 結果の出力
    print("Cleaned Text 3 List:")
    for item in result_list:
        print(item)

import csv

# def clean_rows_first_column(input_csv_path, output_csv_path):
#     # CSVファイルを読み込み、数字で始まる行を削除して新しいCSVファイルに書き込む
#     with open(input_csv_path, 'r', newline='', encoding='utf-8') as input_file, \
#      open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:
        
#         csv_reader = csv.reader(input_file)
#         csv_writer = csv.writer(output_file)
        
#         for row in csv_reader:
#             # 1列目が数字でない場合にのみ行を新しいCSVに書き込む
#             if not row[0].isdigit():
#                 csv_writer.writerow(row)

def clean_rows_first_column(input_csv_path, output_csv_path):
    # CSVファイルを読み込み、数字または1文字のアルファベットで始まる行を削除して新しいCSVファイルに書き込む
    with open(input_csv_path, 'r', newline='', encoding='utf-8') as input_file, \
         open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:

        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)

        for row in csv_reader:
            # 1列目が数字かつ1文字のアルファベットでない場合にのみ行を新しいCSVに書き込む
            if not (row[0].isdigit() or (len(row[0]) == 1 and row[0].isalpha())):
                csv_writer.writerow(row)

if __name__ == "__main__":
    input_csv_path = "../visualization_of_relation/data/word/pdf2text_PyMuPDF_a.csv"  # 入力CSVファイルのパスを指定
    output_csv_path = "../visualization_of_relation/data/word/cut_pdf2text_PyMuPDF_a.csv"  # 出力CSVファイルのパスを指定
    clean_rows_first_column(input_csv_path, output_csv_path)

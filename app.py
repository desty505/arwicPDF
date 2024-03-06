import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os, csv, webbrowser, json
import requests
import time
import threading
import element.pdf_to_references as ptr
import element.csv_cut as cc
import element.serp as serp
import element.pdf2text_csv as p2t
import element.human_jp as hj


text_csv_path = "data/PDF_text.csv"
clean_text_csv_path = "data/cut_PDF_text.csv"
ref_csv_path = "data/references.csv"
json_path = "data/google_scholar.json"

class PDFSelectWindow:
    def __init__(self, root, pdf_viewer_class):
        self.root = root
        self.root.title("PDFファイルを選択")
        self.root.geometry("400x300")  # ウィンドウの初期サイズを設定

        self.pdf_path = tk.StringVar()  # PDFファイルのパスを格納する変数
        self.current_page = 0  # 現在表示中のページ番号

        self.pdf_viewer_class = pdf_viewer_class # pdfを表示するクラス

        self.create_widgets()

    def create_widgets(self):
        # PDFファイルパス入力用ラベル
        label = ttk.Label(self.root, text="PDF File Path:")
        label.pack(padx=10, pady=5)

        # PDFファイルパス入力用エントリー
        pdf_entry = ttk.Entry(self.root, textvariable=self.pdf_path)
        pdf_entry.pack(fill=tk.X, padx=10, pady=5)

        # ファイル参照ボタン
        browse_button = ttk.Button(self.root, text="ファイルを選ぶ", command=self.browse_pdf)
        browse_button.pack(padx=10, pady=5)

        # PDFファイルを開くボタン
        open_button = ttk.Button(self.root, text="PDFを開く", command=self.open_pdf)
        open_button.pack(padx=10, pady=5)
        
        # ドラッグアンドドロップの設定
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def browse_pdf(self):
        # ファイル参照ダイアログを表示してPDFファイルを選択
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path.set(file_path)

    def open_pdf(self):
        # 入力されたPDFファイルを開いて表示
        pdf_path = self.pdf_path.get()
        if pdf_path:
            p2t.pdf_to_csv(pdf_path, text_csv_path)
            cc.clean_rows_first_column(text_csv_path, clean_text_csv_path)
            
            result = ptr.pick_reference_list(pdf_path)
            ptr.save_to_csv(ref_csv_path, result)
            queries = hj.process_csv_file(ref_csv_path)
            serp.delete_json(json_path)
            for query in queries:
                    serp.google_scholar_search(query, json_path)

            # PDFファイルが選択された場合、新しいウィンドウを作成して表示
            pdf_viewer_window = tk.Toplevel(self.root)
            pdf_viewer = self.pdf_viewer_class(pdf_viewer_window, pdf_path)

    def prev_page(self):
        # 前のページを表示
        self.show_page(self.current_page - 1)

    def next_page(self):
        # 次のページを表示
        self.show_page(self.current_page + 1)

    def on_drop(self, event):
        # ドラッグアンドドロップでファイルを読み込む
        file_path = event.data
        normalized_path = os.path.normpath(file_path)   # ファイルのパスを正規化する
        new_file_path = normalized_path[1:-1]   # 取得したファイルパスの不要な部分を削除
        
        if os.path.isfile(new_file_path) and new_file_path.lower().endswith('.pdf'):
            self.pdf_path.set(new_file_path)


    # def on_click(self, event):
    #     x, y = event.x_root, event.y_root
    #     canvas_pos_x = self.canvas.winfo_rootx()  # Canvasのx座標の絶対位置を取得
    #     canvas_pos_y = self.canvas.winfo_rooty()  # Canvasのy座標の絶対位置を取得
    #     x -= canvas_pos_x  # ウィンドウ移動量を考慮して座標を調整
    #     y -= canvas_pos_y
    #     with open('cut_pdf2text.csv', newline='', encoding='utf-8') as csvfile:
    #         csv_reader = csv.reader(csvfile)
    #         next(csv_reader)  # 1行目を読み飛ばす
    #         for row in csv_reader:
    #             word, x_coord, y_coord, width, height, page_num = row
    #             if int(page_num) == self.current_page + 1:
    #                 if float(x_coord) <= x <= float(x_coord) + float(width) and float(y_coord) <= y <= float(y_coord) + float(height):
    #                     print(f"Selected word: {word}")
    #                     # ここに選択された単語に対する処理を追加

    # def on_click(self, event):
    #     x, y = event.x_root, event.y_root
    #     canvas_pos_x = self.canvas.winfo_rootx()  # Canvasのx座標の絶対位置を取得
    #     canvas_pos_y = self.canvas.winfo_rooty()  # Canvasのy座標の絶対位置を取得
    #     x -= canvas_pos_x  # ウィンドウ移動量を考慮して座標を調整
    #     y -= canvas_pos_y
    #     with open('output.csv', newline='', encoding='utf-8') as csvfile:
    #         csv_reader = csv.reader(csvfile)
    #         next(csv_reader)  # 1行目を読み飛ばす
    #         for row in csv_reader:
    #             word, x_coord, y_coord, width, height, page_num = row
    #             if int(page_num) == self.current_page + 1:
    #                 if float(x_coord) <= x <= float(x_coord) + float(width) and float(y_coord) <= y <= float(y_coord) + float(height):
    #                     print(f"Selected word: {word}{x_coord}{y_coord}")
    #                     # 選択されたエリアを強調表示する
    #                     self.highlight_area(float(x_coord), float(y_coord), float(width), float(height))

    # def highlight_area(self, x, y, width, height):
    #     self.canvas.delete("highlight")  # 以前の強調表示を削除
    #     self.canvas.create_rectangle(x, y, x + width, y + height, outline="red", tags="highlight")

class PDFViewerWindow:
    def __init__(self, root, pdf_path):
        self.root = root
        self.root.title("PDF Viewer")
        self.root.geometry("800x600")

        # フレームを作成し、グレーの背景色と線の追加
        self.frame1 = tk.Frame(self.root, bg="#CCCCCC", bd=2)
        self.frame2 = tk.Frame(self.root, bg="#CCCCCC", bd=2)
        self.frame3 = tk.Frame(self.root, bg="#CCCCCC", bd=2)

        self.ref_data_list = []
        self.ref_data_list = self.extract_information(json_path)

        print("data:",self.ref_data_list)

        # # フレーム内の行にウェイトを設定
        # self.frame2.grid_rowconfigure(0, weight=9)  # 1行目のウェイトを9に設定
        # self.frame2.grid_rowconfigure(1, weight=1)  # 2行目のウェイトを1に設定

        # ウィンドウのサイズ変更を検知するイベントを設定
        self.root.bind("<Configure>", self.on_window_resize)

        # フレームの初期配置
        self.place_frames()

        # フレーム内のコンテナを作成
        self.create_sub_containers()

        # # キャンバス内のウィジェットのバインディング
        # self.canvas.bind('<Configure>', self.on_canvas_configure)

        # # フレーム1_1にスライダーを配置
        # self.create_frame1_1()

        # フレーム1_2にテキストを表示するラベルを配置
        self.create_frame1_2()
        
        # # フレーム1の上部にバーを配置
        # self.bar = tk.Scale(self.frame1, orient="horizontal")
        # self.bar.pack(side=tk.TOP, fill=tk.X)
        
        # # フレーム1の下部に複数のテキストを表示するラベルを配置
        # self.label1 = tk.Label(self.frame1, text="Label 1")
        # self.label1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # フレーム2で表示するPDFファイルのパス
        self.pdf_path = pdf_path  # 表示するPDFファイルのパスを指定してください
        self.current_page = 0  # 現在のページ
        self.pdf_document = fitz.open(self.pdf_path) # PDFファイルを開く
        self.max_page = self.pdf_document.page_count # ページ数
        
        # PDFを表示
        self.show_pdf_page(self.current_page)
        
        # フレーム2の下部にページ切り替えボタンを設定
        self.prev_page_button = ttk.Button(self.frame2_2, text="前のページ", command=self.prev_page)
        self.prev_page_button.pack(side=tk.LEFT, padx=150)  # 左寄せ

        self.next_page_button = ttk.Button(self.frame2_2, text="次のページ", command=self.next_page)
        self.next_page_button.pack(side=tk.RIGHT, padx=150)  # 右寄せ
        
        # # フレーム3の上部に複数行のテキストを表示するラベルを配置
        # self.label2 = tk.Label(self.frame3_1, text="Label 2")
        # self.label2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # フレーム3の内容
        self.create_frame3_1()
        self.create_frame3_2()

        # Canvasにクリックイベントをバインド
        self.canvas.bind("<Button-1>", self.on_click)

        # # ウィンドウのリサイズに対応する
        # self.root.grid_columnconfigure(0, weight=1)

    def show_pdf_page(self, page_num):
        # ページを取得
        page = self.pdf_document.load_page(page_num)

        # Canvasのサイズ
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # PDFのサイズ
        pdf_width = page.rect.width
        pdf_height = page.rect.height

        # # 縦横比を保ちつつ、Canvasの横幅に合わせるためのMatrixを計算
        self.scale_factor = canvas_width / pdf_width

        # 縦横比を保ちつつ、Canvasの横幅に合わせるためのMatrixを計算
        # self.scale_factor = canvas_height / pdf_height

        matrix = fitz.Matrix(self.scale_factor, self.scale_factor)

        # ページの画像を描画
        pix = page.get_pixmap(matrix=matrix)

        # PILでImageを作成
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((canvas_width, int(pdf_height * self.scale_factor)))
        # img = img.resize((int(pdf_width * self.scale_factor), canvas_height))

        # ImageTkでCanvasに表示するImageを作成
        img_tk = ImageTk.PhotoImage(img)

        # CanvasにImageを描画（self.canvasに描画）め
        self.canvas.create_image(0, 0, anchor='nw', image=img_tk)
        self.canvas.image = img_tk  # ガベージコレクションを防ぐために参照を保持する

    def prev_page(self):
        if self.current_page > 0:
            # 前のページを表示
            self.current_page -= 1
            self.show_pdf_page(self.current_page)
            print(self.current_page)

    def next_page(self):
        if self.current_page < self.max_page - 1:
            # 次のページを表示
            self.current_page += 1
            self.show_pdf_page(self.current_page)
            print(self.current_page)

    def place_frames(self):
        # フレームの配置
        self.frame1.place(x=0, y=0, relwidth=0.3, relheight=1)
        self.frame2.place(x=0.3, y=0, relwidth=0.4, relheight=1)
        self.frame3.place(x=0.7, y=0, relwidth=0.3, relheight=1)

    # ウィンドウのサイズ変更を検知してキャンバスのサイズをフレームのサイズに合わせる
    def on_window_resize(self, event):
        window_width = event.width
        window_height = event.height

        # フレームの再配置
        self.frame1.place_configure(relwidth=0.3, relheight=1)
        self.frame2.place_configure(relx=0.3, relwidth=0.4, relheight=1)
        self.frame3.place_configure(relx=0.7, relwidth=0.3, relheight=1)

        # # キャンバスのサイズをフレームのサイズに合わせて再設定
        # self.canvas.config(width=self.frame2_1.winfo_width(), height=self.frame2_1.winfo_height())

        # PDF画像を再度表示
        self.show_pdf_page(self.current_page)

        # ウィンドウのサイズを取得
        # windowWidth = event.width
        # windowHeight = event.height

        # print("ウィンドウの幅:", windowWidth)
        # print("ウィンドウの高さ:", windowHeight)

    def create_sub_containers(self):
        # フレーム1内のコンテナを作成
        self.frame1_1 = tk.Frame(self.frame1, bg="white")
        self.frame1_1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.frame1_1.place_configure(relwidth=1.0, relheight=0.5)
        
        self.frame1_2 = tk.Frame(self.frame1, bg="white")
        self.frame1_2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.frame1_2.place_configure(rely=0.5, relwidth=1.0, relheight=0.5)
        

        # frame2内に2つのフレームを配置
        self.frame2_1 = tk.Frame(self.frame2)
        self.frame2_2 = tk.Frame(self.frame2)
        # # frame2の1行目にframe2_1を配置（9:1の比率）
        # self.frame2_1.grid(row=0, sticky='nesw')
        # # frame2の2行目にframe2_2を配置
        # self.frame2_2.grid(row=1, sticky='nesw')

        # フレームの再配置
        pdf_view_size = 0.97

        self.frame2_1.place_configure(relwidth=1.0, relheight=pdf_view_size)
        self.frame2_2.place_configure(rely=pdf_view_size, relwidth=1.0, relheight=1.00-pdf_view_size)


        # フレーム2_1にCanvasを配置
        self.canvas = tk.Canvas(self.frame2_1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # # 垂直方向のスクロールバーを作成
        # self.vscrollbar = ttk.Scrollbar(self.frame2_1, orient="vertical", command=self.canvas.yview)
        # self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # # スクロールバーとCanvasを紐付け
        # self.canvas.configure(yscrollcommand=self.vscrollbar.set)
        
        # フレーム3内のコンテナを作成
        self.frame3_1 = tk.Frame(self.frame3, bg="white", relief=tk.RAISED, bd=2)
        self.frame3_1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.frame3_1.place_configure(relwidth=1.0, relheight=0.5)
        
        self.frame3_2 = tk.Frame(self.frame3, bg="white", relief=tk.RAISED, bd=2)
        self.frame3_2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.frame3_2.place_configure(rely=0.5, relwidth=1.0, relheight=0.5)

    def create_frame1_1(self):
        # フレーム1_1にスライダーを配置
        self.slider = tk.Scale(self.frame1_1, orient="horizontal")
        self.slider.pack(side=tk.TOP, fill=tk.X)

    def create_frame1_2(self):
        # # フレーム1_2にテキストを表示するラベルを配置
        # self.text_label = tk.Label(self.frame1_2, text="Text Label", bg="white", font=("MS ゴシック", 12))
        # self.text_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.Lframe1_2 = tk.LabelFrame(self.frame1_2, text="名詞情報", labelanchor="nw", relief=tk.RAISED, bd=2)
        self.Lframe1_2.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor="n")
        self.Lframe1_2.place_configure(relwidth=1.0, relheight=1.0)
        self.word_label = tk.Message(self.Lframe1_2, text="名詞を選択してください", font=("",12), width=500)
        self.word_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_frame3_1(self):
        # frame3_1_1
        self.frame3_1_1 = tk.LabelFrame(self.frame3_1, text="引用論文選択", labelanchor="nw", relief=tk.RAISED, bd=2)
        self.frame3_1_1.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor="n")
        self.frame3_1_1.place_configure(relwidth=1.0, relheight=0.7)

        # frame3_1_2
        self.frame3_1_2 = tk.LabelFrame(self.frame3_1, text="メッセージ", labelanchor="nw", relief=tk.RAISED, bd=2)
        self.frame3_1_2.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor="n")
        self.frame3_1_2.place_configure(rely=0.7, relwidth=1.0, relheight=0.15)

        # frame3_1_3
        self.frame3_1_3 = tk.LabelFrame(self.frame3_1, text="操作ボタン", labelanchor="nw", relief=tk.RAISED, bd=2)
        self.frame3_1_3.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor="n")
        self.frame3_1_3.place_configure(rely=0.85, relwidth=1.0, relheight=0.15)

        self.selected_data = tk.StringVar()
        self.selected_data.set(0)

        style = ttk.Style()

        # ラジオボタン用のスタイルを設定
        style.configure("TRadiobutton", font=("", 10))  # フォントとサイズを指定

        for index, item in enumerate(self.ref_data_list, start=1):
            self.radio_button = ttk.Radiobutton(self.frame3_1_1, text=f"{index}. {item['title']}", variable=self.selected_data, value=index, style="TRadiobutton")
            self.radio_button.pack(anchor="w", padx=10, pady=5)

        self.ref_error_label = tk.Label(self.frame3_1_2, text="論文を選択してください")
        self.ref_error_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.google_scholar_button = ttk.Button(self.frame3_1_3, text="論文ページを開く", command=lambda: self.open_link(self.ref_data_list[int(self.selected_data.get()) - 1]['link']))
        self.google_scholar_button.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.pdf_button = ttk.Button(self.frame3_1_3, text="PDFを表示", command=lambda: self.open_link(self.ref_data_list[int(self.selected_data.get()) - 1]['resource_link']))
        self.pdf_button.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        # 概要表示ボタン
        self.display_snippet_button = ttk.Button(self.frame3_1_3, text="概要を表示", command=self.display_snippet)
        self.display_snippet_button.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

    def create_frame3_2(self):
        self.frame3_2_1 = tk.LabelFrame(self.frame3_2, text="概要", labelanchor="nw", relief=tk.RAISED, bd=2)
        self.frame3_2_1.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor="n")
        self.frame3_2_1.place_configure(relwidth=1.0, relheight=1.0)
        self.snippet_label = tk.Message(self.frame3_2_1, text="論文を選択してください", font=("",12), width=500)
        self.snippet_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def open_link(self, link):
        if link:
            webbrowser.open(link)
            self.ref_error_label.config(text=link+"を開きました")
        else:
            self.ref_error_label.config(text="URLが存在しませんでした")

    # def display_snippet(self):
    #     index = int(self.selected_data.get()) - 1
    #     snippet = self.ref_data_list[index].get('snippet', '参考文献の概要が存在しませんでした')
    #     self.ref_error_label.config(text="参考文献の概要が存在しませんでした")
    #     self.snippet_label.config(text=snippet)
    #     print(self.frame3_1.winfo_height)
    
    def display_snippet(self):
        index = int(self.selected_data.get()) - 1
        
        # 選択されたデータが存在するか確認
        if 0 <= index < len(self.ref_data_list):
            data = self.ref_data_list[index]
            
            # 'snippet' キーが存在するか確認
            if 'snippet' in data:
                snippet = data['snippet']
                self.ref_error_label.config(text="「"+data['title']+"」"+"の概要を表示しました")
                self.snippet_label.config(text=snippet)
            else:
                # 'snippet' キーが存在しない場合の処理
                self.ref_error_label.config(text="参考文献の概要が存在しませんでした")
                self.snippet_label.config(text="")
        else:
            # 選択されたデータが存在しない場合の処理
            self.ref_error_label.config(text="参考文献の概要が存在しませんでした")
            self.snippet_label.config(text="")

    # def on_click(self, event):
    #     x, y = event.x_root, event.y_root
    #     canvas_pos_x = self.canvas.winfo_rootx()  # Canvasのx座標の絶対位置を取得
    #     canvas_pos_y = self.canvas.winfo_rooty()  # Canvasのy座標の絶対位置を取得
    #     x -= canvas_pos_x  # ウィンドウ移動量を考慮して座標を調整
    #     y -= canvas_pos_y
    #     with open('../visualization_of_relation/data/word/cut_pdf2text_PyMuPDF9.csv', newline='', encoding='utf-8') as csvfile:
    #         csv_reader = csv.reader(csvfile)
    #         next(csv_reader)  # 1行目を読み飛ばす
    #         for row in csv_reader:
    #             word, x_coord, y_coord, width, height, page_num = row
    #             if int(page_num) == self.current_page + 1:
    #                 if float(x_coord) <= x/self.scale_factor <= float(x_coord) + float(width) and float(y_coord) <= y/self.scale_factor <= float(y_coord) + float(height):
    #                     print(f"Selected word: {word}{x_coord}{y_coord}")
    #                     # 選択されたエリアを強調表示する
    #                     self.canvas.delete("highlight")  # 以前の強調表示を削除
    #                     self.canvas.create_rectangle(float(x_coord)*self.scale_factor, 
    #                                                 float(y_coord)*self.scale_factor, 
    #                                                 float(x_coord)*self.scale_factor + float(width)*self.scale_factor, 
    #                                                 float(y_coord)*self.scale_factor + float(height)*self.scale_factor, 
    #                                                 outline="red", tags="highlight")
    #                     self.highlight_area(float(x_coord)*self.scale_factor, 
    #                                         float(y_coord)*self.scale_factor, 
    #                                         float(width)*self.scale_factor, 
    #                                         float(height)*self.scale_factor)
    #                     time.sleep(0.1)
    #                     data = self.get_wiki_data(word)
    #                     self.word_label.config(text=data)
                        
                        # time.sleep(0.1)
                        # self.highlight_area(float(x_coord)*self.scale_factor, float(y_coord)*self.scale_factor, float(width)*self.scale_factor, float(height)*self.scale_factor)
        
    def highlight_area(self, x, y, width, height):
        self.canvas.delete("highlight")  # 以前の強調表示を削除
        self.canvas.create_rectangle(x, y, x + width, y + height, outline="red", tags="highlight")

    def on_click(self, event):
        x, y = event.x_root, event.y_root
        canvas_pos_x = self.canvas.winfo_rootx()  # Canvasのx座標の絶対位置を取得
        canvas_pos_y = self.canvas.winfo_rooty()  # Canvasのy座標の絶対位置を取得
        x -= canvas_pos_x  # ウィンドウ移動量を考慮して座標を調整
        y -= canvas_pos_y
        with open(clean_text_csv_path, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # 1行目を読み飛ばす
            for row in csv_reader:
                word, x_coord, y_coord, width, height, page_num = row
                if int(page_num) == self.current_page + 1:
                    if float(x_coord) <= x/self.scale_factor <= float(x_coord) + float(width) and float(y_coord) <= y/self.scale_factor <= float(y_coord) + float(height):
                        print(f"Selected word: {word} {x_coord} {y_coord}")
                        # # 選択されたエリアを強調表示する
                        # self.highlight_area(float(x_coord)*self.scale_factor, float(y_coord)*self.scale_factor, float(width)*self.scale_factor, float(height)*self.scale_factor)
                        
                        # data = self.get_wiki_data(word)
                        # self.word_label.config(text=data)
                        # バックグラウンドスレッドを開始
                        threading.Thread(target=self.process_click, args=(word, float(x_coord)*self.scale_factor, float(y_coord)*self.scale_factor, float(width)*self.scale_factor, float(height)*self.scale_factor)).start()

    def remove_highlight(self):
        self.canvas.delete("highlight")  # 強調表示を削除

    def process_click(self, word, x, y, w, h):
        # 選択されたエリアを強調表示する
        self.highlight_area(x, y, w, h)
        
        # データを取得してラベルを更新
        data = self.get_wiki_data(word)
        self.word_label.config(text=data)

        # 選択されたエリアを強調表示する
        self.highlight_area(x, y, w, h)

    def extract_information(self, json_file_path):
        # ファイル読み込み
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            print("ok1:",json_data)
        except FileNotFoundError:
            print(f"File not found: {json_file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {json_file_path}")
            return {}

        # データが存在しない場合や指定の条件を満たすものがない場合は空の辞書を返す
        if not json_data or not isinstance(json_data, list):
            return {}

        # 全体のリストを初期化
        output_data = []

        for item in json_data:
            # 各データごとの辞書を初期化
            output_item = {}

            # 必要な情報を抽出
            output_item["title"] = item.get("title", "")
            output_item["link"] = item.get("link", "")
            output_item["snippet"] = item.get("snippet", "")

            resources = item.get("resources", [])
            if resources:
                resource = resources[0]
                output_item["file_format"] = resource.get("file_format", "")
                if output_item["file_format"] == "PDF":
                    output_item["resource_link"] = resource.get("link", "")
                else:
                    output_item["resource_link"] = ""
            else:
                output_item["file_format"] = ""
                output_item["resource_link"] = ""

            cited_by = item.get("inline_links", {}).get("cited_by", {})
            output_item["total_cited_by"] = cited_by.get("total", 0)
            output_item["cited_by_link"] = cited_by.get("link", "")

            # 辞書をリストに追加
            output_data.append(output_item)

        return output_data

    def get_wiki_data(self, word):
        try:
            # time.sleep(0.1)
            data = [None, None]  # 初期化

            # 例: JSONデータを取得するURL
            url = f"https://ja.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&redirects=1&titles={word}&format=json"
            # URLからデータを取得
            response = requests.get(url)
            
            # HTTPステータスコードが200 (成功) の場合
            if response.status_code == 200:
                # JSONデータを辞書型に変換
                json_data = response.json()
                page_id = next(iter(json_data['query']['pages']))

                print(page_id)
                # ページIDに基づいて 'title' と 'extract' を取得
                page_data = json_data['query']['pages'][page_id]
                title = page_data['title']
                # extract = page_data['extract'].replace('\n', '')
                extract = page_data['extract']
                data[0] = title
                data[1] = extract
                # print(title+": "+extract)
                result = f"選択された単語:{data[0]} \n\n{data[1]}"
                print(result)
                return result
            else:
                print(f"HTTPリクエストエラー: {response.status_code}")
                data = "情報を抽出できませんでした"
                return data
        except Exception as e:
            data = "情報を抽出できませんでした2"
            return data

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFSelectWindow(root, PDFViewerWindow)
    root.mainloop()

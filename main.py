import tkinter as tk
from tkinter import scrolledtext
import spacy
from PIL import Image, ImageTk
import customtkinter as ctk
from googletrans import Translator
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import defaultdict
from string import punctuation
from heapq import nlargest

# Tải mô hình tiếng Anh của spaCy
nlp = spacy.load("en_core_web_sm")

class TextSummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        # Khởi tạo các thông số cho TextSummarizer
        self._min_cut = min_cut
        self._max_cut = max_cut 
        self._stopwords = set(stopwords.words('english') + list(punctuation))

    def _compute_frequencies(self, word_sent):
        # Tính tần suất xuất hiện của các từ
        freq = FreqDist(word_sent)
        m = float(max(freq.values()))
        for word in list(freq.keys()):
            freq[word] = freq[word]/m
            if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
                del freq[word]
        return freq

    def summarize(self, text, n):
        # Rút tóm tắt văn bản
        sents = sent_tokenize(text)
        n = min(n, len(sents))  # Đảm bảo không vượt quá số lượng câu
        assert n <= len(sents)
        word_sent = [word for word in word_tokenize(text.lower()) if word not in self._stopwords]
        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i, sent in enumerate(sents):
            for word in word_tokenize(sent.lower()):
                if word in self._freq:
                    ranking[i] += self._freq[word]
        sents_idx = nlargest(n, ranking, key=ranking.get)
        return [sents[j] for j in sorted(sents_idx)]


class MyApplication:
    def __init__(self, root):
        # Khởi tạo ứng dụng
        self.root = root
        self.root.title("Trích dẫn đoạn văn")
        
        # Thiết lập kích thước mặc định cho cửa sổ
        self.root.geometry("1200x600")
        
        # Thay đổi dòng này để sử dụng tệp .ico
        self.root.iconbitmap('icon.ico')
        
        # Thêm ô văn bản
        self.text_entry = ctk.CTkTextbox(root, width=500, height=300, wrap="word")  # Sử dụng wrap="word" để co giãn linh hoạt
        self.text_entry.pack(pady=10)
        
        # Thêm checkbox "Dịch sang tiếng Việt"
        self.translate_checkbox_var = tk.IntVar()
        translate_checkbox = ctk.CTkCheckBox(root, text="Dịch sang tiếng Việt", variable=self.translate_checkbox_var)
        translate_checkbox.pack(pady=5)
        
        # Thêm thanh trượt để điều chỉnh số lượng ý chính
        self.summary_length_var = tk.IntVar(value=5)  # Giá trị mặc định là 5
        summary_length_slider = tk.Scale(root, from_=1, to=10, variable=self.summary_length_var, orient="horizontal")
        summary_length_slider.pack(pady=5)

        # Thêm nút gửi
        send_button = ctk.CTkButton(root, text="Rút ý chính", command=self.extract_summary)
        send_button.pack(pady=10)
        
        # Thêm nút thoát ở góc dưới bên phải
        exit_button = ctk.CTkButton(root, text="Thoát", command=self.quit_application)
        exit_button.pack(side=ctk.BOTTOM, anchor=ctk.SE, padx=10, pady=10)
    
    def extract_summary(self):
        # Xử lý logic khi nút "Rút ý chính" được nhấn
        text = self.text_entry.get("1.0", ctk.END)
        summary_length = self.summary_length_var.get()  # Lấy giá trị từ thanh trượt
        summary = self.summarize_text(text, summary_length)  # Sử dụng giá trị này để xác định số lượng ý chính
        
        # Kiểm tra checkbox "Dịch sang tiếng Việt" và dịch nếu được chọn
        if self.translate_checkbox_var.get():
            summary = self.translate_to_vietnamese(summary)
        
        # Hiển thị kết quả trong cửa sổ popup
        self.show_result_popup(summary)

    
    def summarize_text(self, text, summary_length):
        # Hàm rút ý chính sử dụng TextSummarizer
        summarizer = TextSummarizer()
        summary = summarizer.summarize(text, summary_length)  # Trả về số lượng câu tóm tắt tương ứng
        return "\n".join(summary)

    
    def translate_to_vietnamese(self, text):
        # Hàm dịch văn bản sang tiếng Việt sử dụng Google Translate
        translator = Translator()
        translation = translator.translate(text, dest='vi')  # Sử dụng dest='vi' để chỉ định ngôn ngữ đích là tiếng Việt
        return translation.text

    
    def show_result_popup(self, result):
        # Hiển thị kết quả trong cửa sổ popup
        popup = tk.Toplevel(self.root)
        popup.title("Kết quả")
        
        # Tăng kích thước của cửa sổ popup
        popup.geometry("1000x300")
        
        # Sử dụng scrolledtext để có thể cuộn khi nội dung quá nhiều
        result_text = scrolledtext.ScrolledText(popup, width=80, height=15, wrap="word")
        
        # Chia các ý chính bằng dấu gạch và thêm dấu gạch đầu dòng
        result = "\n------------------------------------------------------------------------\n".join("- " + line for line in result.split("\n"))
        
        result_text.insert(tk.END, result)
        result_text.pack(padx=10, pady=10)
        
        # Thêm nút "Quay lại"
        back_button = tk.Button(popup, text="Quay lại", command=popup.destroy)
        back_button.pack(side=tk.LEFT, padx=5)
        
        # Thêm nút "Sao chép văn bản"
        copy_button = tk.Button(popup, text="Sao chép văn bản", command=lambda: self.copy_to_clipboard(result))
        copy_button.pack(side=tk.RIGHT, padx=5)

        popup.mainloop()


    
    def copy_to_clipboard(self, text):
        # Sao chép văn bản vào clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
    
    def quit_application(self):
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = MyApplication(root)
    root.mainloop()

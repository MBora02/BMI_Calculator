import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import hashlib

class BMI_Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")

        # Değişkenler
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.weight_var = tk.DoubleVar()
        self.height_var = tk.DoubleVar()
        self.result_var = tk.StringVar()
        self.date_var = tk.StringVar()

        # Database kurulum
        self.conn = sqlite3.connect("bmi_data.db")
        self.create_table()

        # UI kurulum
        self.setup_login_ui()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                name TEXT,
                gender TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                weight REAL,
                height REAL,
                bmi REAL,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        self.conn.commit()

    def hash_password(self, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password

    def setup_login_ui(self):
        # Giriş Yazıları
        tk.Label(self.root, text="Kullanıcı Adı:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Şifre:").grid(row=1, column=0, padx=10, pady=10)

        # Giriş widgetları
        tk.Entry(self.root, textvariable=self.username_var).grid(row=0, column=1, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=10, pady=10)

        # Giriş Butonu
        tk.Button(self.root, text="Giriş", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user:
            # mevcut kullanıcı şifre kontrol
            if user[2] == self.hash_password(password):
                self.setup_bmi_ui(user[0])  # Pass the user_id to the main UI setup
            else:
                messagebox.showerror("Hata", "Geçersiz şifre.")
        else:
            # yeni kullanıcı, hesap oluşturma prompt'ları
            response = messagebox.askquestion("Hesap Oluştur", "Kullanıcı adı bulunamadı, yeni bir hesap oluşturmak ister misiniz?")
            if response == 'yes':
                self.setup_create_account_ui()

    def setup_create_account_ui(self):
        # giriş UI destroy
        for widget in self.root.winfo_children():
            widget.destroy()

        # Hesap oluşturma yazıları
        tk.Label(self.root, text="Kullanıcı Adı:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Şifre:").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="İsim Soyisim:").grid(row=2, column=0, padx=10, pady=10)

        # Hesap oluşturma bilgi widgetları
        tk.Entry(self.root, textvariable=self.username_var).grid(row=0, column=1, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.name_var).grid(row=2, column=1, padx=10, pady=10)

        # hesap oluşturma butonu
        tk.Button(self.root, text="Hesap Oluştur", command=self.create_account).grid(row=4, column=0, columnspan=2, pady=10)

    def create_account(self):
        username = self.username_var.get()
        password = self.password_var.get()
        name = self.name_var.get()


        # kullanıcı adı olup olmadığını kontrol et
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            messagebox.showerror("Hata", "Bu kullanıcı adı kullanılıyor lütfen farklı bir kullanıcı adı giriniz.")
        else:
            # şifre hashleme
            hashed_password = self.hash_password(password)

            # database yeni kullanıcı ekle
            cursor.execute("INSERT INTO users (username, password, name) VALUES (?, ?, ?)",
                           (username, hashed_password, name))
            self.conn.commit()

            # yeni kullanıcı BMI hesaplama ekranına yönlendir
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            self.setup_bmi_ui(user[0])

    def setup_bmi_ui(self, user_id):
        # Giriş UI destroy
        for widget in self.root.winfo_children():
            widget.destroy()

        # BMI yazıları
        tk.Label(self.root, text="İSİM:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Cinsiyet:").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Ağırlık (kg):").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Boy (cm):").grid(row=3, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Tarih (yıl-ay-gün):").grid(row=4, column=0, padx=10, pady=10)
        tk.Label(self.root, textvariable=self.result_var).grid(row=5, column=1, padx=10, pady=10)

        # BMI widgetları
        tk.Entry(self.root, textvariable=self.name_var, state='disabled').grid(row=0, column=1, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.gender_var).grid(row=1, column=1, padx=20, pady=10)
        tk.Entry(self.root, textvariable=self.weight_var).grid(row=2, column=1, padx=20, pady=10)
        tk.Entry(self.root, textvariable=self.height_var).grid(row=3, column=1, padx=20, pady=10)
        tk.Entry(self.root, text=self.date_var).grid(row=4, column=1, padx=20, pady=10)

        # BMI hesapla butonu
        tk.Button(self.root, text="BMI HESAPLA", command=lambda: self.calculate_bmi(user_id)).grid(
            row=5, column=0, columnspan=1, pady=10
        )

    def calculate_bmi(self, user_id):
        try:
            weight = self.weight_var.get()
            height = self.height_var.get() / 100  # Convert height to meters
            gender = self.gender_var.get()
            if (gender == 'Male' or gender == 'male'):
                bmi = weight / (height ** 2)
            elif gender == 'Female' or gender == 'female':
                bmi = 0.9 * weight / (height ** 2)
            else:
                self.result_var.set("Geçersiz cinsiyet lütfen 'male' ya da 'female' giriniz ")
                return
            if(0<bmi<=18.4):
                self.result_var.set(f'zayıfsın BMI:{bmi:.2f}')
            elif(18.5<=bmi<=24.9):
                self.result_var.set(f'normal kilolusun BMI:{bmi:.2f}')
            elif(25<=bmi<=29.9):
                self.result_var.set(f'hafif şişmansın BMI:{bmi:.2f}')
            elif(30<=bmi<=34.9):
                self.result_var.set(f'obezsin BMI:{bmi:.2f}')

            # bilgileri datasete kaydet
            self.save_data(user_id, bmi)
        except ZeroDivisionError:
            messagebox.showerror("Hata", "Lütfen geçerli bir boy ve kilo değeri giriniz")

    def save_data(self, user_id, bmi):
        name = self.name_var.get()
        gender = self.gender_var.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO bmi_data (user_id, weight, height, bmi, date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, self.weight_var.get(), self.height_var.get(), bmi, date))
        self.conn.commit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BMI_Calculator(root)
    root.mainloop()

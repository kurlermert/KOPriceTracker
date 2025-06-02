from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import undetected_chromedriver as uc
import requests
import time
import os
import sys
import random
import pyautogui
import win32gui
import json
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import telegram

def get_window_rect(window_title):
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and window_title.lower() in win32gui.GetWindowText(hwnd).lower():
            rect = win32gui.GetWindowRect(hwnd)
            extra.append(rect)
    
    rects = []
    win32gui.EnumWindows(callback, rects)
    return rects[0] if rects else None

def click_relative(window_title, relative_x, relative_y, retries=3):
    for attempt in range(retries):
        try:
            rect = get_window_rect(window_title)
            if not rect:
                print(f"Deneme {attempt + 1}/{retries}: Pencere bulunamadı: {window_title}")
                time.sleep(2)
                continue

            window_left, window_top, window_right, window_bottom = rect
            window_width = window_right - window_left
            window_height = window_bottom - window_top

            scale_x = window_width / 1920
            scale_y = window_height / 1080

            click_x = window_left + int(relative_x * scale_x)
            click_y = window_top + int(relative_y * scale_y)

            pyautogui.click(click_x, click_y)
            print(f"Başarılı tıklama: ({click_x}, {click_y}) - Pencere: {window_title}")
            return True

        except Exception as e:
            print(f"Tıklama hatası (Deneme {attempt + 1}/{retries}): {str(e)}")
            time.sleep(2)
    
    return False

def create_stealth_driver():
    options = uc.ChromeOptions()
    options.add_argument('--user-data-dir=C:\\Users\\' + os.getenv('USERNAME') + '\\AppData\\Local\\Google\\Chrome\\User Data')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--headless=new')  
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')

    driver = uc.Chrome(options=options, use_subprocess=True)

    stealth(driver,
        languages=["tr-TR", "tr", "en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        run_on_insecure_origins=True
    )
    
    return driver

def random_sleep(min_seconds=0.5, max_seconds=1):
    time.sleep(random.uniform(min_seconds, max_seconds))

def search_item(item_name, server_id="btn_zero3", driver=None, wait=None, callback=print):
    try:
        if driver is None:
            callback("Selenium başlatılıyor...")
            driver = create_stealth_driver()
            wait = WebDriverWait(driver, 10)
            
            callback("Siteye bağlanılıyor...")
            driver.get("https://www.uskopazar.com/")
            callback("Sayfanın yüklenmesi bekleniyor...")
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            callback("Ana sayfa yüklendi")
            random_sleep(0.5, 1)
            
            callback("Server seçimi yapılıyor...")
            callback("Dropdown menü açılıyor...")
            try:
                dropdown_toggle = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"][id="filtersPrice"]'))
                )
                dropdown_toggle.click()
                callback("Dropdown menü açıldı")
            except Exception as e:
                callback(f"Dropdown açma hatası: {str(e)}")
                raise
            random_sleep(0.5, 1)
            
            callback(f"Server seçiliyor: {server_id}")
            try:
                server_button = wait.until(
                    EC.element_to_be_clickable((By.ID, server_id))
                )
                server_button.click()
                callback(f"Server seçildi: {server_id}")
            except Exception as e:
                callback(f"Server seçme hatası: {str(e)}")
                raise
            random_sleep(0.5, 1)
        
        callback("Arama kutusu bekleniyor...")
        try:
            search_box = wait.until(
                EC.presence_of_element_located((By.ID, "xsearchInput"))
            )
            callback("Arama kutusu bulundu")
        except Exception as e:
            callback(f"Arama kutusu bulma hatası: {str(e)}")
            raise
        
        callback("Arama kutusu temizleniyor...")
        search_box.clear()
        callback("Arama kutusuna yazılıyor...")
        search_box.send_keys(item_name)
        actual_value = search_box.get_attribute('value')
        callback(f"Yazılan değer: {actual_value}")
        
        if actual_value != item_name:
            callback("Değer doğru yazılamadı, tekrar deneniyor...")
            search_box.clear()
            for char in item_name:
                search_box.send_keys(char)
                time.sleep(0.05)
        
        final_value = search_box.get_attribute('value')
        callback(f"Son yazılan değer: {final_value}")
        callback("Arama yapılıyor...")
        search_box.send_keys(Keys.RETURN)
        callback("Arama sonuçları yükleniyor...")
        time.sleep(1.5)
        
        try:
            callback("Sonuçlar kontrol ediliyor...")
            results = driver.find_elements(By.CSS_SELECTOR, ".flex.border-t.border-jacarta-100")
            
            if results:
                callback(f"{len(results)} sonuç bulundu")
                price_element = results[0].find_element(By.CSS_SELECTOR, "span[style='color: red;']")
                price = price_element.text
                callback(f"Bulunan fiyat: {price}")
                return price, driver, wait
            else:
                callback("Sonuç bulunamadı")
                return None, driver, wait
            
        except Exception as e:
            callback(f"Fiyat bulma hatası: {str(e)}")
            return None, driver, wait
            
    except Exception as e:
        callback(f"Bir hata oluştu: {str(e)}")
        if driver:
            driver.quit()
        return None, None, None

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UskoPazar Arama")
        self.root.geometry("1000x600")  

        main_frame = ttk.Frame(root, padding="5")  
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        style = ttk.Style()
        style.configure('Server.TRadiobutton', padding=3)  
        style.configure('Action.TButton', padding=3)

       
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)

        server_frame = ttk.LabelFrame(top_frame, text="Server Seçimi", padding="3")
        server_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 3))

        self.servers = {
            "btn_zero3": "Zero 3",
            "btn_zero4": "Zero 4",
            "btn_zero5": "Zero 5",
            "btn_agartha3": "Agartha 3",
            "btn_pandora3": "Pandora 3",
            "btn_felis3": "Felis 3",
            "btn_dryads2": "Dryads 2",
            "btn_destan2": "Destan 2",
            "btn_oreads2": "Oreads 2"
        }

        self.selected_server = tk.StringVar(value="btn_zero3")

       
        for i, (server_id, server_name) in enumerate(self.servers.items()):
            row = i // 5
            col = i % 5
            ttk.Radiobutton(
                server_frame,
                text=server_name,
                value=server_id,
                variable=self.selected_server,
                style='Server.TRadiobutton'
            ).grid(row=row, column=col, sticky=tk.W, padx=5)

        quick_search_frame = ttk.LabelFrame(top_frame, text="Hızlı Arama", padding="3")
        quick_search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=3)

        button_frame = ttk.Frame(quick_search_frame)
        button_frame.pack(fill=tk.X, pady=2)

        self.maden_button = ttk.Button(
            button_frame, 
            text="Maden İtemleri", 
            command=self.fill_maden_items,
            style='Action.TButton'
        )
        self.maden_button.pack(side=tk.LEFT, padx=2)

        self.md_button = ttk.Button(
            button_frame,
            text="MD+6 Takip",
            command=self.toggle_md6_tracking,
            style='Action.TButton'
        )
        self.md_button.pack(side=tk.LEFT, padx=2)

        self.test_button = ttk.Button(
            button_frame,
            text="Test Telegram",
            command=self.test_telegram,
            style='Action.TButton'
        )
        self.test_button.pack(side=tk.LEFT, padx=2)

        
        telegram_frame = ttk.Frame(quick_search_frame)
        telegram_frame.pack(fill=tk.X, pady=2)

        ttk.Label(telegram_frame, text="Bot Token:").pack(side=tk.LEFT, padx=2)
        self.bot_token_var = tk.StringVar()
        self.bot_token_entry = ttk.Entry(telegram_frame, textvariable=self.bot_token_var, width=20)
        self.bot_token_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(telegram_frame, text="Chat ID:").pack(side=tk.LEFT, padx=2)
        self.chat_id_var = tk.StringVar()
        self.chat_id_entry = ttk.Entry(telegram_frame, textvariable=self.chat_id_var, width=15)
        self.chat_id_entry.pack(side=tk.LEFT, padx=2)

        
        scan_frame = ttk.Frame(quick_search_frame)
        scan_frame.pack(fill=tk.X, pady=2)

        ttk.Label(scan_frame, text="Tarama Sıklığı:").pack(side=tk.LEFT, padx=2)
        self.scan_interval_var = tk.StringVar(value="10")
        self.scan_interval_entry = ttk.Entry(scan_frame, textvariable=self.scan_interval_var, width=5)
        self.scan_interval_entry.pack(side=tk.LEFT, padx=2)

        self.scan_unit_var = tk.StringVar(value="Saniye")
        self.scan_unit_menu = ttk.Combobox(scan_frame, textvariable=self.scan_unit_var, values=["Saniye", "Dakika"], state="readonly", width=8)
        self.scan_unit_menu.pack(side=tk.LEFT, padx=2)

        search_frame = ttk.LabelFrame(main_frame, text="Arama", padding="3")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=3)

        self.search_var = tk.StringVar()
        ttk.Label(search_frame, text="Ürün Adları (virgülle ayırın):").grid(row=0, column=0, padx=3, pady=2)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)  
        self.search_entry.grid(row=0, column=1, padx=3, pady=2)

        self.search_button = ttk.Button(
            search_frame, 
            text="Ara", 
            command=self.start_search,
            style='Action.TButton'
        )
        self.search_button.grid(row=0, column=2, padx=3, pady=2)

        progress_frame = ttk.LabelFrame(main_frame, text="İşlem Durumu", padding="3")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=3)

        self.progress_var = tk.StringVar(value="Hazır")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)

        self.progress = ttk.Progressbar(progress_frame, mode='determinate', value=0)
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=3, pady=2)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=3)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        log_frame = ttk.LabelFrame(bottom_frame, text="İşlem Detayları", padding="3")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 3))

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=50, height=10)  
        self.log_text.grid(row=0, column=0, padx=3, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        results_frame = ttk.LabelFrame(bottom_frame, text="Sonuçlar", padding="3")
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(3, 0))

        ks_frame = ttk.Frame(results_frame)
        ks_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 2))

        ttk.Label(ks_frame, text="KS Miktarı:").pack(side=tk.LEFT, padx=2)
        self.ks_amount = ttk.Entry(ks_frame, width=10)  
        self.ks_amount.pack(side=tk.LEFT, padx=2)

        self.ks_button = ttk.Button(
            ks_frame, 
            text="KS AT", 
            command=self.apply_ks,
            style='Action.TButton'
        )
        self.ks_button.pack(side=tk.LEFT, padx=2)

        self.copy_button = ttk.Button(
            ks_frame, 
            text="Sonuçları Kopyala", 
            command=self.copy_results,
            style='Action.TButton'
        )
        self.copy_button.pack(side=tk.LEFT, padx=2)

        columns = ("item", "server", "price")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)  
        self.results_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.results_tree.heading("item", text="Ürün")
        self.results_tree.heading("server", text="Server")
        self.results_tree.heading("price", text="Fiyat")

        self.results_tree.column("item", width=200)  
        self.results_tree.column("server", width=80)
        self.results_tree.column("price", width=100)

        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        results_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        self.status_var = tk.StringVar(value="Hazır")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=3)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        self.driver = None
        self.wait = None
        self.md6_tracking_active = False
        self.bot = None

        
        self.load_config()

    def load_config(self):
        """config.json dosyasını oku ve Bot Token ile Chat ID alanlarını doldur."""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    self.bot_token_var.set(config.get("bot_token", ""))
                    self.chat_id_var.set(config.get("chat_id", ""))
                    self.log("Config dosyası yüklendi.")
            else:
                self.log("Config dosyası bulunamadı, yeni dosya oluşturulacak.")
        except Exception as e:
            self.log(f"Config dosyası yüklenirken hata: {str(e)}")

    def save_config(self, bot_token, chat_id):
        """Bot Token ve Chat ID’yi config.json dosyasına kaydet."""
        try:
            config = {
                "bot_token": bot_token,
                "chat_id": chat_id
            }
            with open("config.json", "w") as f:
                json.dump(config, f, indent=4)
            self.log("Config dosyasına kaydedildi.")
        except Exception as e:
            self.log(f"Config dosyasına kaydedilirken hata: {str(e)}")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def add_result(self, item, server, price):
        self.results_tree.insert("", tk.END, values=(item, server, price))

    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

    def escape_markdown(self, text):
        
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    def send_telegram_message_in_thread(self, bot_token, chat_id, message):
        self.log("Telegram mesaj gönderimi başlatılıyor...")
        try:
            bot = telegram.Bot(token=bot_token)
           
            bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')
            self.log(f"Telegram mesajı başarıyla gönderildi: {message}")
        except telegram.error.TelegramError as te:
            self.log(f"Telegram hatası: {str(te)}\nHata detayları: {type(te).__name__}, {te.message}")
        except Exception as e:
            self.log(f"Beklenmeyen hata: {str(e)}\nHata detayları: {type(e).__name__}, {e.args}")
        finally:
            self.log("Telegram mesaj gönderimi tamamlandı.")
            time.sleep(2)  

    def send_telegram_message(self, message):
        bot_token = self.bot_token_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        if not bot_token or not chat_id:
            self.log("Telegram mesajı gönderilemedi: Bot Token veya Chat ID eksik.")
            return

        
        self.save_config(bot_token, chat_id)

        
        thread = threading.Thread(target=self.send_telegram_message_in_thread, args=(bot_token, chat_id, message))
        thread.daemon = True
        thread.start()

    def test_telegram(self):
        self.log("Test mesajı gönderiliyor...")
       
        message = "🔔 *Test Mesajı* 🔔\nBu bir test mesajıdır\\."
        self.send_telegram_message(message)

    def start_search(self):
        items = [item.strip() for item in self.search_var.get().split(",") if item.strip()]
        if not items:
            self.log("Lütfen en az bir ürün adı girin!")
            return

        self.clear_results()
        self.search_button["state"] = "disabled"
        self.status_var.set("Arama yapılıyor...")
        self.progress["maximum"] = len(items)
        self.progress["value"] = 0
        self.log_text.delete(1.0, tk.END)

        thread = threading.Thread(target=self.perform_multiple_search, args=(items,))
        thread.daemon = True
        thread.start()

    def perform_multiple_search(self, items):
        try:
            server_id = self.selected_server.get()
            server_name = self.servers[server_id]

            for i, item_name in enumerate(items, 1):
                self.progress_var.set(f"Aranıyor: {item_name} ({i}/{len(items)})")
                self.log(f"\n--- {item_name} aranıyor ---")
                self.root.update()

                price, self.driver, self.wait = search_item(
                    item_name, 
                    server_id, 
                    driver=self.driver, 
                    wait=self.wait, 
                    callback=self.log
                )

                final_price = price if price else "Bulunamadı"
                self.add_result(item_name, server_name, final_price)

               
                escaped_item_name = self.escape_markdown(item_name)
                escaped_server_name = self.escape_markdown(server_name)
                escaped_final_price = self.escape_markdown(final_price)
                message = (
                    "🔔 *Yeni Tarama Sonucu* 🔔\n"
                    "───────────────\n"
                    f"**Ürün:** {escaped_item_name}\n"
                    f"**Server:** {escaped_server_name}\n"
                    f"**Fiyat:** `{escaped_final_price}`"
                )
                self.send_telegram_message(message)

                self.progress["value"] = i
                self.root.update()

        except Exception as e:
            self.log(f"\nHata oluştu: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None

        finally:
            self.root.after(0, lambda: self.search_button.configure(state="normal"))
            self.root.after(0, lambda: self.status_var.set("Hazır"))
            self.root.after(0, lambda: self.progress_var.set("Tamamlandı"))

    def apply_ks(self):
        try:
            ks_amount = int(self.ks_amount.get())
            items = self.results_tree.get_children()

            for item in items:
                values = self.results_tree.item(item)['values']
                if values[2] != "Bulunamadı":
                    price = int(values[2].replace(',', '').replace('.', ''))
                    new_price = price - ks_amount
                    formatted_price = f"{new_price:,}".replace(',', '.')
                    self.results_tree.item(item, values=(values[0], values[1], formatted_price))

            self.log(f"\nTüm fiyatlardan {ks_amount} KS düşüldü")

        except ValueError:
            self.log("\nLütfen geçerli bir KS miktarı girin!")

    def fill_maden_items(self):
        maden_items = [
            "Transformation Scroll",
            "Spell Stone Powder",
            "Fragment of Sloth",
            "Glutinous Rice Cake",
            "Old Platinum Earring",
            "Old Opal Earring",
            "Old Amulet of Dexterity",
            "Old Amulet of Strength",
            "Old Diamond Ring",
            "Old Ring of Life",
            "Old Ring of Courage",
            "Old Silver Earring",
            "Trina"
        ]
        self.search_var.set(",".join(maden_items))
        self.log("Maden itemleri yüklendi")

    def copy_results(self):
        results = []
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item)['values']
            results.append(f"{values[0]}: {values[2]}")
        result_text = "\n".join(results)
        self.root.clipboard_clear()
        self.root.clipboard_append(result_text)
        self.log("\nSonuçlar panoya kopyalandı")

    def toggle_md6_tracking(self):
        if not self.md6_tracking_active:
            bot_token = self.bot_token_var.get().strip()
            chat_id = self.chat_id_var.get().strip()

            if not bot_token or not chat_id:
                self.log("Lütfen Telegram Bot Token ve Chat ID girin!")
                return

            self.send_telegram_message("🔔 *MD\\+6 Takip Başlatıldı* 🔔")
            self.md6_tracking_active = True
            self.md_button.configure(text="MD+6 Takip Durdur")
            self.log("MD+6 Takip başlatıldı")

            thread = threading.Thread(target=self.perform_md6_tracking)
            thread.daemon = True
            thread.start()
        else:
            self.md6_tracking_active = False
            self.md_button.configure(text="MD+6 Takip")
            self.log("MD+6 Takip durduruldu")
            self.send_telegram_message("🔔 *MD\\+6 Takip Durduruldu* 🔔")

    def perform_md6_tracking(self):
        server_id = self.selected_server.get()
        server_name = self.servers[server_id]
        item_name = "Mirage Dagger(+6)"

       
        try:
            interval = float(self.scan_interval_var.get())
            unit = self.scan_unit_var.get()
            if unit == "Dakika":
                interval *= 60  
            if interval <= 0:
                raise ValueError("Tarama sıklığı sıfırdan büyük olmalıdır.")
        except ValueError as e:
            self.log(f"Tarama sıklığı hatası: {str(e)}. Varsayılan 10 saniye kullanılıyor.")
            interval = 10  

        self.log(f"Tarama sıklığı: {interval} saniye")

        while self.md6_tracking_active:
            self.log(f"\n--- {item_name} aranıyor (Server: {server_name}) ---")
            self.root.update()

            price, self.driver, self.wait = search_item(
                item_name,
                server_id,
                driver=self.driver,
                wait=self.wait,
                callback=self.log
            )

            final_price = price if price else "Bulunamadı"
            self.add_result(item_name, server_name, final_price)

            
            escaped_item_name = self.escape_markdown(item_name)
            escaped_server_name = self.escape_markdown(server_name)
            escaped_final_price = self.escape_markdown(final_price)
            message = (
                "🔔 *Yeni Tarama Sonucu* 🔔\n"
                "───────────────\n"
                f"**Ürün:** {escaped_item_name}\n"
                f"**Server:** {escaped_server_name}\n"
                f"**Fiyat:** `{escaped_final_price}`"
            )
            self.send_telegram_message(message)

            time.sleep(interval)
            self.root.update()

        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()
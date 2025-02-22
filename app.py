import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, NoSuchElementException
import urllib.parse
import random
import time
import threading
import sys
import os
import tempfile

# Default Timer Values
TIMER_MIN = 5
TIMER_MAX = 15

# Paths to bundled files/folders
if getattr(sys, 'frozen', False):
    # Running as a frozen EXE
    base_path = sys._MEIPASS
else:
    # Running as a Python script
    base_path = os.path.dirname(__file__)

# chrome_path = os.path.join(base_path, 'chrome', 'chrome.exe')
chrome_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
chromedriver_path = os.path.join(base_path, 'chromedriver', 'chromedriver.exe')

# Determine a persistent folder in the %temp% directory
def get_persistent_temp_path():
    temp_dir = tempfile.gettempdir()
    persistent_temp_path = os.path.join(temp_dir, "whatsapp_blaster_data")
    if not os.path.exists(persistent_temp_path):
        os.makedirs(persistent_temp_path)
    return persistent_temp_path

# User data path
user_data_path = get_persistent_temp_path()

# Global stop flag
stop_flag = False

def setup_browser(headless=True):
    options = Options()
    options.binary_location = chrome_path
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={user_data_path}")  # Use persistent temp folder
    if headless:
        options.add_argument("--headless")

    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

def first_time_setup(log_text):
    log_text.insert(tk.END, "Launching browser for first-time setup...\n")
    try:
        driver = setup_browser(headless=False)
        driver.get("https://web.whatsapp.com")
        log_text.insert(tk.END, "Waiting for WhatsApp Web login...\n")
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
        )
        log_text.insert(tk.END, "QR code loaded. Please scan with your phone.\n")
        WebDriverWait(driver, 300).until_not(
            EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
        )
        log_text.insert(tk.END, "Logged into WhatsApp Web successfully.\n")
    except NoSuchWindowException:
        log_text.insert(tk.END, "Browser closed. Setup complete.\n")
    except WebDriverException as e:
        log_text.insert(tk.END, f"Unexpected error during setup: {e}\n")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

def send_messages(log_text, contacts_file, message_file, timer_min, timer_max):
    global stop_flag
    log_text.insert(tk.END, "Starting the WhatsApp message blaster...\n")
    try:
        driver = setup_browser()
        driver.get("https://web.whatsapp.com")
        log_text.insert(tk.END, "Waiting for WhatsApp Web to load...\n")

        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']"))
        )
        log_text.insert(tk.END, "WhatsApp Web loaded successfully.\n")

        # Load contacts
        with open(contacts_file, "r") as file:
            contacts = [line.strip() for line in file if line.strip()]

        # Load message
        with open(message_file, "r", encoding="utf-8") as file:
            message = file.read().strip()

        log_text.insert(tk.END, f"Found {len(contacts)} contacts. Sending messages...\n")
        encoded_message = urllib.parse.quote_plus(message)

        for contact in contacts:
            if stop_flag:
                log_text.insert(tk.END, "Process stopped by user.\n")
                break
            try:
                whatsapp_url = f"https://web.whatsapp.com/send?phone={contact}&text={encoded_message}"
                driver.get(whatsapp_url)
                time.sleep(random.uniform(timer_min, timer_max))
                try:
                    send_button = driver.find_element("xpath", "//span[@data-icon='send']")
                    send_button.click()
                    log_text.insert(tk.END, f"Message sent to {contact}.\n")
                except NoSuchElementException:
                    log_text.insert(tk.END, f"Number {contact} not found, retrying...\n")
                    time.sleep(5)
                    try:
                        send_button = driver.find_element("xpath", "//span[@data-icon='send']")
                        send_button.click()
                        log_text.insert(tk.END, f"Message sent to {contact} after retry.\n")
                    except NoSuchElementException:
                        log_text.insert(tk.END, f"Skipping {contact}: Number not found.\n")
                time.sleep(random.uniform(timer_min, timer_max))
            except Exception as e:
                log_text.insert(tk.END, f"Failed to send message to {contact}: {e}\n")

        log_text.insert(tk.END, "All messages sent. Closing browser.\n")
        driver.quit()
    except Exception as e:
        log_text.insert(tk.END, f"Error: {e}\n")
    finally:
        stop_flag = False

def create_gui():
    root = tk.Tk()
    root.title("WhatsApp Blaster")
    root.geometry("600x500")
    root.configure(bg="#333333")

    tk.Label(root, text="WhatsApp Blaster", bg="#333333", fg="white", font=("Arial", 20)).pack(pady=10)
    button_frame = tk.Frame(root, bg="#333333")
    button_frame.pack(pady=10)

    contacts_file = tk.StringVar()
    message_file = tk.StringVar()
    timer_min = tk.StringVar(value=str(TIMER_MIN))
    timer_max = tk.StringVar(value=str(TIMER_MAX))

    def import_contacts():
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            contacts_file.set(file_path)
            log_text.insert(tk.END, f"Contacts file loaded: {file_path}\n")

    def import_message():
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            message_file.set(file_path)
            log_text.insert(tk.END, f"Message file loaded: {file_path}\n")

    def first_time_setup_wrapper():
        threading.Thread(target=first_time_setup, args=(log_text,)).start()

    def send_messages_wrapper():
        if not contacts_file.get():
            messagebox.showerror("Error", "Please load a contacts file first.")
            return
        if not message_file.get():
            messagebox.showerror("Error", "Please load a message file first.")
            return
        try:
            timer_min_val = float(timer_min.get())
            timer_max_val = float(timer_max.get())
            if timer_min_val >= timer_max_val or timer_min_val < 0 or timer_max_val < 0:
                raise ValueError("Invalid timer values.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric timer values.")
            return
        threading.Thread(target=send_messages, args=(log_text, contacts_file.get(), message_file.get(), timer_min_val, timer_max_val)).start()

    def stop_process():
        global stop_flag
        stop_flag = True
        log_text.insert(tk.END, "Stopping process...\n")

    tk.Button(button_frame, text="1) Import Contacts", width=15, command=import_contacts).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="2) Import Message", width=15, command=import_message).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="3) Launch WA Web", width=15, command=first_time_setup_wrapper).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="4) Run", width=15, command=send_messages_wrapper).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="STOP", width=15, command=stop_process).pack(side=tk.LEFT, padx=5)

    timer_frame = tk.Frame(root, bg="#333333")
    timer_frame.pack(pady=10)
    tk.Label(timer_frame, text="Min Timer (sec):", bg="#333333", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Entry(timer_frame, textvariable=timer_min, width=5).pack(side=tk.LEFT, padx=5)
    tk.Label(timer_frame, text="Max Timer (sec):", bg="#333333", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Entry(timer_frame, textvariable=timer_max, width=5).pack(side=tk.LEFT, padx=5)

    tk.Label(root, text="Logs", bg="#333333", fg="white", font=("Arial", 12)).pack(anchor="w", padx=10)
    log_text = scrolledtext.ScrolledText(root, width=70, height=15, font=("Arial", 10))
    log_text.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
import urllib.parse
import random
import time
import threading
import sys
import os
import tempfile

# Determine the base path based on whether running from an EXE or script
if getattr(sys, 'frozen', False):
    # Running as a frozen EXE
    base_path = sys._MEIPASS  # Path where PyInstaller stores bundled files
else:
    # Running as a Python script
    base_path = os.path.dirname(__file__)

# Create a temporary directory for userData
user_data_path = tempfile.mkdtemp(prefix="whatsapp_user_data_")

# Paths to bundled files/folders
chrome_path = os.path.join(base_path, 'chrome', 'chrome.exe')
chromedriver_path = os.path.join(base_path, 'chromedriver', 'chromedriver.exe')

def setup_browser(headless=True):
    options = Options()
    options.binary_location = chrome_path  # Use the bundled chrome executable
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={user_data_path}")  # Use the temporary user data folder
    if headless:
        options.add_argument("--headless")

    service = Service(executable_path=chromedriver_path)  # Use the bundled chromedriver executable
    return webdriver.Chrome(service=service, options=options)

def first_time_setup(log_text):
    log_text.insert(tk.END, "Launching browser for first-time setup...\n")
    try:
        driver = setup_browser(headless=False)
        driver.get("https://web.whatsapp.com")
        log_text.insert(tk.END, "Waiting for WhatsApp Web login...\n")

        # Wait for the main interface or QR code to appear
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
        )
        log_text.insert(tk.END, "WhatsApp Web QR code loaded. Please scan with your phone.\n")

        # Wait until the QR code is replaced by the main interface
        WebDriverWait(driver, 300).until_not(
            EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
        )
        log_text.insert(tk.END, "Logged into WhatsApp Web successfully.\n")
    except NoSuchWindowException:
        # Suppress error when the browser is manually closed
        log_text.insert(tk.END, "Browser closed after login. Setup complete.\n")
    except WebDriverException as e:
        log_text.insert(tk.END, f"Unexpected error during setup: {e}\n")
    finally:
        try:
            driver.quit()
        except Exception:
            pass  # Suppress any errors during driver.quit()

def send_messages(log_text, contacts_file, message_file):
    log_text.insert(tk.END, "Starting the WhatsApp message blaster...\n")
    try:
        driver = setup_browser()
        driver.get("https://web.whatsapp.com")
        log_text.insert(tk.END, "Waiting for WhatsApp Web to load...\n")

        # Wait for the main interface
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
            try:
                whatsapp_url = f"https://web.whatsapp.com/send?phone={contact}&text={encoded_message}"
                driver.get(whatsapp_url)
                time.sleep(random.uniform(6, 20))  # Wait for the chat to load

                send_button = driver.find_element("xpath", "//span[@data-icon='send']")
                send_button.click()
                log_text.insert(tk.END, f"Message sent to {contact}.\n")
                time.sleep(random.uniform(2, 120))  # Small delay
            except Exception as e:
                log_text.insert(tk.END, f"Failed to send message to {contact}: {e}\n")

        log_text.insert(tk.END, "All messages sent. Closing browser.\n")
        driver.quit()
    except Exception as e:
        log_text.insert(tk.END, f"Error: {e}\n")

def create_gui():
    root = tk.Tk()
    root.title("WhatsApp Blaster")
    root.geometry("500x400")
    root.resizable(False, False)
    root.configure(bg="#333333")

    # Title
    tk.Label(root, text="WhatsApp Blaster", bg="#333333", fg="white", font=("Arial", 20)).pack(pady=10)

    # Buttons Section
    button_frame = tk.Frame(root, bg="#333333")
    button_frame.pack(pady=10)

    contacts_file = tk.StringVar()
    message_file = tk.StringVar()

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
        threading.Thread(target=send_messages, args=(log_text, contacts_file.get(), message_file.get())).start()

    tk.Button(button_frame, text="1) Import Contacts", width=15, command=import_contacts).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="2) Import Message", width=15, command=import_message).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="3) Launch WA Web", width=15, command=first_time_setup_wrapper).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="4) Run", width=15, command=send_messages_wrapper).pack(side=tk.LEFT, padx=5)

    # Logs Section
    tk.Label(root, text="Logs", bg="#333333", fg="white", font=("Arial", 12)).pack(anchor="w", padx=10)
    log_text = scrolledtext.ScrolledText(root, width=70, height=15, font=("Arial", 10))
    log_text.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
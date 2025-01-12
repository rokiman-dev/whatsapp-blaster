---

# WhatsApp Blaster

## Overview

WhatsApp Blaster is a desktop application designed to send messages to multiple contacts on WhatsApp Web. Using this tool, you can automate the process of sending pre-written messages to a list of contacts in a convenient and easy-to-use graphical interface.

## Features
- **GUI for ease of use**: The app provides a simple interface with buttons for importing contacts and messages, launching WhatsApp Web, and sending messages.
- **Customizable**: Easily load your contacts and message from text files.
- **Headless operation**: The app can run in headless mode (without showing the browser window) or in regular mode.
- **Automatic WhatsApp Web Login**: Supports first-time login and QR code scanning.

## Requirements

- **Python** (3.x)
- **Selenium**: For controlling the browser and sending messages.
- **Chromedriver**: The required driver for Chrome browser automation.
- **Chrome**: A compatible version of Google Chrome.

## Setup

### 1. Install Dependencies

Ensure you have Python installed, then install the necessary Python packages:

```bash
pip install -r requirements.txt
```

You also need to ensure you have **Chrome** installed and download the appropriate version of **Chromedriver** from:  
[Chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)

### 2. Prepare Your Files

- Place your `chrome` folder, `chromedriver.exe`, and `userData` in the same directory as `run.py`.
- The `chrome` folder contains the Chrome binary.
- The `userData` folder stores session data for WhatsApp Web.
- The `chromedriver.exe` should be placed in the `chromedriver` folder.

### 3. Compile the Application (Optional)

To compile the Python script into a standalone executable:

1. Use **PyInstaller**:

```bash
pip install pyinstaller
```

2. Use the following command to compile the script:

```bash
pyinstaller --onefile --noconsole \
    --add-data "chrome;chrome" \
    --add-data "chromedriver/chromedriver.exe;chromedriver" \
    --add-data "userData;userData" \
    run.py
```

The resulting executable will be found in the `dist` folder.

### 4. Running the Application

Once compiled or if you are using the script directly, you can launch the app by running:

```bash
python run.py
```

Or if you compiled it:

- **Windows**: Double-click the `run.exe` file to launch the GUI.

### 5. Using the Application

- **Import Contacts**: Click the "1) Import Contacts" button and select a `.txt` file with phone numbers (e.g., `+1234567890` format).
- **Import Message**: Click the "2) Import Message" button and select a `.txt` file with the message you want to send.
- **Launch WhatsApp Web**: Click the "3) Launch WA Web" button to open WhatsApp Web and scan the QR code with your phone.
- **Send Messages**: Click the "4) Run" button to start sending messages to your contacts.

The logs will be displayed in the GUI as the application sends messages.

### 6. Troubleshooting

- If the browser doesn't open or the QR code doesn’t load, check if you have the latest version of **Chrome** and **Chromedriver**.
- If the application doesn't work as expected, ensure the `userData` folder is in the correct location and contains valid session data from WhatsApp Web.

---

## License

This application is open-source. You are free to modify and distribute it under your own terms.

---

This README should provide a good starting point for users to understand, set up, and use your application. Feel free to adjust it based on any additional details or requirements!

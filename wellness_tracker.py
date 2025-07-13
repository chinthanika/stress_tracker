import os
import csv
import time
import json
import threading
import queue
from datetime import datetime

import tkinter as tk
from tkinter import simpledialog

from plyer import notification
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

stop_polling = False

# -------------------- CONFIGURATION --------------------

CONFIG_FILE = "config.json"
LOG_FILE = os.path.expanduser("symptom_log.csv")
DEFAULT_ICON_PATH = "icon.png"
default_config = {
    "symptoms": ["Head", "Hand", "Leg"],
    "tags": ["Pain", "Numbness", "Tingling", "Other"],
    "reminders": {
        "Water Reminder": {
            "interval_min": 42,
            "message": "Take a sip of water!"
        },
        "Mood/Stress Check": {
            "interval_min": 60,
            "message": "Log your mood and stress."
        },
        "Stretch Break": {
            "interval_min": 60,
            "message": "Take a short movement break!"
        },
        "Snack Time": {
            "interval_min": 180,
            "message": "Consider a healthy snack."
        }
    }
}


# -------------------- STATE --------------------

config = default_config
last_boot_time = time.time()
dialog_queue = queue.Queue()

# -------------------- UTILITIES --------------------

def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            # Merge missing keys from default_config
            for key, value in default_config.items():
                if key not in loaded:
                    loaded[key] = value
            config = loaded
            print("[INFO] Loaded config.json")
        except Exception as e:
            print(f"[WARN] Failed to load config.json, using defaults: {e}")
            config = default_config
    else:
        print("[INFO] No config.json found, using default settings.")
        config = default_config


def notify(title, message):
    print(f"[NOTIFY] {title}: {message}")
    notification.notify(
        title=title,
        message=message,
        timeout=5,
        app_name="WellnessTracker"
    )


def get_note_dialog():
    # Instead of showing dialog here, send a request to the main thread
    result_queue = queue.Queue()
    dialog_queue.put(result_queue)
    # Wait for the main thread to process and return the result
    return result_queue.get()


def log_entry(entry_type, detail, note=""):
    now = datetime.now()
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            entry_type,
            detail,
            note
        ])
    print(f"[LOG] {entry_type}: {detail} | Note: {note}")


# -------------------- REMINDERS --------------------

def reminder_loop(name, interval_min, message):
    print(f"[INFO] Starting '{name}' every {interval_min} minutes.")
    while True:
        time.sleep(interval_min * 60)
        notify(name, message)


# -------------------- MENU ACTIONS --------------------

def log_symptom(symptom, with_note=False):
    def inner():
        note = get_note_dialog() if with_note else ""
        tag_list = config.get("tags", [])
        tag = tag_list[0] if tag_list else "None"
        log_entry("Symptom", f"{symptom} - {tag}", note)
        notify("Logged", f"{symptom} logged.")
    return inner


def log_mood(level, with_note=False):
    def inner():
        note = get_note_dialog() if with_note else ""
        log_entry("Mood", f"Level {level}", note)
        notify("Logged", f"Mood level {level}")
    return inner


def log_stress(level, with_note=False):
    def inner():
        note = get_note_dialog() if with_note else ""
        log_entry("Stress", f"Level {level}", note)
        notify("Logged", f"Stress level {level}")
    return inner


def exit_app(icon, item):
    global stop_polling
    print("[INFO] Exiting application.")
    stop_polling = True
    icon.stop()

def process_dialog_queue():
    global stop_polling
    if stop_polling:
        return
    try:
        while not dialog_queue.empty():
            result_queue = dialog_queue.get_nowait()
            root = tk.Tk()
            root.withdraw()
            note = simpledialog.askstring("Note", "Note:")
            root.destroy()
            result_queue.put(note or "")
    except Exception as e:
        print(f"[ERROR] Dialog error: {e}")
    # Call again after 200ms
    threading.Timer(0.2, process_dialog_queue).start()



def create_icon():
    try:
        return Image.open(DEFAULT_ICON_PATH)
    except Exception as e:
        print(f"[WARN] Using fallback tray icon: {e}")
        image = Image.new('RGB', (64, 64), color='purple')
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill='white')
        return image


# -------------------- MAIN --------------------

def main():
    print("[INFO] Starting Wellness Tracker...")
    load_config()

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Time", "Type", "Detail", "Note"])
        print("[INFO] Created new symptom_log.csv")
    else:
        print(f"[INFO] Log file exists at {LOG_FILE}")

    now = time.time()
    inactive_hours = round((now - last_boot_time) / 3600, 2)
    log_entry("Inactivity", f"{inactive_hours} hours since last use")

    # Start reminder threads
    for name, data in config["reminders"].items():
        threading.Thread(target=reminder_loop, args=(f"🔔 {name}", data["interval_min"], data["message"]), daemon=True).start()

    # Tray menu structure
    menu = Menu(
        MenuItem("Log Symptom", Menu(
            *[
                MenuItem(symptom, Menu(
                    *[
                        MenuItem(tag, Menu(
                            MenuItem("Just Log", log_symptom(f"{symptom} [{tag}]", with_note=False)),
                            MenuItem("Log with Note", log_symptom(f"{symptom} [{tag}]", with_note=True))
                        )) for tag in config.get("tags", [])
                    ]
                )) for symptom in config.get("symptoms", [])
            ]
        )),
        MenuItem("Log Mood", Menu(
            *[
                MenuItem(f"Level {i}", Menu(
                    MenuItem("Just Log", log_mood(i, with_note=False)),
                    MenuItem("Log with Note", log_mood(i, with_note=True))
                )) for i in range(1, 6)
            ]
        )),
        MenuItem("Log Stress", Menu(
            *[
                MenuItem(f"Level {i}", Menu(
                    MenuItem("Just Log", log_stress(i, with_note=False)),
                    MenuItem("Log with Note", log_stress(i, with_note=True))
                )) for i in range(1, 6)
            ]
        )),
        MenuItem("Exit", exit_app)
    )

    process_dialog_queue()  # Start polling for dialog requests
    icon = Icon("WellnessTracker", icon=create_icon(), menu=menu)
    print("[INFO] Tray icon initialized. Right-click to log.")
    icon.run()


if __name__ == '__main__':
    main()

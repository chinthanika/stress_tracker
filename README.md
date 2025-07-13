# WellnessTracker

A lightweight system tray app for logging symptoms, mood, and stress with optional notes. Includes periodic reminders to hydrate, stretch, and take breaks.

## Features

- Log symptoms by body part and tag  
- Mood and stress logging (scale 1–5)  
- Optional notes for any log entry  
- Periodic reminders for hydration, breaks, and food  
- Logs saved in `symptom_log.csv`  
- Configuration via `config.json`  
- Minimal interface via system tray.

## Usage

1. After running the app, a tray icon will appear in your system tray (bottom-right corner on Windows).
2. Right-click the tray icon to open the menu.
3. From the menu, you can:
   - Log a **symptom** by selecting a body part and tag.
   - Log your **mood** or **stress level** (1 to 5).
   - Choose **"Log with Note"** to add a short description to any entry.
4. The app will send **reminders** at set intervals to:
   - Drink water
   - Take a break
   - Log your mood and stress
5. All logs are saved to `symptom_log.csv` in the project folder.

To exit the app, right-click the tray icon and select **Exit**.


## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/wellnesstracker.git
cd wellnesstracker
```

Install dependencies:

```bash

pip install -r requirements.txt
```
Run the app:

```bash
python wellness_tracker.py
```

## Configuration
Edit config.json (auto-created on first run) to customize:

```json
{
  "symptoms": ["Head", "Hand", "Leg"],
  "tags": ["Pain", "Numbness", "Tingling", "Other"],
  "reminders": {
    "Water Reminder": {
      "interval_min": 42,
      "message": "Take a sip of water!"
    },
    "Stretch Break": {
      "interval_min": 60,
      "message": "Take a short movement break!"
    }
  }
}
```

## Log Format
Logs are saved as CSV with the following fields:

```csv
Date,Time,Type,Detail,Note
```

Example:

```csv
2025-07-12,15:00:12,Symptom,Hand [Numbness],Pins and needles  
2025-07-12,15:30:00,Mood,Level 4,Feeling okay
```

## Notes
- Designed for Windows
- No GUI windows beyond optional note input (May be included in future updates)
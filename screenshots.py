import time
import os
from datetime import datetime
from PIL import ImageGrab

# Folder to store screenshots
save_dir = os.path.join(os.getcwd(), "screenshots")
os.makedirs(save_dir, exist_ok=True)

print("Starting screenshot capture every 5 minutes. Press Ctrl+C to stop.")

try:
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(save_dir, f"screenshot_{timestamp}.png")
        img = ImageGrab.grab()
        img.save(filepath)
        print(f"Saved: {filepath}")
        time.sleep(300)  # 5 minutes = 300 seconds
except KeyboardInterrupt:
    print("Screenshot capture stopped.")

#!/usr/bin/env python3
"""
Consent-based Android remote view + periodic recordings helper.

Features:
- Optionally enable ADB over TCP and connect to a device IP (if you want network).
- Start scrcpy for live viewing (requires scrcpy installed).
- Periodically run `adb shell screenrecord` for short intervals, pull the file to ./recordings/,
  and remove the file from the device.
- Start a simple HTTP server serving the recordings folder (so you can view/download).
- Logs actions to console.

USAGE:
    python android_remote_view_and_record.py

Dependencies:
- Python 3.8+
- adb (Android Platform Tools) on PATH
- scrcpy on PATH (optional but recommended for live viewing)

IMPORTANT:
- Only run on devices you own or have explicit consent to monitor.
"""

import subprocess
import threading
import time
import os
import sys
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

# CONFIG
RECORD_DURATION = 30            # seconds per recording on device
RECORD_INTERVAL = 60            # seconds between recordings (start-to-start)
RECORDINGS_DIR = "recordings"   # local directory to store pulled recordings
ADB_CMD = "adb"                 # adb command (must be on PATH)
SCRCPY_CMD = "scrcpy"           # scrcpy command (must be on PATH) - optional
HTTP_PORT = 8000                # local HTTP server port for serving recordings
ENABLE_SCRCPY = True            # set False if you don't want live mirror
ENABLE_ADB_TCP = False          # if True, script will run `adb tcpip 5555` (you still must connect)
DEVICE_IP = None                # set to device IP if using network (e.g., "192.168.1.42:5555")

# Helper functions
def run_cmd(cmd, capture_output=False, check=False):
    """Run a shell command; returns CompletedProcess."""
    try:
        if capture_output:
            return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check, text=True)
        else:
            return subprocess.run(cmd, shell=True, check=check)
    except subprocess.CalledProcessError as e:
        print(f"[!] Command failed: {cmd}\n    returncode={e.returncode}")
        if capture_output:
            print("    stdout:", e.stdout)
            print("    stderr:", e.stderr)
        return None

def ensure_recordings_dir():
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)

def adb_devices():
    """Return list of connected adb devices (id, status)."""
    cp = run_cmd(f"{ADB_CMD} devices", capture_output=True)
    if not cp:
        return []
    lines = cp.stdout.strip().splitlines()
    devices = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices

def enable_adb_tcp():
    print("[*] Enabling ADB over TCP on device (adb tcpip 5555). Make sure device is connected by USB and authorized.")
    run_cmd(f"{ADB_CMD} tcpip 5555")

def connect_adb_over_tcp(device_ip):
    if not device_ip:
        print("[!] No device IP provided for ADB connect.")
        return False
    print(f"[*] Connecting via adb to {device_ip} ...")
    cp = run_cmd(f"{ADB_CMD} connect {device_ip}", capture_output=True)
    if cp and ("connected" in cp.stdout.lower() or "already connected" in cp.stdout.lower()):
        print("[*] ADB connected over network.")
        return True
    else:
        print("[!] ADB connect result:", cp.stdout if cp else "No output")
        return False

def start_scrcpy():
    if shutil.which(SCRCPY_CMD) is None:
        print("[!] scrcpy not found in PATH. Install scrcpy if you want live mirroring.")
        return None
    print("[*] Starting scrcpy (live mirror). Close the scrcpy window to stop mirroring.")
    # Start scrcpy as a subprocess (no shell to allow Ctrl-C handling)
    return subprocess.Popen([SCRCPY_CMD], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def record_once(local_tag=None):
    """
    Records RECORD_DURATION seconds on the device, pulls the file, and deletes it from device.
    Filename uses timestamp to avoid collisions.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    device_path = f"/sdcard/rec_{timestamp}.mp4"
    local_filename = f"rec_{timestamp}.mp4"
    local_path = os.path.join(RECORDINGS_DIR, local_filename)
    print(f"[*] Starting device recording for {RECORD_DURATION}s -> {device_path}")
    # Start screenrecord on device (blocks until duration or killed)
    # Use --time-limit (Android 9+) or rely on command end when time limit reached
    cmd_record = f'{ADB_CMD} shell screenrecord --time-limit {RECORD_DURATION} "{device_path}"'
    # Run recording (this will block until complete)
    p = run_cmd(cmd_record)
    # Pull file to local
    print("[*] Pulling recording to local machine...")
    run_cmd(f'{ADB_CMD} pull "{device_path}" "{local_path}"')
    # Delete from device
    run_cmd(f'{ADB_CMD} shell rm "{device_path}"')
    if os.path.exists(local_path):
        print(f"[+] Saved recording: {local_path}")
    else:
        print("[!] Recording pull failed or file not found.")

def recording_loop(stop_event):
    """Loop that records periodically until stop_event is set."""
    print("[*] Recording loop started. Press Ctrl+C to stop the script (it will also stop recordings after current cycle).")
    next_time = time.time()
    while not stop_event.is_set():
        now = time.time()
        if now >= next_time:
            try:
                record_once()
            except Exception as e:
                print(f"[!] Error during recording: {e}")
            next_time = now + RECORD_INTERVAL
        # Sleep a short bit and check again
        time.sleep(1)
    print("[*] Recording loop stopped.")

def start_http_server():
    """Starts a simple HTTP server in the recordings directory to serve files for viewing."""
    os.chdir(RECORDINGS_DIR)
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("", HTTP_PORT), handler)
    print(f"[*] Serving recordings folder at http://0.0.0.0:{HTTP_PORT}/ (press Ctrl+C to stop server)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("[*] HTTP server stopped.")

def main():
    print("=== Consent-based Android Live View & Recorder ===")
    print("Make sure USB debugging is enabled and you authorized this PC on the device.")
    print("Only use on devices you own or have explicit permission to monitor.")
    ensure_recordings_dir()

    # Optionally enable adb tcpip
    if ENABLE_ADB_TCP:
        enable_adb_tcp()
        if DEVICE_IP:
            connected = connect_adb_over_tcp(DEVICE_IP)
            if not connected:
                print("[!] Could not connect over TCP. Ensure device IP is correct and on same network.")
    else:
        devices = adb_devices()
        if not devices:
            print("[!] No adb devices found. Connect device via USB or enable adb over network and set ENABLE_ADB_TCP=True")
            return
        else:
            print(f"[*] Found adb devices: {devices}")

    # Start scrcpy in background (if enabled)
    scrcpy_proc = None
    if ENABLE_SCRCPY:
        scrcpy_proc = start_scrcpy()

    # Start recording loop thread
    stop_event = threading.Event()
    rec_thread = threading.Thread(target=recording_loop, args=(stop_event,), daemon=True)
    rec_thread.start()

    # Start HTTP server in main thread to serve recordings
    try:
        start_http_server()
    except KeyboardInterrupt:
        print("[*] KeyboardInterrupt received - shutting down...")
    finally:
        # signal recording loop to stop
        stop_event.set()
        rec_thread.join(timeout=5)
        if scrcpy_proc:
            try:
                scrcpy_proc.terminate()
            except Exception:
                pass
        print("[*] Exiting. Recordings are available in the 'recordings/' directory.")

if __name__ == "__main__":
    main()

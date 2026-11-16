"""Screenshot the Apex client window (copied from apex\r5-tas\tools\snap.py).

    python tools/snap.py build/shots/x.png [--pid N] [--fg]

Default: PrintWindow(PW_RENDERFULLCONTENT). --fg puts the window on top and copies the
screen instead (for when the D3D12 swapchain never reaches the window DC -> black).
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import time
from pathlib import Path

from PIL import Image, ImageGrab

u32 = ctypes.windll.user32
g32 = ctypes.windll.gdi32
u32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))


def find_window(pid=None):
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(h, _):
        if not u32.IsWindowVisible(h):
            return True
        p = wt.DWORD()
        u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        buf = ctypes.create_unicode_buffer(256)
        u32.GetWindowTextW(h, buf, 256)
        if (pid and p.value == pid) or (not pid and buf.value == "Apex Legends"):
            r = wt.RECT()
            u32.GetWindowRect(h, ctypes.byref(r))
            found.append((h, (r.right - r.left) * (r.bottom - r.top)))
        return True

    u32.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("no Apex window")
    return max(found, key=lambda t: t[1])[0]


def print_window(h):
    r = wt.RECT()
    u32.GetClientRect(h, ctypes.byref(r))
    w, hgt = r.right, r.bottom
    hdc = u32.GetDC(h)
    mdc = g32.CreateCompatibleDC(hdc)
    bmp = g32.CreateCompatibleBitmap(hdc, w, hgt)
    g32.SelectObject(mdc, bmp)
    u32.PrintWindow(h, mdc, 3)          # PW_CLIENTONLY | PW_RENDERFULLCONTENT
    bmi = (ctypes.c_byte * 40)()
    ctypes.memmove(bmi, ctypes.byref(ctypes.c_int32(40)), 4)
    ctypes.memmove(ctypes.byref(bmi, 4), ctypes.byref(ctypes.c_int32(w)), 4)
    ctypes.memmove(ctypes.byref(bmi, 8), ctypes.byref(ctypes.c_int32(-hgt)), 4)
    ctypes.memmove(ctypes.byref(bmi, 12), ctypes.byref(ctypes.c_int16(1)), 2)
    ctypes.memmove(ctypes.byref(bmi, 14), ctypes.byref(ctypes.c_int16(32)), 2)
    buf = (ctypes.c_char * (w * hgt * 4))()
    g32.GetDIBits(mdc, bmp, 0, hgt, buf, bmi, 0)
    g32.DeleteObject(bmp)
    g32.DeleteDC(mdc)
    u32.ReleaseDC(h, hdc)
    return Image.frombuffer("RGBA", (w, hgt), bytes(buf), "raw", "BGRA", 0, 1).convert("RGB")


def screen_grab(h):
    u32.SetWindowPos(h, -1, 0, 0, 0, 0, 3)        # topmost
    u32.keybd_event(0x12, 0, 0, 0)
    u32.keybd_event(0x12, 0, 2, 0)
    u32.SetForegroundWindow(h)
    time.sleep(0.7)
    r = wt.RECT()
    u32.GetClientRect(h, ctypes.byref(r))
    p = wt.POINT(0, 0)
    u32.ClientToScreen(h, ctypes.byref(p))
    img = ImageGrab.grab((p.x, p.y, p.x + r.right, p.y + r.bottom), all_screens=True)
    u32.SetWindowPos(h, -2, 0, 0, 0, 0, 3)        # not topmost
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--pid", type=int)
    ap.add_argument("--fg", action="store_true")
    a = ap.parse_args()
    h = find_window(a.pid)
    img = screen_grab(h) if a.fg else print_window(h)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(a.out)
    ext = img.getextrema()
    print("saved", a.out, img.size, "extrema", ext)

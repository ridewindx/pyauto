from ctypes import *
import platform
import os


user32 = windll.user32


EnumWindowsProc = WINFUNCTYPE(c_bool, POINTER(c_void_p), POINTER(c_long))


def win_list(filter=None):
    hwnd_list = []

    def _enum_winows_proc(hwnd, lParam):
        if user32.IsWindowVisible(hwnd) and (filter is None or filter(hwnd)):
            hwnd_list.append(hwnd)
        return True

    enum_winows_proc = EnumWindowsProc(_enum_winows_proc)
    user32.EnumWindows(enum_winows_proc, 0)

    return hwnd_list


user32.GetWindowTextLengthW.argtypes = [c_void_p]
user32.GetWindowTextW.argtypes = [c_void_p, c_wchar_p, c_int]


def win_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    buff = create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

from ctypes import *

kernel32 = windll.kernel32

MAX_PATH = 260

TH32CS_SNAPPROCESS = 0x00000002
SYNCHRONIZE = 1048576
STANDARD_RIGHTS_REQUIRED = 983040
PROCESS_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 4095)


class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('cntUsage', c_ulong),
        ('th32ProcessID', c_ulong),
        ('th32DefaultHeapID', POINTER(c_ulong)),
        ('th32ModuleID', c_ulong),
        ('cntThreads', c_ulong),
        ('th32ParentProcessID', c_ulong),
        ('pcPriClassBase', c_long),
        ('dwFlags', c_ulong),
        ('szExeFile', create_string_buffer(MAX_PATH))
    ]


class MODULEENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('th32ModuleID', c_ulong),
        ('th32ProcessID', c_ulong),
        ('GlblcntUsage', c_ulong),
        ('th32ModuleID', c_ulong),
        ('cntThreads', c_ulong),
        ('th32ParentProcessID', c_ulong),
        ('pcPriClassBase', c_long),
        ('dwFlags', c_ulong),
        ('szExeFile', create_string_buffer(MAX_PATH))
    ]


def get_process_list():
    hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not hProcessSnap:
        return False

    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)

    process_list = []

    def _get_process_info(pe32):
        hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pe32.th32ProcessID)
        dwPriorityClass = 0
        if hProcess:
            dwPriorityClass = kernel32.GetPriorityClass(hProcess) or dwPriorityClass
            kernel32.CloseHandle(hProcess)
        process_list.append({
            'name': pe32.szExeFile,
            'pid': pe32.th32ProcessID,
            'ppid': pe32.th32ParentProcessID,
            'threads': pe32.cntThreads,
            'priority_base': pe32.pcPriClassBase,
            'priority_class': dwPriorityClass
        })

    if kernel32.Process32First(hProcessSnap, pointer(pe32)):
        _get_process_info(pe32)

    while kernel32.Process32Next(hProcessSnap, pointer(pe32)):
        _get_process_info(pe32)


    kernel32.CloseHandle(hProcessSnap)
    return process_list


def get_process_modules(pid):

from ctypes import *

kernel32 = windll.kernel32

INVALID_HANDLE_VALUE = -1
MAX_PATH = 260
MAX_MODULE_NAME32 = 255

TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPTHREAD = 0x00000004
SYNCHRONIZE = 1048576
STANDARD_RIGHTS_REQUIRED = 983040
PROCESS_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 4095)


class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('cntUsage', c_ulong),  # no longer used
        ('th32ProcessID', c_ulong),
        ('th32DefaultHeapID', POINTER(c_ulong)),  # no longer used
        ('th32ModuleID', c_ulong),  # no longer used
        ('cntThreads', c_ulong),
        ('th32ParentProcessID', c_ulong),
        ('pcPriClassBase', c_long),
        ('dwFlags', c_ulong),  # no longer used
        ('szExeFile', c_char * MAX_PATH)
    ]


class MODULEENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('th32ModuleID', c_ulong),
        ('th32ProcessID', c_ulong),
        ('GlblcntUsage', c_ulong),
        ('ProccntUsage', c_ulong),
        ('modBaseAddr', c_void_p),
        ('modBaseSize', c_ulong),
        ('hModule', c_void_p),
        ('szModule', c_char * (MAX_MODULE_NAME32 + 1)),
        ('szExePath', c_char * MAX_PATH)
    ]


class THREADENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('cntUsage', c_ulong),
        ('th32ThreadID', c_ulong),
        ('th32OwnerProcessID', c_ulong),
        ('tpBasePri', c_long),
        ('tpDeltaPri', c_long),
        ('dwFlags', c_ulong),
    ]


kernel32.Process32First.argtypes = [c_void_p, POINTER( PROCESSENTRY32)]
kernel32.Process32Next.argtypes = [c_void_p, POINTER(PROCESSENTRY32)]
kernel32.Module32First.argtypes = [c_void_p, POINTER(MODULEENTRY32)]
kernel32.Module32Next.argtypes = [c_void_p, POINTER(MODULEENTRY32)]
kernel32.Thread32First.argtypes = [c_void_p, POINTER(THREADENTRY32)]
kernel32.Thread32Next.argtypes = [c_void_p, POINTER(THREADENTRY32)]


FORMAT_MESSAGE_FROM_SYSTEM = 0x00001000
FORMAT_MESSAGE_IGNORE_INSERTS = 0x00000200
MAKELANGID = lambda p, s: s << 10 | p
LANG_NEUTRAL = 0x0000
SUBLANG_DEFAULT = 0x0400


def get_last_error():
    enum = kernel32.GetLastError()
    msg = create_string_buffer(256)
    kernel32.FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
         None, enum,
         MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),  # Default language
         msg, 256, None)
    return enum, msg.value.decode('gbk')


def get_process_list():
    hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not hProcessSnap:
        return []

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
            'thread_count': pe32.cntThreads,
            'priority_base': pe32.pcPriClassBase,
            'priority_class': dwPriorityClass,
            'modules': get_process_modules(pe32.th32ProcessID),
            'threads': get_process_threads(pe32.th32ProcessID)
        })

    if kernel32.Process32First(hProcessSnap, pointer(pe32)):
        _get_process_info(pe32)

        while kernel32.Process32Next(hProcessSnap, pointer(pe32)):
            _get_process_info(pe32)

    kernel32.CloseHandle(hProcessSnap)
    return process_list


def get_process_modules(pid):
    hModuleSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
    if hModuleSnap == INVALID_HANDLE_VALUE:
        return []

    me32 = MODULEENTRY32()
    me32.dwSize = sizeof(MODULEENTRY32)

    module_list = []

    def _get_module_info(me32):
        module_list.append({
            'name': me32.szModule,
            'id': me32.th32ModuleID,
            'path': me32.szExePath,
            'pid': me32.th32ProcessID,
            'global_usage_count': me32.GlblcntUsage,
            'process_usage_count': me32.ProccntUsage,
            'base_address': me32.modBaseAddr,
            'base_size': me32.modBaseSize
        })

    if kernel32.Module32First(hModuleSnap, pointer(me32)):
        _get_module_info(me32)

        while kernel32.Module32Next(hModuleSnap, pointer(me32)):
            _get_module_info(me32)

    kernel32.CloseHandle(hModuleSnap)
    return module_list


def get_process_threads(pid):
    hThreadSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if hThreadSnap == INVALID_HANDLE_VALUE:
        return []

    te32 = THREADENTRY32()
    te32.dwSize = sizeof(THREADENTRY32)

    thread_list = []

    def _get_thread_info(te32):
        if te32.th32OwnerProcessID == pid:
            thread_list.append({
                'thread_id': te32.th32ThreadID,
                'base_priority': te32.tpBasePri,
                'delta_priority': te32.tpDeltaPri
            })

    if kernel32.Thread32First(hThreadSnap, pointer(te32)):
        _get_thread_info(te32)

        while kernel32.Thread32Next(hThreadSnap, pointer(te32)):
            _get_thread_info(te32)

    kernel32.CloseHandle(hThreadSnap)
    return thread_list


if __name__ == '__main__':
    l = get_process_list()
    import json
    json.dump(l, open('process_list.json', 'w'), indent=2)

from ctypes import *

kernel32 = windll.kernel32
advapi32 = windll.advapi32

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
        ('cntThreads', c_ulong),  # The number of execution threads started by the process
        ('th32ParentProcessID', c_ulong),
        ('pcPriClassBase', c_long),  # The base priority of any threads created by this process
        ('dwFlags', c_ulong),  # no longer used
        ('szExeFile', c_char * MAX_PATH)  # The name of the executable file for the process
    ]


class MODULEENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('th32ModuleID', c_ulong),  # no longer used
        ('th32ProcessID', c_ulong),
        ('GlblcntUsage', c_ulong),  # The load count of the module, which is not generally meaningful, and usually equal to 0xFFFF
        ('ProccntUsage', c_ulong),  # The load count of the module (same as GlblcntUsage), which is not generally meaningful, and usually equal to 0xFFFF
        ('modBaseAddr', c_void_p),  # The base address of the module in the context of the owning process
        ('modBaseSize', c_ulong),  # The size of the module, in bytes
        ('hModule', c_void_p),  # A handle to the module in the context of the owning process
        ('szModule', c_char * (MAX_MODULE_NAME32 + 1)),  # The module name
        ('szExePath', c_char * MAX_PATH)  # The module path
    ]


class THREADENTRY32(Structure):
    _fields_ = [
        ('dwSize', c_ulong),
        ('cntUsage', c_ulong),  # no longer used
        ('th32ThreadID', c_ulong),  # The thread identifier
        ('th32OwnerProcessID', c_ulong),
        ('tpBasePri', c_long),  # The kernel base priority level assigned to the thread. The priority is a number from 0 to 31, with 0 representing the lowest possible thread priority
        ('tpDeltaPri', c_long),  # no longer used
        ('dwFlags', c_ulong),  # no longer used
    ]


kernel32.CreateToolhelp32Snapshot.argtypes = [c_ulong, c_ulong]
kernel32.CloseHandle.argtypes = [c_void_p]
kernel32.OpenProcessToken.argtypes = [c_void_p, c_ulong, POINTER(c_void_p)]
kernel32.OpenProcess.argtypes = [c_ulong, c_bool, c_ulong]
kernel32.OpenProcess.restype = c_void_p
kernel32.Process32First.argtypes = [c_void_p, POINTER(PROCESSENTRY32)]
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


def get_last_error(context=''):
    enum = kernel32.GetLastError()
    msg = create_string_buffer(256)
    kernel32.FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
         None, enum,
         MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),  # Default language
         msg, 256, None)
    if context:
        print context, ': ',
    print enum,
    print msg.value.decode('gbk')


def get_process_list():
    thread_list = get_threads()  # get list of all threads

    hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if not hProcessSnap:
        get_last_error('CreateToolhelp32Snapshot')
        return []

    pe32 = PROCESSENTRY32()
    pe32.dwSize = sizeof(PROCESSENTRY32)

    process_list = []

    def _get_process_info(pe32):
        dwPriorityClass = None

        if pe32.th32ProcessID != 0:
            hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pe32.th32ProcessID)

            if not hProcess:
                get_last_error('OpenProcess, pid %s' % pe32.th32ProcessID)
            else:
                dwPriorityClass = kernel32.GetPriorityClass(hProcess) or dwPriorityClass

                enable_debug_privilege(hProcess)

                kernel32.CloseHandle(hProcess)


        process_list.append({
            'name': pe32.szExeFile,
            'pid': pe32.th32ProcessID,
            'ppid': pe32.th32ParentProcessID,
            'priority_base': pe32.pcPriClassBase,
            'priority_class': dwPriorityClass,
            'modules': get_process_modules(pe32.th32ProcessID),
            'thread_count': pe32.cntThreads,
            'threads': [t for t in thread_list if t['pid'] == pe32.th32ProcessID]
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
        get_last_error('CreateToolhelp32Snapshot, TH32CS_SNAPMODULE, pid %s' % pid)
        return []

    me32 = MODULEENTRY32()
    me32.dwSize = sizeof(MODULEENTRY32)

    module_list = []

    def _get_module_info(me32):
        module_list.append({
            'name': me32.szModule,
            'path': me32.szExePath,
            'pid': me32.th32ProcessID,
            'base_address': me32.modBaseAddr,
            'base_size': me32.modBaseSize
        })

    if kernel32.Module32First(hModuleSnap, pointer(me32)):
        _get_module_info(me32)

        while kernel32.Module32Next(hModuleSnap, pointer(me32)):
            _get_module_info(me32)

    kernel32.CloseHandle(hModuleSnap)
    return module_list


def get_threads(pid=None):
    hThreadSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if hThreadSnap == INVALID_HANDLE_VALUE:
        get_last_error('CreateToolhelp32Snapshot, TH32CS_SNAPTHREAD')
        return []

    te32 = THREADENTRY32()
    te32.dwSize = sizeof(THREADENTRY32)

    thread_list = []

    def _get_thread_info(te32):
        if pid is None or te32.th32OwnerProcessID == pid:
            thread_list.append({
                'tid': te32.th32ThreadID,
                'pid': te32.th32OwnerProcessID,
                'base_priority': te32.tpBasePri
            })

    if kernel32.Thread32First(hThreadSnap, pointer(te32)):
        _get_thread_info(te32)

        while kernel32.Thread32Next(hThreadSnap, pointer(te32)):
            _get_thread_info(te32)

    kernel32.CloseHandle(hThreadSnap)
    return thread_list


ANYSIZE_ARRAY = 1
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_QUERY = 0x0008
SE_DEBUG_NAME = 'SeDebugPrivilege'
SE_PRIVILEGE_ENABLED = 2


class LUID(Structure):
    _fields_ = [
        ('LowPart', c_ulong),
        ('HighPart', c_long)
    ]


class LUID_AND_ATTRIBUTES(Structure):
    _fields_ = [
        ('Luid', LUID),
        ('Attributes', c_ulong)
    ]


class TOKEN_PRIVILEGES(Structure):
    _fields_ = [
        ('PrivilegeCount', c_ulong),
        ('Privileges', LUID_AND_ATTRIBUTES * ANYSIZE_ARRAY)
    ]


advapi32.LookupPrivilegeValueA.argtypes = [c_char_p, c_char_p, POINTER(LUID)]
advapi32.AdjustTokenPrivileges.argtypes = [c_void_p, c_bool, POINTER(TOKEN_PRIVILEGES),
                                           c_ulong, POINTER(TOKEN_PRIVILEGES), POINTER(c_ulong)]


def enable_debug_privilege(process_handle):
    hToken = c_void_p()
    if not kernel32.OpenProcessToken(process_handle,
                                     TOKEN_ADJUST_PRIVILEGES | TOKEN_ADJUST_PRIVILEGES,
                                     pointer(hToken)):
        get_last_error('OpenProcessToken')
        return False

    luid = LUID()
    if not advapi32.LookupPrivilegeValueA(None, SE_DEBUG_NAME, pointer(luid)):
        get_last_error('LookupPrivilegeValueA')
        kernel32.CloseHandle(hToken)
        return False

    tp = TOKEN_PRIVILEGES()
    tp.PrivilegeCount = 1
    tp.Privileges[0].Luid = luid
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED

    if not advapi32.AdjustTokenPrivileges(hToken, False, pointer(tp), sizeof(TOKEN_PRIVILEGES), None, None):
        get_last_error('AdjustTokenPrivileges')
        kernel32.CloseHandle(hToken)
        return False

    kernel32.CloseHandle(hToken)
    return True


if __name__ == '__main__':
    l = get_process_list()
    import json
    json.dump(l, open('process_list.json', 'w'), indent=2)

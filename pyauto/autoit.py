from ctypes import *
import platform
import os


arch = platform.architecture()[0]
audll = 'AutoItX3_x64.dll' if arch == '64bit' else 'AutoItX3.dll'
audll = os.path.join(os.path.dirname(__file__), audll)
au = windll.LoadLibrary(audll)   # windll, since "#define WINAPI __stdcall"


au.AU3_ProcessClose.argtypes = [c_wchar_p]
au.AU3_ProcessExists.argtypes = [c_wchar_p]
au.AU3_ProcessSetPriority.argtypes = [c_wchar_p, c_int]
au.AU3_ProcessWait.argtypes = [c_wchar_p, c_int]
au.AU3_ProcessWaitClose.argtypes = [c_wchar_p, c_int]
au.AU3_Run.argtypes = [c_wchar_p, c_wchar_p, c_int]
au.AU3_RunWait.argtypes = [c_wchar_p, c_wchar_p, c_int]
au.AU3_Shutdown.argtypes = [c_int]
au.AU3_INTDEFAULT = -2147483647
au.AU3_ToolTip.argtypes = [c_wchar_p, c_int, c_int]
au.AU3_ClipGet.argtypes = [c_wchar_p, c_int]
au.AU3_ClipPut.argtypes = [c_wchar_p]
au.AU3_AutoItSetOption.argtypes = [c_wchar_p, c_int]
au.AU3_MouseClick.argtypes = [c_wchar_p, c_int, c_int, c_int, c_int]
au.AU3_MouseClickDrag.argtypes = [c_wchar_p, c_int, c_int, c_int, c_int, c_int]
au.AU3_MouseDown.argtypes = [c_wchar_p]
au.AU3_MouseGetPos.argtypes = []
au.AU3_MouseMove.argtypes = [c_int, c_int, c_int]
au.AU3_MouseUp.argtypes = [c_wchar_p]
au.AU3_MouseWheel.argtypes = [c_wchar_p, c_int]
au.AU3_Send.argtypes = [c_wchar_p, c_int]


def is_admin():
    """Checks if the current user has administrator privileges.
    Always return 1 under Window 95/98/Me.

    :return: 1 if the current user has administrator privileges, 0 if user lacks admin privileges
    """
    return au.AU3_IsAdmin()


def process_close(process):
    """Terminates a named process.
    Process names are executables without the full path, e.g., "notepad.exe" or "winword.exe".
    If multiple processes have the same name, the one with the highest PID is terminated--regardless
    of how recently the process was spawned.
    PID is the unique number which identifies a Process.

    :param process: The name or PID of the process to terminate, e.g., "notepad.exe" or 3647
    :return: None
    """
    au.AU3_ProcessClose(unicode(process))


def process_exists(process):
    """Checks to see if a specified process exists.
    Process names are executables without the full path, e.g., "notepad.exe" or "winword.exe".
    PID is the unique number which identifies a Process.

    :param process: The name or PID of the process to check, e.g., "notepad.exe" or 3647
    :return: the PID of the process, or 0 if process does not exist
    """
    return au.AU3_ProcessExists(unicode(process))


def process_set_priority(process, priority):
    """Changes the priority of a process.

    :param process: The name or PID of the process to check
    :param priority: 'idle'/'low', 'below_normal', 'normal', 'above_normal', 'high', 'realtime'
    :return: 1 if success, 0 if failure
    """
    priority_mapping = {'idle': 0, 'low': 0,
                        'below_normal': 1,
                        'normal': 2,
                        'above_normal': 3,
                        'high': 4,
                        'realtime': 5}  # Use with caution, may make the system unstable
    return au.AU3_ProcessSetPriority(unicode(process), priority_mapping[priority])


def process_wait(process, timeout=0):
    """Pauses script execution until a given process exists.
    Process names are executables without the full path, e.g., "notepad.exe" or "winword.exe".
    This function is the only process function not to accept a PID.
    Because PIDs are allocated randomly, waiting for a particular PID to exist doesn't make sense.

    :param process: The name of the process to check, e.g., "notepad.exe"
    :param timeout: Specifies how long to wait (default 0 is to wait indefinitely)
    :return: 1 if success, 0 if the wait timed out
    """
    return au.AU3_ProcessWait(unicode(process), timeout)


def process_wait_close(process, timeout=0):
    """Pauses script execution until a given process does not exist.
    Process names are executables without the full path, e.g., "notepad.exe" or "winword.exe"
    PID is the unique number which identifies a Process.

    :param process: The name or PID of the process to check
    :param timeout: Specifies how long to wait (default 0 is to wait indefinitely)
    :return: 1 if success, 0 if the wait timed out
    """
    return au.AU3_ProcessWaitClose(unicode(process), timeout)


# The show state of the window:
SW_HIDE = 0
SW_SHOWNORMAL = 1
SW_NORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3
SW_MAXIMIZE = 3
SW_SHOWNOACTIVATE = 4
SW_SHOW = 5
SW_MINIMIZE = 6
SW_SHOWMINNOACTIVE = 7
SW_SHOWNA = 8
SW_RESTORE = 9
SW_SHOWDEFAULT = 10
SW_FORCEMINIMIZE = 11
SW_MAX = 11


def run(filename, workingdir=u'', show_flag=SW_SHOWNORMAL):
    """Runs an external program.
    After running the requested program the script continues.
    To pause execution of the script until the spawned program has finished use the RunWait function instead.

    :param filename: The name of the executable (EXE, BAT, COM, or PIF) to run
    :param workingdir: The working directory
    :param show_flag: The "show" flag of the executed program
    :return: The PID of the process that was launched, or 0 on failure
    """
    return au.AU3_Run(unicode(filename), unicode(workingdir), show_flag)


def run_wait(filename, workingdir=u'', show_flag=SW_SHOWNORMAL):
    """Runs an external program and pauses script execution until the program finishes.
    After running the requested program the script pauses until the program terminates.
    To run a program and then immediately continue script execution use the Run function instead.

    Some programs will appear to return immediately even though they are still running;
    these programs spawn another process - you may be able to use the ProcessWaitClose function to handle these cases.

    :param filename: The name of the executable (EXE, BAT, COM, or PIF) to run
    :param workingdir: The working directory
    :param show_flag: The "show" flag of the executed program
    :return: Returns the exit code of the program that was run
    """
    return au.AU3_RunWait(unicode(filename), unicode(workingdir), show_flag)


def shutdown(codes):
    """Shuts down the system.
    Add the required values together.
    To shutdown and power down, for example, the code would be 9 (shutdown + power down = 1 + 8 = 9).

    :param codes: A combination of shutdown codes: 'logoff', 'shutdown', 'reboot', 'force', 'powerdown'
    :return: 1 if success, 0 if failure
    """
    code_mapping = {'logoff': 0, 'shutdown': 1, 'reboot': 2, 'force': 4, 'powerdown': 8}
    return au.AU3_Shutdown(sum(map(code_mapping.get, codes)))


def tooltip(text, x=None, y=None):
    """Creates a tooltip anywhere on the screen.
    If the x and y coordinates are omitted the, tip is placed near the mouse cursor.
    If the coords would cause the tooltip to run off screen, it is repositioned to visible.
    Tooltip appears until it is cleared, until script terminates, or sometimes until it is clicked upon.
    You may use a linefeed character to create multi-line tooltips.

    :param text: The text of the tooltip. (An empty string clears a displaying tooltip)
    :param x: The y position of the tooltip
    :param y: The y position of the tooltip
    :return: None
    """
    au.AU3_ToolTip(unicode(text), x if x is None else au.AU3_INTDEFAULT, y if y is None else au.AU3_INTDEFAULT)


def clip_get(bufsize=4096):
    """Retrieves text from the clipboard.
    If the clipboard contains a non-text entry, retrieves the file path to that entry.

    :param bufsize: The maximal length of the returned string, may be truncated
    :return: A string containing the text on the clipboard
    """
    b = create_unicode_buffer(bufsize + 1)
    au.AU3_ClipGet(b, bufsize + 1)
    return b.value


def clip_put(value):
    """Writes text to the clipboard.
    Any existing clipboard contents are overwritten.

    :param value: The text to write to the clipboard
    :return: 1 if success, 0 if failure
    """
    return au.AU3_ClipPut(unicode(value))


def set_option(option, value):
    """Changes the operation of various AutoIt functions/parameters.

    :param option: The option to change
    :param value: The value of the option setting
    :return: The value of the previous setting
    """
    return au.AU3_AutoItSetOption(unicode(option), value)


def set_mouse_click_delay(delay=10):
    """Alters the length of the brief pause in between mouse clicks.

    :param delay: Time in milliseconds to pause (default=10)
    :return:
    """
    return set_option('MouseClickDelay', delay)


def set_mouse_click_down_delay(delay=10):
    """Alters the length a click is held down before release.

    :param delay: Time in milliseconds to pause (default=10)
    :return:
    """
    return set_option('MouseClickDownDelay', delay)


def set_mouse_click_drag_delay(delay=250):
    """Alters the length of the brief pause at the start and end of a mouse drag operation.

    :param delay: Time in milliseconds to pause (default=250)
    :return:
    """
    return set_option('MouseClickDragDelay', delay)


def mouse_click(button='', x=None, y=None, clicks=1, speed=10):
    """Perform a mouse click operation.

    :param button: The button to click: "left", "right", "middle", "main", "menu", "primary", "secondary".
    If the button is an empty string, the left button will be clicked.
    If the user has swapped the left and right mouse buttons in the control panel,
    the "primary" or "main" button will be the main click, whether or not the buttons are swapped.
    the "secondary" or "menu" buttons will usually bring up the context menu, whether the buttons are swapped or not
    :param x: The x/y coordinates to move the mouse to. If no x and y coords are given, the current position is used
    :param y: The x/y coordinates to move the mouse to. If no x and y coords are given, the current position is used
    :param clicks: The number of times to click the mouse. Default is 1
    :param speed: The speed to move the mouse in the range 1 (fastest) to 100 (slowest).
    A speed of 0 will move the mouse instantly. Default speed is 10
    :return: None
    """
    au.AU3_MouseClick(unicode(button),
                      x if x is None else au.AU3_INTDEFAULT, y if y is None else au.AU3_INTDEFAULT,
                      clicks, speed)


def mouse_click_drag(button, x1, y1, x2, y2, speed=10):
    """Perform a mouse click and drag operation.

    :param button: The button to click: "left", "right", "middle", "main", "menu", "primary", "secondary"
    :param x1: The x/y coords to start the drag operation from
    :param y1: The x/y coords to start the drag operation from
    :param x2: The x/y coords to start the drag operation to
    :param y2: The x/y coords to start the drag operation to
    :param speed: The speed to move the mouse in the range 1 (fastest) to 100 (slowest).
    A speed of 0 will move the mouse instantly. Default speed is 10
    :return: None
    """
    au.AU3_MouseClickDrag(unicode(button), x1, y1, x2, y2, speed)


def mouse_down(button=''):
    """Perform a mouse down event at the current mouse position.
    Use responsibly: For every mouse_down there should eventually be a corresponding mouse_up event.

    :param button: The button to click: "left", "right", "middle", "main", "menu", "primary", "secondary"
    :return: None
    """
    au.AU3_MouseDown(unicode(button))


def mouse_up(button=''):
    """Perform a mouse up event at the current mouse position.
    Use responsibly: For every mouse_down there should eventually be a corresponding mouse_up event.

    :param button: The button to click: "left", "right", "middle", "main", "menu", "primary", "secondary"
    :return: None
    """
    au.AU3_MouseUp(unicode(button))


def mouse_move(x, y, speed=10):
    """Moves the mouse pointer.
    User mouse movement is hindered during a non-instantaneous MouseMove operation.
    If MouseCoordMode is relative positioning, numbers may be negative.

    :param x: The screen x coordinate to move the mouse to
    :param y: The screen y coordinate to move the mouse to
    :param speed: The speed to move the mouse in the range 1 (fastest) to 100 (slowest).
    A speed of 0 will move the mouse instantly. Default speed is 10
    :return: None
    """
    au.AU3_MouseMove(x, y, speed)


def mouse_wheel(direction, clicks=1):
    """Moves the mouse wheel up or down. XP ONLY.

    :param direction: "up" or "down"
    :param clicks: The number of times to move the wheel. Default is 1
    :return: None
    """
    au.AU3_MouseWheel(unicode(direction), clicks)


class _Point(Structure):
    _fields_ = [('x', c_long), ('y', c_long)]


def mouse_get_pos():
    """Retrieves the current X,Y position of the mouse cursor.

    :return: A tuple of the x,y positions of the mouse cursor
    """
    ppos = pointer(_Point())
    au.AU3_MouseGetPos(ppos)
    return ppos.contents.x, ppos.contents.y


UNKNOWN = 0  # (this includes pointing and grabbing hand icons)
APPSTARTING = 1
ARROW = 2
CROSS = 3
HELP = 4
IBEAM = 5
ICON = 6
NO = 7
SIZE = 8
SIZEALL = 9
SIZENESW = 10
SIZENS = 11
SIZENWSE = 12
SIZEWE = 13
UPARROW = 14
WAIT = 15


def mouse_get_cursor():
    """Returns a cursor ID Number of the current Mouse Cursor.

    :return: A cursor ID Number
    """
    return au.AU3_MouseGetCursor()


# ------------------------------ Begin send keystrokes ------------------------------


def send(keys, flag=0):
    """Sends simulated keystrokes to the active window.
    The "Send" command syntax is similar to that of ScriptIt and the Visual Basic "SendKeys" command.
    Characters are sent as written with the exception of the following characters:

    '!'
    This tells AutoIt to send an ALT keystroke,
    therefore Send("This is text!a") would send the keys "This is text" and then press "ALT+a".
    N.B. Some programs are very choosy about capital letters and ALT keys, i.e. "!A" is different to "!a".
    The first says ALT+SHIFT+A, the second is ALT+a. If in doubt, use lowercase!

    '+'
    This tells AutoIt to send a SHIFT keystroke, therefore Send("Hell+o") would send the text "HellO".
    Send("!+a") would send "ALT+SHIFT+a".

    '^'
    This tells AutoIt to send a CONTROL keystroke, therefore Send("^!a") would send "CTRL+ALT+a".
    N.B. Some programs are very choosy about capital letters and CTRL keys, i.e. "^A" is different to "^a".
    The first says CTRL+SHIFT+A, the second is CTRL+a. If in doubt, use lowercase!

    '#'
    The hash now sends a Windows keystroke;
    therefore, Send("#r") would send Win+r which launches the Run dialog box.


    Send Command (if zero flag)                 Resulting Keypress
    {!}                                         !
    {#}                                         #
    {+}                                         +
    {^}                                         ^
    {{}                                         {
    {}}                                         }
    {SPACE}                                     SPACE
    {ENTER}                                     ENTER key on the main keyboard
    {ALT}                                       ALT
    {BACKSPACE} or {BS}                         BACKSPACE
    {DELETE} or {DEL}                           DELETE
    {UP}                                        Cursor up
    {DOWN}                                      Cursor down
    {LEFT}                                      Cursor left
    {RIGHT}                                     Cursor right
    {HOME}                                      HOME
    {END}                                       END
    {ESCAPE} or {ESC}                           ESCAPE
    {INSERT} or {INS}                           INS
    {PGUP}                                      PageUp
    {PGDN}                                      PageDown
    {F1} - {F12}                                Function keys
    {TAB}                                       TAB
    {PRINTSCREEN}                               Print Screen key
    {LWIN}                                      Left Windows key
    {RWIN}                                      Right Windows key
    {NUMLOCK on}                                NUMLOCK (on/off/toggle)
    {CAPSLOCK off}                              CAPSLOCK (on/off/toggle)
    {SCROLLLOCK toggle}                         SCROLLLOCK (on/off/toggle)
    {BREAK}                                     for Ctrl+Break processing
    {PAUSE}                                     PAUSE
    {NUMPAD0} - {NUMPAD9}                       Numpad digits
    {NUMPADMULT}                                Numpad Multiply
    {NUMPADADD}                                 Numpad Add
    {NUMPADSUB}                                 Numpad Subtract
    {NUMPADDIV}                                 Numpad Divide
    {NUMPADDOT}                                 Numpad period
    {NUMPADENTER}                               Enter key on the numpad
    {APPSKEY}                                   Windows App key
    {LALT}                                      Left ALT key
    {RALT}                                      Right ALT key
    {LCTRL}                                     Left CTRL key
    {RCTRL}                                     Right CTRL key
    {LSHIFT}                                    Left Shift key
    {RSHIFT}                                    Right Shift key
    {SLEEP}                                     Computer SLEEP key
    {ALTDOWN}                                   Holds the ALT key down until {ALTUP} is sent
    {SHIFTDOWN}                                 Holds the SHIFT key down until {SHIFTUP} is sent
    {CTRLDOWN}                                  Holds the CTRL key down until {CTRLUP} is sent
    {LWINDOWN}                                  Holds the left Windows key down until {LWINUP} is sent
    {RWINDOWN}                                  Holds the right Windows key down until {RWINUP} is sent
    {ASC nnnn}                                  Send the ALT+nnnn key combination
    {BROWSER_BACK}                              XP Only: Select the browser "back" button
    {BROWSER_FORWARD}                           XP Only: Select the browser "forward" button
    {BROWSER_REFRESH}                           XP Only: Select the browser "refresh" button
    {BROWSER_STOP}                              XP Only: Select the browser "stop" button
    {BROWSER_SEARCH}                            XP Only: Select the browser "search" button
    {BROWSER_FAVORITES}                         XP Only: Select the browser "favorites" button
    {BROWSER_HOME}                              XP Only: Launch the browser and go to the home page
    {VOLUME_MUTE}                               XP Only: Mute the volume
    {VOLUME_DOWN}                               XP Only: Reduce the volume
    {VOLUME_UP}                                 XP Only: Increase the volume
    {MEDIA_NEXT}                                XP Only: Select next track in media player
    {MEDIA_PREV}                                XP Only: Select previous track in media player
    {MEDIA_STOP}                                XP Only: Stop media player
    {MEDIA_PLAY_PAUSE}                          XP Only: Play/pause media player
    {LAUNCH_MAIL}                               XP Only: Launch the email application
    {LAUNCH_MEDIA}                              XP Only: Launch media player
    {LAUNCH_APP1}                               XP Only: Launch user app1
    {LAUNCH_APP2}                               XP Only: Launch user app2


    :param keys: The sequence of keys to send
    :param flag: Changes how "keys" is processed:
    flag = 0 (default), text contains special characters like + and ! to indicate SHIFT and ALT key presses;
    flag = 1, keys are sent raw
    :return: None
    """
    au.AU3_Send(keys, flag)


def send_text(text):
    """Sends raw text to the active window

    :param text: The raw text
    :return: None
    """
    send(text, flag=1)


def send_alt():
    send(u'!')


def send_shift():
    send(u'+')


def send_ctrl():
    send(u'^')


def send_win():
    send(u'#')


def send_lbrace():
    send(u'{{}')


def send_rbrace():
    send(u'{}}')


def send_space():
    send(u'{SPACE}')


def send_enter():
    send(u'{ENTER}')


def send_backspace():
    send(u'{BACKSPACE}')  # or send(u'{BS}')


def send_bs():
    send_backspace()


def send_ins():
    send(u'{INSERT}')  # or send(u'{INS}')


def send_insert():
    send_ins()


def send_del():
    send(u'{DELETE}')  # or send(u'{DEL}')


def send_home():
    send(u'{HOME}')


def send_end():
    send(u'{END}')


def send_esc():
    send(u'{ESCAPE}')  # or send(u'{ESC}')


def send_escape():
    send_esc()


def send_pgup():
    send(u'{PGUP}')


def send_pageup():
    send_pgup()


def send_pgdn():
    send(u'{PGDN}')


def send_pagedown():
    send_pgdn()


def send_fx(x):
    assert 1 <= x <= 12, 'x must be in range [1, 12]'
    send(u'F%d' % x)


def send_f1():
    send(u'F1')


def send_f2():
    send(u'F2')


def send_f3():
    send(u'F3')


def send_f4():
    send(u'F4')


def send_f5():
    send(u'F5')


def send_f6():
    send(u'F6')


def send_f7():
    send(u'F7')


def send_f8():
    send(u'F8')


def send_f9():
    send(u'F9')


def send_f10():
    send(u'F10')


def send_f11():
    send(u'F11')


def send_f12():
    send(u'F12')


def send_tab():
    send(u'{TAB}')


def send_prtscn():
    send(u'{PRINTSCREEN}')


def send_printscreen():
    send_prtscn()


def send_lwin():
    send(u'{LWIN}')


def send_rwin():
    send(u'{RWIN}')


def send_numlock(action='toggle'):
    """Sends NUMLOCK (on/off/toggle) keystroke.

    :param action: 'on', 'off', 'toggle'
    :return: None
    """
    send(u'{NUMLOCK %s}' % action)


def send_capslock(action='toggle'):
    """Sends CAPSLOCK (on/off/toggle) keystroke.

    :param action: 'on', 'off', 'toggle'
    :return: None
    """
    send(u'{CAPSLOCK %s}' % action)


def send_scrolllock(action='toggle'):
    """Sends SCROLLLOCK (on/off/toggle) keystroke.

    :param action: 'on', 'off', 'toggle'
    :return: None
    """
    send(u'{SCROLLLOCK %s}' % action)


def send_pause():
    send(u'{PAUSE}')


def send_break():
    """For Ctrl+Break processing.

    :return: None
    """
    send(u'{BREAK}')


def send_lalt():
    send(u'{LALT}')


def send_ralt():
    send(u'{RALT}')


def send_lctrl():
    send(u'{LCTRL}')


def send_rctrl():
    send(u'{RCTRL}')


def send_lshift():
    send(u'{LSHIFT}')


def send_rshift():
    send(u'{RSHIFT}')


def send_alt_down():
    send(u'{ALTDOWN}')


def send_alt_up():
    send(u'{ALTUP}')


def send_ctrl_down():
    send(u'{CTRLDOWN}')


def send_ctrl_up():
    send(u'{CTRLUP}')


def send_shift_down():
    send(u'{SHIFTDOWN}')


def send_shift_up():
    send(u'{SHIFTUP}')


# ------------------------------ End send keystrokes ------------------------------


class _Rect(Structure):
    _fields_ = [('left', c_long), ('top', c_long), ('right', c_long), ('bottom', c_long)]


def pixel_checksum(left, top, right, bottom, step):
    """Generates a checksum for a region of pixels.
    Performing a checksum of a region is very time consuming, so use the smallest region you are able to reduce CPU
    load. On some machines a checksum of the whole screen could take many seconds!

    A checksum only allows you to see if "something" has changed in a region - it does not tell you exactly what has
    changed.

    When using a step value greater than 1 you must bear in mind that the checksumming becomes less reliable for small
    changes as not every pixel is checked.

    :param left: left coordinate of rectangle
    :param top: top coordinate of rectangle
    :param right: right coordinate of rectangle
    :param bottom: bottom coordinate of rectangle
    :param step: Instead of checksumming each pixel use a value larger than 1 to skip pixels (for speed).
    E.g., a value of 2 will only check every other pixel. Default is 1
    :return: The checksum value of the region
    """
    return au.AU3_PixelChecksum(pointer(_Rect(left, top, right, bottom)), step)


def pixel_get_color(x, y):
    """Returns a pixel color according to x,y pixel coordinates.

    :param x: x coordinate of pixel
    :param y: y coordinate of pixel
    :return: decimal value of pixel's color, or -1 if invalid coordinates
    """
    return au.AU3_PixelGetColor(x, y)

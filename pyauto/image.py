from ctypes import *
import platform
import os


_arch = platform.architecture()[0]
_isdll = 'ImageSearchDLL_x64.dll' if _arch == '64bit' else 'ImageSearchDLL.dll'
_isdll = os.path.join(os.path.dirname(__file__), _isdll)
_isdll = windll.LoadLibrary(_isdll)


_isdll.ImageSearch.argtypes = [c_int, c_int, c_int, c_int, c_char_p]
_isdll.ImageSearch.restype = c_char_p


def search(image_file, x, y, width, height, tolerance=100, position='top_left'):
    """
    :param image_file:
    :param x: X coordinate of top left corner of search area
    :param y: Y coordinate of top left corner of search area
    :param width: width of of search area
    :param height: height of of search area
    :param tolerance: 0~255; 0 for no tolerance
    :param position: select position to return: 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'
    :return: tuple of x, y coordinates of selected position
    """
    res = _isdll.ImageSearch(x, y, x + width, y + height, '*%s %s' % (tolerance, image_file))
    res = res.split('|')
    if res[0] == '1':
        return {
            'top_left': lambda x, y, w, h: (x, y),
            'top_right': lambda x, y, w, h: (x + w, y),
            'bottom_left': lambda x, y, w, h: (x, y + h),
            'bottom_right': lambda x, y, w, h: (x + w, y + h),
            'center': lambda x, y, w, h: (int(x + w / 2), int(y + h / 2))
        }[position](int(res[1]), int(res[2]), int(res[3]), int(res[4]))
    else:
        return False, False

__all__ = [
    "base_string",
    "bstr",
    "long_int",
    "max_int",
    "ustr",
]


bstr = bytes
try:
    ustr = unicode
except NameError:
    ustr = str

base_string = (bstr, ustr)

try:
    long_int = long
except NameError:
    long_int = int

try:
    from sys import maxint as max_int
except ImportError:
    from sys import maxsize as max_int

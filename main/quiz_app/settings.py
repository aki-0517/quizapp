# ...
try:
    from .local_settings import *
except ImportError:
    # local_settings.py が存在しなくてもエラーにならないようにする
    pass
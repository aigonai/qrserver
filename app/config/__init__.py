# (c) Stefan Loesch 2026. All rights reserved.
try:
    from .config import *
    CONFIG_SOURCE = "config"
except ImportError:
    from .example import *
    CONFIG_SOURCE = "example"

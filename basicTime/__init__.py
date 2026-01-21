"""
basicTime

All methods, public and private, use a custom logging system.
Each function logs:
- FUNCTION_RAN on entry
- FUNCTION_RETURNED before returning
- FUNCTION_RAISED on exception
"""
from core import Clock
__all__ = ["Clock"]
"""defined exception
"""

class CommonException(Exception):
    """Base Exception
    """
    message="An exception occured"

    def __init__(self,**kwargs):
        try:
            self._error_str = self.message % kwargs
        except Exception:
            self._error_str = self.message

    def __str__(self):
        return self._error_str

class NotImplementedError(CommonException):
    """An exception 
    """
    message = "Exception: %(func)s is not implemented."

class TimeOutError(CommonException):
    """Time out exception
    """
    message = "Exception: %(func)s is Timeout."
class RTCException(Exception):
    """Base exception class for all errors
    """

    pass


class BadValue(RTCException):
    pass


class NotFound(RTCException):
    pass


class EmptyAttrib(RTCException):
    pass

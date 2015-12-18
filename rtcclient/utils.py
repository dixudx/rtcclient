import logging
import functools
from xml.parsers.expat import ExpatError
import xmltodict
from rtcclient.exception import RTCException


def setup_basic_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(name)s: "
                               "%(message)s")


def token_expire_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        rtc_obj = args[0].get_rtc_obj()

        if not hasattr(rtc_obj, "headers") or rtc_obj.headers is None:
            # still in the initialization or relogin
            # directly call the method
            return func(*args, **kwargs)
        else:
            # check whether token expires
            try:
                resp = func(*args, **kwargs)
                xmltodict.parse(resp.content)
                return resp
            except ExpatError as excp:
                if "invalid token" in str(excp):
                    # expires
                    try:
                        rtc_obj.relogin()
                    except RTCException:
                        raise RTCException("Relogin Failed: "
                                           "Invalid username or password")
                    kwargs["headers"]["Cookie"] = rtc_obj.headers["Cookie"]
                    return func(*args, **kwargs)
                else:
                    # not expires
                    # raise the actual exception
                    raise ExpatError(excp)

    return wrapper

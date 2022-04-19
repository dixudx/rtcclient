import functools
import logging
from xml.parsers.expat import ExpatError

import six
import xmltodict
from lxml import etree

from rtcclient.exception import RTCException, BadValue


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


def capitalize(keyword):
    """Only capitalize the first character and make the left unchanged

    :param keyword: the input string
    :return: the capitalized string
    """

    if keyword is None:
        raise BadValue("Invalid value. None is not supported")

    if isinstance(keyword, six.string_types):
        if len(keyword) > 1:
            return keyword[0].upper() + keyword[1:]
        else:
            return keyword.capitalize()
    else:
        raise BadValue("Input value %s is not string type" % keyword)


def remove_empty_elements(docs):
    root = etree.fromstring(bytes(docs, 'utf-8'))
    for element in root.xpath("//*[not(node())]"):
        if "rdf:resource" not in str(etree.tostring(element)):
            element.getparent().remove(element)

    return etree.tostring(root)

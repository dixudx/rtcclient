import requests

try:
    requests.packages.urllib3.disable_warnings()
except ImportError:
    pass

try:
    import urlparse
    from urllib import quote as urlquote  # noqa: F401
    from urllib import urlencode
    from urllib import unquote as urlunquote
except ImportError:
    # Python3
    import urllib.parse as urlparse  # noqa: F401
    from urllib.parse import quote as urlquote  # noqa: F401
    from urllib.parse import urlencode  # noqa: F401
    from urllib.parse import unquote as urlunquote  # noqa: F401

try:  # pragma no cover
    import xmltodict
    _xml_to_dict_version = [int(x) for x in xmltodict.__version__.split('.')]
    # on xmltodict >= 0.13 it returns a dict
    if _xml_to_dict_version[0] == 0 and _xml_to_dict_version[1] >= 13:
        OrderedDict = dict
    else:
        from collections import OrderedDict
except ImportError:  # pragma no cover
    try:
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = dict

from rtcclient.client import RTCClient  # noqa: F401

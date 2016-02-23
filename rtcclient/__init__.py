import requests
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

try:
    import urlparse
    from urllib import quote as urlquote
    from urllib import urlencode
    from urllib import unquote as urlunquote
except ImportError:
    # Python3
    import urllib.parse as urlparse
    from urllib.parse import quote as urlquote
    from urllib.parse import urlencode
    from urllib.parse import unquote as urlunquote

try:  # pragma no cover
    from collections import OrderedDict
except ImportError:  # pragma no cover
    try:
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = dict

import os
_path = os.path.realpath(os.path.dirname(__file__))
_search_path = os.path.join(_path, 'templates')

from rtcclient.client import RTCClient

import abc
import requests
import urllib
from requests.packages import urllib3
urllib3.disable_warnings()


class ConfigValue(object):

    def getattr(self, attr):
        try:
            return self.__getattribute__(attr)
        except:
            return None

    def setattr(self, attr, value):
        self.__setattr__(attr, value)


class Workitem(ConfigValue):
    def __repr__(self):
        return "<Workitem {0.id}>".format(self)

    @property
    def id(self):
        return self.identifier


class RTCBase(object):
    __metaclass__ = abc.ABCMeta

    CONTENT_XML = "text/xml"
    CONTENT_JSON = "application/json"
    CONTENT_URL_ENCODED = 'application/x-www-form-urlencoded'
    OSLC_CR_XML = "application/x-oslc-cm-change-request+xml"
    OSLC_CR_JSON = "application/x-oslc-cm-change-request+json"

    def __init__(self, baseurl, username, password):
        self.baseurl = baseurl
        self.username = username
        self.password = password
        self.headers = self._get_headers()

    def _get_headers(self):
        _headers = {'Content-type': RTCBase.CONTENT_XML}
        resp = requests.get(self.baseurl + "/authenticated/identity",
                            verify=False,
                            headers=_headers,
                            timeout=60)

        _headers['Content-type'] = RTCBase.CONTENT_URL_ENCODED
        _headers['Cookie'] = resp.headers.get('set-cookie')
        credentials = urllib.urlencode({'j_username': self.username,
                                        'j_password': self.password})

        resp = requests.post(self.baseurl+'/authenticated/j_security_check',
                             data=credentials,
                             verify=False,
                             headers=_headers)

        resp = requests.get(self.baseurl + "/authenticated/identity",
                            verify=False,
                            headers=_headers,
                            timeout=60)

        _headers['Cookie'] = resp.headers.get('set-cookie')
        _headers['Accept'] = RTCBase.CONTENT_XML
        return _headers

    @abc.abstractproperty
    def workitems(self):
        pass

    @abc.abstractmethod
    def get(self, req_url):
        pass

    @abc.abstractmethod
    def post(self, req_url):
        pass

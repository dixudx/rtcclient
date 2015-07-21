import abc
import logging


class RTCBase(object):
    __metaclass__ = abc.ABCMeta

    CONTENT_XML = "text/xml"
    CONTENT_JSON = "application/json"
    CONTENT_URL_ENCODED = 'application/x-www-form-urlencoded'
    OSLC_CR_XML = "application/x-oslc-cm-change-request+xml"
    OSLC_CR_JSON = "application/x-oslc-cm-change-request+json"

    def __init__(self, url):
        self.url = self.validate_url(url)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__,
                            str(self))

    @abc.abstractmethod
    def __str__(self):
        pass

    def __eq__(self, other):
        """
        identify whether the other one represents a connection to the server
        """
        if not isinstance(other, self.__class__):
            return False
        if not other.url == self.url:
            return False
        return True

    def getattr(self, attr):
        try:
            return self.__getattribute__(attr)
        except:
            return None

    def setattr(self, attr, value):
        self.__setattr__(attr, value)

    @abc.abstractmethod
    def get_rtc_obj(self):
        pass

    def get_response(self, req_url, ssl_verify=False, params=None):
        requester = self.get_rtc_obj().requester
        response = requester.get_url(req_url, ssl_verify, params)
        if response.status_code != 200:
            logging.error('Failed request at <%s> with params: %s and ssl %s',
                          req_url,
                          params,
                          "enabled" if ssl_verify else "disabled")
            response.raise_for_status()
        return response

    @classmethod
    def validate_url(cls, url):
        """
        strip and trailing slash to validate a url
        """
        url = url.strip()
        while url.endswith('/'):
            url = url[:-1]
        return url

    def _initialize(self, data):
        for (key, value) in data.iteritems():
            if key.startswith("@"):
                continue
            attr = key.split(":")[-1].replace("-", "_")
            self.setattr(attr, value)

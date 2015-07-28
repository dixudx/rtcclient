import abc
import logging
from rtcclient import requests
from collections import OrderedDict


class RTCBase(object):
    __metaclass__ = abc.ABCMeta
    log = logging.getLogger("base:RTCBase")

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

    @abc.abstractmethod
    def get_rtc_obj(self):
        pass

    def get(self, url,
            verify=False, headers=None,
            timeout=60, **kwargs):
        """Sends a GET request. Refactor from requests module

        :param url: URL for the new :class:`Request` object.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param headers: (optional) Dictionary of HTTP Headers to send with
            the :class:`Request`.
        :type timeout: float or tuple
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Get response from %s", url)
        response = requests.get(url, verify=verify, headers=headers,
                                timeout=timeout, **kwargs)
        if response.status_code != 200:
            self.log.error('Failed GET request at <%s> with response: %s',
                           url,
                           response.content)
            response.raise_for_status()
        return response

    def post(self, url, data=None, json=None,
             verify=False, headers=None, timeout=60, **kwargs):
        """Sends a POST request. Refactor from requests module

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to
            send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of
            the :class:`Request`.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param headers: (optional) Dictionary of HTTP Headers to send with
            the :class:`Request`.
        :type timeout: float or tuple
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Post a request to %s with data: %s and json: %s",
                       url, data, json)
        response = requests.post(url, data=data, json=json,
                                 verify=verify, headers=headers,
                                 timeout=timeout, **kwargs)

        if response.status_code not in [200, 201]:
            self.log.error('Failed POST request at <%s> with response: %s',
                           url,
                           response.content)
            self.log.info(response.status_code)
            response.raise_for_status()
        return response

    def put(self, url, data=None, verify=False,
            headers=None, timeout=60, **kwargs):
        """Sends a PUT request. Refactor from requests module

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to
            send in the body of the :class:`Request`.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param headers: (optional) Dictionary of HTTP Headers to send with
            the :class:`Request`.
        :type timeout: float or tuple
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Put a request to %s with data: %s",
                       url, data)
        response = requests.post(url, data=data,
                                 verify=verify, headers=headers,
                                 timeout=timeout, **kwargs)
        if response.status_code not in [200, 201]:
            self.log.error('Failed PUT request at <%s> with response: %s',
                           url,
                           response.content)
            response.raise_for_status()
        return response

    @classmethod
    def validate_url(cls, url):
        """Strip and trailing slash to validate a url

        :param url: the url address
        :return: the valid url address
        :rtype: string
        """

        if url is None:
            return None

        url = url.strip()
        while url.endswith('/'):
            url = url[:-1]
        return url


class FieldBase(RTCBase):
    __metaclass__ = abc.ABCMeta
    log = logging.getLogger("base.FieldBase")

    def __init__(self, url, rtc_obj, raw_data=None):
        RTCBase.__init__(self, url)
        self.field_alias = dict()
        self.rtc_obj = rtc_obj
        self.raw_data = raw_data
        if raw_data:
            self.__initializeFromRaw()
        elif self.url:
            self._initialize()

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def get_rtc_obj(self):
        pass

    def _initialize(self):
        """Initialize the object from the response xml data

        :param data: xml data for initialization
        """

        self.log.debug("Start initializing data from %s",
                       self.url)
        self.__initialize()
        self.log.info("Finish the initialization for <%s %s>",
                      self.__class__.__name__, self)

#     @abc.abstractmethod
    def __initialize(self):
        """Request to get response

        """
        pass

    def __initializeFromRaw(self):
        """Initialze from raw data (OrderedDict)

        """
        for (key, value) in self.raw_data.iteritems():
            if key.startswith("@"):
                continue

            attr = key.split(":")[-1].replace("-", "_")
            attr_list = attr.split(".")
            if len(attr_list) > 1:
                attr = "_".join([attr_list[-2],
                                 attr_list[-1]])

            self.field_alias[attr] = key

            # TODO: object not url
            if isinstance(value, OrderedDict):
                value = value.values()[0]
            self.setattr(attr, value)

    def setattr(self, attr, value):
        self.__setattr__(attr, value)

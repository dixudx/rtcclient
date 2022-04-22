from multiprocessing.pool import ThreadPool as Pool
import abc
import logging
from rtcclient import requests
import xmltodict
from rtcclient import urlunquote, OrderedDict
from rtcclient import exception
from rtcclient.utils import token_expire_handler


class RTCBase(object):
    __metaclass__ = abc.ABCMeta
    log = logging.getLogger("base.RTCBase")

    CONTENT_XML = "text/xml"
    CONTENT_URL_ENCODED = "application/x-www-form-urlencoded"
    OSLC_CR_XML = "application/x-oslc-cm-change-request+xml"
    OSLC_CR_JSON = "application/x-oslc-cm-change-request+json"

    def __init__(self, url):
        self.url = self.validate_url(url)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self))

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
        except Exception:
            return None

    def __getitem__(self, key):
        return self.__getattribute__(key)

    @abc.abstractmethod
    def get_rtc_obj(self):
        pass

    @token_expire_handler
    def get(self,
            url,
            verify=False,
            headers=None,
            proxies=None,
            timeout=60,
            **kwargs):
        """Sends a GET request. Refactor from requests module

        :param url: URL for the new :class:`Request` object.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param headers: (optional) Dictionary of HTTP Headers to send with
            the :class:`Request`.
        :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
        :param timeout: (optional) How long to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read
            timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Get response from %s", url)
        response = requests.get(url,
                                verify=verify,
                                headers=headers,
                                proxies=proxies,
                                timeout=timeout,
                                **kwargs)
        if response.status_code != 200:
            self.log.error("Failed GET request at <%s> with response: %s", url,
                           response.content)
            response.raise_for_status()
        return response

    @token_expire_handler
    def post(self,
             url,
             data=None,
             json=None,
             verify=False,
             headers=None,
             proxies=None,
             timeout=60,
             **kwargs):
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
        :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
        :param timeout: (optional) How long to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read
            timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Post a request to %s with data: %s and json: %s", url,
                       data, json)
        response = requests.post(url,
                                 data=data,
                                 json=json,
                                 verify=verify,
                                 headers=headers,
                                 proxies=proxies,
                                 timeout=timeout,
                                 **kwargs)

        if response.status_code not in [200, 201]:
            self.log.error("Failed POST request at <%s> with response: %s", url,
                           response.content)
            self.log.info(response.status_code)
            response.raise_for_status()
        return response

    @token_expire_handler
    def put(self,
            url,
            data=None,
            verify=False,
            headers=None,
            proxies=None,
            timeout=60,
            **kwargs):
        """Sends a PUT request. Refactor from requests module

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to
            send in the body of the :class:`Request`.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param headers: (optional) Dictionary of HTTP Headers to send with
            the :class:`Request`.
        :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
        :param timeout: (optional) How long to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read
            timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Put a request to %s with data: %s", url, data)
        response = requests.put(url,
                                data=data,
                                verify=verify,
                                headers=headers,
                                proxies=proxies,
                                timeout=timeout,
                                **kwargs)
        if response.status_code not in [200, 201]:
            self.log.error("Failed PUT request at <%s> with response: %s", url,
                           response.content)
            response.raise_for_status()
        return response

    @token_expire_handler
    def delete(self,
               url,
               headers=None,
               verify=False,
               proxies=None,
               timeout=60,
               **kwargs):
        """Sends a DELETE request. Refactor from requests module

        :param url: URL for the new :class:`Request` object.
        :param headers: (optional) Dictionary of HTTP Headers to send with
            the :class:`Request`.
        :param verify: (optional) if ``True``, the SSL cert will be verified.
            A CA_BUNDLE path can also be provided.
        :param proxies: (optional) Dictionary mapping protocol to the URL of
            the proxy.
        :param timeout: (optional) How long to wait for the server to send data
            before giving up, as a float, or a :ref:`(connect timeout, read
            timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        self.log.debug("Delete a request to %s", url)
        response = requests.delete(url,
                                   headers=headers,
                                   verify=verify,
                                   proxies=proxies,
                                   timeout=timeout,
                                   **kwargs)
        if response.status_code not in [200, 201]:
            self.log.error("Failed DELETE request at <%s> with response: %s",
                           url, response.content)
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
        while url.endswith("/"):
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
        if raw_data is not None:
            self.__initializeFromRaw()
        elif self.url:
            self._initialize()

    @abc.abstractmethod
    def __str__(self):
        pass

    def get_rtc_obj(self):
        return self.rtc_obj

    def _initialize(self):
        """Initialize the object from the request"""

        self.log.debug("Start initializing data from %s", self.url)
        resp = self.get(
            self.url,
            verify=False,
            proxies=self.rtc_obj.proxies,
            headers=self.rtc_obj.headers,
        )
        self.__initialize(resp)
        self.log.info("Finish the initialization for <%s %s>",
                      self.__class__.__name__, self)

    def __initialize(self, resp):
        """Initialize from the response"""

        raw_data = xmltodict.parse(resp.content)
        root_key = list(raw_data.keys())[0]
        self.raw_data = raw_data.get(root_key)
        self.__initializeFromRaw()

    def __initializeFromRaw(self):
        """Initialze from raw data (OrderedDict)"""

        with Pool() as pool:
            for processed in pool.map(self.__process_items,
                                      self.raw_data.items()):
                if processed is None:
                    continue
                key, attr, value = processed
                self.field_alias[attr] = key
                self.setattr(attr, value)

    def __process_items(self, item):
        """Process a single work item element"""
        key, value = item
        if key.startswith("@"):
            # be compatible with IncludedInBuild
            if "@oslc_cm:label" != key:
                return None

        attr = key.split(":")[-1].replace("-", "_")
        attr_list = attr.split(".")

        # ignore long attributes
        if len(attr_list) > 1:
            # attr = "_".join([attr_list[-2],
            #                  attr_list[-1]])
            return None

        if isinstance(value, OrderedDict):
            value_text = value.get("#text")
            if value_text is not None:
                value = value_text
            else:
                # request detailed info using rdf:resource
                value = list(value.values())[0]

                try:
                    value = self.__get_rdf_resource_title(value)
                except (exception.RTCException, Exception):
                    self.log.error("Unable to handle %s", value)
        return key, attr, value

    def __get_rdf_resource_title(self, rdf_url):
        # handle for /jts/users
        if "/jts/users" in rdf_url:
            return urlunquote(rdf_url.split("/")[-1])

        # keep query result url
        if rdf_url.endswith("rtc_cm:results"):
            return rdf_url

        # keep attachment url
        if "/resource/content/" in rdf_url:
            return rdf_url

        resp = self.get(
            rdf_url,
            verify=False,
            proxies=self.rtc_obj.proxies,
            headers=self.rtc_obj.headers,
        )
        raw_data = xmltodict.parse(resp.content)

        root_key = list(raw_data.keys())[0]
        total_count = raw_data[root_key].get("@oslc_cm:totalCount")
        if total_count is None:
            # no total count
            # only single resource
            # compatible with IncludedInBuild
            return raw_data[root_key].get("dc:title") or raw_data[root_key].get(
                "foaf:nick")
        else:
            # multiple resource
            result_list = list()
            entry_keys = [
                entry_key for entry_key in raw_data[root_key].keys()
                if not entry_key.startswith("@")
            ]
            for entry_key in entry_keys:
                entries = raw_data[root_key][entry_key]
                if isinstance(entries, OrderedDict):
                    entry_result = self.__handle_rdf_entry(entries)
                    result_list.append(entry_result)
                else:
                    for entry in entries:
                        entry_result = self.__handle_rdf_entry(entry)
                        result_list.append(entry_result)

            if not result_list:
                return None
            return result_list

    def __handle_rdf_entry(self, entry):
        # only return useful info instead of the whole object
        return_fields = ["rtc_cm:userId", "dc:title", "dc:description"]
        subkeys = entry.keys()
        for return_field in return_fields:
            if return_field in subkeys:
                return entry.get(return_field)
        raise exception.RTCException()

    def setattr(self, attr, value):
        self.__setattr__(attr, value)

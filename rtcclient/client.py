from rtcclient.base import RTCBase
import xmltodict
import requests

try:
    import urlparse
    from urllib import quote as urlquote, urlencode
except ImportError:
    # Python3
    import urllib.parse as urlparse
    from urllib.parse import quote as urlquote, urlencode


class RTCClient(RTCBase):

    def __init__(self, baseurl, username, password):
        self.username = username
        self.password = password
        RTCBase.__init__(self, baseurl)
        self.headers = self._get_headers()

    def __str__(self):
        return "RTC Server at %s" % self.baseurl

    def get_rtc_obj(self):
        return self

    def _get_headers(self):
        """
        TODO
        """
        _headers = {'Content-type': RTCBase.CONTENT_XML}
        resp = requests.get(self.baseurl + "/authenticated/identity",
                            verify=False,
                            headers=_headers,
                            timeout=60)

        _headers['Content-type'] = RTCBase.CONTENT_URL_ENCODED
        _headers['Cookie'] = resp.headers.get('set-cookie')
        credentials = urlencode({'j_username': self.username,
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

    def getCatalog(self):
        """
        get oslc catalog
        """
        catalog_url = "/".join([self.baseurl,
                                "oslc-scm/catalog"])
        resp = requests.get(catalog_url,
                            verify=False,
                            headers=self.headers)
        projectareas = xmltodict.parse(resp.content)
        return projectareas

    def getProjectAreaId(self, projectarea_name):
        """
        @param projectarea_name: the project area name
        """
        projectareas = self.getCatalog()
        sp_catalog = projectareas.get("oslc_disc:ServiceProviderCatalog")
        entries = sp_catalog.get("oslc_disc:entry")
        for entry in entries:
            sp = entry.get("oslc_disc:ServiceProvider")
            if sp.get("dcterms:title") == projectarea_name:
                details_url = sp.get("oslc_disc:details").get("@rdf:resource")
                projectarea_id = details_url.split("/")[-1]
                break
            continue
        else:
            return None
        return projectarea_id

    def get_query_url(self, projectarea_name, query_str=""):
        """
        :param projectarea_name: the project area name
        :param query_str: the query string
        :return: the url for query
        """
        projectarea_id = self.getProjectAreaId(projectarea_name)
        url = "/".join([self.base_url,
                        "oslc/contexts/%s" % projectarea_id,
                        "workitems?oslc_cm.query=%s" % urlquote(query_str)])
        return url

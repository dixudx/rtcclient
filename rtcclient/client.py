from rtcclient.base import RTCBase
import xmltodict
import requests


class RTCClient(RTCBase):

    def workitems(self):
        pass

    def getCatalog(self):
        """
        get oslc catalog
        """
        catalog_url = self.baseurl + "/oslc-scm/catalog"
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

    def get(self, req_url, verify=False, headers=self.headers):
        pass

    def post(self, req_url):
        pass

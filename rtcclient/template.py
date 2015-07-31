from rtcclient.base import RTCBase
import logging
import xmltodict
import os


class Template(RTCBase):
    log = logging.getLogger("template.Template")

    def __init__(self, rtc_obj):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, self.rtc_obj.url)

    def __str__(self):
        return "Template for %s" % self.rtc_obj

    def get_rtc_obj(self):
        return self.rtc_obj

    def getTemplate(self, workitem_id, template_name, template_folder,
                    keep=False, encoding="UTF-8"):
        """Get template from some certain workitem

        :param workitem_id: the copied workitem id
        :param template_name: the template file name
        :param template_folder: the folder to store template file
        :param keep (default is False): If True, below fields will be kept
            the same with the copied workitem.
                * Team Area
                * Owned By
                * Planned For
                * Severity
                * Priority
                * Filed Against
            otherwise for False
        :param encoding (default is "UTF-8"): coding format
        """

        # TODO: template_folder default value
        template_file_path = os.path.join(template_folder,
                                          template_name)
        template_file = open(template_file_path, "w")

        workitem_url = "/".join([self.url,
                                 "oslc/workitems/%s" % workitem_id])
        resp = self.get(workitem_url,
                        verify=False,
                        headers=self.rtc_obj.headers)
        raw_data = xmltodict.parse(resp.content)

        # pre-adjust the template:
        # remove some attribute to avoid being overwritten, which will only be
        # generated when the workitem is created
        wk_raw_data = raw_data.get("oslc_cm:ChangeRequest")

        print xmltodict.unparse(raw_data, encoding=encoding,
                                pretty=True)

        self._remove_long_fields(wk_raw_data)

        # Be cautious when you want to modify these fields
        # These fields have been tested as must-removed one
        remove_fields = ["@rdf:about",
                         "dc:created",
                         "dc:creator",
                         "dc:identifier",
                         "rtc_cm:contextId",
                         "rtc_cm:comments",
                         "rtc_cm:state",
                         "dc:type",
                         "rtc_cm:subscribers",
                         "dc:modified",
                         "rtc_cm:modifiedBy",
                         "rtc_cm:resolved",
                         "rtc_cm:resolvedBy",
                         "rtc_cm:resolution",
                         "rtc_cm:startDate",
                         "rtc_cm:timeSpent",
                         "rtc_cm:progressTracking",
                         "rtc_cm:projectArea",
                         "oslc_cm:relatedChangeManagement",
                         "oslc_cm:trackedWorkItem",
                         "oslc_cm:tracksWorkItem",
                         "rtc_cm:timeSheet",
                         "oslc_pl:schedule"]

        for remove_field in remove_fields:
            try:
                wk_raw_data.pop(remove_field)
                self.log.debug("Successfully remove field [%s] from the "
                               "template originated from <Workitem %s>",
                               remove_field,
                               workitem_id)
            except:
                self.log.warning("No field named [%s] in this template "
                                 "from <Workitem %s>", remove_field, workitem_id)
                continue

        wk_raw_data["dc:description"] = "{{ description }}"
        wk_raw_data["dc:title"] = "{{ title }}"

        if keep:
            xmltodict.unparse(raw_data, output=template_file,
                              encoding=encoding,
                              pretty=True)
            self.log.info("Successfully write the template to file %s"
                          "with [keep]=True", template_file_path)
            return

        replace_fields = [("rtc_cm:teamArea", "{{ teamArea_name }}"),
                          ("rtc_cm:ownedBy", "{{ ownedBy }}"),
                          ("rtc_cm:plannedFor", "{{ plannedFor }}"),
                          ("oslc_cm:severity", "{{ severity }}"),
                          ("oslc_cm:priority", "{{ priority }}"),
                          ("rtc_cm:filedAgainst", "{{ filedAgainst }}")]
        for field in replace_fields:
            try:
                wk_raw_data[field[0]]["@rdf:resource"] = field[1]
                self.log.debug("Successfully replace field [%s] with [%s]",
                               field[0], field[1])
            except:
                self.log.warning("Cannot replace field [%s]", field[0])
                continue

        xmltodict.unparse(raw_data, output=template_file,
                          encoding=encoding,
                          pretty=True)
        self.log.info("Successfully write the template to file %s",
                      template_file_path)

    def _remove_long_fields(self, wk_raw_data):
        """Remove long fields: These fields are can only customized after
        the workitems are created

        """

        match_str_list = ["rtc_cm:com.ibm.",
                          "calm:"]
        for key in wk_raw_data.keys():
            for match_str in match_str_list:
                if key.startswith(match_str):
                    try:
                        wk_raw_data.pop(key)
                        self.log.debug("Successfully remove field [%s] from "
                                       "the template", key)
                    except:
                        self.log.warning("Cannot remove field [%s] from the "
                                         "template", key)
                    continue

from rtcclient.base import RTCBase
import logging
import xmltodict
import os
import jinja2
from rtcclient import exception


class Template(RTCBase):
    log = logging.getLogger("template.Template")

    def __init__(self, rtc_obj, searchpath="./templates"):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, self.rtc_obj.url)
        self.searchpath = searchpath
        self.loader = jinja2.FileSystemLoader(searchpath=self.searchpath)
        self.environment = jinja2.Environment(loader=self.loader,
                                              trim_blocks=True)

    def __str__(self):
        return "Template for %s" % self.rtc_obj

    def get_rtc_obj(self):
        return self.rtc_obj

    def render(self, template, **kwargs):
        """Renders the template

        :param template: The template to render.
            The template is actually a file, which is usually generated
            by `Template.getTemplate()` and can also be modified by user
            accordingly.
        :param kwargs: The kwargs dict used to fill the template
            These two parameter are mandatory:
            * description
            * title

            below parameters are mandatory if keep (parameter in
            `Template.getTemplate`) is set to False; optional for otherwise
            * teamArea_name (Team Area)
            * ownedBy (Owned By)
            * plannedFor(Planned For)
            * severity(Severity)
            * priority(Priority)
            * filedAgainst(Filed Against)
        """

        temp = self.environment.get_template(template)
        return temp.render(**kwargs)

    def renderFromWorkitem(self, workitem_id, keep=False,
                           encoding="UTF-8", **kwargs):
        """Render the template directly from some certain workitem without
        saving to a file

        :param workitem_id: the copied workitem id
        :param keep (default is False): If True, below fields will remain
            unchangeable with the copied workitem.
                * Team Area
                * Owned By
                * Planned For
                * Severity
                * Priority
                * Filed Against
            otherwise for False
        :param encoding (default is "UTF-8"): coding format
        :param kwargs: The kwargs dict used to fill the template
            These two parameter are mandatory:
            * description
            * title

            below parameters are mandatory if keep is set to False; optional
            for otherwise
            * teamArea_name (Team Area)
            * ownedBy (Owned By)
            * plannedFor(Planned For)
            * severity(Severity)
            * priority(Priority)
            * filedAgainst(Filed Against)
        """

        temp = jinja2.Template(self.getTemplate(workitem_id,
                                                template_name=None,
                                                template_folder=None,
                                                keep=keep,
                                                encoding=encoding))
        return temp.render(**kwargs)

    def getTemplate(self, workitem_id, template_name=None,
                    template_folder=None,
                    keep=False, encoding="UTF-8"):
        """Get template from some certain workitem

        The resulting XML document is returned as a string, but if
        `template_name` (a string value) is specified,
        it is written there instead.

        :param workitem_id: the copied workitem id
        :param template_name: the template file name
        :param template_folder: the folder to store template file
        :param keep (default is False): If True, below fields will remain
            unchangeable with the copied workitem.
                * Team Area
                * Owned By
                * Planned For
                * Severity
                * Priority
                * Filed Against
            otherwise for False
        :param encoding (default is "UTF-8"): coding format
        """

        self.log.info("Fetch the template from <Workitem %s> with [keep]=%s",
                      workitem_id, keep)

        if template_folder is None:
            template_folder = self.searchpath

        # identify whether output to a file
        if template_name is not None:
            template_file_path = os.path.join(template_folder,
                                              template_name)
            output = open(template_file_path, "w")
        else:
            template_file_path = None
            output = None

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
            if template_file_path:
                self.log.info("Writing the template to file %s",
                              template_file_path)
            return xmltodict.unparse(raw_data, output=output,
                                     encoding=encoding,
                                     pretty=True)

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

        if template_file_path:
            self.log.info("Writing the template to file %s",
                          template_file_path)

        return xmltodict.unparse(raw_data, output=output,
                                 encoding=encoding,
                                 pretty=True)

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

    def getTemplates(self, workitems, template_folder=None,
                     template_names=None, keep=False, encoding="UTF-8"):
        """Get templates from a group of workitems and write them to files
        named in template_names respectively.

        :param workitems: a list/tuple/set contains the IDs of
            copied workitems
        :param template_names: a list/tuple/set contains the template file
            names from copied workitems.
            If None, the file names will be named after the workitem ID with
            ".template" as a postfix
        :param template_folder: refer to Template.getTemplate
        :param keep (default is False): refer to Template.getTemplate
        :param encoding (default is "UTF-8"): refer to Template.getTemplate
        """

        if template_names is not None:
            if len(workitems) != len(template_names):
                self.log.error("Parameters workitems and template_names have "
                               "different length")
                raise exception.BadValue("Mismatched length for parameters "
                                         "workitems and template_names")

        for index, wk_id in enumerate(workitems):
            try:
                if template_names is not None:
                    template_name = template_names[index]
                else:
                    template_name = ".".join([wk_id, "template"])
                self.getTemplate(wk_id,
                                 template_name=template_name,
                                 template_folder=template_folder,
                                 keep=keep,
                                 encoding=encoding)
            except Exception, excp:
                self.log.error("Exception occurred when fetching"
                               "template from <Workitem %s>: %s",
                               wk_id, excp)
                continue
        self.log.info("Successfully fetch all the templates from "
                      "workitems: %s", workitems)

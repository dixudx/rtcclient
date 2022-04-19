import logging
import os
from xml.sax.saxutils import escape

import jinja2
import jinja2.meta
import six
import xmltodict

from rtcclient import exception
from rtcclient.base import RTCBase
from rtcclient.utils import remove_empty_elements


class Templater(RTCBase):
    """A wrapped class used to generate and render templates
    from some copied workitems

    :param rtc_obj: a reference to the
        :class:`rtcclient.client.RTCClient` object
    :param searchpath: the folder to store your templates.
        If `None`, the default search path
        (/your/site-packages/rtcclient/templates) will be loaded automatically.

    """

    log = logging.getLogger("template.Templater")

    def __init__(self, rtc_obj, searchpath=None):
        self.rtc_obj = rtc_obj
        RTCBase.__init__(self, self.rtc_obj.url)
        if searchpath is None:
            self.searchpath = os.path.join(
                os.path.realpath(os.path.dirname(__file__)), 'templates')
        else:
            self.searchpath = searchpath
        self.loader = jinja2.FileSystemLoader(searchpath=self.searchpath)
        self.environment = jinja2.Environment(loader=self.loader,
                                              trim_blocks=True)

    def __str__(self):
        return "Templater for %s" % self.rtc_obj

    def get_rtc_obj(self):
        return self.rtc_obj

    def render(self, template, **kwargs):
        """Renders the template

        :param template: The template to render.
            The template is actually a file, which is usually generated
            by :class:`rtcclient.template.Templater.getTemplate`
            and can also be modified by user accordingly.
        :param kwargs: The `kwargs` dict is used to fill the template.
            These two parameter are mandatory:

                * description
                * title

            Some of below parameters (which may not be included in some
            customized workitem type ) are mandatory if `keep` (parameter in
            :class:`rtcclient.template.Templater.getTemplate`) is set to
            `False`; Optional for otherwise.

                * teamArea (Team Area)
                * ownedBy (Owned By)
                * plannedFor(Planned For)
                * severity(Severity)
                * priority(Priority)
                * filedAgainst(Filed Against)

            Actually all these needed keywords/attributes/fields can be
            retrieved by :class:`rtcclient.template.Templater.listFields`

        :return: the :class:`string` object
        :rtype: string
        """

        if kwargs.get("title", None) is not None:
            kwargs["title"] = escape(kwargs["title"])

        if kwargs.get("description", None) is not None:
            kwargs["description"] = escape(kwargs["description"])

        try:
            temp = self.environment.get_template(template)
            return temp.render(**kwargs)
        except AttributeError:
            err_msg = "Invalid value for 'template'"
            self.log.error(err_msg)
            raise exception.BadValue(err_msg)

    def renderFromWorkitem(self,
                           copied_from,
                           keep=False,
                           encoding="UTF-8",
                           **kwargs):
        """Render the template directly from some to-be-copied
        :class:`rtcclient.workitem.Workitem` without saving to a file

        :param copied_from: the to-be-copied
            :class:`rtcclient.workitem.Workitem` id
        :param keep (default is False): If `True`, some of the below fields
            will remain unchangeable with the to-be-copied
            :class:`rtcclient.workitem.Workitem`.
            Otherwise for `False`.

                * teamArea (Team Area)
                * ownedBy (Owned By)
                * plannedFor(Planned For)
                * severity(Severity)
                * priority(Priority)
                * filedAgainst(Filed Against)
        :param encoding (default is "UTF-8"): coding format
        :param kwargs: The `kwargs` dict is used to fill the template.
            These two parameter are mandatory:

                * description
                * title

            Some of below parameters (which may not be included in some
            customized workitem type ) are mandatory if `keep` is set to
            `False`; Optional for otherwise.

                * teamArea (Team Area)
                * ownedBy (Owned By)
                * plannedFor(Planned For)
                * severity(Severity)
                * priority(Priority)
                * filedAgainst(Filed Against)

            Actually all these needed keywords/attributes/fields can be
            retrieved by
            :class:`rtcclient.template.Templater.listFieldsFromWorkitem`

        :return: the :class:`string` object
        :rtype: string
        """

        temp = jinja2.Template(
            self.getTemplate(copied_from,
                             template_name=None,
                             template_folder=None,
                             keep=keep,
                             encoding=encoding))

        rendered_data = temp.render(**kwargs)
        return remove_empty_elements(rendered_data)

    def listFields(self, template):
        """List all the attributes to be rendered from the template file

        :param template: The template to render.
            The template is actually a file, which is usually generated
            by :class:`rtcclient.template.Templater.getTemplate` and can also
            be modified by user accordingly.
        :return: a :class:`set` contains all the needed attributes
        :rtype: set
        """

        try:
            temp_source = self.environment.loader.get_source(
                self.environment, template)
            return self.listFieldsFromSource(temp_source)
        except AttributeError:
            err_msg = "Invalid value for 'template'"
            self.log.error(err_msg)
            raise exception.BadValue(err_msg)

    def listFieldsFromWorkitem(self, copied_from, keep=False):
        """List all the attributes to be rendered directly from some
        to-be-copied :class:`rtcclient.workitem.Workitem`

        :param copied_from: the to-be-copied
            :class:`rtcclient.workitem.Workitem` id
        :param keep: (default is False) If `True`, some of below parameters
            (which will not be included in some customized
            :class:`rtcclient.workitem.Workitem` type ) will remain
            unchangeable with the to-be-copied
            :class:`rtcclient.workitem.Workitem`.
            Otherwise for `False`.

                * teamArea (Team Area)
                * ownedBy (Owned By)
                * plannedFor(Planned For)
                * severity(Severity)
                * priority(Priority)
                * filedAgainst(Filed Against)
        :return: a :class:`set` contains all the needed attributes
        :rtype: set
        """

        temp_source = self.getTemplate(copied_from,
                                       template_name=None,
                                       template_folder=None,
                                       keep=keep)
        return self.listFieldsFromSource(temp_source)

    def listFieldsFromSource(self, template_source):
        """List all the attributes to be rendered directly from template
        source

        :param template_source: the template source (usually represents the
            template content in string format)
        :return: a :class:`set` contains all the needed attributes
        :rtype: set
        """

        ast = self.environment.parse(template_source)
        return jinja2.meta.find_undeclared_variables(ast)

    def getTemplate(self,
                    copied_from,
                    template_name=None,
                    template_folder=None,
                    keep=False,
                    encoding="UTF-8"):
        """Get template from some to-be-copied
        :class:`rtcclient.workitem.Workitem`

        The resulting XML document is returned as a :class:`string`, but if
        `template_name` (a string value) is specified,
        it is written there instead.

        :param copied_from: the to-be-copied
            :class:`rtcclient.workitem.Workitem` id (integer or
            equivalent string)
        :param template_name: the template file name
        :param template_folder: the folder to store template file
        :param keep: (default is False) If `True`, some of below parameters
            (which may not be included in some customized
            :class:`rtcclient.workitem.Workitem` type ) will remain
            unchangeable with the to-be-copied
            :class:`rtcclient.workitem.Workitem`.
            Otherwise for `False`.

                * teamArea (Team Area)
                * ownedBy (Owned By)
                * plannedFor(Planned For)
                * severity(Severity)
                * priority(Priority)
                * filedAgainst(Filed Against)
        :param encoding: (default is "UTF-8") coding format
        :return:

            * a :class:`string` object: if `template_name` is not specified
            * write the template to file `template_name`: if `template_name` is
              specified
        """

        try:
            if isinstance(copied_from, bool) or isinstance(copied_from, float):
                raise ValueError()
            if isinstance(copied_from, six.string_types):
                copied_from = int(copied_from)
            if not isinstance(copied_from, int):
                raise ValueError()
        except ValueError:
            err_msg = "Please input a valid workitem id you want to copy from"
            self.log.error(err_msg)
            raise exception.BadValue(err_msg)

        self.log.info("Fetch the template from <Workitem %s> with [keep]=%s",
                      copied_from, keep)

        if template_folder is None:
            template_folder = self.searchpath

        # identify whether output to a file
        if template_name is not None:
            template_file_path = os.path.join(template_folder, template_name)
            output = open(template_file_path, "w")
        else:
            template_file_path = None
            output = None

        workitem_url = "/".join([self.url, "oslc/workitems/%s" % copied_from])
        resp = self.get(workitem_url,
                        verify=False,
                        proxies=self.rtc_obj.proxies,
                        headers=self.rtc_obj.headers)
        raw_data = xmltodict.parse(resp.content)

        # pre-adjust the template:
        # remove some attribute to avoid being overwritten, which will only be
        # generated when the workitem is created
        wk_raw_data = raw_data.get("oslc_cm:ChangeRequest")
        self._remove_long_fields(wk_raw_data)

        # Be cautious when you want to modify these fields
        # These fields have been tested as must-removed one
        remove_fields = [
            "@rdf:about", "dc:created", "dc:creator", "dc:identifier",
            "rtc_cm:contextId", "rtc_cm:comments", "rtc_cm:state", "dc:type",
            "rtc_cm:subscribers", "dc:modified", "rtc_cm:modifiedBy",
            "rtc_cm:resolved", "rtc_cm:resolvedBy", "rtc_cm:resolution",
            "rtc_cm:startDate", "rtc_cm:timeSpent", "rtc_cm:progressTracking",
            "rtc_cm:projectArea", "oslc_cm:relatedChangeManagement",
            "oslc_cm:trackedWorkItem", "oslc_cm:tracksWorkItem",
            "rtc_cm:timeSheet", "oslc_pl:schedule"
        ]

        for remove_field in remove_fields:
            try:
                wk_raw_data.pop(remove_field)
                self.log.debug(
                    "Successfully remove field [%s] from the "
                    "template originated from <Workitem %s>", remove_field,
                    copied_from)
            except Exception:
                self.log.warning(
                    "No field named [%s] in this template "
                    "from <Workitem %s>", remove_field, copied_from)
                continue

        wk_raw_data["dc:description"] = "{{ description }}"
        wk_raw_data["dc:title"] = "{{ title }}"

        if keep:
            if template_file_path:
                self.log.info("Writing the template to file %s",
                              template_file_path)
            return xmltodict.unparse(raw_data,
                                     output=output,
                                     encoding=encoding,
                                     pretty=True)

        replace_fields = [("rtc_cm:teamArea", "{{ teamArea }}"),
                          ("rtc_cm:ownedBy", "{{ ownedBy }}"),
                          ("rtc_cm:plannedFor", "{{ plannedFor }}"),
                          ("rtc_cm:foundIn", "{{ foundIn }}"),
                          ("oslc_cm:severity", "{{ severity }}"),
                          ("oslc_cm:priority", "{{ priority }}"),
                          ("rtc_cm:filedAgainst", "{{ filedAgainst }}")]
        for field in replace_fields:
            try:
                if field[0] in wk_raw_data:
                    wk_raw_data[field[0]]["@rdf:resource"] = field[1]
                    self.log.debug("Successfully replace field [%s] with [%s]",
                                   field[0], field[1])
            except Exception:
                self.log.warning("Cannot replace field [%s]", field[0])
                continue

        if template_file_path:
            self.log.info("Writing the template to file %s", template_file_path)

        return xmltodict.unparse(raw_data, output=output, encoding=encoding)

    def _remove_long_fields(self, wk_raw_data):
        """Remove long fields: These fields are can only customized after
        the workitems are created

        """

        match_str_list = ["rtc_cm:com.ibm.", "calm:"]
        keys = list(wk_raw_data.keys())
        for key in keys:
            for match_str in match_str_list:
                if key.startswith(match_str):
                    try:
                        wk_raw_data.pop(key)
                        self.log.debug(
                            "Successfully remove field [%s] from "
                            "the template", key)
                    except Exception:
                        self.log.warning(
                            "Cannot remove field [%s] from the "
                            "template", key)
                    continue

    def getTemplates(self,
                     workitems,
                     template_folder=None,
                     template_names=None,
                     keep=False,
                     encoding="UTF-8"):
        """Get templates from a group of to-be-copied :class:`Workitems` and
        write them to files named after the names in `template_names`
        respectively.

        :param workitems: a :class:`list`/:class:`tuple`/:class:`set`
            contains the ids (integer or equivalent string) of some
            to-be-copied :class:`Workitems`
        :param template_names: a :class:`list`/:class:`tuple`/:class:`set`
            contains the template file names for copied :class:`Workitems`.
            If `None`, the new template files will be named after the
            :class:`rtcclient.workitem.Workitem` id with "`.template`" as a
            postfix
        :param template_folder: refer to
            :class:`rtcclient.template.Templater.getTemplate`
        :param keep: (default is False) refer to
            :class:`rtcclient.template.Templater.getTemplate`
        :param encoding: (default is "UTF-8") refer to
            :class:`rtcclient.template.Templater.getTemplate`
        """

        if (not workitems or isinstance(workitems, six.string_types) or
                isinstance(workitems, int) or isinstance(workitems, float) or
                not hasattr(workitems, "__iter__")):
            error_msg = "Input parameter 'workitems' is not iterable"
            self.log.error(error_msg)
            raise exception.BadValue(error_msg)

        if template_names is not None:
            if not hasattr(template_names, "__iter__"):
                error_msg = "Input parameter 'template_names' is not iterable"
                self.log.error(error_msg)
                raise exception.BadValue(error_msg)

            if len(workitems) != len(template_names):
                error_msg = "".join([
                    "Input parameters 'workitems' and ",
                    "'template_names' have different length"
                ])
                self.log.error(error_msg)
                raise exception.BadValue(error_msg)

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
            except Exception as excp:
                self.log.error(
                    "Exception occurred when fetching"
                    "template from <Workitem %s>: %s", str(wk_id), excp)
                continue
        self.log.info(
            "Successfully fetch all the templates from "
            "workitems: %s", workitems)

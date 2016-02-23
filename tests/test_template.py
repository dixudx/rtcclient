import requests
import pytest
import utils_test
from rtcclient.exception import BadValue
from jinja2 import exceptions as jinja2_excp
import xmltodict


class TestTemplater:

    @pytest.fixture(autouse=True)
    def myrtcclient(self, rtcclient):
        myclient = rtcclient
        return myclient

    @pytest.fixture(autouse=True)
    def mytemplater(self, myrtcclient):
        return myrtcclient.templater

    def test_init_templater(self, mytemplater, myrtcclient):
        assert mytemplater.url == "http://test.url:9443/jazz"
        assert mytemplater.searchpath == utils_test._search_path
        assert mytemplater.rtc_obj == myrtcclient
        assert str(mytemplater) == "".join(["Templater for RTC Server ",
                                            "at http://test.url:9443/jazz"])

    def test_list_fields(self, mytemplater):
        # invalid template names
        invalid_names = [None, True, False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                mytemplater.listFields(invalid_name)

        # nonexistent template names
        fake_names = ["fake_name1", "fake_name2"]
        for fake_name in fake_names:
            with pytest.raises(jinja2_excp.TemplateNotFound):
                mytemplater.listFields(fake_name)

        # existent template
        fields = mytemplater.listFields(utils_test.template_name)
        fields_set = set(["severity", "title", "teamArea",
                          "description", "filedAgainst", "priority",
                          "ownedBy", "plannedFor"])
        assert fields == fields_set

    def test_render(self, mytemplater):
        # invalid template names
        invalid_names = [None, True, False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                mytemplater.render(invalid_name)

    def test_get_template(self, mytemplater, mocker):
        # invalid template names
        invalid_names = [None, True, False, "", u"", 123.4]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                mytemplater.getTemplate(invalid_name,
                                        template_name=None,
                                        template_folder=None,
                                        keep=False,
                                        encoding="UTF-8")

        # valid template name
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.workitem1_raw
        mocked_get.return_value = mock_resp

        copied_from_valid_names = [161, "161", u"161"]
        for copied_from in copied_from_valid_names:
            template_161 = mytemplater.getTemplate(copied_from,
                                                   template_name=None,
                                                   template_folder=None,
                                                   keep=False,
                                                   encoding="UTF-8")
            assert (list(xmltodict.parse(template_161).items()).sort() ==
                    list(utils_test.template_ordereddict.items()).sort())

    def test_get_templates_exception(self, mytemplater):
        # invalid workitem ids
        invalid_names = [None, True, False, "", u"", "test", u"test",
                         123, 123.4]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                mytemplater.getTemplates(invalid_name,
                                         template_folder=None,
                                         template_names=None,
                                         keep=False,
                                         encoding="UTF-8")

        # invalid template names
        invalid_names = [True, False, "", u"", "test", u"test"]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                mytemplater.getTemplates(["valid_id_1", "valid_id_2"],
                                         template_folder=None,
                                         template_names=invalid_name,
                                         keep=False,
                                         encoding="UTF-8")

        # unequal length
        with pytest.raises(BadValue):
            mytemplater.getTemplates(["valid_id_1", "valid_id_2"],
                                     template_folder=None,
                                     template_names=["valid_name"],
                                     keep=False,
                                     encoding="UTF-8")

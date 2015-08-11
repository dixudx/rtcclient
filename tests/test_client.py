from rtcclient.client import RTCClient
import requests
import pytest
import utils_test
from rtcclient.project_area import ProjectArea
import xmltodict
from rtcclient.exception import BadValue, NotFound, RTCException, EmptyAttrib


def test_headers(mocker):
    mocked_get = mocker.patch("requests.get")
    mocker_post = mocker.patch("requests.post")

    mock_resp = mocker.MagicMock(spec=requests.Response)
    mock_resp.status_code = 200
    mock_resp.headers = {"set-cookie": "cookie-id"}
    mocked_get.return_value = mock_resp
    mocker_post.return_value = mock_resp

    expected_headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "Cookie": "cookie-id",
                        "Accept": "text/xml"}

    client = RTCClient(url="http://test.url:9443/jazz",
                       username="user",
                       password="password")
    assert client.headers == expected_headers


class TestRTCClient:
    @pytest.fixture(autouse=True)
    def myrtcclient(self, rtcclient):
        myclient = rtcclient
        return myclient

    @pytest.fixture
    def mock_get_pas(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("projectareas.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_projectareas_unarchived(self, myrtcclient, mock_get_pas):
        projectareas = myrtcclient.getProjectAreas(archived=False)

        raw_content = utils_test.pa2
        pa = ProjectArea("/".join(["http://test.url:9443/jazz/oslc",
                                   "projectareas/_CuZu0HUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         xmltodict.parse(raw_content))
        assert projectareas == [pa]

    def test_get_projectareas_archived(self, myrtcclient, mock_get_pas):
        projectareas = myrtcclient.getProjectAreas(archived=True)

        raw_content = utils_test.pa1
        pa = ProjectArea("/".join(["http://test.url:9443/jazz/oslc",
                                   "projectareas/_0qMJUMfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         xmltodict.parse(raw_content))
        assert projectareas == [pa]

    def test_get_projectarea_unarchived(self, myrtcclient, mock_get_pas):
        pa = myrtcclient.getProjectArea(projectarea_name="ProjectArea2",
                                        archived=False)

        raw_content = utils_test.pa2
        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_CuZu0HUwEeKicpXBddtqNA"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 xmltodict.parse(raw_content))

    def test_get_projectarea_exception(self, myrtcclient):
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getProjectArea(projectarea_name=invalid_name,
                                           archived=False)

    def test_get_projectarea_archived(self, myrtcclient, mock_get_pas):
        pa = myrtcclient.getProjectArea(projectarea_name="ProjectArea1",
                                        archived=True)

        raw_content = utils_test.pa1
        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_0qMJUMfiEd6yW_0tvNlbrw"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 xmltodict.parse(raw_content))

    def test_get_projectarea_byid(self, myrtcclient, mock_get_pas):
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        pa = myrtcclient.getProjectAreaByID(projectarea_id=pa_id,
                                            archived=False)
        raw_content = utils_test.pa2
        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_CuZu0HUwEeKicpXBddtqNA"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 xmltodict.parse(raw_content))

    def test_get_projectarea_id(self, myrtcclient, mock_get_pas):
        pa_id = myrtcclient.getProjectAreaID(projectarea_name="ProjectArea1",
                                             archived=True)
        assert pa_id == "_0qMJUMfiEd6yW_0tvNlbrw"

        pa_id = myrtcclient.getProjectAreaID(projectarea_name="ProjectArea2",
                                             archived=False)
        assert pa_id == "_CuZu0HUwEeKicpXBddtqNA"

    def test_get_projectarea_ids(self, myrtcclient, mock_get_pas):

        pa_id = myrtcclient.getProjectAreaIDs(projectarea_name="ProjectArea1",
                                              archived=True)
        assert pa_id == ["_0qMJUMfiEd6yW_0tvNlbrw"]

        pa_id = myrtcclient.getProjectAreaIDs(archived=True)
        assert pa_id == ["_0qMJUMfiEd6yW_0tvNlbrw"]

        pa_id = myrtcclient.getProjectAreaIDs(projectarea_name="ProjectArea2",
                                              archived=False)
        assert pa_id == ["_CuZu0HUwEeKicpXBddtqNA"]

        pa_id = myrtcclient.getProjectAreaIDs(archived=False)
        assert pa_id == ["_CuZu0HUwEeKicpXBddtqNA"]

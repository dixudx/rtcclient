from rtcclient.client import RTCClient
import requests
import pytest
import utils_test
from rtcclient.project_area import ProjectArea, TeamArea
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

    def test_get_projectareas_unarchived(self, myrtcclient, mock_get_pas,
                                         mocker):
        projectareas = myrtcclient.getProjectAreas(archived=False)

        raw_content = utils_test.pa2
        pa = ProjectArea("/".join(["http://test.url:9443/jazz/oslc",
                                   "projectareas/_CuZu0HUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         xmltodict.parse(raw_content).get("rtc_cm:Project"))
        assert projectareas == [pa]
        assert str(pa) == "ProjectArea2"

        # test for None
        mock_cmd = "rtcclient.client.RTCClient._get_paged_resources"
        mock_get_no_pas = mocker.patch(mock_cmd)
        mock_get_no_pas.return_value = None
        myrtcclient._get_paged_resources = mock_get_no_pas

        projectareas = myrtcclient.getProjectAreas(archived=False)
        assert projectareas is None

    def test_get_projectareas_archived(self, myrtcclient, mock_get_pas,
                                       mocker):
        projectareas = myrtcclient.getProjectAreas(archived=True)

        raw_content = utils_test.pa1
        pa = ProjectArea("/".join(["http://test.url:9443/jazz/oslc",
                                   "projectareas/_0qMJUMfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         xmltodict.parse(raw_content).get("rtc_cm:Project"))
        assert projectareas == [pa]
        assert str(pa) == "ProjectArea1"

        # test for None
        mock_cmd = "rtcclient.client.RTCClient._get_paged_resources"
        mock_get_no_pas = mocker.patch(mock_cmd)
        mock_get_no_pas.return_value = None
        myrtcclient._get_paged_resources = mock_get_no_pas

        projectareas = myrtcclient.getProjectAreas(archived=True)
        assert projectareas is None

    def test_get_projectarea_unarchived(self, myrtcclient, mock_get_pas):
        pa = myrtcclient.getProjectArea(projectarea_name="ProjectArea2",
                                        archived=False)

        raw_content = utils_test.pa2
        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_CuZu0HUwEeKicpXBddtqNA"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 xmltodict.parse(raw_content))
        assert str(pa) == "ProjectArea2"

    def test_get_projectarea_exception(self, myrtcclient, mock_get_pas):
        # test for invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getProjectArea(projectarea_name=invalid_name,
                                           archived=False)

            with pytest.raises(BadValue):
                myrtcclient.getProjectArea(projectarea_name=invalid_name,
                                           archived=True)
        # test for undefined names
        invalid_names = ["fake_name1", "fake_name2"]
        for invalid_name in invalid_names:
            with pytest.raises(NotFound):
                myrtcclient.getProjectArea(projectarea_name=invalid_name,
                                           archived=False)

            with pytest.raises(NotFound):
                myrtcclient.getProjectArea(projectarea_name=invalid_name,
                                           archived=True)

    def test_get_projectarea_archived(self, myrtcclient, mock_get_pas):
        pa = myrtcclient.getProjectArea(projectarea_name="ProjectArea1",
                                        archived=True)

        raw_content = utils_test.pa1
        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_0qMJUMfiEd6yW_0tvNlbrw"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 xmltodict.parse(raw_content))
        assert str(pa) == "ProjectArea1"

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
        assert str(pa) == "ProjectArea2"

    def test_get_projectarea_id(self, myrtcclient, mock_get_pas):
        pa_id = myrtcclient.getProjectAreaID(projectarea_name="ProjectArea1",
                                             archived=True)
        assert pa_id == "_0qMJUMfiEd6yW_0tvNlbrw"

        pa_id = myrtcclient.getProjectAreaID(projectarea_name="ProjectArea2",
                                             archived=False)
        assert pa_id == "_CuZu0HUwEeKicpXBddtqNA"

    def test_get_projectarea_id_exception(self, myrtcclient, mock_get_pas):
        # test for invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getProjectAreaID(projectarea_name=invalid_name,
                                             archived=False)

            with pytest.raises(BadValue):
                myrtcclient.getProjectAreaID(projectarea_name=invalid_name,
                                             archived=True)

        # test for undefined names
        invalid_names = ["fake_name1", "fake_name2"]
        for invalid_name in invalid_names:
            with pytest.raises(NotFound):
                myrtcclient.getProjectAreaID(projectarea_name=invalid_name,
                                             archived=False)

            with pytest.raises(NotFound):
                myrtcclient.getProjectAreaID(projectarea_name=invalid_name,
                                             archived=True)

    def test_get_projectarea_byid_exception(self, myrtcclient, mock_get_pas):
        # test for invalid names
        invalid_ids = [None, "", False]
        for invalid_id in invalid_ids:
            with pytest.raises(BadValue):
                myrtcclient.getProjectAreaByID(projectarea_id=invalid_id,
                                               archived=False)

            with pytest.raises(BadValue):
                myrtcclient.getProjectAreaByID(projectarea_id=invalid_id,
                                               archived=True)

        # test for undefined names
        invalid_ids = ["fake_id1", "fake_id2"]
        for invalid_id in invalid_ids:
            with pytest.raises(NotFound):
                myrtcclient.getProjectAreaByID(projectarea_id=invalid_id,
                                               archived=False)

            with pytest.raises(NotFound):
                myrtcclient.getProjectAreaByID(projectarea_id=invalid_id,
                                               archived=True)

    def test_get_projectarea_ids(self, myrtcclient, mock_get_pas, mocker):

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

        # test for None
        mock_cmd = "rtcclient.client.RTCClient.getProjectAreaIDs"
        mock_get_no_pas = mocker.patch(mock_cmd)
        mock_get_no_pas.return_value = None
        myrtcclient.getProjectAreas = mock_get_no_pas
        assert myrtcclient.getProjectAreaIDs() is None
        assert myrtcclient.getProjectAreaIDs(archived=False) is None
        assert myrtcclient.getProjectAreaIDs(archived=True) is None

    def test_get_projectarea_ids_exception(self, myrtcclient):
        # test for invlaid names
        invalid_names = ["", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getProjectAreaIDs(projectarea_name=invalid_name,
                                              archived=False)

            with pytest.raises(BadValue):
                myrtcclient.getProjectAreaIDs(projectarea_name=invalid_name,
                                              archived=True)

    def test_check_projectarea_id(self, myrtcclient, mock_get_pas):
        bool_value = myrtcclient.checkProjectAreaID("_0qMJUMfiEd6yW_0tvNlbrw",
                                                    archived=True)
        assert True == bool_value

        bool_value = myrtcclient.checkProjectAreaID("_CuZu0HUwEeKicpXBddtqNA",
                                                    archived=False)
        assert True == bool_value

        bool_value = myrtcclient.checkProjectAreaID("fake_id",
                                                    archived=True)
        assert False == bool_value

        bool_value = myrtcclient.checkProjectAreaID("fake_id",
                                                    archived=False)
        assert False == bool_value

    @pytest.fixture
    def mock_get_tas(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("teamareas.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_teamareas_unarchived(self, myrtcclient, mock_get_tas,
                                      mocker):
        teamareas = myrtcclient.getTeamAreas()

        # Team1
        raw_content = utils_test.ta1
        ta1 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_ECYfMHUwEeKicpXBddtqNA"]),
                       myrtcclient,
                       xmltodict.parse(raw_content).get("rtc_cm:Team"))
        assert str(ta1) == "Team1"
        assert ta1.members == ["Team1", "Team2"]
        assert ta1.administrators == ["Team1", "Team2"]

        # Team2
        raw_content = utils_test.ta2
        ta2 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_XazXEPbZEeGWkpg5MjeYZQ"]),
                       myrtcclient,
                       xmltodict.parse(raw_content).get("rtc_cm:Team"))
        assert str(ta2) == "Team2"
        assert ta2.members == ["Team1", "Team2"]
        assert ta2.administrators == ["Team1", "Team2"]

        assert teamareas == [ta1, ta2]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getTeamAreas(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        teamareas = myrtcclient.getTeamAreas(projectarea_id=pa_id)
        assert teamareas == [ta1, ta2]

    def test_get_teamareas_archived(self, myrtcclient, mock_get_tas,
                                    mocker):
        teamareas = myrtcclient.getTeamAreas(archived=True)

        assert teamareas is None

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getTeamAreas(projectarea_id="fake_id",
                                     archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        teamareas = myrtcclient.getTeamAreas(projectarea_id=pa_id,
                                             archived=True)
        assert teamareas is None

    def test_get_teamarea_unarchived(self, myrtcclient, mock_get_tas, mocker):
        ta = myrtcclient.getTeamArea("Team1")

        raw_content = utils_test.ta1
        ta1 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_ECYfMHUwEeKicpXBddtqNA"]),
                       myrtcclient,
                       xmltodict.parse(raw_content).get("rtc_cm:Team"))
        assert ta == ta1

        # test invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getTeamArea(invalid_name,
                                        projectarea_id="fake_id")

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getTeamArea("Team1",
                                    projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        teamarea = myrtcclient.getTeamArea("Team1",
                                           projectarea_id=pa_id)
        assert teamarea == ta1

    def test_get_teamarea_archived(self, myrtcclient, mock_get_tas, mocker):
        with pytest.raises(NotFound):
            myrtcclient.getTeamArea("Team1",
                                    archived=True)

        # test invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getTeamArea(invalid_name,
                                        projectarea_id="fake_id",
                                        archived=True)

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getTeamArea("Team1",
                                    projectarea_id="fake_id",
                                    archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        with pytest.raises(NotFound):
            myrtcclient.getTeamArea("Team1",
                                    projectarea_id=pa_id,
                                    archived=True)

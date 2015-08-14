from rtcclient.client import RTCClient
import requests
import pytest
import utils_test
from rtcclient.project_area import ProjectArea, TeamArea, Member, PlannedFor
from rtcclient.project_area import Severity
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
        # fake data: pls ignore the value
        assert ta1.members == ["Team1", "Team2"]
        assert ta1.administrators == ["Team1", "Team2"]

        # Team2
        raw_content = utils_test.ta2
        ta2 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_XazXEPbZEeGWkpg5MjeYZQ"]),
                       myrtcclient,
                       xmltodict.parse(raw_content).get("rtc_cm:Team"))
        assert str(ta2) == "Team2"
        # fake data: pls ignore the value
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

    def test_get_owned_by(self, myrtcclient):
        member = myrtcclient.getOwnedBy("tester1@email.com")
        url = "http://test.url:9443/jts/users/tester1%40email.com"
        assert member == Member(url,
                                myrtcclient)
        assert member.email == "tester1@email.com"

    @pytest.fixture
    def mock_get_plannedfors(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("plannedfors.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_plannedfors_unarchived(self, myrtcclient,
                                        mock_get_plannedfors, mocker):
        plannedfors = myrtcclient.getPlannedFors()

        # PlannedFor1
        raw_content = utils_test.plannedfor1
        pf1 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_00J9ocfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         xmltodict.parse(raw_content).get("rtc_cm:Iteration"))
        assert str(pf1) == "Release 1.0"
        assert pf1.identifier == "1.0"
        assert pf1.startDate == "2009-11-02T06:00:00.000Z"
        assert pf1.endDate == "2009-12-12T06:00:00.000Z"
        # fake data: pls ignore the value
        assert pf1.timeline == ["Release 1.0", "Sprint 1 (1.0)"]
        assert pf1.projectArea == ["Release 1.0", "Sprint 1 (1.0)"]

        # PlannedFor1
        raw_content = utils_test.plannedfor2
        pf2 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_DbGcwHUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         xmltodict.parse(raw_content).get("rtc_cm:Iteration"))
        assert str(pf2) == "Sprint 1 (1.0)"
        assert pf2.identifier == "1.0 S1"
        assert pf2.startDate == "2013-02-12T06:00:00.000Z"
        assert pf2.endDate == "2013-03-04T06:00:00.000Z"
        # fake data: pls ignore the value
        assert pf2.timeline == ["Release 1.0", "Sprint 1 (1.0)"]
        assert pf2.projectArea == ["Release 1.0", "Sprint 1 (1.0)"]

        assert plannedfors == [pf2]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getPlannedFors(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        plannedfors = myrtcclient.getPlannedFors(projectarea_id=pa_id)
        assert plannedfors == [pf2]

    def test_get_plannedfors_archived(self, myrtcclient,
                                      mock_get_plannedfors, mocker):
        plannedfors = myrtcclient.getPlannedFors(archived=True)

        # PlannedFor1
        raw_content = utils_test.plannedfor1
        pf1 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_00J9ocfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         xmltodict.parse(raw_content).get("rtc_cm:Iteration"))
        assert plannedfors == [pf1]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getTeamAreas(projectarea_id="fake_id",
                                     archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        plannedfors = myrtcclient.getPlannedFors(projectarea_id=pa_id,
                                                 archived=True)
        assert plannedfors == [pf1]

    def test_get_plannedfor_unarchived(self, myrtcclient,
                                       mock_get_plannedfors, mocker):
        plannedfor = myrtcclient.getPlannedFor("Sprint 1 (1.0)")

        raw_content = utils_test.plannedfor2
        pf2 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_DbGcwHUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         xmltodict.parse(raw_content).get("rtc_cm:Iteration"))
        assert plannedfor == pf2

        # test for a plannedfor which is archived
        with pytest.raises(NotFound):
            myrtcclient.getPlannedFor("Release 1.0")

        # test invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getPlannedFor(invalid_name,
                                          projectarea_id="fake_id")

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getPlannedFor("Sprint 1 (1.0)",
                                      projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        plannedfor = myrtcclient.getPlannedFor("Sprint 1 (1.0)",
                                               projectarea_id=pa_id)
        assert plannedfor == pf2

    def test_get_plannedfor_archived(self, myrtcclient,
                                     mock_get_plannedfors, mocker):
        # test for a plannedfor which is unarchived
        with pytest.raises(NotFound):
            myrtcclient.getPlannedFor("Sprint 1 (1.0)",
                                      archived=True)

        # test invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getPlannedFor(invalid_name,
                                          projectarea_id="fake_id",
                                          archived=True)

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getPlannedFor("Release 1.0",
                                      projectarea_id="fake_id",
                                      archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        with pytest.raises(NotFound):
            myrtcclient.getPlannedFor("Release 1.0",
                                      projectarea_id=pa_id,
                                      archived=True)

    @pytest.fixture
    def mock_get_severities(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("severities.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_severities(self, myrtcclient,
                            mock_get_severities, mocker):
        with pytest.raises(EmptyAttrib):
            myrtcclient.getSeverities()

        # Severity1
        raw_content = utils_test.severity1
        url1 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "severity/severity.literal.l1"])
        s1 = Severity(url1,
                      myrtcclient,
                      xmltodict.parse(raw_content).get("rtc_cm:Literal"))
        assert str(s1) == "Unclassified"
        assert s1.url == url1
        assert s1.identifier == "severity.literal.l1"
        icon_url = "".join(["http://test.url:9443/jazz/service/",
                            "com.ibm.team.workitem.common.internal.model.",
                            "IImageContentService/processattachment/",
                            "_CuZu0HUwEeKicpXBddtqNA/enumeration/",
                            "unassigned2.gif"])
        assert s1.iconUrl == icon_url

        # Severity2
        raw_content = utils_test.severity2
        url2 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "severity/severity.literal.l2"])
        s2 = Severity(url2,
                      myrtcclient,
                      xmltodict.parse(raw_content).get("rtc_cm:Literal"))
        assert str(s2) == "Normal"
        assert s2.url == url2
        assert s2.identifier == "severity.literal.l2"
        icon_url = "".join(["http://test.url:9443/jazz/service/",
                            "com.ibm.team.workitem.common.internal.model.",
                            "IImageContentService/processattachment/",
                            "_CuZu0HUwEeKicpXBddtqNA/enumeration/",
                            "normal.gif"])
        assert s2.iconUrl == icon_url

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getSeverities(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        severities = myrtcclient.getSeverities(projectarea_id=pa_id)
        assert severities == [s1, s2]

    def test_get_severity(self, myrtcclient,
                          mock_get_severities, mocker):
        with pytest.raises(EmptyAttrib):
            myrtcclient.getSeverity("Unclassified")

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getSeverity("Unclassified",
                                    projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        severity = myrtcclient.getSeverity("Unclassified",
                                           projectarea_id=pa_id)

        # Severity1
        raw_content = utils_test.severity1
        url1 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "severity/severity.literal.l1"])
        s1 = Severity(url1,
                      myrtcclient,
                      xmltodict.parse(raw_content).get("rtc_cm:Literal"))

        assert severity == s1

        # test for None
        with pytest.raises(NotFound):
            myrtcclient.getSeverity("fake_severity_name",
                                    projectarea_id=pa_id)

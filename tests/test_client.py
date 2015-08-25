from rtcclient.client import RTCClient
import requests
import pytest
import utils_test
from rtcclient.project_area import ProjectArea
from rtcclient.models import Severity, Priority, FoundIn, FiledAgainst
from rtcclient.models import TeamArea, Member, PlannedFor
from rtcclient.workitem import Workitem
from rtcclient.exception import BadValue, NotFound, RTCException, EmptyAttrib


def test_headers(mocker):
    mocked_get = mocker.patch("requests.get")
    mocked_post = mocker.patch("requests.post")

    mock_resp = mocker.MagicMock(spec=requests.Response)
    mock_resp.status_code = 200

    mocked_get.return_value = mock_resp
    mocked_post.return_value = mock_resp

    expected_headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "Cookie": "cookie-id",
                        "Accept": "text/xml"}

    # auth failed
    mock_resp.headers = {"set-cookie": "cookie-id",
                         "x-com-ibm-team-repository-web-auth-msg": "authfailed"}
    with pytest.raises(RTCException):
        RTCClient(url="http://test.url:9443/jazz",
                  username="user",
                  password="password")

    mock_resp.headers = {"set-cookie": "cookie-id"}
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

        # ProjectArea2
        pa = ProjectArea("/".join(["http://test.url:9443/jazz/oslc",
                                   "projectareas/_CuZu0HUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         utils_test.pa2)
        assert projectareas == [pa]
        assert str(pa) == "ProjectArea2"
        assert pa.description == "Demo for test: Project Area Two"
        assert pa.initialized == "true"
        assert pa.archived == "false"

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

        # ProjectArea1
        pa = ProjectArea("/".join(["http://test.url:9443/jazz/oslc",
                                   "projectareas/_0qMJUMfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         utils_test.pa1)
        assert projectareas == [pa]
        assert str(pa) == "ProjectArea1"
        assert pa.description == "Demo for test: Project Area One"
        assert pa.initialized == "true"
        assert pa.archived == "true"

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

        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_CuZu0HUwEeKicpXBddtqNA"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 utils_test.pa2)
        assert str(pa) == "ProjectArea2"

    def test_get_projectarea_exception(self, myrtcclient, mock_get_pas):
        # test for invalid names
        invalid_names = [None, "", False, True]
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

        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_0qMJUMfiEd6yW_0tvNlbrw"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 utils_test.pa1)
        assert str(pa) == "ProjectArea1"

    def test_get_projectarea_byid(self, myrtcclient, mock_get_pas):
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        pa = myrtcclient.getProjectAreaByID(projectarea_id=pa_id,
                                            archived=False)
        url = "/".join(["http://test.url:9443/jazz/oslc",
                        "projectareas/_CuZu0HUwEeKicpXBddtqNA"])
        assert pa == ProjectArea(url,
                                 myrtcclient,
                                 utils_test.pa2)
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
        invalid_names = [None, "", False, True]
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
        invalid_ids = [None, "", False, True]
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
        invalid_names = ["", False, True]
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

        # TeamArea1
        ta1 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_ECYfMHUwEeKicpXBddtqNA"]),
                       myrtcclient,
                       utils_test.ta1)
        assert str(ta1) == "Team1"
        # fake data: pls ignore the value
        assert ta1.members == ["Team1", "Team2"]
        assert ta1.administrators == ["Team1", "Team2"]

        # TeamArea2
        ta2 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_XazXEPbZEeGWkpg5MjeYZQ"]),
                       myrtcclient,
                       utils_test.ta2)
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

        # TeamArea1
        ta1 = TeamArea("/".join(["http://test.url:9443/jazz/oslc",
                                 "teamareas/_ECYfMHUwEeKicpXBddtqNA"]),
                       myrtcclient,
                       utils_test.ta1)
        assert ta == ta1

        # test invalid names
        invalid_names = [None, "", False, True]
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
        invalid_names = [None, "", False, True]
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

        # test invalid emails
        invalid_emails = [None, "", False, True, "test%40email.com"]
        for invalid_email in invalid_emails:
            with pytest.raises(BadValue):
                myrtcclient.getOwnedBy(invalid_email)

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

        # PlannedFor2
        pf2 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_DbGcwHUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         utils_test.plannedfor2)
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
        pf1 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_00J9ocfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         utils_test.plannedfor1)
        assert str(pf1) == "Release 1.0"
        assert pf1.identifier == "1.0"
        assert pf1.startDate == "2009-11-02T06:00:00.000Z"
        assert pf1.endDate == "2009-12-12T06:00:00.000Z"
        # fake data: pls ignore the value
        assert pf1.timeline == ["Release 1.0", "Sprint 1 (1.0)"]
        assert pf1.projectArea == ["Release 1.0", "Sprint 1 (1.0)"]

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
        # test for a plannedfor which is archived
        with pytest.raises(NotFound):
            myrtcclient.getPlannedFor("Release 1.0")

        plannedfor = myrtcclient.getPlannedFor("Sprint 1 (1.0)")

        # Plannedfor2
        pf2 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_DbGcwHUwEeKicpXBddtqNA"]),
                         myrtcclient,
                         utils_test.plannedfor2)
        assert plannedfor == pf2

        # test invalid names
        invalid_names = [None, "", False, True]
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

        plannedfor = myrtcclient.getPlannedFor("Release 1.0",
                                               archived=True)

        # Plannedfor1
        pf1 = PlannedFor("/".join(["http://test.url:9443/jazz/oslc",
                                   "iterations/_00J9ocfiEd6yW_0tvNlbrw"]),
                         myrtcclient,
                         utils_test.plannedfor1)
        assert plannedfor == pf1

        # test invalid names
        invalid_names = [None, "", False, True]
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
        url1 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "severity/severity.literal.l1"])
        s1 = Severity(url1,
                      myrtcclient,
                      utils_test.severity1)
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
        url2 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "severity/severity.literal.l2"])
        s2 = Severity(url2,
                      myrtcclient,
                      utils_test.severity2)
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
        # test invalid names
        invalid_names = [None, "", False, True]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getSeverity(invalid_name,
                                        projectarea_id="fake_id")

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
        url1 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "severity/severity.literal.l1"])
        s1 = Severity(url1,
                      myrtcclient,
                      utils_test.severity1)

        assert severity == s1

        # test for None
        with pytest.raises(NotFound):
            myrtcclient.getSeverity("fake_severity_name",
                                    projectarea_id=pa_id)

    @pytest.fixture
    def mock_get_priorities(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("priorities.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_priorities(self, myrtcclient,
                            mock_get_priorities, mocker):
        with pytest.raises(EmptyAttrib):
            myrtcclient.getPriorities()

        # Priority1
        url1 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "priority/priority.literal.l01"])
        p1 = Priority(url1,
                      myrtcclient,
                      utils_test.priority1)
        assert str(p1) == "Unassigned"
        assert p1.url == url1
        assert p1.identifier == "priority.literal.l01"
        icon_url = "".join(["http://test.url:9443/jazz/service/",
                            "com.ibm.team.workitem.common.internal.model.",
                            "IImageContentService/processattachment/",
                            "_CuZu0HUwEeKicpXBddtqNA/enumeration/",
                            "unassigned.gif"])
        assert p1.iconUrl == icon_url

        # Priority2
        url2 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "priority/priority.literal.l11"])
        p2 = Priority(url2,
                      myrtcclient,
                      utils_test.priority2)
        assert str(p2) == "High"
        assert p2.url == url2
        assert p2.identifier == "priority.literal.l11"
        icon_url = "".join(["http://test.url:9443/jazz/service/",
                            "com.ibm.team.workitem.common.internal.",
                            "model.IImageContentService/processattachment/",
                            "_CuZu0HUwEeKicpXBddtqNA/enumeration/high.gif"])
        assert p2.iconUrl == icon_url

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getPriorities(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        priorities = myrtcclient.getPriorities(projectarea_id=pa_id)
        assert priorities == [p1, p2]

    def test_get_priority(self, myrtcclient,
                          mock_get_priorities, mocker):
        # test invalid names
        invalid_names = [None, "", False, True]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getPriority(invalid_name,
                                        projectarea_id="fake_id")

        with pytest.raises(EmptyAttrib):
            myrtcclient.getPriority("Unassigned")

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getPriority("Unassigned",
                                    projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        priority = myrtcclient.getPriority("Unassigned",
                                           projectarea_id=pa_id)

        # Priority1
        url1 = "/".join(["http://test.url:9443/jazz/oslc",
                         "enumerations/_CuZu0HUwEeKicpXBddtqNA",
                         "priority/priority.literal.l01"])
        p1 = Priority(url1,
                      myrtcclient,
                      utils_test.priority1)

        assert priority == p1

        # test for None
        with pytest.raises(NotFound):
            myrtcclient.getPriority("fake_priority_name",
                                    projectarea_id=pa_id)

    @pytest.fixture
    def mock_get_foundins(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("foundins.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_foundins_unarchived(self, myrtcclient,
                                     mock_get_foundins, mocker):
        foundins = myrtcclient.getFoundIns()

        # Foundin2
        f2 = FoundIn("/".join(["http://test.url:9443/jazz/resource",
                               "itemOid/com.ibm.team.workitem.Deliverable",
                               "_vztkUOW3Ed6ThJa-QCz7dg"]),
                     myrtcclient,
                     utils_test.foundin2)
        assert str(f2) == "Sprint2"
        assert f2.filtered == "false"
        assert f2.modified == "2015-07-21T01:46:12.096Z"
        assert f2.artifact is None
        assert f2.archived == "false"
        assert f2.created is None
        assert f2.description is None
        # fake data: pls ignore the value
        assert f2.projectArea == ["Sprint1", "Sprint2"]
        assert f2.modifiedBy == "tester2@email.com"

        assert foundins == [f2]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFoundIns(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        foundins = myrtcclient.getFoundIns(projectarea_id=pa_id)
        assert foundins == [f2]

    def test_get_foundins_archived(self, myrtcclient,
                                   mock_get_foundins, mocker):
        foundins = myrtcclient.getFoundIns(archived=True)

        # Foundin1
        f1 = FoundIn("/".join(["http://test.url:9443/jazz/resource",
                               "itemOid/com.ibm.team.workitem.Deliverable",
                               "_Hx5_wKOlEeKPvqjjtP1sGw"]),
                     myrtcclient,
                     utils_test.foundin1)
        assert str(f1) == "Sprint1"
        assert f1.filtered == "true"
        assert f1.modified == "2009-11-05T11:36:00.596Z"
        assert f1.artifact is None
        assert f1.archived == "true"
        assert f1.created is None
        assert f1.description is None
        # fake data: pls ignore the value
        assert f1.projectArea == ["Sprint1", "Sprint2"]
        assert f1.modifiedBy == "tester1@email.com"

        assert foundins == [f1]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFoundIns(projectarea_id="fake_id",
                                    archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        foundins = myrtcclient.getFoundIns(projectarea_id=pa_id,
                                           archived=True)
        assert foundins == [f1]

    def test_get_foundin_unarchived(self, myrtcclient,
                                    mock_get_foundins, mocker):
        # test for a foundin which is archived
        with pytest.raises(NotFound):
            myrtcclient.getFoundIn("Sprint1")

        foundin = myrtcclient.getFoundIn("Sprint2")

        # Foundin2
        f2 = FoundIn("/".join(["http://test.url:9443/jazz/resource",
                               "itemOid/com.ibm.team.workitem.Deliverable",
                               "_vztkUOW3Ed6ThJa-QCz7dg"]),
                     myrtcclient,
                     utils_test.foundin2)

        assert foundin == f2

        # test invalid names
        invalid_names = [None, "", False, True]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getFoundIn(invalid_name,
                                       projectarea_id="fake_id")

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFoundIn("Sprint2",
                                   projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        foundin = myrtcclient.getFoundIn("Sprint2",
                                         projectarea_id=pa_id)
        assert foundin == f2

    def test_get_foundin_archived(self, myrtcclient,
                                  mock_get_foundins, mocker):
        # test for a foundin which is unarchived
        with pytest.raises(NotFound):
            myrtcclient.getFoundIn("Sprint2",
                                   archived=True)

        # Foundin1
        f1 = FoundIn("/".join(["http://test.url:9443/jazz/resource",
                               "itemOid/com.ibm.team.workitem.Deliverable",
                               "_Hx5_wKOlEeKPvqjjtP1sGw"]),
                     myrtcclient,
                     utils_test.foundin1)

        # test invalid names
        invalid_names = [None, "", False]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getFoundIn(invalid_name,
                                       projectarea_id="fake_id",
                                       archived=True)

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFoundIn("Sprint1",
                                   projectarea_id="fake_id",
                                   archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        foundin = myrtcclient.getFoundIn("Sprint1",
                                         projectarea_id=pa_id,
                                         archived=True)
        assert foundin == f1

    @pytest.fixture
    def mock_get_filedagainsts(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("filedagainsts.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_filedagainsts_unarchived(self, myrtcclient,
                                          mock_get_filedagainsts, mocker):
        filedagainsts = myrtcclient.getFiledAgainsts()

        # Filedagainst2
        fa2 = FiledAgainst("/".join(["http://test.url:9443/jazz/resource",
                                     "itemOid/com.ibm.team.workitem.Category",
                                     "_XcFwgfbZEeGWkpg5MjeYZQ"]),
                           myrtcclient,
                           utils_test.filedagainst2)

        assert str(fa2) == "Category 1"
        assert fa2.hierarchicalName == "Category 1"
        assert fa2.description == "Category to organize your work items."
        assert fa2.defaultTeamArea is None
        assert fa2.depth == "0"
        assert fa2.archived == "false"
        # fake data: pls ignore the value
        assert fa2.projectArea == ["Unassigned", "Category 1"]

        assert filedagainsts == [fa2]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFiledAgainsts(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        filedagainsts = myrtcclient.getFiledAgainsts(projectarea_id=pa_id)
        assert filedagainsts == [fa2]

    def test_get_filedagainsts_archived(self, myrtcclient,
                                        mock_get_filedagainsts, mocker):
        filedagainsts = myrtcclient.getFiledAgainsts(archived=True)

        # Filedagainst1
        fa1 = FiledAgainst("/".join(["http://test.url:9443/jazz/resource",
                                     "itemOid/com.ibm.team.workitem.Category",
                                     "_D5dMsHUwEeKicpXBddtqNA"]),
                           myrtcclient,
                           utils_test.filedagainst1)

        assert str(fa1) == "Unassigned"
        assert fa1.hierarchicalName == "Unassigned"
        assert fa1.description is None
        assert fa1.defaultTeamArea is None
        assert fa1.depth == "0"
        assert fa1.archived == "true"
        # fake data: pls ignore the value
        assert fa1.projectArea == ["Unassigned", "Category 1"]

        assert filedagainsts == [fa1]

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFiledAgainsts(projectarea_id="fake_id",
                                         archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        filedagainsts = myrtcclient.getFiledAgainsts(projectarea_id=pa_id,
                                                     archived=True)
        assert filedagainsts == [fa1]

    def test_get_filedagainst_unarchived(self, myrtcclient,
                                         mock_get_filedagainsts, mocker):
        # test for a filedagainst which is archived
        with pytest.raises(NotFound):
            myrtcclient.getFiledAgainst("Unassigned")

        filedagainst = myrtcclient.getFiledAgainst("Category 1")

        # Filedagainst2
        fa2 = FiledAgainst("/".join(["http://test.url:9443/jazz/resource",
                                     "itemOid/com.ibm.team.workitem.Category",
                                     "_XcFwgfbZEeGWkpg5MjeYZQ"]),
                           myrtcclient,
                           utils_test.filedagainst2)

        assert filedagainst == fa2

        # test invalid names
        invalid_names = [None, "", False, True]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getFiledAgainst(invalid_name,
                                            projectarea_id="fake_id")

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFiledAgainst("Category 1",
                                        projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        filedagainst = myrtcclient.getFiledAgainst("Category 1",
                                                   projectarea_id=pa_id)
        assert filedagainst == fa2

    def test_get_filedagainst_archived(self, myrtcclient,
                                       mock_get_filedagainsts, mocker):
        # test for a filedagainst which is unarchived
        with pytest.raises(NotFound):
            myrtcclient.getFiledAgainst("Category 1",
                                        archived=True)

        # Filedagainst1
        fa1 = FiledAgainst("/".join(["http://test.url:9443/jazz/resource",
                                     "itemOid/com.ibm.team.workitem.Category",
                                     "_D5dMsHUwEeKicpXBddtqNA"]),
                           myrtcclient,
                           utils_test.filedagainst1)

        # test invalid names
        invalid_names = [None, "", False, True]
        for invalid_name in invalid_names:
            with pytest.raises(BadValue):
                myrtcclient.getFiledAgainst(invalid_name,
                                            projectarea_id="fake_id",
                                            archived=True)

        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getFiledAgainst("Unassigned",
                                        projectarea_id="fake_id",
                                        archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_0qMJUMfiEd6yW_0tvNlbrw"
        filedagainst = myrtcclient.getFiledAgainst("Unassigned",
                                                   projectarea_id=pa_id,
                                                   archived=True)
        assert filedagainst == fa1

    def test_get_workitem(self, mocker, myrtcclient):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.workitem1_raw
        mocked_get.return_value = mock_resp

        # Workitem1
        workitem1 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                             myrtcclient,
                             workitem_id=161,
                             raw_data=utils_test.workitem1)
        assert workitem1.identifier == "161"
        assert workitem1.archived == "false"
        assert workitem1.browser is None
        assert workitem1.collabnet_id is None
        assert workitem1.contextId == "_CuZu0HUwEeKicpXBddtqNA"
        assert workitem1.correctedEstimate is None
        assert workitem1.created == "2009-12-03T20:33:42.543Z"
        assert workitem1.creator == "tester1@email.com"
        assert workitem1.description == "description for test demo"
        assert workitem1.due is None
        assert workitem1.estimate is None
        assert workitem1.foundIn is None
        assert workitem1.resolution is None
        assert workitem1.subject is None
        assert workitem1.modified == "2010-02-16T16:04:00.244Z"
        assert workitem1.resolved == "2010-02-16T16:03:59.164Z"
        assert workitem1.startDate is None
        assert workitem1.title == "input title here for 161"

        # fake data: ignore these
        # just list two attributes here
        # skip other attributes with rdf:resource
        assert workitem1.plannedFor == "input title here for 161"
        assert workitem1.filedAgainst == "input title here for 161"
        assert workitem1.comments == "input title here for 161"

        # test for invalid workitem id
        invalid_ids = [None, "", True, False]
        for invalid_id in invalid_ids:
            with pytest.raises(BadValue):
                myrtcclient.getWorkitem(invalid_id)

        # test for valid workitem id
        workitem = myrtcclient.getWorkitem(161)
        assert workitem == workitem1

        workitem11 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                              myrtcclient,
                              raw_data=utils_test.workitem1)
        assert workitem1 == workitem11

        workitem = myrtcclient.getWorkitem("161")
        assert workitem == workitem1

    @pytest.fixture
    def mock_get_workitems(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("workitems.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_workitems_unarchived(self, myrtcclient,
                                      mock_get_workitems, mocker):
        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getWorkitems(projectarea_id="fake_id")

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        workitems = myrtcclient.getWorkitems(projectarea_id=pa_id)

        # Workitem1
        workitem1 = Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                             myrtcclient,
                             workitem_id=161,
                             raw_data=utils_test.workitem1)

        assert workitems == [workitem1]

        # test for None
        workitems = myrtcclient.getWorkitems(projectarea_id="other_valid_id")
        assert workitems is None

    def test_get_workitems_archived(self, myrtcclient,
                                    mock_get_workitems, mocker):
        # test for invalid projectarea id
        mocked_check_pa_id = mocker.patch("rtcclient.client.RTCClient."
                                          "checkProjectAreaID")
        mocked_check_pa_id.return_value = False
        with pytest.raises(BadValue):
            myrtcclient.getWorkitems(projectarea_id="fake_id",
                                     archived=True)

        # test for valid projectarea id
        mocked_check_pa_id.return_value = True
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        workitems = myrtcclient.getWorkitems(projectarea_id=pa_id,
                                             archived=True)

        # Workitem2
        workitem2 = Workitem("http://test.url:9443/jazz/oslc/workitems/6329",
                             myrtcclient,
                             workitem_id=6329,
                             raw_data=utils_test.workitem2)

        assert workitems == [workitem2]

        # test for None
        workitems = myrtcclient.getWorkitems(projectarea_id="other_valid_id",
                                             archived=True)
        assert workitems is None

    def test_list_fields(self, myrtcclient):
        fields = myrtcclient.listFields(utils_test.template_name)
        fields_set = set(["severity", "title", "teamArea",
                          "description", "filedAgainst", "priority",
                          "ownedBy", "plannedFor"])
        assert fields == fields_set

    def test_list_fields_from_workitem(self, myrtcclient,
                                       mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.workitem1_raw
        mocked_get.return_value = mock_resp

        fields = myrtcclient.listFieldsFromWorkitem(161,
                                                    keep=False)
        assert fields == set(["priority", "severity", "title", "teamArea",
                              "description", "ownedBy", "filedAgainst",
                              "plannedFor"])

        fields = myrtcclient.listFieldsFromWorkitem(161,
                                                    keep=True)
        assert fields == set(["description",
                              "title"])

    def test_create_workitem(self, myrtcclient):
        # TODO
        pass

    def test_copy_workitem(self, myrtcclient):
        # TODO
        pass

    def test_update_workitem(self, myrtcclient):
        # TODO
        pass

    def test_check_itemtype(self, myrtcclient, mock_get_pas, mocker):
        # test for invalid ProjectArea ids
        invalid_ids = [None, "", False, True]
        for invalid_id in invalid_ids:
            checked_result = myrtcclient.checkType("fake_name",
                                                   projectarea_id=invalid_id)
            assert checked_result is False

        # test for undefined ProjectArea ids
        invalid_ids = ["fake_id1", "fake_id2"]
        for invalid_id in invalid_ids:
            checked_result = myrtcclient.checkType("fake_name",
                                                   projectarea_id=invalid_id)
            assert checked_result is False

        # test for valid ProjectArea id
        pa_id = "_CuZu0HUwEeKicpXBddtqNA"
        mocked_get = mocker.patch("rtcclient.project_area.ProjectArea."
                                  "getItemType")
        mocked_get.return_value = True
        checked_result = myrtcclient.checkType("valid_name",
                                               projectarea_id=pa_id)
        assert checked_result is True

        mocked_get.return_value = False
        checked_result = myrtcclient.checkType("valid_name",
                                               projectarea_id=pa_id)
        assert checked_result is False

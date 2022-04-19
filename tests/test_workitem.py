import requests
import pytest
import utils_test
from rtcclient.exception import BadValue, NotFound
from rtcclient.workitem import Workitem
from rtcclient.models import Comment, Action, State, IncludedInBuild
from rtcclient.models import ChangeSet, Attachment


class TestWorkitem:

    @pytest.fixture(autouse=True)
    def myrtcclient(self, rtcclient):
        myclient = rtcclient
        return myclient

    @pytest.fixture(autouse=True)
    def workitem1(self, myrtcclient):
        return Workitem("http://test.url:9443/jazz/oslc/workitems/161",
                        myrtcclient,
                        workitem_id=161,
                        raw_data=utils_test.workitem1)

    @pytest.fixture
    def mock_get_comments(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("comments.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_comments(self, myrtcclient, mock_get_comments, workitem1):
        # Comment1
        comment1_url = "/".join([
            "http://test.url:9443/jazz/oslc", "workitems/161/rtc_cm:comments/0"
        ])
        comment1 = Comment(comment1_url,
                           myrtcclient,
                           raw_data=utils_test.comment1)
        assert comment1.id == "0"
        assert str(comment1) == "0"
        assert comment1.created == "2015-07-27T02:35:47.391Z"
        assert comment1.creator == "tester1@email.com"
        assert comment1.description == "comment test"

        # Comment2
        comment2_url = "/".join([
            "http://test.url:9443/jazz/oslc", "workitems/161/rtc_cm:comments/1"
        ])
        comment2 = Comment(comment2_url,
                           myrtcclient,
                           raw_data=utils_test.comment2)
        assert comment2.id == "1"
        assert str(comment2) == "1"
        assert comment2.created == "2015-07-27T10:48:55.197Z"
        assert comment2.creator == "tester2@email.com"
        assert comment2.description == "add comment test2"

        comments = workitem1.getComments()
        assert comments == [comment1, comment2]

    def test_get_comment(self, myrtcclient, mock_get_comments, workitem1):
        # test for invalid comment id
        invalid_comment_ids = ["", None, True, False, "test"]
        for invalid_comment_id in invalid_comment_ids:
            with pytest.raises(BadValue):
                workitem1.getCommentByID(invalid_comment_id)

        # test for valid comment id
        # Comment1
        comment1_url = "/".join([
            "http://test.url:9443/jazz/oslc", "workitems/161/rtc_cm:comments/0"
        ])
        comment1 = Comment(comment1_url,
                           myrtcclient,
                           raw_data=utils_test.comment1)

        # Comment2
        comment2_url = "/".join([
            "http://test.url:9443/jazz/oslc", "workitems/161/rtc_cm:comments/1"
        ])
        comment2 = Comment(comment2_url,
                           myrtcclient,
                           raw_data=utils_test.comment2)

        comment_valid_ids = [0, "0", u"0"]
        for comment_id in comment_valid_ids:
            comment = workitem1.getCommentByID(comment_id)
            assert comment == comment1

        comment_valid_ids = [1, "1", u"1"]
        for comment_id in comment_valid_ids:
            comment = workitem1.getCommentByID(comment_id)
            assert comment == comment2

    def test_add_comment(self, myrtcclient, mocker, workitem1):
        # TODO: add comment test
        pass

    @pytest.fixture
    def mock_get_subscribers(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        # mock_resp.content = utils_test.read_fixture("subscribers.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_susbscribers(self, myrtcclient, mock_get_subscribers):
        # TODO: add susbscirbers.xml
        pass

    @pytest.fixture
    def mock_get_actions(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("actions.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_actions(self, myrtcclient, mock_get_actions, workitem1):
        # Action1
        action1_url = "/".join([
            "http://test.url:9443/jazz/oslc/workflows",
            "_CuZu0HUwEeKicpXBddtqNA/actions",
            "default_workflow/default_workflow.action.a1"
        ])
        action1 = Action(action1_url, myrtcclient, raw_data=utils_test.action1)
        assert str(action1) == "Close"
        assert action1.title == "Close"
        assert action1.identifier == "default_workflow.action.a1"
        # fake data: pls ignore these values
        assert action1.resultState == ["Close", "Start Working"]

        # Action2
        action2_url = "/".join([
            "http://test.url:9443/jazz/oslc/workflows",
            "_CuZu0HUwEeKicpXBddtqNA/actions",
            "default_workflow/default_workflow.action.a2"
        ])
        action2 = Action(action2_url, myrtcclient, raw_data=utils_test.action2)
        assert str(action2) == "Start Working"
        assert action2.title == "Start Working"
        assert action2.identifier == "default_workflow.action.a2"
        # fake data: pls ignore these values
        assert action2.resultState == ["Close", "Start Working"]

        actions = workitem1.getActions()
        assert actions == [action1, action2]

    def get_test_action(self, myrtcclient, mock_get_actions, workitem1):
        # test for invalid name
        invalid_action_names = ["", u"", None, True, False]
        for invalid_action_name in invalid_action_names:
            with pytest.raises(BadValue):
                workitem1.getAction(invalid_action_name)

        # Action1
        action1_url = "/".join([
            "http://test.url:9443/jazz/oslc/workflows",
            "_CuZu0HUwEeKicpXBddtqNA/actions",
            "default_workflow/default_workflow.action.a1"
        ])
        action1 = Action(action1_url, myrtcclient, raw_data=utils_test.action1)

        # Action2
        action2_url = "/".join([
            "http://test.url:9443/jazz/oslc/workflows",
            "_CuZu0HUwEeKicpXBddtqNA/actions",
            "default_workflow/default_workflow.action.a2"
        ])
        action2 = Action(action2_url, myrtcclient, raw_data=utils_test.action2)

        # test for valid name
        action_valid_names = ["Close", u"Close"]
        for action_name in action_valid_names:
            action = workitem1.getAction(action_name)
            assert action == action1

        # test for valid name
        action_valid_names = ["Start Working", u"Start Working"]
        for action_name in action_valid_names:
            action = workitem1.getAction(action_name)
            assert action == action2

        # test for fake name
        action_fake_names = ["Fake_Action", u"Fake_Action"]
        for action_name in action_fake_names:
            with pytest.raises(NotFound):
                workitem1.getAction(action_name)

    @pytest.fixture
    def mock_get_states(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("states.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_states(self, myrtcclient, mock_get_states, workitem1):
        # State1
        state1_url = "/".join([
            "http://test.url:9443/jazz/oslc/workflows",
            "_CuZu0HUwEeKicpXBddtqNA/states",
            "default_workflow/default_workflow.state.s1"
        ])
        state1 = State(state1_url, myrtcclient, raw_data=utils_test.state1)
        assert str(state1) == "Closed"
        assert state1.title == "Closed"
        assert state1.identifier == "default_workflow.state.s1"
        assert state1.group == "inprogress"

        # State2
        state2_url = "/".join([
            "http://test.url:9443/jazz/oslc/workflows",
            "_CuZu0HUwEeKicpXBddtqNA/states",
            "default_workflow/default_workflow.state.s2"
        ])
        state2 = State(state2_url, myrtcclient, raw_data=utils_test.state2)
        assert str(state2) == "In Progress"
        assert state2.title == "In Progress"
        assert state2.identifier == "default_workflow.state.s2"
        assert state2.group == "closed"

        states = workitem1.getStates()
        assert states == [state1, state2]

    @pytest.fixture
    def mock_get_iib(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("includedinbuilds.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_includedinbuilds(self, myrtcclient, mock_get_iib, workitem1):
        # IncludedInBuild1
        iib1_url = ("http://test.url:9443/jazz/resource/itemOid/"
                    "com.ibm.team.build.BuildResult/_2NXr8Fx3EeWfxsy-c6nRWw")
        iib1 = IncludedInBuild(iib1_url,
                               myrtcclient,
                               raw_data=utils_test.includedinbuild1)
        assert iib1.url == iib1_url
        assert iib1.identifier == "_2NXr8Fx3EeWfxsy-c6nRWw"
        assert iib1.name == "20150916-0836"
        assert iib1.created == "2015-09-16T13:35:51.342Z"
        assert iib1.started == "2015-09-16T13:36:01.122Z"
        assert iib1.ended == "2015-09-16T13:43:20.183Z"
        assert iib1.reason == "MANUAL"
        assert iib1.state == "COMPLETED"
        assert iib1.verdict == "OK"
        assert iib1.subject is None

        # fake data
        assert iib1.plan == ("http://test.url:9443/jazz/oslc/automation/"
                             "plans/_-xFK4AH0EeSgb7B1Epikyg")
        assert iib1.creator == ("http://test.url:9443/jazz/oslc/automation/"
                                "persons/_Ult00OjfEd6dKb6PaBIgvQ")
        assert iib1.contributions == ("http://test.url:9443/jazz/oslc/"
                                      "automation/results/"
                                      "_2NXr8Fx3EeWfxsy-c6nRWw/contributions")

        # IncludedInBuild2
        iib2_url = ("http://test.url:9443/jazz/resource/itemOid/"
                    "com.ibm.team.build.BuildResult/_b0KuAFuPEeWfxsy-c6nRWw")
        iib2 = IncludedInBuild(iib2_url,
                               myrtcclient,
                               raw_data=utils_test.includedinbuild2)
        assert iib2.url == iib2_url
        assert iib2.identifier == "_b0KuAFuPEeWfxsy-c6nRWw"
        assert iib2.name == "20150915-0452"
        assert iib2.created == "2015-09-15T09:52:10.975Z"
        assert iib2.started == "2015-09-15T09:52:19.544Z"
        assert iib2.ended == "2015-09-15T10:03:05.743Z"
        assert iib2.reason == "MANUAL"
        assert iib2.state == "COMPLETED"
        assert iib2.verdict == "OK"
        assert iib2.subject is None

        # fake data
        assert iib2.plan == ("http://test.url:9443/jazz/oslc/automation/"
                             "plans/_0-o5QJ4DEeOwXZhplBr4Rw")
        assert iib2.creator == ("http://test.url:9443/jazz/oslc/automation/"
                                "persons/_mYwwQGA5EeKE8fx0mWPe-A")
        assert iib2.contributions == ("http://test.url:9443/jazz/oslc/"
                                      "automation/results/"
                                      "_b0KuAFuPEeWfxsy-c6nRWw/contributions")

        iibs = workitem1.getIncludedInBuilds()
        assert iibs == [iib1, iib2]

    @pytest.fixture
    def mock_get_children(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("children.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_children(self, myrtcclient, mock_get_children, workitem1):
        # chidlren1
        children1 = Workitem("http://test.url:9443/jazz/oslc/workitems/142990",
                             myrtcclient,
                             workitem_id=142990,
                             raw_data=utils_test.children1)

        # chidlren2
        children2 = Workitem("http://test.url:9443/jazz/oslc/workitems/142989",
                             myrtcclient,
                             workitem_id=142989,
                             raw_data=utils_test.children1)

        children = workitem1.getChildren()
        assert children == [children1, children2]

    @pytest.fixture
    def mock_get_parent(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("parent.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_parent(self, myrtcclient, mock_get_parent, workitem1):
        # parent
        parent = Workitem("http://test.url:9443/jazz/oslc/workitems/141872",
                          myrtcclient,
                          workitem_id=141872,
                          raw_data=utils_test.parent)

        assert workitem1.getParent() == parent

    @pytest.fixture
    def mock_get_changesets(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("changesets.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_changesets(self, myrtcclient, mock_get_changesets, workitem1):
        # changeset1
        changeset1_url = ("http://test.url:9443/jazz/resource/itemOid/"
                          "com.ibm.team.scm.ChangeSet/"
                          "_VAjiUGHIEeWDLNtG9052Dw")
        changeset1 = ChangeSet(changeset1_url,
                               myrtcclient,
                               raw_data=utils_test.changeset1)

        assert changeset1.url == changeset1_url
        assert str(changeset1) == ("Changes 1 - Comment 1 - User1 - "
                                   "Sep 23, 2015 2:54 AM")

        # changeset2
        changeset2_url = ("http://test.url:9443/jazz/resource/itemOid/"
                          "com.ibm.team.scm.ChangeSet/"
                          "_aVKuMGHWEeWDLNtG9052Dw")
        changeset2 = ChangeSet(changeset2_url,
                               myrtcclient,
                               raw_data=utils_test.changeset2)

        # changeset3
        changeset3_url = ("http://test.url:9443/jazz/resource/itemOid/"
                          "com.ibm.team.scm.ChangeSet/"
                          "_nBUMsF0gEeWfxsy-c6nRWw")
        changeset3 = ChangeSet(changeset3_url,
                               myrtcclient,
                               raw_data=utils_test.changeset3)

        changesets = workitem1.getChangeSets()
        assert changesets == [changeset1, changeset2, changeset3]

    def test_add_attachment(self, myrtcclient, mocker, workitem1):
        # TODO: add attachment test
        pass

    @pytest.fixture
    def mock_get_attachments(self, mocker):
        mocked_get = mocker.patch("requests.get")
        mock_resp = mocker.MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.content = utils_test.read_fixture("attachment.xml")
        mocked_get.return_value = mock_resp
        return mocked_get

    def test_get_attachments(self, myrtcclient, mock_get_attachments,
                             workitem1):
        # Attachment1
        attachment1_url = ("http://test.url:9443/ccm/resource/itemOid/"
                           "com.ibm.team.workitem.Attachment/"
                           "_bsU_gTk1EeeUpchvxQKZYg")
        attachment1 = Attachment(attachment1_url,
                                 myrtcclient,
                                 raw_data=utils_test.attachment1)
        assert attachment1.identifier == "22"
        assert str(attachment1) == "22: cgobench1.go"
        assert attachment1.title == "cgobench1.go"
        assert attachment1.description == "cgobench1.go"
        assert attachment1.contentLength == "351"
        assert attachment1.created == "2017-05-15T06:12:11.264Z"
        assert attachment1.creator == "tester1"
        assert attachment1.modified == "2017-05-15T06:12:11.440Z"
        assert attachment1.content == ("http://test.url:9443/ccm/resource/"
                                       "content/_bsRVIDk1EeeUpchvxQKZYg")

        # Attachment2
        attachment2_url = ("http://test.url:9443/ccm/resource/itemOid/"
                           "com.ibm.team.workitem.Attachment/"
                           "_yUgkwTkeEeeUpchvxQKZYg")
        attachment2 = Attachment(attachment2_url,
                                 myrtcclient,
                                 raw_data=utils_test.attachment2)
        assert attachment2.identifier == "21"
        assert str(attachment2) == "21: cgobench2.go"
        assert attachment2.title == "cgobench2.go"
        assert attachment2.description == "cgobench2.go"
        assert attachment2.contentLength == "351"
        assert attachment2.created == "2017-05-15T03:30:04.686Z"
        assert attachment2.creator == "tester2"
        assert attachment2.modified == "2017-05-15T03:30:04.690Z"
        assert attachment2.content == ("http://test.url:9443/ccm/resource/"
                                       "content/_yUfWoDkeEeeUpchvxQKZYg")

        attachements = workitem1.getAttachments()
        assert attachements == [attachment1, attachment2]

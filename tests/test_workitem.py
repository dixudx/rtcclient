import requests
import pytest
import utils_test
from rtcclient.exception import BadValue, NotFound
from rtcclient.workitem import Workitem
from rtcclient.models import Comment, Action, State


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

    def test_get_comments(self, myrtcclient, mock_get_comments,
                          workitem1):
        # Comment1
        comment1_url = "/".join(["http://test.url:9443/jazz/oslc",
                                 "workitems/161/rtc_cm:comments/0"])
        comment1 = Comment(comment1_url,
                           myrtcclient,
                           raw_data=utils_test.comment1)
        assert comment1.id == "0"
        assert str(comment1) == "0"
        assert comment1.created == "2015-07-27T02:35:47.391Z"
        assert comment1.creator == "tester1@email.com"
        assert comment1.description == "comment test"

        # Comment2
        comment2_url = "/".join(["http://test.url:9443/jazz/oslc",
                                 "workitems/161/rtc_cm:comments/1"])
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

    def test_get_comment(self, myrtcclient, mock_get_comments,
                         workitem1):
        # test for invalid comment id
        invalid_comment_ids = ["", None, True, False, "test"]
        for invalid_comment_id in invalid_comment_ids:
            with pytest.raises(BadValue):
                workitem1.getCommentByID(invalid_comment_id)

        # test for valid comment id
        # Comment1
        comment1_url = "/".join(["http://test.url:9443/jazz/oslc",
                                 "workitems/161/rtc_cm:comments/0"])
        comment1 = Comment(comment1_url,
                           myrtcclient,
                           raw_data=utils_test.comment1)

        # Comment2
        comment2_url = "/".join(["http://test.url:9443/jazz/oslc",
                                 "workitems/161/rtc_cm:comments/1"])
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

    def test_get_actions(self, myrtcclient, mock_get_actions,
                         workitem1):
        # Action1
        action1_url = "/".join(["http://test.url:9443/jazz/oslc/workflows",
                                "_CuZu0HUwEeKicpXBddtqNA/actions",
                                "default_workflow/default_workflow.action.a1"])
        action1 = Action(action1_url,
                         myrtcclient,
                         raw_data=utils_test.action1)
        assert str(action1) == "Close"
        assert action1.title == "Close"
        assert action1.identifier == "default_workflow.action.a1"
        # fake data: pls ignore these values
        assert action1.resultState == ["Close", "Start Working"]

        # Action2
        action2_url = "/".join(["http://test.url:9443/jazz/oslc/workflows",
                                "_CuZu0HUwEeKicpXBddtqNA/actions",
                                "default_workflow/default_workflow.action.a2"])
        action2 = Action(action2_url,
                         myrtcclient,
                         raw_data=utils_test.action2)
        assert str(action2) == "Start Working"
        assert action2.title == "Start Working"
        assert action2.identifier == "default_workflow.action.a2"
        # fake data: pls ignore these values
        assert action2.resultState == ["Close", "Start Working"]

        actions = workitem1.getActions()
        assert actions == [action1, action2]

    def get_test_action(self, myrtcclient, mock_get_actions,
                        workitem1):
        # test for invalid name
        invalid_action_names = ["", u"", None, True, False]
        for invalid_action_name in invalid_action_names:
            with pytest.raises(BadValue):
                workitem1.getAction(invalid_action_name)

        # Action1
        action1_url = "/".join(["http://test.url:9443/jazz/oslc/workflows",
                                "_CuZu0HUwEeKicpXBddtqNA/actions",
                                "default_workflow/default_workflow.action.a1"])
        action1 = Action(action1_url,
                         myrtcclient,
                         raw_data=utils_test.action1)

        # Action2
        action2_url = "/".join(["http://test.url:9443/jazz/oslc/workflows",
                                "_CuZu0HUwEeKicpXBddtqNA/actions",
                                "default_workflow/default_workflow.action.a2"])
        action2 = Action(action2_url,
                         myrtcclient,
                         raw_data=utils_test.action2)

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

    def test_get_states(self, myrtcclient, mock_get_states,
                        workitem1):
        # State1
        state1_url = "/".join(["http://test.url:9443/jazz/oslc/workflows",
                                "_CuZu0HUwEeKicpXBddtqNA/states",
                                "default_workflow/default_workflow.state.s1"])
        state1 = State(state1_url,
                       myrtcclient,
                       raw_data=utils_test.state1)
        assert str(state1) == "Closed"
        assert state1.title == "Closed"
        assert state1.identifier == "default_workflow.state.s1"
        assert state1.group == "inprogress"

        # State2
        state2_url = "/".join(["http://test.url:9443/jazz/oslc/workflows",
                                "_CuZu0HUwEeKicpXBddtqNA/states",
                                "default_workflow/default_workflow.state.s2"])
        state2 = State(state2_url,
                       myrtcclient,
                       raw_data=utils_test.state2)
        assert str(state2) == "In Progress"
        assert state2.title == "In Progress"
        assert state2.identifier == "default_workflow.state.s2"
        assert state2.group == "closed"

        states = workitem1.getStates()
        assert states == [state1, state2]

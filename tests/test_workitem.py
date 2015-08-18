import requests
import pytest
import utils_test
from rtcclient.exception import BadValue, NotFound
from rtcclient.workitem import Workitem
from rtcclient.models import Comment, Action


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

        comment = workitem1.getCommentByID(0)
        assert comment == comment1

        comment = workitem1.getCommentByID(1)
        assert comment == comment2

        comment = workitem1.getCommentByID("0")
        assert comment == comment1

        comment = workitem1.getCommentByID("1")
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
        invalid_action_names = ["", None, True, False]
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
        action = workitem1.getAction("Close")
        assert action == action1

        # test for valid name
        action = workitem1.getAction("Start Working")
        assert action == action2

        # test for fake name
        with pytest.raises(NotFound):
            workitem1.getAction("Fake_Action")

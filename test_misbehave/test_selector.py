from unittest import mock

import misbehave.selector as selector
from misbehave.common import State

from test_misbehave.utils import Actor


def test_base_selector_instance():
    node = selector.BaseSelector(lambda a, c: State.SUCCESS, lambda a, c: State.SUCCESS)
    assert isinstance(node, selector.BaseSelector)


def test_concurrent_selector_success():
    behavior_1: mock.Mock = mock.Mock(return_value=State.SUCCESS)
    behavior_2:mock.Mock = mock.Mock(return_value=State.SUCCESS)

    tree = selector.Concurrent(behavior_1, behavior_2)

    result = tree(Actor(), None)
    assert result is State.SUCCESS
    behavior_1.assert_called()
    behavior_2.assert_called()

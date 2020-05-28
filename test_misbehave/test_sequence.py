import misbehave.selector as selector
from misbehave.common import State


def test_base_selector_instance():
    node = selector.BaseSelector(lambda a, c: State.SUCCESS, lambda a, c: State.SUCCESS)
    assert isinstance(node, selector.BaseSelector)

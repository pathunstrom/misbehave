from misbehave import action
from misbehave.common import State


def test_action_idle():
    node = action.Idle()

    class Actor: pass

    assert node(Actor(), None) is State.RUNNING

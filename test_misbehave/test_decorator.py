import misbehave.decorator as decorator
from misbehave.common import State


def test_base_decorator():
    node = decorator.Decorator(lambda a, c: State.SUCCESS)
    assert isinstance(node, decorator.Decorator)

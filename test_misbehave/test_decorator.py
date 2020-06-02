import misbehave.decorator as decorator
from misbehave.common import State


def test_base_decorator():
    node = decorator.Decorator(lambda a, c: State.SUCCESS)
    assert isinstance(node, decorator.Decorator)


def test_debounce():

    times = (x for x in range(5))

    def timer():
        return next(times)

    tree = decorator.Debounce(lambda a, c: State.SUCCESS, delay=1.5, timer=timer)

    class Actor:
        pass

    test_actor = Actor()

    result = tree(test_actor, None)
    assert result is State.SUCCESS

    result = tree(test_actor, None)
    assert result is State.FAILED

    result = tree(test_actor, None)
    assert result is State.SUCCESS

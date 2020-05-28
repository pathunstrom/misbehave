from time import perf_counter
from typing import Any, AnyStr, Callable

from misbehave.common import BaseNode, State


class CheckValue(BaseNode):
    """
    Checks that an actor has the given attribute and it's Truthy.
    """

    def __init__(self, attribute_name: AnyStr):
        self.attribute_name = attribute_name

    def __call__(self, actor: Any, context: Any) -> State:
        val = getattr(actor, self.attribute_name, None)
        if val:
            return State.SUCCESS
        return State.FAILED


class SetCurrentTime(BaseNode):
    """
    Set the current time at a given attribute name.
    """

    def __init__(self, attribute_name, timer: Callable[[], float] = perf_counter):
        self.attribute_name = attribute_name
        self.timer = timer

    def __call__(self, actor: Any, context: Any) -> State:
        setattr(actor, self.attribute_name, self.timer())
        return State.SUCCESS


class SetValue(BaseNode):
    """
    Set a value to the given attribute_name
    """

    def __init__(self, attribute_name, value):
        self.attribute_name = attribute_name
        self.value = value

    def __call__(self, actor: Any, context: Any) -> State:
        setattr(actor, self.attribute_name, self.value)
        return State.SUCCESS


class Wait(BaseNode):
    """
    Do nothing for a delay.

    Must set the attribute in another action node.
    """

    def __init__(self, attribute_name, wait_time, timer=perf_counter):
        self.attribute_name = attribute_name
        self.wait_time = wait_time
        self.timer = timer

    def __call__(self, actor: Any, context: Any) -> State:
        start_time = getattr(actor, self.attribute_name)
        now = self.timer()
        if now >= start_time + self.wait_time:
            return State.SUCCESS
        return State.RUNNING


class Idle(BaseNode):
    """
    Do nothing for an arbitrarily long time.

    Good when used in conjunction with :class:`~misbehave.selector.Concurrent`
    """

    def __call__(self, actor: Any, context: Any) -> State:
        return State.RUNNING


class IncreaseValue(BaseNode):
    """
    Increase a numerical value at a given attribute by a value.

    Attribute must already exist.
    """

    def __init__(self, attribute_name, value=1):
        self.attribute_name = attribute_name
        self.value = value

    def __call__(self, actor: Any, context: Any) -> State:
        val = getattr(actor, self.attribute_name)
        val += self.value
        setattr(actor, self.attribute_name, val)
        return State.SUCCESS

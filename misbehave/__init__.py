from time import perf_counter
from typing import Any, List





class CheckValue(Node):
    """
    Checks that an actor has the attribute and it's Truthy.
    """
    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def visit(self, actor: Any, context: Any) -> State:
        val = getattr(actor, self.attribute_name, None)
        if val:
            return State.SUCCESS
        return State.FAILED


class SetCurrentTime(Node):

    def __init__(self, attribute_name, timer=perf_counter):
        self.attribute_name = attribute_name
        self.timer = timer

    def visit(self, actor: Any, context: Any) -> State:
        setattr(actor, self.attribute_name, self.timer())
        return State.SUCCESS


class SetValue(Node):

    def __init__(self, attribute_name, value):
        self.attribute_name = attribute_name
        self.value = value

    def visit(self, actor: Any, context: Any) -> State:
        setattr(actor, self.attribute_name, self.value)
        return State.SUCCESS


class Wait(Node):
    """
    Must set the attribute in another action node.
    """
    def __init__(self, attribute_name, wait_time, timer=perf_counter):
        self.attribute_name = attribute_name
        self.wait_time = wait_time
        self.timer = timer

    def visit(self, actor: Any, context: Any) -> State:
        start_time = getattr(actor, self.attribute_name)
        now = self.timer()
        if now >= start_time + self.wait_time:
            return State.SUCCESS
        return State.RUNNING


class Idle(Node):

    def visit(self, actor: Any, context: Any) -> State:
        return State.RUNNING


class IncreaseValue(Node):

    def __init__(self, attribute_name, value=1):
        self.attribute_name = attribute_name
        self.value = value

    def visit(self, actor: Any, context: Any) -> State:
        val = getattr(actor, self.attribute_name)
        val += self.value
        setattr(actor, self.attribute_name, val)
        return State.SUCCESS

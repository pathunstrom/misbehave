from time import perf_counter
from typing import Any, List


class Decorator(Node):
    """
    Adds functionality similarly to a decorator function.

    Subclass and do work before and after the call.
    """
    def __init__(self, child, **_):
        self.child = child

    def visit(self, actor: Any, context: Any) -> State:
        return self.child.visit(actor, context)

    def reset(self):
        self.state = State.READY
        self.child.reset()


class Inverter(Decorator):
    """
    Changes Success to Failure and vice versa
    """

    def visit(self, actor: Any, context: Any) -> State:
        result = super().visit(actor, context)
        if result is State.SUCCESS:
            return State.FAILED
        elif result is State.FAILED:
            return State.SUCCESS
        else:
            return result


class ThrowEventOnSuccess(Decorator):

    def __init__(self, child, *, event_type, get_event_params):
        super().__init__(child)
        self.event_type = event_type
        self.get_event_params = get_event_params

    def visit(self, actor: Any, context: Any) -> State:
        result = self.child.visit(actor, context)
        if result is State.SUCCESS:
            context.signal(self.event_type(*self.get_event_params(actor)))
        return result


class Debounce(Decorator):

    def __init__(self, child, *, cool_down=0.5, timer=perf_counter):
        super().__init__(child)
        self.cool_down = cool_down
        self.timer = timer
        self.attr = f"debounce_{id(self)}_last"

    def visit(self, actor: Any, context: Any) -> State:
        if self.timer() <= getattr(actor, self.attr, -10) + self.cool_down:
            return State.FAILED
        result = self.child.visit(actor, context)
        if result is State.SUCCESS:
            setattr(actor, self.attr, self.timer())
        return result


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

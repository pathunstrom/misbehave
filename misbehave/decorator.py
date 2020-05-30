from time import perf_counter
from typing import Any

from misbehave.common import BaseNode, State


__all__ = ["Decorator", "Debounce", "Inverter"]


class Decorator(BaseNode):
    """
    Adds functionality similarly to a decorator function.

    Subclass and do work before or after the call.
    """

    def __init__(self, child, **_):
        self.child = child

    def __call__(self, actor: Any, context: Any) -> State:
        return self.child.visit(actor, context)


class Inverter(Decorator):
    """
    Changes Success to Failure and vice versa
    """

    def __call__(self, actor: Any, context: Any) -> State:
        result = super().__call__(actor, context)
        if result is State.SUCCESS:
            return State.FAILED
        elif result is State.FAILED:
            return State.SUCCESS
        else:
            return result


class Debounce(Decorator):
    """
    If child node is successful, only run again after a delay.
    """

    def __init__(self, child, *, delay=0.5, timer=perf_counter):
        super().__init__(child)
        self.cool_down = delay
        self.timer = timer
        self.attr = f"debounce_{id(self)}_last"

    def __call__(self, actor: Any, context: Any) -> State:
        if self.timer() <= getattr(actor, self.attr, -10) + self.cool_down:
            return State.FAILED
        result = self.child.visit(actor, context)
        if result is State.SUCCESS:
            setattr(actor, self.attr, self.timer())
        return result

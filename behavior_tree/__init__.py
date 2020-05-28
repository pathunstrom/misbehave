from dataclasses import dataclass
from enum import Enum, auto
from time import perf_counter
from typing import Any, Callable, List

import ppb


@dataclass
class Context:
    scene: ppb.BaseScene
    event: ppb.events.Update  # TODO: Figure out if this is the right type hint
    signal: Callable[[Any], None]


class State(Enum):
    READY = auto()
    SUCCESS = auto()
    RUNNING = auto()
    FAILED = auto()
    ERROR = auto()


class Node:
    state: State = State.READY

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        return State.SUCCESS

    def reset(self):
        self.state = State.READY

    def __repr__(self):
        values = []
        for k, v in vars(self).items():
            if isinstance(v, Node):
                v = f"{type(v).__name__}(...)"
            values.append(f"{k}={v}")
        return f"{type(self).__name__}({', '.join(values)})"


class Selector(Node):
    stop_states: List[State]
    final_state: State
    continue_states: List[State] = [State.RUNNING]
    start: int = 0

    def __init__(self, *children: Node, **_):
        self.children = children

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        new_state = self.final_state
        i = 0
        for i, child in enumerate(self.children[self.start:], start=self.start):
            result = child.visit(actor, context)
            if result in self.stop_states:
                new_state = result
                break
        self.state = new_state
        self.start = i
        return self.state

    def reset(self):
        for child in self.children:
            child.reset()
        if self.state not in self.continue_states:
            self.start = 0
        super().reset()


class Priority(Selector):
    """
    Select the first running or successful behavior in order.
    """
    stop_states = [State.SUCCESS, State.RUNNING]
    final_state = State.FAILED


class Sequence(Selector):
    """
    Run behavior in sequence.
    """
    stop_states = [State.FAILED, State.RUNNING]
    final_state = State.SUCCESS


class Concurrent(Selector):
    """
    Run all behaviors. Bails on preferred # fails.
    """

    def __init__(self, *children, num_fail=1, **kwargs):
        super().__init__(*children, **kwargs)
        self.num_fail = num_fail

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        num_failed = 0
        states = []
        for child in self.children:
            states.append(child.visit(actor, context))
            if sum(1 for state in states if state is State.FAILED) >= self.num_fail:
                return State.FAILED
        if all(state == State.SUCCESS for state in states):
            return State.SUCCESS
        return State.RUNNING


class Decorator(Node):
    """
    Adds functionality similarly to a decorator function.

    Subclass and do work before and after the call.
    """
    def __init__(self, child, **_):
        self.child = child

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        return self.child.visit(actor, context)

    def reset(self):
        self.state = State.READY
        self.child.reset()


class Inverter(Decorator):
    """
    Changes Success to Failure and vice versa
    """

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
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

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
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

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
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

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        val = getattr(actor, self.attribute_name, None)
        if val:
            return State.SUCCESS
        return State.FAILED


class SetCurrentTime(Node):

    def __init__(self, attribute_name, timer=perf_counter):
        self.attribute_name = attribute_name
        self.timer = timer

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        setattr(actor, self.attribute_name, self.timer())
        return State.SUCCESS


class SetValue(Node):

    def __init__(self, attribute_name, value):
        self.attribute_name = attribute_name
        self.value = value

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
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

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        start_time = getattr(actor, self.attribute_name)
        now = self.timer()
        if now >= start_time + self.wait_time:
            return State.SUCCESS
        return State.RUNNING


class Idle(Node):

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        return State.RUNNING


class IncreaseValue(Node):

    def __init__(self, attribute_name, value=1):
        self.attribute_name = attribute_name
        self.value = value

    def visit(self, actor: 'BehaviorMixin', context: Context) -> State:
        val = getattr(actor, self.attribute_name)
        val += self.value
        setattr(actor, self.attribute_name, val)
        return State.SUCCESS


class BlackBoard:
    pass


class BehaviorMixin(ppb.sprites.BaseSprite):
    behavior_tree: Node

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_update(self, event: ppb.events.Update, signal: Callable[[Any], None]):
        self.behavior_tree.reset()
        self.behavior_tree.visit(self, Context(event.scene, event, signal))

from typing import Any, List

from misbehave.common import BaseNode, State


__all__ = ["Concurrent", "Priority", "Sequence"]


class BaseSelector(BaseNode):
    """
    A node with multiple children.
    """

    def __init__(self, *children: BaseNode):
        self.children = children

    def reset(self, actor):
        for child in self.children:
            try:
                child.reset(actor)
            except AttributeError:
                pass


class Concurrent(BaseSelector):
    """
    Run all behaviors, failing early upon reaching a certain number of failures.
    """

    def __init__(self, *children: BaseNode, num_fail: int = 1):
        """
        :param children: Behavior nodes.
        :param num_fail: The number of possible failures from children nodes.
        """
        super().__init__(*children)
        self.num_fail = num_fail

    def __call__(self, actor: Any, context: Any) -> State:
        states = []
        for child in self.children:
            states.append(child(actor, context))
            if sum(1 for state in states if state is State.FAILED) >= self.num_fail:
                return State.FAILED
        if all(state == State.SUCCESS for state in states):
            return State.SUCCESS
        return State.RUNNING


class ContinuableSelector(BaseSelector):
    """
    A node that can resume where it left off.
    """

    stop_states: List[State]
    final_state: State
    continue_states: List[State] = [State.RUNNING]

    def __init__(self, *children):
        super().__init__(*children)
        self.continue_attr = f"{type(self).__name__}_{id(self)}_start"

    def __call__(self, actor: Any, context: Any) -> State:
        new_state = self.final_state
        i = 0
        start = getattr(actor, self.continue_attr, 0)
        for i, child in enumerate(self.children[start:], start=start):
            result = child(actor, context)
            if result in self.stop_states:
                new_state = result
                break
        if i == len(self.children) - 1:
            i = 0
        if new_state in self.continue_states:
            setattr(actor, self.continue_attr, i)
        else:
            setattr(actor, self.continue_attr, 0)

        if new_state is not State.RUNNING:
            self.reset(actor)

        return new_state

    def reset(self, actor):
        super().reset(actor)
        setattr(actor, self.continue_attr, 0)


class Priority(ContinuableSelector):
    """
    Select the first running or successful behavior in order.
    """

    stop_states = [State.SUCCESS, State.RUNNING]
    final_state = State.FAILED


class Sequence(ContinuableSelector):
    """
    Run behavior in sequence.
    """

    stop_states = [State.FAILED, State.RUNNING]
    final_state = State.SUCCESS

from enum import Enum, auto
from typing import Any


__all__ = ["BaseNode", "State"]


class State(Enum):
    READY = auto()
    SUCCESS = auto()
    RUNNING = auto()
    FAILED = auto()
    ERROR = auto()


def is_node_function(node: Any):
    """
    Check if an arbitrary object is a Node.

    If it looks like a Node, it's a Node. A node is a Callable that accepts
    two parameters: An actor and a context.

    :param node: The callable to check.
    :type node: Any
    :return: bool
    """
    if not callable(node):
        return False
    from inspect import signature

    sig = signature(node)
    if len(sig.parameters) != 2:
        return False
    return True


class BaseNode:
    """
    A Basic Node.
    """

    def __call__(self, actor: Any, context: Any) -> State:
        """
        Perform an action.

        BaseNode only returns :class:`Success <State>`.

        :param actor: The object that this tree is controlling.
        :param context: A context object, intended to hold world state.
        :return:
        """
        return State.SUCCESS

    def __repr__(self):
        values = []
        for k, v in vars(self).items():
            if isinstance(v, BaseNode) or is_node_function(v):
                v = f"{type(v).__name__}(...)"
            values.append(f"{k}={v}")
        return f"{type(self).__name__}({', '.join(values)})"

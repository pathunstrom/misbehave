"""
Behavior trees for Python.

The best way to think of behavior trees is as the building blocks of complex
actions. In Misbehave, a tree is a callable that accepts an ``actor`` and
``context`` then returns a :class:`~misbehave.common.State`. Each node in the
tree needs to match this signature. For simple behaviors, these can be defined
as functions. For more complex ones, you may need to prove some parameters to
your behaviors via closures.

When you call the root node on a tree, it is traversed depth first until it
reaches a stopping condition. You should read about the various
:mod:`selectors <~misbehave.selector>` for what a stopping condition looks like.

As the tree is traversed various :mod:`~misbehave.action` nodes will change
state on your ``actor`` object. When any node is complete, it returns one of
three :class:`states <~misbehave.common.State>`: ``SUCCESS``, ``RUNNING`` or
``FAILED``. A ``FAILED`` result performed no actions, a `RUNNING` result means
a particular action was started, but had not completed, and a `SUCCESS` result
means that whichever behavior was performed finished.

See the individual modules for more details on the included nodes.

Exports:

* :class:`~misbehave.common.BaseNode`
* :class:`~misbehave.common.State`
* :mod:`~misbehave.action`
* :mod:`~misbehave.decorator`
* :mod:`~misbehave.selector`
* :data:`~misbehave.version.version`
"""

from misbehave import action
from misbehave import decorator
from misbehave import selector
from misbehave.common import *
from misbehave.version import version

__all__ = [BaseNode, State, action, decorator, selector, version]

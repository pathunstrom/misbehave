Getting Started
=====================================

Misbehave does little on its own, and is best used as a dependency for a game
project that you're working on. To start, you'll want to add it to your
dependency list in requirements.txt:

.. code-block::
   :caption: requirements.txt

   misbehave

And then install it into your virtual environment

.. code-block::

   (.venv)$ python -m pip install -r requirements.txt

Once you've set that up, you can define your tree like so:

.. code-block:: python

   import misbehave

   import my_actions

   tree = misbehave.selector.Sequence(
       misbehave.action.IncreaseValue("behavior_tree_runs"),
       my_actions.MoveForward(10),
       my_actions.Rotate(90)
   )

   running = True
   while running:
       tree(my_actor, None)

This simplified example demonstrates the basic usage:

You combine selectors with your own action and decorator nodes to produce a
tree structure. Then, each tick (or some number of ticks) through your main loop
you pass in the object the tree controls, and a context object (which is
``None`` here.)

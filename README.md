# misbehave

Misbehave is a Python behavior tree implementation. A behavior tree is a design
pattern that breaks complex state-based actions into their component parts to
improve readability and re-usability for autonomous agents. A good starting
place to understand them is [here]](https://www.gamasutra.com/blogs/ChrisSimpson/20140717/221339/Behavior_trees_for_AI_How_they_work.php).

Misbehave focused on python language features not available in other languages,
so some of the common features of AI design are missing by default. The rest of
this document is lightly hedged in its language as behavior trees can be useful
for video games or robots.

## How to use Misbehave

A node in a Misbehave behavior tree is simply a callable. While the ones
provided with this library are classes, you can use functions or closures to
define them.

The signature of a node's function is simple:

    def MyNode(actor: Any, context: Any) -> misbehave.State
        # Perform actions here.

An actor is an object representing the thing the behavior tree is controlling.
In a video game, this would be the mob object.

The context is available for providing access to things like sensors, controls,
other code objects representing things in space. If you don't need them, you can
pass None here.

An example of a tree might look like this in your code:

    class MyActor():
        tree = misbehave.selector.Sequence(
            misbehave.action.IncreaseValue("behavior_tree_runs"),
            my_actions.MoveForward(10),
            my_actions.Rotate(90)
        )
        behavior_tree_runs = 0

This simple tree keeps track of how many times the entire tree was run, and then
moves the actor in a square. You must implement the specifics of the actions
here.

## Development

Misbehave requires Python 3.6 or later.

To work on misbehave, after forking and cloning locally, you'll want to setup
a virtual environment. You'll notice we don't have any requirement files: all
requirements are listed in setup.cfg either as setup_requires or as extras.

In your project directory, with your virtual environment active:

    python -m pip install -e .[dev, tests]

If you do not do an editable install of misbehave, `misbehave.version` will be
missing and the library will fail to work.

Other than that, we are ready for PEP 518 and 517, so if you're using a build
tool that supports them, feel free!

It is strongly encouraged that you run `black` on the misbehave directory and
then `pytest` before commiting to any working branch. Failure to lint will
disqualify a PR.

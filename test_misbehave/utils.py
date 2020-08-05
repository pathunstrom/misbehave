from misbehave import BaseNode, State


class Actor:
    pass


def FailIfRun(actor, context):
    assert False, "FailIfRun ran."


class RunThenSucceed(BaseNode):

    def __call__(self, actor, context):
        run_once = getattr(actor, "run_once", False)
        if run_once:
            return State.SUCCESS
        actor.run_once = True
        return State.RUNNING

    def reset(self, actor):
        actor.run_once = False


def run_only_once(
        state: State = State.SUCCESS,
        message: str = "run_only_once called twice."
):
    run_once = False

    def function(_, __):
        nonlocal run_once
        if run_once:
            assert False, message
        run_once = True
        return state

    function.__name__ = run_only_once.__name__
    return function

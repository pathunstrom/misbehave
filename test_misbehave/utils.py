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

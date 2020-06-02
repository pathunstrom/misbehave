from unittest import mock

import misbehave

from test_misbehave.utils import Actor, FailIfRun, RunThenSucceed


def test_reset_on_success():
    actor = Actor()
    mock_behavior = mock.Mock(return_value=misbehave.State.SUCCESS)

    tree = misbehave.selector.Priority(
        misbehave.selector.Sequence(
            misbehave.action.CheckValue("priority_action"),
            mock_behavior,
            misbehave.action.SetValue("priority_action", False)
        ),
        misbehave.selector.Concurrent(
            misbehave.decorator.Inverter(
                misbehave.action.CheckValue("priority_action")
            ),
            misbehave.selector.Sequence(
                misbehave.action.SetValue("priority_action", True),
                RunThenSucceed(),
                FailIfRun,
            )
        )
    )

    result = tree(actor, None)
    assert result is misbehave.State.RUNNING

    result = tree(actor, None)
    assert result is misbehave.State.SUCCESS

    result = tree(actor, None)
    assert result is misbehave.State.RUNNING

    result = tree(actor, None)
    assert result is misbehave.State.SUCCESS

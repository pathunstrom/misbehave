import misbehave.common as common


def test_is_node_function():
    assert common.is_node_function(lambda a, c: common.State.SUCCESS)

import pytest

def test_0(solver, dimension, expected):
    result = solver.solve()

    assert isinstance(result, list)
    assert len(result) == (dimension ** 2)
    assert all(isinstance(r, list) for r in result)
    assert all(len(r) == (dimension ** 2) for r in result)

    print(result)

    # for index, row in enumerate(result):
        # assert row == expected[index]

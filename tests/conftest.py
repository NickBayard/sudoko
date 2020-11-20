import pytest
from sudoku import Sudoku


@pytest.fixture
def dimension():
    return 3

@pytest.fixture
def game_array():
    return [(0, 3, 2),
            (0, 8, 8),
            (1, 0, 1),
            (1, 2, 9),
            (1, 7, 6),
            (2, 1, 2),
            (2, 5, 9),
            (2, 8, 3),
            (3, 0, 2),
            (3, 1, 7),
            (3, 3, 4),
            (4, 0, 6),
            (4, 1, 5),
            (4, 4, 8),
            (5, 0, 8),
            (5, 6, 3),
            (6, 3, 8),
            (6, 5, 4),
            (6, 6, 7),
            (6, 8, 1),
            (7, 1, 1),
            (7, 4, 2),
            (8, 0, 5),
            (8, 4, 6),
            (8, 8, 9),
            ]

@pytest.fixture
def expected():
    return [
            [3, 6, 5, 2, 4, 7, 1 ,9, 8],
            [1, 4, 9, 5, 3, 8, 2, 6, 7],
            [7, 2, 8, 6, 1, 9, 5, 4, 3],
            [2, 7, 3, 4, 9, 5, 8, 1, 6],
            [6, 5, 1, 3, 8, 2, 9, 7, 4],
            [8, 9, 4, 1, 7, 6, 3, 5, 2],
            [9, 3, 6, 8, 5, 4, 7, 2, 1],
            [4, 1, 7, 9, 2, 3, 6, 8, 5],
            [5, 8, 2, 7, 6, 1, 4, 3, 9]
           ]



@pytest.fixture
def solver(dimension, game_array):
    return Sudoku(dimension, game_array)

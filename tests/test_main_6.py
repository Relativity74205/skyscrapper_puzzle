import pytest

from main import *


@pytest.fixture
def ss_grid():
    sg = SkyscraperGrid(clues=[3, 2, 2, 3, 2, 1, 1, 2, 3, 3, 2, 2, 5, 1, 2, 2, 4, 3, 3, 2, 1, 2, 2, 4],
                        grid_dimension=6)
    return sg


@pytest.mark.parametrize("test_input, expected", [
    (0, ('col', 0, False)),
    (6, ('row', 0, True)),
    (11, ('row', 5, True)),
    (12, ('col', 5, True)),
    (17, ('col', 0, True)),
    (18, ('row', 5, False))
])
def test_get_column(ss_grid, test_input, expected):
    assert ss_grid.get_column(test_input) == expected


@pytest.mark.parametrize("test_input1, test_input2, test_input3, expected", [
    ('col', 0, False, [2, [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]]),
    ('col', 3, False, [[2, 3], [1, 2, 3, 4, 5, 6], 3, [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]]),
    ('row', 0, False, [2, [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [2, 3], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]]),
    ('row', 0, True, [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [2, 3], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], 2]),
    ('row', 2, False, [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], 3, [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]])
])
def test_get_array(ss_grid, test_input1, test_input2, test_input3, expected):
    ss_grid.grid[0][0] = [2]
    ss_grid.grid[0][3] = [2, 3]
    ss_grid.grid[2][3] = [3]

    assert ss_grid.get_array(test_input1, test_input2, test_input3) == expected


def test_get_shortest_domain(ss_grid):
    grid = [[list(range(1, i*j)) for i in range(1, 5)] for j in range(1, 5)]
    ss_grid.grid = grid
    assert ss_grid.get_shortest_domain() == (0, 2)
    ss_grid.grid[0][2] = list(range(6))
    assert ss_grid.get_shortest_domain() == (2, 0)
    ss_grid.grid = [[[1] for _ in range(4)] for _ in range(4)]
    assert not ss_grid.get_shortest_domain()


@pytest.mark.parametrize("test_input, expected", [
    ([[1], [2], [3], [4]], 4),
    ([4, 3, 2, 1], 1),
    ([3, 6, 5, 2, 4, 1], 2),
    ([1, 4, 2, 5, 6, 3], 4),
    ([2, 3, 6, 1, 5, 4], 3),
    ([[1, 2], 2, 3, 4], 1),
    ([1, [1, 2], 3, 4], 1),
    ([1, 2, [3, 4], 4], 2),
    ([2, [1, 4], [3, 4], 4], 1),
    ([2, 3, 4, [1, 2]], 3),
    ([2, [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]], 1),
    ([4, [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]], 1)
])
def test_get_visible_buildings(ss_grid, test_input, expected):
    assert ss_grid.get_visible_buildings(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [
    ([1, 2, 3, 4, 5, 6], 6),
    ([6, 5, 4, 3, 2, 1], 1),
    ([1, [2, 3], [2, 3], 4, 5, 6], 6),
    ([5, [2, 3], [2, 3], 4, 1, 6], 2),
    ([2, [1, 3], [1, 3], 4, 5, 6], 5),
    ([4, 5, 6, [1, 2], [1, 2], [1, 2]], 3),
    ([5, 4, 6, [1, 2], [1, 2], [1, 2]], 2),
    ([3, [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]], 4),
    ([4, [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]], 3),
    ([5, [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]], 2),
    ([6, [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]], 1)
])
def test_get_max_visible_buildings(ss_grid, test_input, expected):
    assert ss_grid.get_max_visible_buildings(test_input) == expected


def test_clean_grid(ss_grid):
    assert ss_grid.clean_grid()
    ss_grid.grid[0][0] = [4]
    ss_grid.grid[0][1] = [1, 4]
    assert not ss_grid.clean_grid()
    ss_grid.grid[0][0] = [1]
    ss_grid.grid[0][1] = [1, 4]
    assert not ss_grid.clean_grid()


def test_process_point_1(ss_grid):
    ss_grid.grid[1][0] = [2]
    assert ss_grid.process_point([0, 0])
    assert ss_grid.grid[0][0] == [1]
    ss_grid.grid[2][0] = [3]
    assert ss_grid.process_point([0, 0])
    assert ss_grid.grid[0][0] == []


def test_add_neighbours(ss_grid):
    queue = deque()
    queue = ss_grid.add_neighbours([0, 0], queue)
    assert len(queue) == 6
    queue = deque()
    ss_grid.grid[0][1] = [2]
    queue.append([1, 0])
    queue = ss_grid.add_neighbours([0, 0], queue)
    assert len(queue) == 5


def test_violates_constraints(ss_grid):
    #assert not ss_grid.violates_constraints([1, 1], 2)
    ss_grid.grid[1][0] = [2]
    #assert ss_grid.violates_constraints([1, 1], 2)
    #assert not ss_grid.violates_constraints([1, 0], 2)
    ss_grid.grid[1][0] = [2]
    assert not ss_grid.violates_constraints([1, 1], 3)
    assert not ss_grid.violates_constraints([1, 1], 1)
    ss_grid.grid[1][0] = [3]
    assert not ss_grid.violates_constraints([1, 1], 2)
    ss_grid.grid[1][0] = [2, 3]
    assert not ss_grid.violates_constraints([1, 1], 2)
    ss_grid.grid[1][0] = [1]
    ss_grid.grid[1][2] = [3]
    assert ss_grid.violates_constraints([1, 1], 2)
    assert ss_grid.grid[1][1] == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("test_input1, test_input2, expected", [
    # ([1, 2, 3, 4, 5, 6], 6, False),
    # ([1, 2, 3, 4, 5, 6], 5, True),
    # ([1, 6, 3, 4, 5, 2], 2, False),
    # ([5, [1, 2], [1, 2], [1, 2], [1, 2], [1, 2]], 2, False),
    # ([[1, 2], 5, [1, 2], [1, 2], [1, 2], [1, 2]], 3, False),
    ([[1, 2], 5, [1, 2], [1, 2], [1, 2], [1, 2]], 2, True),
    ([[1, 2], 5, [1, 2], [1, 2], [1, 2], [1, 2]], 1, False),
    ([[1, 2], 5, [1, 2], [1, 2], [1, 2], [1, 2]], 4, True)
#[4, 3, [4, 6], 5, 2, 1], 3
])
def test_violates_constraints_array(ss_grid, test_input1, test_input2, expected):
    assert ss_grid.violates_constraints_array(test_input1, test_input2) == expected


@pytest.mark.parametrize("test_input1, test_input2, expected", [
    (0, 0, [0, 6, 17, 23]),
    (1, 2, [1, 8, 16, 21]),
    (3, 3, [3, 9, 14, 20])
])
def test_get_relevant_clues(ss_grid, test_input1, test_input2, expected):
    assert ss_grid.get_relevant_clues(test_input1, test_input2) == expected

from copy import deepcopy
from collections import deque
import cProfile

all_neighbour_points = {}


class SkyscraperGrid:
    def __init__(self, grid_dimension, clues):
        self.grid_dimension = grid_dimension
        self.clues = clues
        self.grid = None

        self.init_grid()
        self.set_neighbour_points()

    def init_grid(self):
        self.grid = [[list(range(1, self.grid_dimension + 1)) for _ in range(1, self.grid_dimension + 1)]
                     for _ in range(1, self.grid_dimension + 1)]

    def get_array(self, dim, i, reverse):
        if dim == 'col':
            arr = [row[i] for row in self.grid]
        else:
            arr = self.grid[i][:]

        if reverse:
            arr = arr[::-1]

        first_non_elemental = self.grid_dimension
        new_arr = []
        #new_arr = [ele[0] if len(ele) == 1 else ele for index, ele in enumerate(arr)]
        for index, ele in enumerate(arr):
            if len(ele) == 1:
                new_arr.append(ele[0])
            else:
                new_arr.append(ele)
                if first_non_elemental == self.grid_dimension:
                    first_non_elemental = index

        return new_arr, first_non_elemental

    def get_shortest_domain(self):
        xy = [(i, j, len(self.grid[i][j])) for i in range(self.grid_dimension) for j in range(self.grid_dimension)
              if len(self.grid[i][j]) >= 2]
        xy = sorted(xy, key=lambda x: x[2])

        if len(xy) == 0:
            return None
        else:
            return xy[0][0], xy[0][1]

    def set_neighbour_points(self):
        for i in range(self.grid_dimension):
            for j in range(self.grid_dimension):
                all_neighbour_points[(i, j)] = self.get_neighbour_points([i, j])

    def get_neighbour_points(self, p):
        neighbours = [[i, p[1]] for i in range(self.grid_dimension) if i != p[0]]
        neighbours = [[p[0], j] for j in range(self.grid_dimension) if j != p[1]] + neighbours

        return neighbours

    def add_neighbours(self, p, queue):
        # neighbours = self.get_neighbour_points()
        for i in range(self.grid_dimension):
            if i != p[0] and len(self.grid[i][p[1]]) > 1:
                if [i, p[1]] not in queue:
                    queue.append([i, p[1]])

        for i in range(self.grid_dimension):
            if i != p[1] and len(self.grid[p[0]][i]) > 1:
                if [p[0], i] not in queue:
                    queue.append([p[0], i])

        return queue

    def clean_grid(self, p=None, initial=False):
        if p is None:
            queue = deque()
            for i in range(self.grid_dimension):
                for j in range(self.grid_dimension):
                    if len(self.grid[i][j]) > 1:
                        queue.append([i, j])
        else:
            queue = self.add_neighbours(p, deque())

        while len(queue) > 0:
            p = queue.popleft()

            if self.process_point(p, initial=initial):
                if len(self.grid[p[0]][p[1]]) == 0:
                    return False
                if len(self.grid[p[0]][p[1]]) == 1:
                    queue = self.add_neighbours(p, queue)
        return True

    def process_point(self, p, initial=False):
        flag_changed = False
        to_remove = []
        for num in self.grid[p[0]][p[1]]:
            if self.violates_constraints(p, num, initial=initial):
                to_remove.append(num)
                flag_changed = True

        for num in to_remove:
            self.grid[p[0]][p[1]].remove(num)

        return flag_changed

    def violates_constraints(self, p, num, initial=False):
        for point in (point for point in all_neighbour_points[tuple(p)] if len(self.grid[point[0]][point[1]]) == 1):
            if self.grid[point[0]][point[1]][0] == num:
                return True

        clue_indizes = self.get_relevant_clues(p[1], p[0])

        old_val, self.grid[p[0]][p[1]] = self.grid[p[0]][p[1]], [num]
        for clue_index in clue_indizes:
            clue = self.clues[clue_index]
            if clue > 0:
                arr, first_non_elemental = self.get_array(*self.get_column(clue_index))

                if self.violates_constraints_array(arr, clue, first_non_elemental, initial=initial):
                    self.grid[p[0]][p[1]] = old_val
                    return True

        self.grid[p[0]][p[1]] = old_val

        return False

    def violates_constraints_array(self, arr, clue, first_non_elemental, initial=False):
        visible_buildings = self.get_visible_buildings(arr, first_non_elemental)
        if visible_buildings > clue or (visible_buildings != clue and first_non_elemental == self.grid_dimension):
            return True

        if initial:
            max_visible_buildings = self.get_max_visible_buildings(arr)
            if max_visible_buildings < clue:
                return True

        return False

    def get_relevant_clues(self, x, y):
        clue_indizes = list()
        clue_indizes.append(x)
        clue_indizes.append(y + self.grid_dimension)
        clue_indizes.append(3 * self.grid_dimension - x - 1)
        clue_indizes.append(4 * self.grid_dimension - y - 1)
        return clue_indizes

    @staticmethod
    def get_visible_buildings(arr, first_non_elemental):
        if arr[0] == 6:
            return 1

        clues = 0

        for i in range(first_non_elemental):
            if arr[i] >= max(arr[0:i] + [0]):
                clues += 1

        if clues == 0:
            clues = 1

        return clues

    def get_max_visible_buildings(self, arr, rec_level=0):
        max_height = (-1, 0)
        for i in range(len(arr)):
            if not isinstance(arr[i], list):
                if arr[i] >= max_height[1]:
                    max_height = (i, arr[i])

        max_visible = 1 + max_height[0] + (self.grid_dimension - rec_level - max_height[1])
        sub_arr = arr[:max_height[0]]
        if len(sub_arr) > 1:
            max_visible_sub_arr = self.get_max_visible_buildings(sub_arr, rec_level=rec_level + 1)
            if max_visible_sub_arr + 1 < max_visible:
                max_visible = max_visible_sub_arr + 1

        return max_visible

    def get_column(self, clue_index):
        if 0 <= clue_index <= (self.grid_dimension - 1):
            dim, i, reverse = 'col', clue_index, False
        elif self.grid_dimension <= clue_index <= (2 * self.grid_dimension - 1):
            dim, i, reverse = 'row', clue_index - self.grid_dimension, True
        elif 2 * self.grid_dimension <= clue_index <= (3 * self.grid_dimension - 1):
            dim, i, reverse = 'col', (3 * self.grid_dimension - 1) - clue_index, True
        elif 3 * self.grid_dimension <= clue_index <= (4 * self.grid_dimension - 1):
            dim, i, reverse = 'row', (4 * self.grid_dimension - 1) - clue_index, False
        else:
            dim, i, reverse = None, None, None

        return dim, i, reverse

    def rewrite_grid(self, grid_backup):
        for i in range(self.grid_dimension):
            for j in range(self.grid_dimension):
                self.grid[i][j] = list(grid_backup.grid[i][j])


def backtracking(grid):
    next_point = grid.get_shortest_domain()
    if next_point is None:
        return True
    grid_backup = deepcopy(grid)
    for value in sorted(grid.grid[next_point[0]][next_point[1]], reverse=False):
        grid.grid[next_point[0]][next_point[1]] = [value]
#        TO DO remove value from neighbors here

        if grid.clean_grid(p=next_point, initial=False):
            if backtracking(grid):
                return True

        grid.rewrite_grid(grid_backup)
    return False


def solve_puzzle(clues):
    grid_dimension = 6
    grid = SkyscraperGrid(clues=clues, grid_dimension=grid_dimension)
    grid.clean_grid(p=None, initial=True)
    backtracking(grid)

    return tuple(tuple(j[0] for j in i)for i in grid.grid)


if __name__ == "__main__":
    clues_6_array = [(3, 2, 2, 3, 2, 1,
                      1, 2, 3, 3, 2, 2,
                      5, 1, 2, 2, 4, 3,
                      3, 2, 1, 2, 2, 4),
                     (0, 0, 0, 2, 2, 0,
                      0, 0, 0, 6, 3, 0,
                      0, 4, 0, 0, 0, 0,
                      4, 4, 0, 3, 0, 0),
                     (0, 3, 0, 5, 3, 4,
                      0, 0, 0, 0, 0, 1,
                      0, 3, 0, 3, 2, 3,
                      3, 2, 0, 3, 1, 0)
                     ]

    clues_array = (
        (2, 2, 1, 3,
         2, 2, 3, 1,
         1, 2, 2, 3,
         3, 2, 1, 3),
        (0, 0, 1, 2,
         0, 2, 0, 0,
         0, 3, 0, 0,
         0, 1, 0, 0)
    )

    pr = cProfile.Profile()
    pr.enable()

    print(solve_puzzle(clues_6_array[2]))

    pr.disable()
    pr.print_stats(sort='time')

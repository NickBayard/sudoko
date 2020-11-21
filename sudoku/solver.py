from queue import Queue
from copy import copy
# from copy import deepcopy


class GameError(Exception):
    pass


class Field:
    def __init__(self, value:int=None):
        self.possible = list(range(1, 10))
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v=None):
        self._value = v
        if v is not None:
            self.possible = [v]

    def remove_possible(self, value):
        result = False
        if value in self.possible:
            self.possible.remove(value)
            if len(self.possible) == 1:
                self._value = self.possible[0]
                result = True
        return result


class Sudoku:
    def __init__(self, dimension, game_array):
        self.dimension = dimension
        self.depth = dimension ** 2
        self.queue = Queue()
        self.create_array(game_array)
        self._solved = False

        # For complex_solve only
        # self.candidate_values = Queue()
        # self.backup_array = None

    def __repr__(self):
        result = []
        for row in range(self.depth):
            r = []
            for column in range(self.depth):
                cell = self.array[row][column]
                value = '.' if cell.value is None else str(cell.value)
                r.append(f'({row}, {column})<{value}>{cell.possible}')
            result.append('\n'.join(r))
        return '\n\n'.join(result)

    @property
    def solved(self):
        if not self._solved:
            for row in self.array:
                if any(cell.value is None for cell in row):
                    break
            else:
                self._solved = True
        return self._solved

    def create_array(self, game_array):
        self.array = []

        for _ in range(self.depth):
            self.array.append([Field() for _ in range(self.depth)])

        # Populate known cells
        for entry in game_array:
            self.array[entry[0]][entry[1]].value = entry[2]
            self.queue.put((entry[0], entry[1]))

    def solve(self):
        while not self.queue.empty():
            if self.solved:
                break
            self.prune_impossible()
            self.find_islands()

        if not self.solved:
            raise GameError('Unsolved!')

        return self.build_result()

    def prune_impossible(self):
        while not self.queue.empty():
            row, column = self.queue.get()
            self.update_cell(row, column)

    def update_cell(self, row, column):
        value = self.array[row][column].value
        # update and enqueue row
        for index in range(self.depth):
            if index == column:
                continue
            cell = self.array[row][index]
            if cell.value is None and cell.remove_possible(value):
                self.queue.put((row, index))

        # update column
        for index in range(self.depth):
            if index == row:
                continue
            cell = self.array[index][column]
            if cell.value is None and cell.remove_possible(value):
                self.queue.put((index, column))

        # update dimension*dimension block
        block_row_start = (row // self.dimension) * self.dimension
        block_column_start = (column // self.dimension) * self.dimension

        for row_index in range(block_row_start, block_row_start + self.dimension):
            for column_index in range(block_column_start, block_column_start + self.dimension):
                if row_index == row or column_index == column:
                    continue
                cell = self.array[row_index][column_index]
                if cell.value is None and cell.remove_possible(value):
                    self.queue.put((row_index, column_index))

    def find_islands(self):
        self.find_row_islands()
        self.find_column_islands()
        self.find_block_islands()

    def find_row_islands(self):
        for row_index in range(self.depth):
            sets = [set(l.possible) for l in self.array[row_index]]

            for column_index, orig_set in enumerate(sets):
                if len(orig_set) == 1:
                    continue

                cell_pos = copy(orig_set)

                for column_index2, cell_set2 in enumerate(sets):
                    if column_index == column_index2:
                        continue

                    cell_pos = cell_pos - cell_set2

                if len(cell_pos) == 1:
                    self.array[row_index][column_index].value = cell_pos.pop()
                    self.queue.put((row_index, column_index))

    def find_column_islands(self):
        for column_index in range(self.depth):
            sets = []
            for row_index in range(self.depth):
                sets.append(set(self.array[row_index][column_index].possible))

            for row_index, orig_set in enumerate(sets):
                if len(orig_set) == 1:
                    continue

                cell_pos = copy(orig_set)

                for row_index2, cell_set2 in enumerate(sets):
                    if row_index == row_index2:
                        continue

                    cell_pos = cell_pos - cell_set2

                if len(cell_pos) == 1:
                    self.array[row_index][column_index].value = cell_pos.pop()
                    self.queue.put((row_index, column_index))

    def find_block_islands(self):
        for block_row in range(self.dimension):
            for block_column in range(self.dimension):
                # build sets from cells in this block
                sets = []
                for row_index in range(block_row, block_row + self.dimension):
                    for column_index in range(block_column, block_column + self.dimension):
                        sets.append(set(self.array[row_index][column_index].possible))

                for index, orig_set in enumerate(sets):
                    if len(orig_set) == 1:
                        continue

                    cell_pos = copy(orig_set)

                    for index2, cell_set2 in enumerate(sets):
                        if index == index2:
                            continue

                        cell_pos = cell_pos - cell_set2

                    if len(cell_pos) == 1:
                        # Calculate absolute row and column indices
                        row_index = (block_row * self.dimension) + (index // self.dimension)
                        column_index = (block_column * self.dimension) + (index % self.dimension)
                        self.array[row_index][column_index].value = cell_pos.pop()
                        self.queue.put((row_index, column_index))

    def build_result(self):
        result = []
        for row in self.array:
            result.append([cell.value for cell in row])
        return result

    # def solve(self):
        # try:
            # return self.simple_solve()
        # except GameError:
            # return self.complex_solve()

    # def complex_solve(self):
        # '''
        # "Guess" with one of the possible values for each candidate.
        # Temporarily update that cell and try to solve.
        # If this doesn't work, self.backup_array will restore the original
        # array state on the next pass through.
        # '''
        # self.enqueue_candidates()

        # while not self.candidate_values.empty():
            # if self.backup_array is None:
                # self.backup_array = deepcopy(self.array)
            # else:
                # self.array = self.backup_array

            # row, column, value = self.candidate_values.get()
            # cell = self.array[row][column]
            # cell.value = value
            # self.queue.put((row, column))
            # try:
                # return self.simple_solve()
            # except GameError:
                # pass
        # else:
            # raise GameError('Unable to solve')


    # def enqueue_candidates(self):
        # '''
        # Find the cells with the minimum number of possibilities.
        # Enqueue those cells and possibilities into candidate_values.
        # '''
        # if self.candidate_values.empty():
            # minimum = 9

            # # find mininum
            # for row in range(self.depth):
                # for column in range(self.depth):
                    # cell = self.array[row][column]
                    # if len(cell.possible) < minimum and len(cell.possible) > 1:
                        # minimum = len(cell.possible)

            # # find candidates with minimum possibilities
            # for row in range(self.depth):
                # for column in range(self.depth):
                    # cell = self.array[row][column]
                    # if len(cell.possible) == minimum:
                        # # candidate has the fewest possible values.
                        # # we can try each of them
                        # for value in cell.possible:
                            # self.candidate_values.put((row, column, value))

from dataclasses import dataclass
from queue import Queue
from copy import deepcopy


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
                self.value = self.possible[0]
                result = True
        return result


class GameError(Exception):
    pass


class Sudoku:
    def __init__(self, dimension, game_array):
        self.dimension = dimension
        self.depth = dimension ** 2
        self.queue = Queue()
        self.candidate_values = None
        self.create_array(game_array)
        self.backup_array = None

    def __repr__(self):
        result = []
        for row in self.array:
            result.append('\n'.join([str(k.possible) for k in row]))
        return '\n\n'.join(result)

    def create_array(self, game_array):
        self.array = []
        # Create empty row
        for _ in range(self.depth):
            self.array.append([])
        for row in self.array:
            for _ in range(self.depth):
                row.append(Field())
        # Populate rows
        for entry in game_array:
            self.array[entry[0]][entry[1]].value = entry[2]
            self.queue.put((entry[0], entry[1]))

    def solve(self):
        try:
            return self.simple_solve()
        except GameError:
            return self.complex_solve()

    def simple_solve(self):
        while not self.queue.empty():
            row, column = self.queue.get()
            self.update_cell(row, column)
        return self.build_result()

    def complex_solve(self):
        '''
        "Guess" with one of the possible values for each candidate.
        Temporarily update that cell and try to solve.
        If this doesn't work, self.backup_array will restore the original
        array state on the next pass through.
        '''
        self.enqueue_candidates()

        while not self.candidate_values.empty():
            if self.backup_array is None:
                self.backup_array = deepcopy(self.array)
            else:
                self.array = self.backup_array

            row, column, value = self.candidate_values.get()
            cell = self.array[row][column]
            cell.value = value
            self.queue.put((row, column))
            try:
                return self.simple_solve()
            except GameError:
                pass
        else:
            raise GameError('Unable to solve')


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
                self.queue.put((row, index))

        # update dimension*dimension block
        block_row_start = (row // self.dimension) * self.dimension
        block_column_start = (column // self.dimension) * self.dimension

        for row_index in range(block_row_start, block_row_start + self.dimension):
            for column_index in range(block_column_start, block_column_start + self.dimension):
                if row_index == row or column_index == column:
                    continue
                cell = self.array[row_index][column_index]
                if cell.value is None and cell.remove_possible(value):
                    self.queue.put((row, index))

    def build_result(self):
        result = []
        for row in self.array:
            cells = [cell.value for cell in row]
            if any(c is None for c in cells):
                raise GameError('Not solved')
            result.append(cells)
        return result

    def enqueue_candidates(self):
        '''
        Find the cells with the minimum number of possibilities.
        Enqueue those cells and possibilities into candidate_values.
        '''
        self.candidate_values = Queue()

        if self.candidate_values.empty():
            minimum = 9

            # find mininum
            for row in range(self.depth):
                for column in range(self.depth):
                    cell = self.array[row][column]
                    if len(cell.possible) < minimum and len(cell.possible) > 1:
                        minimum = len(cell.possible)

            # find candidates with minimum possibilities
            for row in range(self.depth):
                for column in range(self.depth):
                    cell = self.array[row][column]
                    if len(cell.possible) == minimum:
                        # candidate has the fewest possible values.
                        # we can try each of them
                        for value in cell.possible:
                            self.candidate_values.put((row, column, value))

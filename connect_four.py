import numpy as np
import pygame

# COLORS = [(255, 255, 255),
#           (255, 0, 0),
#           (0, 255, 0),
#           (0, 0, 255),
#           (128, 0, 255)]

# class Board:
#     def __init__(self, board_size=(6, 7), board_size_in_pixels=(480, 720), position=(0, 0)):
#         self.position = position
#         self.board_height = board_size[0]
#         self.board_width = board_size[1]
#         self.board_height_in_pixels = board_size_in_pixels[0]
#         self.board_width_in_pixels = board_size_in_pixels[1]
    
#         self.cell_height = board_size_in_pixels[0] / self.board_height
#         self.cell_width = board_size_in_pixels[1] / self.board_width
#         self.radius = min(self.cell_width, self.cell_height) / 4
#         self.board = np.zeros(board_size).astype('int')
#         self.board_columns = [pygame.Rect(j * self.cell_width, 0.0, self.cell_width, self.board_height_in_pixels) for j
#                                     in range(self.board_width)]
    
#     def draw_board(self, screen):
#         for i in range(self.board_height):
#             for j in range(self.board_width):
#                 color = COLORS[self.board[i][j]]
#                 x = self.position[1] + j * self.cell_width + self.cell_width / 2
#                 y = self.position[0] + i * self.cell_height + self.cell_height / 2
#                 pygame.draw.circle(screen, color, (x, y), self.radius)

#     def column_clicked(self):
#         position = pygame.mouse.get_pos()
#         clicked_column_ind = [j for j, column in enumerate(self.board_columns) if column.collidepoint(position)]
#         print(clicked_column_ind)
#         if clicked_column_ind:
#             return clicked_column_ind[0]

#     def update_board(self, current_player):
#         clicked_column_ind = self.column_clicked()
#         if clicked_column_ind is None:
#             return False
#         clicked_column = self.board[:, clicked_column_ind]
#         ind = 0
#         while ind < len(clicked_column) and clicked_column[ind] == 0:
#             ind += 1
#         if ind != 0:
#             self.board[ind - 1, clicked_column_ind] = current_player
#             return True
#         return False
            
        
class PlayingBoard:
    '''Representation of the connect four playing board'''

    # note: the board is stored in column-major order, i.e., the first index is the column
    # moreover, row 0 is the bottom row and row 5 is the top row
    board = np.zeros([7,6], dtype = np.float32)

    def __init__(self):
        self.board = np.zeros([7,6], dtype = np.float32)

    def reset_board(self):
        '''resets the board to all empty cells'''
        self.board = np.zeros([7, 6], dtype = np.float32)

    def get_board(self):
        '''returns a copy of the board as a numpy array (column-major order), player one is represented as 1, player two as -1, empty cells are 0'''
        return np.copy(self.board)

    def set_board(self, board):
        '''sets the state of the board, e.g., to restore a saved play situation'''
        assert(board.shape == (7,6)), "board shape does not fit"
        assert(np.min(board) >= -1), "board contains values < -1"
        assert(np.max(board) <= 1), "board contains values > 1"

        self.board = np.copy(board.astype(np.float32))

    def print_board(self):
        '''simple function for printing the board for debugging purposed'''
        print(np.flip(self.board, 1).transpose())

    def check_column(self, column):
        '''check if a marker can be inserted into the column (False if the column is filled, True else)'''
        assert((column >= 0) and (column < 7)), "column must be in range[0, 6]"
        return (0 in self.board[column])

    def insert(self, column, player):
        '''insert into given column (must be between 0 and 6) for the given player (must be 1 for player one, -1 for player two)'''
        assert((column >= 0) and (column < 7)), "column must be in range[0, 6]"
        assert((player == -1) or (player == 1)), "player must be 1 or -1"
        assert(self.check_column(column)), "cannot insert into column"

        index = np.min(np.where(self.board[column] == 0))
        self.board[column,index] = player

    def check_terminal_state(self):
        '''Checks if the game is finished and returns a pair [Boolean, reason] where the first value represents if the board is in a terminal state and if this is True, the second value identifies the reason: 1 if player one won, -1 if player two won, or 0 if all columns are filled'''
        
        # check for player one and two if they won
        for player in [1, -1]:
            # check columns
            for column in range(0,7):
                current_col = self.board[column]
                for starting_row in range(0, 3):
                    if np.equal(current_col[starting_row:starting_row+4], np.asarray([player,player,player,player])).all():
                        return [True, player]

            # check rows
            for row in range(0,6):
                current_row = self.board[:,row]
                for starting_col in range(0,4):
                    if np.equal(current_row[starting_col:(starting_col+4)], np.asarray([player,player,player,player])).all():
                        return [True, player]

            # check diagonals
            for starting_column in range(0, 4):
                # ascending
                for starting_row in range(0,3):
                    current_list = []
                    for index in range(0,4):
                        current_list.append(self.board[starting_column + index,starting_row + index])
                    if np.equal(np.asarray(current_list), np.asarray([player,player,player,player])).all():
                        return [True, player]

                # descending
                for starting_row in range(3,5):
                    current_list = []
                    for index in range(0,4):
                        current_list.append(self.board[starting_column + index,starting_row - index])
                    if np.equal(np.asarray(current_list), np.asarray([player,player,player,player])).all():
                        return [True, player]

        return [not (0 in self.board), 0]

    def invert_board(self):
        '''Inverts player one and two'''
        # instead of self.board = -1.0 self.board: to prevent -0.0 in board
        self.board = np.where(self.board, self.board * -1.0, self.board)



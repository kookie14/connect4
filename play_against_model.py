import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import numpy as np 
import connect_four
import pygame
import sys
import os

pygame.init()

# Constants
CELL_SIZE = 100
BOARD_WIDTH = 7
BOARD_HEIGHT = 6
WINDOW_WIDTH = BOARD_WIDTH * CELL_SIZE
WINDOW_HEIGHT = (BOARD_HEIGHT + 1) * CELL_SIZE
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0,0,0)

# Create Connect 4 Board
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


# helper functions
def board_to_column_vector(board):
    '''converts a playing board (i.e., 2D numpy array with shape [7,6]) to a column vector with shape [1, 42]'''
    assert(board.shape == (7,6)), "board does not have shape (7,6)"
    return np.reshape(board.flatten(), (1, 42))

def print_current_board(board):
    playing_board = board.get_board()
    screen.fill(WHITE)
    # print(" 0 1 2 3 4 5 6 ")
    for row in [0,1,2,3,4,5]:
        # print("|", end='', flush=True)
        for col in range(0, 7):
            pygame.draw.rect(screen, BLACK ,(col * CELL_SIZE, (row + 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.circle(screen, WHITE, (col * CELL_SIZE + CELL_SIZE // 2, (row + 1) * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 5)

            cell_content = playing_board[col, row]
            if cell_content == -1:
                pygame.draw.circle(screen, RED, (col * CELL_SIZE + CELL_SIZE // 2, (row + 1) * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
            elif cell_content == 1:
                pygame.draw.circle(screen, YELLOW, (col * CELL_SIZE + CELL_SIZE // 2, (row + 1) * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
    pygame.display.flip()
# check command line arguments
if not len(sys.argv) == 2:
    print("usage: python3 play_against_model <model_path>")
    exit(-1)

import_path = sys.argv[1]

if not os.path.isdir(import_path):
    print(import_path + " is not a valid directory")
    exit(-1)

# create tensorflow session 
test_session = tf.Session()
tf.reset_default_graph()

# import model
meta_graph_def = tf.saved_model.loader.load(
           test_session,
          [tf.saved_model.tag_constants.SERVING],
          import_path)
signature = meta_graph_def.signature_def

# get input and output tensors
signature_key = tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
input_tensor_name = signature[signature_key].inputs["input_x"].name
output_tensor_name = signature[signature_key].outputs["network_output"].name

input_x = test_session.graph.get_tensor_by_name(input_tensor_name)
network_output = test_session.graph.get_tensor_by_name(output_tensor_name)

tf.get_default_graph().finalize()


# playing board as global variable
playing_board = connect_four.PlayingBoard()

print("Welcome! Here is the starting board")
print_current_board(playing_board)

player = 1
terminal_state = playing_board.check_terminal_state()
while (not terminal_state[0]):
    # the neural net is player 1
    if player == 1:
        print("The AI makes its turn... result:")
        estimates = test_session.run(network_output, {input_x : board_to_column_vector(playing_board.get_board())} )[0]
        action = np.argmax(estimates)
        if not playing_board.check_column(action):
            print("AI selected a full column... terminating")
            exit(0)
        else:
            playing_board.insert(action, 1)
    else:
        # the human player's turn
        action = input("Your column (0-6)?")
        action = int(action)
        if action < 0 or action > 6:
            print("Invalid input... terminating")
            exit(0)
        elif not playing_board.check_column(action):
            print("You selected a full column... terminating")
            exit(0)
        else:
            playing_board.insert(action, -1)

    print_current_board(playing_board)

    terminal_state = playing_board.check_terminal_state()
    # switch current player
    player *= -1

if terminal_state[1] == 1:
    print("The AI won!")
elif terminal_state[1] == -1:
    print("You won!")
else:
    print("Draw")

test_session.close()

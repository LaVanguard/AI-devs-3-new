"""
Not-that-simple solution to 4th task.
- Get the board map (in list format)
- suggest the moves.
"""

import requests
import re
import sys
from pprint import pp

from secrets import openai_api_key
from lib.myai import MyAI

# Define the task source
model = "gpt-4o-mini"
ai = MyAI(openai_api_key, False, 2)     # Report each token use, limit to 2 cents

# Load the maze:
board = [
  ['p', 'X', 'p', 'p', 'p', 'p'],
  ['p', 'p', 'p', 'X', 'p', 'p'],
  ['p', 'X', 'p', 'X', 'p', 'p'],
  ['o', 'X', 'p', 'p', 'p', 'F']
];

dictionary = {}
dictionary['p'] = "O"
dictionary['X'] = "X"
dictionary['o'] = "P"
dictionary['F'] = "D"
# Translate the symbols from Banan page to our OXPD dictionary
for yindex, yentry in enumerate(board):
    for xindex, xentry in enumerate(yentry):
        board[yindex][xindex] = dictionary[xentry]
y = len(board)
x = len(board[0])
for yindex in range(y):
    board[yindex].insert(0,"X")
    board[yindex].append("X")
x += 2
board.insert(0, ["X" for i in range(x)])
board.append(["X" for i in range(x)])
y += 2
print ("The board is:")
pp (board, indent=4)

# Transform board list to board_text string
# With "\n" separating each line and ", " separating line entries
board_lines = [", ".join(line) for line in board]
board_text = "\n".join(board_lines)

# Generate the prompt
prompt = f"""
You will play a game. The game takes place on a rectangle board with {x}x{y} squares ({x} columns and {y} rows). There is one pawn you will move, step by step (horizontally or vertically) to get the pawn to the destination field. The board squares are as follows:
{board_text}
where:
"O" - available square
"X" - wall (unavailable square)
"P" - pawn (available square with current pawn position)
"D" - destination square
Based on the board plan and the descriptions:
- re-write the board plan with coordinates of each square
- write down the coordinates of the pawn
- write down the coordinates of the destination square
- write down the coordinates for each wall
Then proceed with the movement analysis. 
The pawn CAN NOT move to a wall - at any time pawn's new coordinates cannot be the coordinates of a wall.
The pawn can move just one square at a time: UP, DOWN, LEFT or RIGHT. Pawn can just move to the neighboring square, it can't jump few squares. Pawn cannot hit the wall, cannot jump above the walls and cannot leave the board.
Your goal is go get the pawn to destination, step by step.
First please prepare the movement plan for the pawn. For each suggested pawn position:
1. List all neighboring squares, for each writing if it is a wall or not, and if it was already visited on the way or not.
2. Analyze the available directions (removing the ones with walls and ones visited before)
3. For the available squares - calculate the distance to the destination (distance between the square coordinates and the destination coordinates), and select the one with lowest distance.
4. Move to the suggested square. Calculate the new coordinates.
5. Analyze the new position.
If at any position there are no available moves (not hitting walls and not going back) - please go back in analysis to the previous step and try different move in previous step. If needed - keep stepping back to the last position with available unchecked options.
In the end:
- Write tag "<RESULT>"
- Write JSON object, with one key named "steps", and value which is the string containing the list of steps (UP, DOWN, LEFT, RIGHT) separated by comma and a space. In this value list all steps needed for the pawn to move from starting position to the destination, skipping the parts where pawn needed to go back.
- Write tag "</RESULT>"
"""

messages = [
    {"role": "user", "content": prompt}
]
print ("\n\nThe prompt is:\n\n")
print (prompt)
answer = ai.chat_completion(messages, model, 2000, 0)
print ("\n\nThe solution is:\n\n")
print (answer)

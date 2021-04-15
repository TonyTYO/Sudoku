row_poss = [[[1, 2, 3], [1, 2, 3], [1, 2, 3]], [["a", "b", "c"], ["a", "b", "c"], ["a", "b", "c"]],[["x", "y", "z"], ["x", "y", "z"], ["x", "y", "z"]]]

arr = [{"1","2","3","4"}, {"8","7","3","2"}, {"9","7","6","3"}, {"8","1","2","4"}]

arr = [{"1","2"}, {"2"}, {"9","7","6","3"}, {"1","2","3"}, {"1", "2", "4"}]
arr = [{1, 7}, {6, 7, 9}, {1, 6, 7, 9}, {1, 7}, {1, 4, 7, 6}, {2, 3, 6, 7}, {3, 4, 6, 8, 9}, {2, 3, 4, 6, 8}, {5}] # pairs

import itertools

no = 4

if no == 2:
    arr = [set(), {1, 2, 4, 5}, {1, 4, 5}, {2, 4, 5}, set(), {8, 6}, {8, 6}, {1, 8, 6}, set()] # pairs 5, 6
elif no == 3:
    arr = [{1, 6}, {1, 5, 7, 8}, {1, 5, 7}, {1, 4, 3}, {1, 3, 4, 5, 7, 8}, set(), {1, 4, 6}, set(), {1, 4}] # triples 0, 6, 8
elif no == 4:
    arr = [{5, 7, 9}, {1, 4, 5, 7}, {1, 4, 5, 6}, {2, 7}, set(), {1, 8}, {2, 5, 9}, {2, 5}, {6, 8} ] # quads 0, 3, 6, 7


#initialise empty 9 by 9 grid
grid = []
grid.append([3, 0, 6, 5, 0, 8, 4, 0, 0])
grid.append([5, 2, 0, 0, 0, 0, 0, 0, 0])
grid.append([0, 8, 7, 0, 0, 0, 0, 3, 1])
grid.append([0, 0, 3, 0, 1, 0, 0, 8, 0])
grid.append([9, 0, 0, 8, 6, 3, 0, 0, 5])
grid.append([0, 5, 0, 0, 9, 0, 6, 0, 0])
grid.append([1, 3, 0, 0, 0, 0, 2, 5, 0])
grid.append([0, 0, 0, 0, 0, 0, 0, 7, 4])
grid.append([0, 0, 5, 2, 0, 6, 3, 0, 0])

def checkGrid(grid):
  for row in range(0,9):
      for col in range(0,9):
        if grid[row][col]==0:
          return False

  #We have a complete grid!
  return True

#A backtracking/recursive function to check all possible combinations of numbers until a solution is found
def solveGrid(grid):
  #Find next empty cell
  for i in range(0,81):
    row=i//9
    col=i%9
    if grid[row][col]==0:
      for value in range (1,10):
        #Check that this value has not already be used on this row
        if not(value in grid[row]):
          #Check that this value has not already be used on this column
          if not value in (grid[0][col],grid[1][col],grid[2][col],grid[3][col],grid[4][col],grid[5][col],grid[6][col],grid[7][col],grid[8][col]):
            #Identify which of the 9 squares we are working on
            square=[]
            if row<3:
              if col<3:
                square=[grid[i][0:3] for i in range(0,3)]
              elif col<6:
                square=[grid[i][3:6] for i in range(0,3)]
              else:
                square=[grid[i][6:9] for i in range(0,3)]
            elif row<6:
              if col<3:
                square=[grid[i][0:3] for i in range(3,6)]
              elif col<6:
                square=[grid[i][3:6] for i in range(3,6)]
              else:
                square=[grid[i][6:9] for i in range(3,6)]
            else:
              if col<3:
                square=[grid[i][0:3] for i in range(6,9)]
              elif col<6:
                square=[grid[i][3:6] for i in range(6,9)]
              else:
                square=[grid[i][6:9] for i in range(6,9)]
            #Check that this value has not already be used on this 3x3 square
            if not value in (square[0] + square[1] + square[2]):
              grid[row][col]=value
              if checkGrid(grid):
                print("Grid Complete and Checked")
                return True
              else:
                if solveGrid(grid):
                  return True
      break
  print("Backtrack")
  grid[row][col]=0

solved = solveGrid(grid)
if solved:
  print("Sudoku Grid Solved")

else:
  print("Cannot Solve Sudoku Grid")

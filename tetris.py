import decimal
import cs112_n21_week4_linter
import math
import copy
import random

from cmu_112_graphics import *

#################################################
# Helper functions
#################################################


def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)


def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


# Returns a four-tuple containing the dimensions for the game


def gameDimensions():
    rows = 20
    cols = 10
    cellSize = 30
    margin = 25
    return (rows, cols, cellSize, margin)

# Initializes all the neccessary values for the game


def appStarted(app):
    app.timerDelay = 200
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.emptyColor = 'blue'
    app.board = []
    for row in range(app.rows):
        app.board += [[app.emptyColor]*app.cols]
    (app.iPiece, app.jPiece, app.lPiece, app.oPiece,
        app.sPiece, app.tPiece, app.zPiece) = pieces()
    app.tetrisPieces = [app.iPiece, app.jPiece, app.lPiece,
                        app.oPiece, app.sPiece, app.tPiece, app.zPiece]
    app.fallingPiece = None
    app.fallingColor = None
    app.tetrisPieceColors = ["red", "yellow", "magenta", "pink",
                             "cyan", "green", "orange"]
    app.fallingPieceRow = 0
    app.fallingPieceCol = None
    app.numFallingPieceCols = 0
    app.pause = False
    app.isGameOver = False
    app.score = 0
    newFallingPiece(app)

# In this design, the falling piece is represented by a 2-dimensional
# list of booleans, indicating whether the given cell is or is not
# painted in this piece. This function returns all the possible pieces based on
# this description.


def pieces():
    iPiece = [
        [True,  True,  True,  True]
    ]
    jPiece = [
        [True, False, False],
        [True,  True,  True]
    ]
    lPiece = [
        [False, False,  True],
        [True,  True,  True]
    ]
    oPiece = [
        [True,  True],
        [True,  True]
    ]
    sPiece = [
        [False,  True,  True],
        [True,  True, False]
    ]
    tPiece = [
        [False,  True, False],
        [True,  True,  True]
    ]
    zPiece = [
        [True,  True, False],
        [False,  True,  True]
    ]
    return iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece

# This function returns coordinates that represent a cells top-right and
# bottom-left based on its row and column.


def getCellBounds(app, row, col):
    x0 = app.margin + app.cellSize*col
    x1 = app.margin + app.cellSize*(col+1)
    y0 = app.margin + app.cellSize*row
    y1 = app.margin + app.cellSize*(row+1)
    return x0, x1, y0, y1

# Responsible for randomly choosing a new piece, setting its color, and
# positioning it in the middle of the top row.


def newFallingPiece(app):
    randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
    app.fallingPiece = app.tetrisPieces[randomIndex]
    app.fallingColor = app.tetrisPieceColors[randomIndex]
    app.fallingPieceRow = 0
    app.numFallingPieceCols = len(app.fallingPiece[0])
    app.fallingPieceCol = app.cols//2 - app.numFallingPieceCols//2

# Moves the falling piece a given number of rows and columns.
# If the move isn't legal we reset the pieces row and column and return False,
# otherwise we move the falling piece a given number of rows and columns and
# return True


def moveFallingPiece(app, drow, dcol):
    app.fallingPieceRow += drow
    app.fallingPieceCol += dcol
    if not fallingPieceIsLegal(app):
        app.fallingPieceRow -= drow
        app.fallingPieceCol -= dcol
        return False
    return True

# This function iterates over every cell in the
# fallingPiece, and for those cells which are part of the falling piece
# it confirms that the cell is in fact on the board and the color at that
# location on the board is the emptyColor. If either of these checks fails,
# the function immediately returns False. If all the checks succeed for every
# True cell in the fallingPiece, the function returns True.


def fallingPieceIsLegal(app):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[row])):
            if app.fallingPiece[row][col] == False:
                continue
            elif app.fallingPieceRow + row not in range(len(app.board)):
                return False
            elif app.fallingPieceCol + col not in range(len(app.board[row])):
                return False
            elif (app.board[app.fallingPieceRow+row][app.fallingPieceCol+col]
                  != app.emptyColor):
                return False
    return True

# This function rotates the current falling piece around the piece's center by
# creating a 2D list of None values and puts the corresponding values of the
# piece to the new list. It then checks whether the new piece is legal. If it
# isn't, it restores all values before rotation.


def rotateFallingPiece(app):
    fallingPiece = app.fallingPiece
    numFallingPieceRow = len(app.fallingPiece)
    numFallingPieceCol = len(app.fallingPiece[0])
    fallingPieceRow = app.fallingPieceRow
    fallingPieceCol = app.fallingPieceCol
    result = []
    for row in range(numFallingPieceCol):
        result += [[None]*numFallingPieceRow]
    for row in range(numFallingPieceRow):
        for col in range(numFallingPieceCol):
            newRow = numFallingPieceCol - (1 + col)
            newCol = row
            result[newRow][newCol] = fallingPiece[row][col]
    app.fallingPiece = result
    app.fallingPieceRow = (fallingPieceRow + numFallingPieceRow//2 -
                           len(app.fallingPiece)//2)
    app.fallingPieceCol = (fallingPieceCol + numFallingPieceCol//2 -
                           len(app.fallingPiece[0])//2)
    if not fallingPieceIsLegal(app):
        app.fallingPiece = fallingPiece
        app.fallingPieceRow = fallingPieceRow
        app.fallingPieceCol = fallingPieceCol

# Every 100 milliseconds this funtion is called and it keeps calling doStep()
# if the game isn't paused or over.


def timerFired(app):
    if app.pause or app.isGameOver:
        return
    doStep(app)

# This funtion moves the falling piece down if it isn't already the farthest
# it can go


def doStep(app):
    if moveFallingPiece(app, +1, 0) == False:
        placeFallingPiece(app)

# This function loads the corresponding cells of the fallingPiece onto the board
# with the fallingPieceColor.


def placeFallingPiece(app):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[row])):
            if app.fallingPiece[row][col] == True:
                curRow = app.fallingPieceRow + row
                curCol = app.fallingPieceCol + col
                app.board[curRow][curCol] = app.fallingColor
    removeFullRows(app)
    newFallingPiece(app)
    if not fallingPieceIsLegal(app):
        app.isGameOver = True

# This function will clear any full rows from the board, move the rows above
# them down, and fill the top with empty rows.


def removeFullRows(app):
    fullRows = 0
    newBoard = []
    for row in range(len(app.board)):
        if app.emptyColor not in app.board[row]:
            fullRows += 1
        else:
            newBoard.append(app.board[row])
    app.score += fullRows**2
    for i in range(fullRows):
        newBoard.insert(0, [app.emptyColor]*app.cols)
    app.board = newBoard

# Certain actions occur based on what a keypress signifies


def keyPressed(app, event):
    if event.key == "r":
        appStarted(app)
    elif app.isGameOver:
        return
    elif event.key == "Up":
        rotateFallingPiece(app)
    elif event.key == "Down":
        moveFallingPiece(app, +1, 0)
    elif event.key == "Right":
        moveFallingPiece(app, 0, +1)
    elif event.key == "Left":
        moveFallingPiece(app, 0, -1)
    elif event.key == "p":
        app.pause = not app.pause
    elif event.key == "s":
        doStep(app)
    elif event.key == "Space":
        while moveFallingPiece(app, +1, 0):
            continue
        placeFallingPiece(app)

# Draws the background of the entire game (orange).
# Then it will use top-down design to draw the rest of the components


def redrawAll(app, canvas):
    # Background
    canvas.create_rectangle(0, 0, app.width, app.height, fill="orange")

    drawBoard(app, canvas)
    drawFallingPiece(app, canvas)
    drawGameOver(app, canvas)
    drawScore(app, canvas)

# Draws the score


def drawScore(app, canvas):
    canvas.create_text(app.width/2, app.margin/2, text=f'Score: {app.score}',
                       fill='blue', font="Helvetica 15 bold")

# Draws a box and text signifying the game is over


def drawGameOver(app, canvas):
    if app.isGameOver:
        canvas.create_rectangle(app.margin, app.margin + app.cellSize,
                                app.width - app.margin, app.margin + app.cellSize*3,
                                fill="black")
        canvas.create_text(app.width/2,
                           (app.margin + app.cellSize +
                            app.margin + app.cellSize*3)/2,
                           text='Game Over!', fill='yellow',
                           font="Helvetica 15 bold")

# Draws the board and iterates over every cell and repeatedly call
# the drawCell function


def drawBoard(app, canvas):
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            color = app.board[row][col]
            drawCell(app, canvas, row, col, color)

# Draws the given cell using the color stored in the board corresponding
# to that cell


def drawCell(app, canvas, row, col, color):
    x0, x1, y0, y1 = getCellBounds(app, row, col)
    canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=3)

# The falling piece is drawn over the board. To draw the falling piece,
# iterate over each cell in the fallingPiece, and if the value of that cell is
# True, then we should draw it using drawCell with the color of the fallingPiece


def drawFallingPiece(app, canvas):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[row])):
            if app.fallingPiece[row][col] == True:
                drawCell(app, canvas, app.fallingPieceRow + row,
                         app.fallingPieceCol + col, app.fallingColor)

# Calculates the width and height of the screen using the dimensions provided by
# gameDimensions(), then calls runApp


def playTetris():
    rows, cols, cellSize, margin = gameDimensions()
    width = margin*2 + cellSize*cols
    height = margin*2 + cellSize*rows
    runApp(width=width, height=height)

#################################################
# main
#################################################


def main():
    playTetris()


if __name__ == '__main__':
    main()

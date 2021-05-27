import pygame
from pygame.locals import *
import sys, os
import time
import math
import copy

DISPLAYSURF = pygame.display.set_mode(flags=pygame.RESIZABLE)
#my computer is 1366 by 768 (except for bar at top: it is 705 with this bar)
#my new computer is 1536 by 845
WINDOWWIDTH = pygame.Surface.get_size(DISPLAYSURF)[0]
WINDOWHEIGHT = pygame.Surface.get_size(DISPLAYSURF)[1] - 63 #subtract 63 to account for taskbar
#WINDOWHEIGHT = pygame.Surface.get_size(DISPLAYSURF)[1]
SPACESIZE = 35 #pixels in one board space; adjust later
SQUARE = SPACESIZE * SPACESIZE
BOARDWIDTH = 19 #rows on board
BOARDHEIGHT = 19 #columns on board

KOMI = SQUARE * 7 #temporary; adjust later

BOARDMARGIN = 2 * SPACESIZE #length of the board's margin, separating the playable area from the table
TABLEXMARGIN = int((WINDOWWIDTH - (2 * BOARDMARGIN + (BOARDWIDTH - 1) * SPACESIZE)) / 2) #table space between screen edge and board horizontally
TABLEYMARGIN = int((WINDOWHEIGHT - (2 * BOARDMARGIN + (BOARDHEIGHT - 1) * SPACESIZE)) / 2) #table space between screen edge and board vertically

MAXDRAW = SPACESIZE #length the user may draw in a turn

SCORETHRESHOLD = SQUARE * 8 #temp threshold, fix later

#                          R    G    B    A
BLACK       = pygame.Color(0,   0,   0)
WHITE       = pygame.Color(255, 255, 255)
TAN         = pygame.Color(227, 195, 122)
GRAY        = pygame.Color(128, 128, 128)
GRAYALPHA   = pygame.Color(128, 128, 128, 100)
RED         = pygame.Color(255, 0,   0)
GREEN       = pygame.Color(0,   255, 0)
LIGHTGRAY   = pygame.Color(200, 200, 200)
BLUE        = pygame.Color(0,   0,   232)

TEXTCOLOR           = WHITE
BOARDCOLOR          = TAN #background color of board, including margins
TABLECOLOR          = GRAY #background color of table, the area surrounding the board; consider changing
GRIDLINECOLOR       = GRAYALPHA
PROJECTIONCOLOR     = RED #color of potential lines and dots indicating click
SLIDERCOLOR         = LIGHTGRAY
SLIDERCIRCLECOLOR   = GREEN
BUTTONCOLOR         = BLUE




class button():
    def __init__(self, color, x, y, width, height, text):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, outline=None):
        #draws a button
        if outline:
            pygame.draw.rect(DISPLAYSURF, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(DISPLAYSURF, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 20)
            text = font.render(self.text, 1, (0, 0, 0))
            DISPLAYSURF.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False




CHECKBLACKAREASBUTTON = button(BLUE, 20, 70, 210, 20, "CHECK BLACK SECTION AREAS")
CHECKWHITEAREASBUTTON = button(BLUE, 20, 120, 210, 20, "CHECK WHITE SECTION AREAS")
DECREASEMAGNETBUTTON = button(BLUE, 20, 200, 20, 20, "<-")
INCREASEMAGNETBUTTON = button(BLUE, 80, 200, 20, 20, "->")
#ENDTURNBUTTON
#UNDOBUTTON
DRAWBUTTON = button(BLUE, 20, 300, 100, 20, "DRAW GAME")
PASSBUTTON = button(BLUE, 20, 400, 60, 20, "PASS")
SCOREBUTTON = button(BLUE, 20, 500, 100, 20, "SCORE GAME")
NEWGAMEBUTTON = button(BLUE, 20, 600, 100, 20, "NEW GAME")
RESUMEBUTTON = button(BLUE, 20, 100, 100, 20, "RESUME PLAY")

#SPACESIZE 35:
#bottom right is on board borders: x: 1153 -> 1154, y: 776 -> 777
#bottom right margin borders: x: 1083 -> 1084, y: 706 -> 707
#margin borders: top left: (453, 76), bottom right: (1083, 706)

def main():
    global FONT
    pygame.init()
    pygame.display.set_caption('Continuous Go')
    FONT = pygame.font.Font('freesansbold.ttf', 16)


    board = getNewBoard() #keeps track of pixels drawn
    boardLines = [] #keeps track of lines drawn
    magnetDist = 4 #starting mouse magnet distance, can adjust later
    turn = "black" #black always goes first
    turnLength = 0 #keeps track of the length of a turn
    click = []
    continuousDraw = False  #keeps track of whether the user is in the process of making a continuous draw
    pixelsDrawn = []
    drawBoard(boardLines, turn, turnLength, magnetDist)
    while True:
        for event in pygame.event.get():
            position = convertScreenToBoard(pygame.mouse.get_pos())
            if isOnBoard(position):
                if event.type == MOUSEBUTTONDOWN:
                    if len(click) == 0:
                        continuousDraw = True
                        startPosition = position
                    recentClick = True #flag that user has clicked and not moved the mouse
                elif event.type == MOUSEBUTTONUP:
                    if recentClick:
                        click.append(position)
                        if len(click) == 2:
                            x = findLine(click[0], click[1], turn, board, turnLength)
                            if len(x) > 0:
                                for dot in x:
                                    board[dot[1]][dot[0]] = turn
                                    pixelsDrawn.append((dot[0], dot[1]))
                                boardLines.append((x[0], x[-1], turn))
                                turnLength += max(1, lineDistance(x[0], x[-1]))
                                if turnLength >= (MAXDRAW * 0.97): #temporary threshold: figure out later
                                    turn = opposite(turn)
                                    turnLength = 0
                                drawBoard(boardLines, turn, turnLength, magnetDist)
                            click = []
                        recentClick = False
                    continuousDraw = False
                elif event.type == MOUSEMOTION:
                    if continuousDraw:
                        x = findLine(startPosition, position, turn, board, turnLength)
                        startPosition = position
                        if len(x) > 0:
                            for dot in x:
                                board[dot[1]][dot[0]] = turn
                            boardLines.append((x[0], x[-1], turn))
                            turnLength += lineDistance(x[0], x[-1])
                            if x[-1] != position: #line has been cut off
                                continuousDraw = False
                            if turnLength >= (MAXDRAW * 0.97): #temporary threshold: figure out later
                                turn = opposite(turn)
                                turnLength = 0
                                continuousDraw = False
                            drawBoard(boardLines, turn, turnLength, magnetDist)
                    else:
                        jump = findClosestPixel(board, position, turn, magnetDist)
                        if jump:
                            pygame.mouse.set_pos(convertBoardToScreen(jump))
                            position = jump
                        drawBoard(boardLines, turn, turnLength, magnetDist)
                        #pygame.display.update()
                        if len(click) == 1:
                            x = findLine(click[0], position, turn, board, turnLength)
                            if len(x) > 0:
                                pygame.draw.line(DISPLAYSURF, PROJECTIONCOLOR, convertBoardToScreen(x[0]), convertBoardToScreen(x[-1]))
                    recentClick = False
            else:
                if event.type == MOUSEBUTTONDOWN:
                    recentClick = True
                elif event.type == MOUSEBUTTONUP:
                    if recentClick:
                        position = pygame.mouse.get_pos()
                        if CHECKBLACKAREASBUTTON.isOver(position):
                            checkAreas(board, "black")
                            drawBoard(boardLines, turn, turnLength, magnetDist)
                        elif CHECKWHITEAREASBUTTON.isOver(position):
                            checkAreas(board, "white")
                            drawBoard(boardLines, turn, turnLength, magnetDist)
                        elif DECREASEMAGNETBUTTON.isOver(position):
                            if magnetDist > 0:
                                magnetDist -= 1
                                drawBoard(boardLines, turn, turnLength, magnetDist)
                        elif INCREASEMAGNETBUTTON.isOver(position):
                            if magnetDist < 10: #temporary maximum magnet
                                magnetDist += 1
                                drawBoard(boardLines, turn, turnLength, magnetDist)
                        #elif DRAWBUTTON.isOver(position):
                        elif PASSBUTTON.isOver(position):
                            turn = opposite(turn)
                            turnLength = 0
                            click = []
                            drawBoard(boardLines, turn, turnLength, magnetDist)
                        elif SCOREBUTTON.isOver(position):

                            '''
                            count = 0
                            for q in board:
                                for p in q:
                                    if p == "black":
                                        count += 1
                            print(count)
                            '''

                            scoredGame = scoreGame(board, pixelsDrawn)
                            board = scoredGame[0]
                            score = [scoredGame[1], scoredGame[2], scoredGame[3], scoredGame[4]]

                            '''
                            count = 0
                            for q in board:
                                for p in q:
                                    if p == "black":
                                        count += 1
                            print(count)
                            '''

                            drawScoredBoard(board, False, turn, turnLength, magnetDist, score)


                            #drawBoard(boardLines, turn, turnLength, magnetDist)
                        elif NEWGAMEBUTTON.isOver(position):
                            board = getNewBoard()
                            boardLines = []
                            turn = "black"
                            turnLength = 0
                            click = []
                            drawBoard(boardLines, turn, turnLength, magnetDist)
                    recentClick = False
                elif event.type == MOUSEMOTION:
                    recentClick = False
                continuousDraw = False
            checkForQuit(event)
        pygame.display.update()

def getNewBoard():
    #generates a new game board
    board = []
    i = 0
    while i <= SPACESIZE * (BOARDHEIGHT - 1):
        newRow = []
        j = 0
        while j <= SPACESIZE * (BOARDWIDTH - 1):
            newRow.append("")
            j += 1
        board.append(newRow)
        i += 1
    return board

def convertScreenToBoard(position):
    #converts the position of a pixel on the screen to align with the board
    return (position[0] - TABLEXMARGIN - BOARDMARGIN, position[1] - TABLEYMARGIN - BOARDMARGIN)

def convertBoardToScreen(position):
    #converts the position of a spot on the board back to a pixel on the screen
    #convertBoardToScreen(convertScreenToBoard(x)) == x
    return (position[0] + TABLEXMARGIN + BOARDMARGIN, position[1] + TABLEYMARGIN + BOARDMARGIN)

def opposite(turn):
    if turn == "black":
        return "white"
    if turn == "white":
        return "black"

def lineDistance(start, end):
    #return the distance from start to end
    return math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)

def crossThrough(first, second, turn, board):
    #checks if the diagonal line from first to second crosses through another diagonal line of the color opposite(turn)
    if first[0] < second[0]:
        if first[1] < second[1]:
            pixel1 = (first[0] + 1, first[1])
            pixel2 = (first[0], first[1] + 1)
        else: #first[1] > second[1]
            pixel1 = (first[0], first[1] - 1)
            pixel2 = (first[0] + 1, first[1])
    else: #first[0] > second[0]
        if first[1] < second[1]:
            pixel1 = (first[0] - 1, first[1])
            pixel2 = (first[0], first[1] + 1)
        else: #first[1] > second[1]
            pixel1 = (first[0], first[1] - 1)
            pixel2 = (first[0] - 1, first[1])
    return board[pixel1[1]][pixel1[0]] == opposite(turn) and board[pixel2[1]][pixel2[0]] == opposite(turn)

def findLine(start, end, turn, board, turnLength):
    #returns a line composed of pixels from start to end, cut off where appropriate

    #imitation of Pygame code for a line: https://github.com/pygame/pygame/blob/main/src_c/draw.c, line 1553
    x0 = start[0]
    y0 = start[1]
    x1 = end[0]
    y1 = end[1]
    result = []
    if x0 == x1 and y0 == y1: #point
        result.append(start)
    elif y0 == y1: #horizontal line
        if x0 < x1:
            dx = 1
        else:
            dx = -1
        i = 0
        while i <= abs(x0 - x1):
            result.append((x0 + dx * i, y0))
            i += 1
    elif x0 == x1: #vertical line
        if y0 < y1:
            dy = 1
        else:
            dy = -1
        i = 0
        while i <= abs(y0 - y1):
            result.append((x0, y0 + dy * i))
            i += 1
    else:
        dx = abs(x0 - x1)
        if x0 < x1:
            sx = 1
        else:
            sx = -1
        dy = abs(y0 - y1)
        if y0 < y1:
            sy = 1
        else:
            sy = -1
        if dx > dy:
            err = dx / 2
        else:
            err = -dy / 2
        while x0 != x1 or y0 != y1:
            result.append((x0, y0))
            e2 = err
            if e2 > -dx:
                err -= dy
                x0 += sx
            if e2 < dy:
                err += dx
                y0 += sy
        result.append((x1, y1))

    #cut off line when a) goes outside margins, b) intersects opposing player's line, or c) goes past drawing length limit
    i = 0
    newResult = []
    remainingLength = MAXDRAW - turnLength
    while i < len(result) and ((not isInsideMargins(result[i])) or board[result[i][1]][result[i][0]] == opposite(turn)):
        i += 1
    if i != len(result):
        newResult.append(result[i])
        i += 1
    while i < len(result) and isInsideMargins(result[i]) and lineDistance(newResult[0], result[i]) <= remainingLength and board[result[i][1]][result[i][0]] != opposite(turn) and not crossThrough(result[i - 1], result[i], turn, board):
        newResult.append(result[i])
        i += 1
    if len(newResult) > 0 and (newResult[0] != start or newResult[-1] != end): #the line to draw has been shortened
        return findLine(newResult[0], newResult[-1], turn, board, turnLength) #redo algorithm on this new range
    return newResult

def convertColor(col):
    # converts turn to color
    if col == 'white':
        return WHITE
    if col == 'black':
        return BLACK

def drawBoard(boardLines, turn, turnLength, magnetDist):
    #draws the board and the informational text about the game

    #draw background of table area surrounding board
    DISPLAYSURF.fill(TABLECOLOR)

    #draw background of board
    boardRect = pygame.Rect(TABLEXMARGIN, TABLEYMARGIN, 2 * BOARDMARGIN + SPACESIZE * (BOARDWIDTH - 1), 2 * BOARDMARGIN + SPACESIZE * (BOARDHEIGHT - 1))
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, boardRect)

    #draw the horizontal lines
    for y in range(BOARDHEIGHT):
        startx = TABLEXMARGIN + BOARDMARGIN
        starty = TABLEYMARGIN + BOARDMARGIN + (y * SPACESIZE)
        endx = TABLEXMARGIN + BOARDMARGIN + ((BOARDHEIGHT - 1) * SPACESIZE)
        endy = starty
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    #draw the vertical lines
    for x in range(BOARDWIDTH):
        startx = TABLEXMARGIN + BOARDMARGIN + (x * SPACESIZE)
        starty = TABLEYMARGIN + BOARDMARGIN
        endx = startx
        endy = TABLEYMARGIN + BOARDMARGIN + ((BOARDHEIGHT - 1) * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    #draw the star points (small circles) on the go board
    if BOARDWIDTH == 19 and BOARDHEIGHT == 19:
        for x in {3, 9, 15}:
            for y in {3, 9, 15}:
                pygame.draw.circle(DISPLAYSURF, GRIDLINECOLOR, (TABLEXMARGIN + BOARDMARGIN + x * SPACESIZE, TABLEYMARGIN + BOARDMARGIN + y * SPACESIZE), SPACESIZE // 7, 0)
    elif BOARDWIDTH == 9 and BOARDHEIGHT == 9:
        for (x, y) in {(2, 2), (6, 2), (4, 4), (2, 6), (6, 6)}:
            pygame.draw.circle(DISPLAYSURF, GRIDLINECOLOR, (TABLEXMARGIN + BOARDMARGIN + x * SPACESIZE, TABLEYMARGIN + BOARDMARGIN + y * SPACESIZE), SPACESIZE // 7, 0)

    #draw the lines on the board created by the players
    for i in boardLines:
        pygame.draw.line(DISPLAYSURF, convertColor(i[2]), convertBoardToScreen(i[0]), convertBoardToScreen(i[1]))

    #draw informational text about the state of the game
    drawTurn(turn)
    drawTurnLength(turnLength)
    drawMagnetStrength(magnetDist)
    drawButtons()



def drawScoredBoard(board, partial, turn=None, turnLength=None, magnetDist=None, score=None):
    #if game is over, draws the ending board and the informational text about the game
    #otherwise, draws the board as is along with highlighted user-selected sections

    #draw background of table area surrounding board
    DISPLAYSURF.fill(TABLECOLOR)

    #draw background of board
    boardRect = pygame.Rect(TABLEXMARGIN, TABLEYMARGIN, 2 * BOARDMARGIN + SPACESIZE * (BOARDWIDTH - 1), 2 * BOARDMARGIN + SPACESIZE * (BOARDHEIGHT - 1))
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, boardRect)

    #draw the horizontal lines
    for y in range(BOARDHEIGHT):
        startx = TABLEXMARGIN + BOARDMARGIN
        starty = TABLEYMARGIN + BOARDMARGIN + (y * SPACESIZE)
        endx = TABLEXMARGIN + BOARDMARGIN + ((BOARDHEIGHT - 1) * SPACESIZE)
        endy = starty
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    #draw the vertical lines
    for x in range(BOARDWIDTH):
        startx = TABLEXMARGIN + BOARDMARGIN + (x * SPACESIZE)
        starty = TABLEYMARGIN + BOARDMARGIN
        endx = startx
        endy = TABLEYMARGIN + BOARDMARGIN + ((BOARDHEIGHT - 1) * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    #draw the star points (small circles) on the go board
    if BOARDWIDTH == 19 and BOARDHEIGHT == 19:
        for x in {3, 9, 15}:
            for y in {3, 9, 15}:
                pygame.draw.circle(DISPLAYSURF, GRIDLINECOLOR, (TABLEXMARGIN + BOARDMARGIN + x * SPACESIZE, TABLEYMARGIN + BOARDMARGIN + y * SPACESIZE), SPACESIZE // 7, 0)
    elif BOARDWIDTH == 9 and BOARDHEIGHT == 9:
        for (x, y) in {(2, 2), (6, 2), (4, 4), (2, 6), (6, 6)}:
            pygame.draw.circle(DISPLAYSURF, GRIDLINECOLOR, (TABLEXMARGIN + BOARDMARGIN + x * SPACESIZE, TABLEYMARGIN + BOARDMARGIN + y * SPACESIZE), SPACESIZE // 7, 0)

    #draw the pixels on the board created by the players
    for j in range(len(board)):
        for i in range(len(board[0])):
            if board[j][i] == "black":
                DISPLAYSURF.set_at((TABLEXMARGIN + BOARDMARGIN + i, TABLEYMARGIN + BOARDMARGIN + j), BLACK)
            elif board[j][i] == "white":
                DISPLAYSURF.set_at((TABLEXMARGIN + BOARDMARGIN + i, TABLEYMARGIN + BOARDMARGIN + j), WHITE)
            elif board[j][i] == "gray":
                DISPLAYSURF.set_at((TABLEXMARGIN + BOARDMARGIN + i, TABLEYMARGIN + BOARDMARGIN + j), GRAY)
            elif board[j][i] == "green":
                DISPLAYSURF.set_at((TABLEXMARGIN + BOARDMARGIN + i, TABLEYMARGIN + BOARDMARGIN + j), GREEN)

    if not partial:
        #draw informational text about the state of the game
        drawTurn(turn)
        drawTurnLength(turnLength)
        drawMagnetStrength(magnetDist)
        drawButtons()
        drawScore(score)







def drawTurn(turn):
    #displays whose turn it is at the bottom of the screen
    turnSurf = FONT.render("%s's Turn" % (turn.title()), True, TEXTCOLOR)
    turnRect = turnSurf.get_rect()
    turnRect.bottomleft = (10, WINDOWHEIGHT - 60)
    DISPLAYSURF.blit(turnSurf, turnRect)

def drawTurnLength(turnLength):
    #displays how much of the turn's line length has been drawn so far
    lengthSurf = FONT.render("%f Percent Drawn" % (100 * turnLength / MAXDRAW), True, TEXTCOLOR)
    lengthRect = lengthSurf.get_rect()
    lengthRect.bottomleft = (10, WINDOWHEIGHT - 110)
    DISPLAYSURF.blit(lengthSurf, lengthRect)

    '''
    lengthSurf = FONT.render("%.2f Drawn" % (round(turnLength, 2)), True, TEXTCOLOR)
    lengthRect = lengthSurf.get_rect()
    lengthRect.bottomleft = (10, WINDOWHEIGHT - 120)
    DISPLAYSURF.blit(lengthSurf, lengthRect)

    lengthSurf2 = FONT.render("(Out Of %.2f)" % (MAXDRAW), True, TEXTCOLOR)
    lengthRect2 = lengthSurf.get_rect()
    lengthRect2.bottomleft = (10, WINDOWHEIGHT - 100)
    DISPLAYSURF.blit(lengthSurf2, lengthRect2)
    '''

def drawMagnetStrength(magnetDist):
    #draws the strength of the magnet
    magnetSurf = FONT.render("%i" % (magnetDist), True, TEXTCOLOR)
    magnetRect = magnetSurf.get_rect()
    magnetRect.topleft = (55, 205)
    DISPLAYSURF.blit(magnetSurf, magnetRect)
    return

def drawButtons():
    CHECKBLACKAREASBUTTON.draw()
    CHECKWHITEAREASBUTTON.draw()
    DECREASEMAGNETBUTTON.draw()
    INCREASEMAGNETBUTTON.draw()
    DRAWBUTTON.draw()
    PASSBUTTON.draw()
    SCOREBUTTON.draw()
    NEWGAMEBUTTON.draw()

def drawScore(score):
    blackScore = score[0]
    whiteScore = score[1]
    bothScore = score[2]
    neitherScore = score[3]

    #blackSurf = FONT.render("final black score: %i" % (blackScore), True, TEXTCOLOR)
    blackSurf = FONT.render("final black score: %f" % (blackScore / SQUARE), True, TEXTCOLOR)
    blackRect = blackSurf.get_rect()
    blackRect.topleft = (1200, 350)
    DISPLAYSURF.blit(blackSurf, blackRect)

    #whiteSurf = FONT.render("final white score (without komi): %i" % (whiteScore), True, TEXTCOLOR)
    whiteSurf = FONT.render("final white score (without komi): %f" % (whiteScore / SQUARE), True, TEXTCOLOR)
    whiteRect = whiteSurf.get_rect()
    whiteRect.topleft = (1200, 370)
    DISPLAYSURF.blit(whiteSurf, whiteRect)

    #bothSurf = FONT.render("final both score: %i" % (bothScore), True, TEXTCOLOR)
    bothSurf = FONT.render("final both score: %f" % (bothScore / SQUARE), True, TEXTCOLOR)
    bothRect = bothSurf.get_rect()
    bothRect.topleft = (1200, 390)
    DISPLAYSURF.blit(bothSurf, bothRect)

    #neitherSurf = FONT.render("final neither score: %i" % (neitherScore), True, TEXTCOLOR)
    neitherSurf = FONT.render("final neither score: %f" % (neitherScore / SQUARE), True, TEXTCOLOR)
    neitherRect = neitherSurf.get_rect()
    neitherRect.topleft = (1200, 410)
    DISPLAYSURF.blit(neitherSurf, neitherRect)

    #komiSurf = FONT.render("komi: %i" % (KOMI), True, TEXTCOLOR)
    komiSurf = FONT.render("komi: %f" % (KOMI / SQUARE), True, TEXTCOLOR)
    komiRect = komiSurf.get_rect()
    komiRect.topleft = (1200, 430)
    DISPLAYSURF.blit(komiSurf, komiRect)

    if blackScore > whiteScore + KOMI:
        finalText = "black wins"
    elif whiteScore + KOMI > blackScore:
        finalText = "white wins"
    else:
        finalText = "tie"

    finalSurf = FONT.render((finalText), True, TEXTCOLOR)
    finalRect = finalSurf.get_rect()
    finalRect.topleft = (1200, 450)
    DISPLAYSURF.blit(finalSurf, finalRect)


def drawHighlightedScore(color, score):
    #draws the total of the areas that the users has highlighted
    scoreSurf = FONT.render("you have highlighted %f squares of %s's area" % (score, color), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (1000, 350)
    DISPLAYSURF.blit(scoreSurf, scoreRect)




def isInsideMargins(position):
    #returns True iff the coordinates are located on the board within the gridlines
    maxX = SPACESIZE * (BOARDWIDTH - 1)
    maxY = SPACESIZE * (BOARDHEIGHT - 1)
    return 0 <= position[0] and position[0] <= maxX and 0 <= position[1] and position[1] <= maxY

def isOnBoard(position):
    #returns True iff the coordinates are located on the board, whether within the gridlines or within the margins
    maxX = SPACESIZE * (BOARDWIDTH - 1) + BOARDMARGIN
    maxY = SPACESIZE * (BOARDHEIGHT - 1) + BOARDMARGIN
    return -BOARDMARGIN <= position[0] and position[0] <= maxX and -BOARDMARGIN <= position[1] and position[1] <= maxY

def findClosestPixel(board, position, turn, magnetDist):
    #returns the closest pixel among player's own to position as long as it is within magnetDist; otherwise returns None
    closestPixel = None
    closestDistance = magnetDist
    x = position[0] - magnetDist
    while x <= position[0] + magnetDist:
        y = position[1] - magnetDist
        while y <= position[1] + magnetDist:
            if isInsideMargins((x, y)) and board[y][x] == turn:
                dist = lineDistance(position, (x, y))
                if dist <= closestDistance:
                    closestDistance = dist
                    closestPixel = (x, y)
            y += 1
        x += 1
    return closestPixel

def neighbors(position, board):
    #finds the same-colored neighbors of the pixel at position within board
    # 1 2 3
    # 4 X 5
    # 6 7 8
    x = position[0]
    y = position[1]
    color = board[y][x]
    result = []
    if y > 0:
        if board[y - 1][x] == color:
            result.append((x, y - 1)) #2
        if x > 0:
            if board[y - 1][x - 1] == color:
                result.append((x - 1, y - 1)) #1
        if x < len(board[0]) - 1:
            if board[y - 1][x + 1] == color:
                result.append((x + 1, y - 1)) #3
    if y < len(board) - 1:
        if board[y + 1][x] == color:
            result.append((x, y + 1)) #7
        if x > 0:
            if board[y + 1][x - 1] == color:
                result.append((x - 1, y + 1)) #6
        if x < len(board[0]) - 1:
            if board[y + 1][x + 1] == color:
                result.append((x + 1, y + 1)) #8
    if x > 0:
        if board[y][x - 1] == color:
            result.append((x - 1, y)) #4
    if x < len(board[0]) - 1:
        if board[y][x + 1] == color:
            result.append((x + 1, y)) #5
    return result

def isOnBorder(position, board):
    #determines if position is on border of board
    x = position[0]
    y = position[1]
    if y == 0 or x == 0 or y == len(board) - 1 or x == len(board[0]) - 1:
        return True
    return False







def floodFillSection(board, point, color):
    #fills in section by getting set of pixels within area contained by lines of given color via algorithm modified from one found on Wikipedia: https://en.wikipedia.org/wiki/Flood_fill#Span_Filling
    #also return set of pixels of given color on borders surrounding this section (both inside and out)
    s = [] #stack of points to check
    fillSet = set() #fill points
    borderSet = set() #border points
    s.append((point, (0, 0, "")))
    while len(s) > 0:
        temp = s.pop()
        point = temp[0]
        completedRange = temp[1]
        #fill in the row to the left and right of point; add the pixels to the left and right of this range to borderSet
        leftPoint = (point[0] - 1, point[1])
        while isInsideMargins(leftPoint) and board[leftPoint[1]][leftPoint[0]] != color:
            fillSet.add(leftPoint)
            leftPoint = (leftPoint[0] - 1, leftPoint[1])
        if isInsideMargins(leftPoint) and board[leftPoint[1]][leftPoint[0]] == color:
            borderSet.add(leftPoint)
        while isInsideMargins(point) and board[point[1]][point[0]] != color:
            fillSet.add(point)
            point = (point[0] + 1, point[1])
        if isInsideMargins(point) and board[point[1]][point[0]] == color:
            borderSet.add(point)
        #add the rows above and below point to the stack; add the border points here to borderSet
        added = False
        for i in range(leftPoint[0] + 1, point[0]):
            newPoint = (i, point[1] - 1)
            if not isInsideMargins(newPoint):
                break
            if completedRange[2] == "below" and (completedRange[0] <= i and i < completedRange[1]):
                continue
            if newPoint in fillSet or board[newPoint[1]][newPoint[0]] == color:
                if board[newPoint[1]][newPoint[0]] == color:
                    borderSet.add(newPoint)
                added = False
            elif not added:
                s.append((newPoint, (leftPoint[0] + 1, point[0], "above")))
                added = True
        added = False
        for i in range(leftPoint[0] + 1, point[0]):
            newPoint = (i, point[1] + 1)
            if not isInsideMargins(newPoint):
                break
            if completedRange[2] == "above" and (completedRange[0] <= i and i < completedRange[1]):
                continue
            if newPoint in fillSet or board[newPoint[1]][newPoint[0]] == color:
                if board[newPoint[1]][newPoint[0]] == color:
                    borderSet.add(newPoint)
                added = False
            elif not added:
                s.append((newPoint, (leftPoint[0] + 1, point[0], "below")))
                added = True
        #add any corners of the range checked to borderSet
        corners = [(leftPoint[0], point[1] - 1), (point[0], point[1] - 1), (leftPoint[0], point[1] + 1), (point[0], point[1] + 1)]
        for corner in corners:
            if isInsideMargins(corner) and board[corner[1]][corner[0]] == color:
                borderSet.add(corner)

    #print("\n")
    #print("borderSet:")
    #print(borderSet)

    return (fillSet, borderSet)





'''
def findBorderPoint(point, board, color):
    i = point[0]
    j = point[1]
    while isInsideMargins((i, j - 1)):
        j -= 1
        if board[j][i] == color:
            return (i, j)
    while isInsideMargins((i - 1, j)):
        i -= 1
        if board[j][i] == color:
            return (i, j)
    while isInsideMargins((i, j + 1)):
        j += 1
        if board[j][i] == color:
            return (i, j)
    while isInsideMargins((i + 1, j)):
        i += 1
        if board[j][i] == color:
            return (i, j)
'''





def illegalConnection(a, b, crossings, board):
    #tests whether the line from a to b should be disallowed by checking crossings
    color = board[a[1]][a[0]]
    for i in crossings:
        if i[2] != color:
            square = ((i[0], i[1]), (i[0] + 1, i[1]), (i[0], i[1] + 1), (i[0] + 1, i[1] + 1))
            if a in square and b in square:
                return True
    return False






def scoreGame(board, pixelsDrawn):
    #scores the game

    if len(board) == 0 or len(board[0]) == 0:
        return (board, 0, 0, 0, 0)



    #identify locations where lines of opposite color cross each other and find which line was drawn first in these locations
    crossings = set()
    for j in range(len(board) - 1):
        for i in range(len(board[0]) - 1):
            if board[j][i] == "black" and board[j + 1][i] == "white" and board[j][i + 1] == "white" and board[j + 1][i + 1] == "black":
                a = pixelsDrawn.index((i, j))
                b = pixelsDrawn.index((i, j + 1))
                c = pixelsDrawn.index((i + 1, j))
                d = pixelsDrawn.index((i + 1, j + 1))
                if (a > b and a > c) or (d > b and d > c):
                    crossings.add((i, j, "white"))
                else:
                    crossings.add((i, j, "black"))
            elif board[j][i] == "white" and board[j + 1][i] == "black" and board[j][i + 1] == "black" and board[j + 1][i + 1] == "white":
                a = pixelsDrawn.index((i, j))
                b = pixelsDrawn.index((i, j + 1))
                c = pixelsDrawn.index((i + 1, j))
                d = pixelsDrawn.index((i + 1, j + 1))
                if (a > b and a > c) or (d > b and d > c):
                    crossings.add((i, j, "black"))
                else:
                    crossings.add((i, j, "white"))




    #divides the board into sections for each color via floodFillSection
    blackSections = [] #list of sections segmented by black's pixels
    blackFilled = set() #set of pixels checked for black segmentation already
    whiteSections = [] #list of sections segmented by white's pixels
    whiteFilled = set() #set of pixels checked for white segmentation already
    for j in range(len(board)):
        for i in range(len(board[0])):
            if board[j][i] != "black" and (i, j) not in blackFilled:
                newSection = floodFillSection(board, (i, j), "black")
                blackSections.append(newSection)
                blackFilled.update(newSection[0])
            if board[j][i] != "white" and (i, j) not in whiteFilled:
                newSection = floodFillSection(board, (i, j), "white")
                whiteSections.append(newSection)
                whiteFilled.update(newSection[0])




    #combine sections that should connect across a crossing
    for i in crossings:
        x = i[0]
        y = i[1]
        if i[2] == "black":
            if board[y][x] == "black":
                for j in whiteSections:
                    if (x, y) in j[0]:
                        if (x + 1, y + 1) not in j[0]:
                            for k in whiteSections:
                                if (x + 1, y + 1) in k[0]:
                                    whiteSections.append((j[0].union(k[0]), j[1].union(k[1])))
                                    whiteSections.remove(j)
                                    whiteSections.remove(k)
                                    break
                        break
            elif board[y][x] == "white":
                for j in whiteSections:
                    if (x + 1, y) in j[0]:
                        if (x, y + 1) not in j[0]:
                            for k in whiteSections:
                                if (x, y + 1) in k[0]:
                                    whiteSections.append((j[0].union(k[0]), j[1].union(k[1])))
                                    whiteSections.remove(j)
                                    whiteSections.remove(k)
                                    break
                        break
        elif i[2] == "white":
            if board[y][x] == "white":
                for j in blackSections:
                    if (x, y) in j[0]:
                        if (x + 1, y + 1) not in j[0]:
                            for k in blackSections:
                                if (x + 1, y + 1) in k[0]:
                                    blackSections.append((j[0].union(k[0]), j[1].union(k[1])))
                                    blackSections.remove(j)
                                    blackSections.remove(k)
                                    break
                        break
            elif board[y][x] == "black":
                for j in blackSections:
                    if (x + 1, y) in j[0]:
                        if (x, y + 1) not in j[0]:
                            for k in blackSections:
                                if (x, y + 1) in k[0]:
                                    blackSections.append((j[0].union(k[0]), j[1].union(k[1])))
                                    blackSections.remove(j)
                                    blackSections.remove(k)
                                    break
                        break


    '''
    print("\n")
    print("blackSections:")
    print(blackSections)
    print("whiteSections:")
    print(whiteSections)
    '''



    #eliminates sections larger than SCORETHRESHOLD as they are too large to count
    i = 0
    while i < len(blackSections):
        if len(blackSections[i][0]) + len(blackSections[i][1]) > SCORETHRESHOLD:
            del blackSections[i]
        else:
            i += 1
    i = 0
    while i < len(whiteSections):
        if len(whiteSections[i][0]) + len(whiteSections[i][1]) > SCORETHRESHOLD:
            del whiteSections[i]
        else:
            i += 1


    '''
    print("\n")
    print("blackSections:")
    print(blackSections)
    print("whiteSections:")
    print(whiteSections)
    '''



    #segment the connected lines of each color into groups
    blackLineGroups = []
    whiteLineGroups = []
    blackPixels = set()
    whitePixels = set()
    for j in range(len(board)):
        for i in range(len(board[0])):
            if board[j][i] == "":
                continue
            elif board[j][i] == "black" and (i, j) not in blackPixels:
                s = [(i, j)]
                pixels = {(i, j)}
                while len(s) > 0:
                    position = s.pop()
                    currentNeighbors = neighbors(position, board)
                    for i in currentNeighbors:
                        if (i not in pixels) and (not illegalConnection(position, i, crossings, board)):
                            s.append(i)
                            pixels.add(i)
                blackLineGroups.append(pixels)
                blackPixels.update(pixels)
            elif board[j][i] == "white" and (i, j) not in whitePixels:
                s = [(i, j)]
                pixels = {(i, j)}
                while len(s) > 0:
                    position = s.pop()
                    currentNeighbors = neighbors(position, board)
                    for i in currentNeighbors:
                        if (i not in pixels) and (not illegalConnection(position, i, crossings, board)):
                            s.append(i)
                            pixels.add(i)
                whiteLineGroups.append(pixels)
                whitePixels.update(pixels)


    '''
    print("\n")
    print("blackLineGroups:")
    print(blackLineGroups)
    print("whiteLineGroups:")
    print(whiteLineGroups)
    '''


    #combine sections and line groups into groups by determining the connections between sections and groups
    #then eliminate groups that are too small and consolidate all pixels for each color into one set
    originalBlackSections = copy.deepcopy(blackSections)
    finalBlackPixels = set()
    while len(blackSections) > 0:
        group = blackSections.pop()
        while True:
            indicator = 0
            for i in blackSections:
                if not i[1].isdisjoint(group[1]):
                    group = (group[0].union(i[0]), group[1].union(i[1]))
                    blackSections.remove(i)
                    indicator = 1
                    break
            for i in blackLineGroups:
                if not i.isdisjoint(group[1]):
                    group = (group[0], group[1].union(i))
                    blackLineGroups.remove(i)
                    indicator = 1
                    break
            if indicator == 0:
                break
        '''
        #for pure Chinese scoring:
        if len(group[0]) + len(group[1]) >= SCORETHRESHOLD:
            finalBlackPixels.update(group[0])
            finalBlackPixels.update(group[1])
        '''

        newGroup = set()
        for i in originalBlackSections:
            if not i[0].isdisjoint(group[0]):
                newGroup.update(i[0])
                newGroup.update(i[1])
        if len(newGroup) >= SCORETHRESHOLD:
            finalBlackPixels.update(newGroup)


    originalWhiteSections = copy.deepcopy(whiteSections)
    finalWhitePixels = set()
    while len(whiteSections) > 0:
        group = whiteSections.pop()
        while True:
            indicator = 0
            for i in whiteSections:
                if not i[1].isdisjoint(group[1]):
                    group = (group[0].union(i[0]), group[1].union(i[1]))
                    whiteSections.remove(i)
                    indicator = 1
                    break
            for i in whiteLineGroups:
                if not i.isdisjoint(group[1]):
                    group = (group[0], group[1].union(i))
                    whiteLineGroups.remove(i)
                    indicator = 1
                    break
            if indicator == 0:
                break
        '''
        #for pure Chinese scoring:
        if len(group[0]) + len(group[1]) >= SCORETHRESHOLD:
            finalWhitePixels.update(group[0])
            finalWhitePixels.update(group[1])
        '''

        newGroup = set()
        for i in originalWhiteSections:
            if not i[0].isdisjoint(group[0]):
                newGroup.update(i[0])
                newGroup.update(i[1])
        if len(newGroup) >= SCORETHRESHOLD:
            finalWhitePixels.update(newGroup)



    #replaces the board with a scored version and determines final score
    blackScore = 0
    whiteScore = 0
    bothScore = 0
    neitherScore = 0
    for j in range(len(board)):
        for i in range(len(board[0])):
            if (i, j) in finalBlackPixels:
                if (i, j) in finalWhitePixels:
                    board[j][i] = "gray"
                    bothScore += 1
                else:
                    board[j][i] = "black"
                    blackScore += 1
            elif (i, j) in finalWhitePixels:
                board[j][i] = "white"
                whiteScore += 1
            else:
                board[j][i] = ""
                neitherScore += 1

    return (board, blackScore, whiteScore, bothScore, neitherScore)






def checkAreas(board, color):
    #run a game loop where the user can click on sections to get the areas
    tempBoard = copy.deepcopy(board)
    drawScoredBoard(tempBoard, True)
    RESUMEBUTTON.draw()
    filledSections = []
    while True:
        for event in pygame.event.get():
            position = convertScreenToBoard(pygame.mouse.get_pos())
            if isInsideMargins(position):
                if event.type == MOUSEBUTTONDOWN:
                    recentClick = True #flag that user has clicked and not moved the mouse
                elif event.type == MOUSEBUTTONUP:
                    if recentClick:
                        if board[position[1]][position[0]] != color: #have not clicked on territory's boundary, so can proceed to fill or unfill
                            if tempBoard[position[1]][position[0]] != "green":
                                x = floodFillSection(board, position, color)
                                newSection = x[0].union(x[1])
                                filledSections.append(newSection)
                                for i in newSection:
                                    tempBoard[i[1]][i[0]] = "green"
                            else:
                                breakLoop = False
                                for i in filledSections:
                                    for j in i:
                                        if j == position:
                                            filledSections.remove(i)
                                            tempBoard = copy.deepcopy(board)
                                            for a in filledSections:
                                                for b in a:
                                                    tempBoard[b[1]][b[0]] = "green"
                                            breakLoop = True
                                            break
                                    if breakLoop:
                                        breakLoop = False
                                        break
                            drawScoredBoard(tempBoard, True)
                            RESUMEBUTTON.draw()


                            score = 0
                            for i in tempBoard:
                                for j in i:
                                    if j == "green":
                                        score += 1
                            #score = 0
                            #for i in filledSections:
                            #    score += len(i)

                            score = score / SQUARE

                            drawHighlightedScore(color, score)
                        recentClick = False
                elif event.type == MOUSEMOTION:
                    recentClick = False
            else:
                if event.type == MOUSEBUTTONDOWN:
                    recentClick = True
                elif event.type == MOUSEBUTTONUP:
                    if recentClick:
                        position = pygame.mouse.get_pos()
                        if RESUMEBUTTON.isOver(position):
                            return
                    recentClick = False
                elif event.type == MOUSEMOTION:
                    recentClick = False
            checkForQuit(event)
        pygame.display.update()





def checkForQuit(event):
    #if the user has quit or hit the escape key, quit the program
    if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    main()

#to do:
    #revise 0.97 threshold
        #with higher threshold, sometimes mistakenly left with very small draw after what should be a full line
    #check if need to pump
    #figure out gridline color (GRAYALPHA)
    #determine if better way to write text than current FONT method
    #make sure displays work with different screen sizes
    #figure out resizing/zooming
    #add line weaving function
    #add ability to undo turns
    #force end game, consider disallowing drawing over what has already been drawn
    #condsider tool to check area of neutral territory
    #fix game loop: should use both while True and for event?; goal: should have low use when doing nothing
    #somehow make it easier to check for tiny gaps in lines

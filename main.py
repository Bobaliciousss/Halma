import tkinter as tk

PADDING = 5
WINDOW_WIDTH = 750
WINDOW_HEIGHT = 750
MARGIN = 50
BOARD_HEIGHT = WINDOW_HEIGHT - MARGIN*2
PLAYER_1 = 1 # Red
PLAYER_2 = 2 # Green
MOVE_LIMIT = 5 # seconds per move

class Piece:
    def __init__( self, canvas: tk.Canvas, player: int, pieceId: int, row : int, col : int ):
        self.canvas = canvas
        self.player = player
        self.pieceId = pieceId   
        self.row = row
        self.column = col

    def draw( self ):
        global cellSize
        x = self.column * cellSize + MARGIN
        y = self.row * cellSize + MARGIN
        color = "green"
        if self.player == PLAYER_1:
            color = "red"
        self.pieceId = self.canvas.create_oval( 
                    x + PADDING, y + PADDING,
                    x + cellSize - PADDING, y + cellSize - PADDING,
                    fill=color
                )
        self.canvas.tag_bind( self.pieceId, '<Button-1>', self.onClick )

    def onClick( self, event ):
        # print( f"Clicked on {self.player}'s piece. Located at position {self.column}, {self.row}" )
        if self.player != currentPlayer:
            canvas.itemconfigure(msgText, text="Cannot move other player's piece.")
            return
        global highlight
        global legalHighlights
        if highlight != None:
            self.canvas.delete( highlight )
        if legalHighlights != None:
            # print( legalHighlights )
            for legalMoveObject in legalHighlights:
                self.canvas.delete( legalMoveObject.highlightId )
                # print( "Deleted legal move highlight" )
            legalHighlights = None
        global cellSize
        x = self.column * cellSize + MARGIN
        y = self.row * cellSize + MARGIN
        highlight = self.canvas.create_rectangle(
            x + 2, y + 2, 
            x + cellSize - 2, y + cellSize - 2,
            outline="green", width=3
        )
        legalMoves = getLegalMoves( self )
        legalHighlights = []
        for coord in legalMoves:
            legalX = coord[ 0 ] * cellSize + MARGIN
            legalY = coord[ 1 ] * cellSize + MARGIN
            newHighlightId = self.canvas.create_rectangle(
                legalX + 2, legalY + 2, 
                legalX + cellSize - 2, legalY + cellSize - 2,
                fill="yellow", width=3
            )
            newMove = LegalMove( self.canvas, newHighlightId, self, coord[ 0 ], coord[ 1 ] )
            self.canvas.tag_bind( newHighlightId, '<Button-1>', newMove.onClick )
            legalHighlights.append( newMove )

        

    def moveTo( self, newX: int, newY: int ):
        global highlight
        global legalHighlights
        if highlight != None:
            self.canvas.delete( highlight )
        if legalHighlights != None:
            # print( legalHighlights )
            for legalMoveObject in legalHighlights:
                 self.canvas.delete( legalMoveObject.highlightId )
                 # print( "Deleted legal move highlight" )
            legalHighlights = None

        global boardList
        boardList[ self.row ][ self.column ] = None
        boardList[ newY ][ newX ] = self.player
        self.canvas.delete( self.pieceId )
        self.row = newY
        self.column = newX
        self.draw()
        onMove()
        

class LegalMove:
    def __init__( self, canvas: tk.Canvas, highlightId: int, ownerPiece: Piece, x: int, y: int ):
        self.highlightId = highlightId
        self.canvas = canvas
        self.x = x
        self.y = y
        self.owner = ownerPiece
    
    def onClick( self, event ):
        # print( f"Move piece at { self.owner.column }, { self.owner.row } to { self.x }, { self.y }")
        self.owner.moveTo( self.x, self.y )

highlight: int|None = None
legalHighlights: list[LegalMove]|None = None
boardList: list[list[Piece|None]]
cellSize: int = 0
timeLeft = MOVE_LIMIT # seconds
timerId = None
currentPlayer = PLAYER_1
camp1 = [] # player 1 origin spots
camp2 = [] # player 2 origin spots
score1 = 0 # player 1 score
score2 = 0 # player 2 score

def getPieceDistanceScore( piece: Piece ):
    return 1/10
    

def scoreUpdate():
    global score1, score2
    newScore1 = 0
    newScore2 = 0
    # Loop through board rows
    for row in boardList:
        # Loops through board columns
        for cell in row:
            # If piece exists
            if cell != None:
                print( cell )
                if cell.player == PLAYER_1:
                    # If in other player's goal
                    if (cell.row,cell.column) in camp2:
                        # Add 1 to piece's player's score
                        score1 += 1
                    # Else (not in other player's goal)
                    else:
                        # Add getPieceDistanceScore to piece's player's score
                        score1 += getPieceDistanceScore( cell )
                elif cell.player == PLAYER_2:
                    if (cell.row,cell.column) in camp1:
                        score2 += 1
                    else:
                        score2 += getPieceDistanceScore( cell )
                
    score1 = newScore1
    score2 = newScore2
    canvas.itemconfigure(statusText, text=f"RED:{score1}  GREEN:{score2}")

def onMove():
    global timeLeft, timerId, currentPlayer
    if timerId is not None:
        root.after_cancel(timerId)
    timeLeft = MOVE_LIMIT
    if currentPlayer == PLAYER_1:
        currentPlayer = PLAYER_2
        canvas.itemconfigure(statusText, text="GREEN's Move")
    else:
        currentPlayer = PLAYER_1
        canvas.itemconfigure(statusText, text="RED's Move")
    scoreUpdate()
    countdown()
    

def countdown():
    global timeLeft, timerId
    canvas.itemconfigure(timerText, text=f"Time: {timeLeft}")
    
    if timeLeft > 0:
        timeLeft -= 1
        
        timerId = root.after(1000, countdown)
    else:
        canvas.itemconfigure(statusText, text="Time's up! Turn skipped.")

def getJumpMoves( originX: int, originY: int, visited=None ):
    global boardList
    if visited is None:
        visited = set()
    visited.add( ( originX, originY ) )
    x = originX
    y = originY
    maxX = len( boardList[0] )
    maxY = len( boardList )
    jumpMoves = []
    for localX in range( -1, 2 ):
        neighborX = x + localX
        if -1 < neighborX and neighborX < maxX:
            for localY in range( -1, 2 ):
                neighborY = y + localY
                if ( ( -1 < neighborY and neighborY < maxY )
                    and ( (neighborX, neighborY) != (x, y) ) ):
                        if boardList[ neighborY ][ neighborX ] != None:
                            jumpX = ( neighborX - x ) + neighborX
                            jumpY = ( neighborY - y ) + neighborY 
                            if ( ( ( jumpX, jumpY ) not in visited )
                                and ( -1 < jumpX and jumpX < maxX ) 
                                and ( -1 < jumpY and jumpY < maxY )
                                and boardList[ jumpY ][ jumpX ] == None ):
                                jumpMoves.append( ( jumpX, jumpY ) )
                                jumpMoves = jumpMoves + getJumpMoves( jumpX, jumpY, visited )
    return jumpMoves

# Returns a list of coordinate tuples
def getLegalMoves( piece : Piece ) -> list[tuple[int,int]]:
    global boardList
    x = piece.column
    y = piece.row
    maxX = len( boardList[0] )
    maxY = len( boardList )
    legalMoves = []
    for localX in range( -1, 2 ):
        neighborX = x + localX
        if -1 < neighborX and neighborX < maxX:
            for localY in range( -1, 2 ):
                neighborY = y + localY
                if ( ( -1 < neighborY and neighborY < maxY )
                    and ( (neighborX, neighborY) != (x, y) ) ):
                        if boardList[ neighborY ][ neighborX ] == None:
                            legalMoves.append( ( neighborX, neighborY ) )
                        else:
                            jumpX = ( neighborX - x ) + neighborX
                            jumpY = ( neighborY - y ) + neighborY
                            if ( ( -1 < jumpX and jumpX < maxX ) 
                                and ( -1 < jumpY and jumpY < maxY )
                                and boardList[ jumpY ][ jumpX ] == None ):
                                legalMoves.append( ( jumpX, jumpY ) )
                                legalMoves = legalMoves + getJumpMoves( jumpX, jumpY )
    # print( legalMoves )
    return legalMoves

def doPieceBoard( newBoardList, canvas: tk.Canvas, size: int ):
    global cellSize, camp1, camp2
    letters = [ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P" ]
    for column in range( size ):
        canvas.create_text( MARGIN + cellSize/2 + cellSize*column, BOARD_HEIGHT + MARGIN*1.5, text=letters[column], font=("Arial",24,"bold"), fill="black"  )
    for row in range( size ):
        canvas.create_text( MARGIN/2, MARGIN + cellSize/2 + cellSize*row, text=row+1, font=("Arial",24,"bold"), fill="black" )
        for column in range( size ):
            if ( row, column ) in camp1:
                newPiece = Piece( canvas, PLAYER_1, id, row, column )
                newPiece.draw()
                newBoardList[ row ][ column ] = newPiece
            elif ( row, column ) in camp2:
                newPiece = Piece( canvas, PLAYER_2, id, row, column )
                newPiece.draw()
                newBoardList[ row ][ column ] = newPiece



    return newBoardList

def do16PieceBoard( canvas: tk.Canvas ) -> list[list[Piece|None]]:
    global camp1, camp2
    camp1 = [        (0,0), (0,1), (0,2), (0,3), (0,4),
                     (1,0), (1,1), (1,2), (1,3), (1,4),
                     (2,0), (2,1), (2,2), (2,3),
                     (3,0), (3,1), (3,2),
                     (4,0), (4,1)]
    camp2 = [                                   (11,14), (11,15),
                                       (12,13), (12,14), (12,15),
                              (13,12), (13,13), (13,14), (13,15),
                     (14,11), (14,12), (14,13), (14,14), (14,15),
                     (15,11), (15,12), (15,13), (15,14), (15,15)]
    newBoardList = [ [ None for _ in range( 16 ) ] for _ in range( 16 ) ]
    
    return doPieceBoard( newBoardList, canvas, 16 )

def do10PieceBoard( canvas: tk.Canvas ) -> list[list[Piece|None]]:
    global camp1, camp2
    camp1 = [        (0,0), (0,1), (0,2), (0,3), (0,4),
                     (1,0), (1,1), (1,2), (1,3),
                     (2,0), (2,1), (2,2),
                     (3,0), (3,1),
                     (4,0)]
    camp2 = [                                    (5,9),
                                          (6,8), (6,9),
                                   (7,7), (7,8), (7,9),
                            (8,6), (8,7), (8,8), (8,9),
                     (9,5), (9,6), (9,7), (9,8), (9,9)]
    newBoardList = [ [ None for _ in range( 10 ) ] for _ in range( 10 ) ]

    return doPieceBoard( newBoardList, canvas, 10 )

def do8PieceBoard( canvas: tk.Canvas ) -> list[list[Piece|None]]:
    global camp1, camp2
    camp1 = [        (0,0), (0,1), (0,2), (0,3),
                     (1,0), (1,1), (1,2),
                     (2,0), (2,1),
                     (3,0)]
    camp2 = [                             (4,7),
                                   (5,6), (5,7),
                            (6,5), (6,6), (6,7),
                     (7,4), (7,5), (7,6), (7,7)]
    newBoardList = [ [ None for _ in range( 8 ) ] for _ in range( 8 ) ]

    return doPieceBoard( newBoardList, canvas, 8 )
    
def createBoard( boardSize: int ) -> tuple[ tk.Tk, tk.Canvas ]:
    root = tk.Tk()
    root.title("Halma")
    root.geometry(f"{ WINDOW_WIDTH }x{ WINDOW_HEIGHT }")
    
    rows = boardSize
    columns = boardSize
    global cellSize
    cellSize = min( BOARD_HEIGHT / columns, BOARD_HEIGHT / rows )

    # Create drawable board
    canvas = tk.Canvas( root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="tan" )
    canvas.pack()
    for row in range( rows + 1 ):
        y = MARGIN + row * cellSize
        canvas.create_line( MARGIN, y, columns * cellSize + MARGIN, y )
    for col in range( columns + 1 ):
        x = MARGIN + col * cellSize
        canvas.create_line( x, MARGIN, x, rows * cellSize + MARGIN )
    # Display one player’s starting pieces (e.g., white or black circles) 
    # in one corner(canvas.create_oval). 
    global boardList
    if boardSize == 8:
        boardList = do8PieceBoard( canvas )
    elif boardSize == 10:
        boardList = do10PieceBoard( canvas )
    elif boardSize == 16:
        boardList = do16PieceBoard( canvas )
    return root, canvas

root, canvas = createBoard( 10 )
timerText = canvas.create_text(WINDOW_WIDTH*0.10, MARGIN/2, text=f"Time: {MOVE_LIMIT}", width=WINDOW_WIDTH*0.25, font=("Arial", 24, "bold"))
statusText = canvas.create_text(WINDOW_WIDTH*0.325, MARGIN/2, text="RED's Turn", width=WINDOW_WIDTH*0.25, font=("Arial", 18))
scoreText = canvas.create_text(WINDOW_WIDTH*0.60, MARGIN/2, text="RED:0  GREEN:0", width=WINDOW_WIDTH*0.25, font=("Arial", 12))
msgText = canvas.create_text(WINDOW_WIDTH*0.85, MARGIN/2, text="...", width=WINDOW_WIDTH*0.25, font=("Arial", 10))


root.mainloop()
import tkinter as tk

PADDING = 5
WINDOW_WIDTH = 750
WINDOW_HEIGHT = 750
PLAYER_1 = 1
PLAYER_2 = 2

class Piece:
    def __init__( self, canvas: tk.Canvas, player: int, pieceId: int, row : int, col : int ):
        self.canvas = canvas
        self.player = player
        self.pieceId = pieceId   
        self.row = row
        self.column = col

    def draw( self ):
        global cellSize
        x = self.column * cellSize
        y = self.row * cellSize
        self.pieceId = self.canvas.create_oval( 
                    x + PADDING, y + PADDING,
                    x + cellSize - PADDING, y + cellSize - PADDING,
                    fill="black" 
                )
        self.canvas.tag_bind( self.pieceId, '<Button-1>', self.onClick )

    def onClick( self, event ):
        # print( f"Clicked on {self.player}'s piece. Located at position {self.column}, {self.row}" )
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
        x = self.column * cellSize
        y = self.row * cellSize
        highlight = self.canvas.create_rectangle(
            x + 2, y + 2, 
            x + cellSize - 2, y + cellSize - 2,
            outline="green", width=3
        )
        legalMoves = getLegalMoves( self )
        legalHighlights = []
        for coord in legalMoves:
            legalX = coord[ 0 ] * cellSize
            legalY = coord[ 1 ] * cellSize
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
        

class LegalMove:
    def __init__( self, canvas: tk.Canvas, highlightId: int, ownerPiece: Piece, x: int, y: int ):
        self.highlightId = highlightId
        self.canvas = canvas
        self.x = x
        self.y = y
        self.owner = ownerPiece
    
    def onClick( self, event ):
        print( f"Move piece at { self.owner.column }, { self.owner.row } to { self.x }, { self.y }")
        self.owner.moveTo( self.x, self.y )

highlight: int|None = None
legalHighlights: list[LegalMove]|None = None
boardList: list[list[Piece|None]]
cellSize: int = 0

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
        if -1 < neighborX and neighborX <= maxX:
            for localY in range( -1, 2 ):
                neighborY = y + localY
                if ( ( -1 < neighborY and neighborY <= maxY )
                    and ( (neighborX, neighborY) != (x, y) ) ):
                        if boardList[ neighborY ][ neighborX ] == None:
                            legalMoves.append( ( neighborX, neighborY ) )
                        else:
                            jumpX = ( neighborX - x ) + neighborX
                            jumpY = ( neighborY - y ) + neighborY
                            if ( ( -1 < jumpX and jumpX <= maxX ) 
                                and ( -1 < jumpY and jumpY <= maxY )
                                and boardList[ jumpY ][ jumpX ] == None ):
                                legalMoves.append( ( jumpX, jumpY ) )
    # print( legalMoves )
    return legalMoves

def do8PieceBoard( canvas: tk.Canvas ) -> list[list[Piece|None]]:
    player1Coords = [(0,0), (0,1), (0,2), (0,3),
                     (1,0), (1,1), (1,2),
                     (2,0), (2,1),
                     (3,0)]
    newBoardList = [ [ None for _ in range( 8 ) ] for _ in range( 8 ) ]
    global cellSize

    # Player 1
    for row in range( 8 ):
        for column in range( 8 ):
            if ( row, column ) in player1Coords:
                newPiece = Piece( canvas, PLAYER_1, id, row, column )
                newPiece.draw()
                newBoardList[ row ][ column ] = newPiece

    return newBoardList
    
def createBoard( boardSize: 8 | 10 | 16 ) -> tuple[ tk.Tk, tk.Canvas ]:
    root = tk.Tk()

    root.title("Halma")
    root.geometry(f"{ WINDOW_WIDTH }x{ WINDOW_HEIGHT }")

    if not ( boardSize == 8 | boardSize == 10 | boardSize == 16 ):
        boardSize = 8

    rows = boardSize
    columns = boardSize
    global cellSize
    cellSize = min( WINDOW_WIDTH / columns, WINDOW_HEIGHT / rows )

    # Create drawable board
    canvas = tk.Canvas( root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="tan" )
    canvas.pack()
    for row in range( rows + 1 ):
        y = row * cellSize
        canvas.create_line( 0, y, columns * cellSize, y )
    for col in range( columns + 1 ):
        x = col * cellSize
        canvas.create_line( x, 0, x, rows * cellSize )

    # Display one player’s starting pieces (e.g., white or black circles) 
    # in one corner(canvas.create_oval). 
    global boardList
    boardList = do8PieceBoard( canvas )
    print( boardList )
    return root, canvas

root, canvas = createBoard( 8 )

root.mainloop()
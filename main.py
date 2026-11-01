import tkinter as tk

WINDOW_WIDTH = 750
WINDOW_HEIGHT = 750
PLAYER_1 = 1
PLAYER_2 = 2

highlight: int|None = None

class Piece:
    def __init__( self, canvas: tk.Canvas, player: int, pieceId: int, row : int, col : int ):
        self.canvas = canvas
        self.player = player
        self.pieceId = pieceId   
        self.row = row
        self.column = col

    def draw( self, cellSize: int ):
        x = self.column * cellSize
        y = self.row * cellSize
        self.pieceId = self.canvas.create_oval( 
                    x + 5, y + 5,
                    x + cellSize - 5, y + cellSize - 5,
                    fill="black" 
                )
        self.canvas.tag_bind( self.pieceId, '<Button-1>', self.onClick )

    def onClick( self, event ):
        print( f"Clicked on {self.player}'s piece. Located at position {self.row}, {self.column}" )
        if highlight != None:
            self.canvas.delete( highlight )
        highlight = self.canvas
    
def do8PieceBoard( canvas: tk.Canvas, cellSize: int ) -> list[list[Piece|None]]:
    player1Coords = [(0,0), (0,1), (0,2), (0,3),
                     (1,0), (1,1), (1,2),
                     (2,0), (2,1),
                     (3,0)]
    newBoardList = [ [ None for _ in range( 8 ) ] for _ in range( 8 ) ]
    
    # Player 1
    for row in range( 8 ):
        for column in range( 8 ):
            if ( row, column ) in player1Coords:
               
                newPiece = Piece( canvas, PLAYER_1, id, row, column )
                newPiece.draw( cellSize )
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
    boardList = do8PieceBoard( canvas, cellSize )
    print( boardList )
    return root, canvas

root, canvas = createBoard( 8 )

root.mainloop()
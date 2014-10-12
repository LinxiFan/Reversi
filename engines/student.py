from engines import Engine
from copy import deepcopy

DEPTH = 4
class StudentEngine(Engine):
    """ Game engine that implements a simple fitness function maximizing the
    difference in number of pieces in the given color's favor. """
    def __init__(self):
        self.alpha_beta = False

    def get_move(self, board, color, move_num=None,
                 time_remaining=None, time_opponent=None):
        """ Return a move for the given color that maximizes the difference in 
        number of pieces for that color. """
        
        W, B = to_bitboard(board)
        
        print_bitboard(W)
        print_bitboard(B)
        
        print "white me"
        print_bitboard(move_gen(W, B))
        print "black me"
        print_bitboard(move_gen(B, W))
        
        print [to_bitmove(m) for m in board.get_legal_moves(color)]
        
        return board.get_legal_moves(color)[0]

        # Get a list of all legal moves.
#         if self.alpha_beta:
#             return self.alphabeta(board, color, DEPTH, -float("inf"), float("inf"))[1]
#         else:
#             return self.minimax(board, color, DEPTH)[1]
    
    def minimax(self, board, color, depth):
        if depth == 0:
            return (self.eval(board, color), None)
        movelist = board.get_legal_moves(color)
        best = - float("inf")
        bestmv = None if len(movelist)==0 else movelist[0]
        for mv in movelist:
            newboard = deepcopy(board)
            newboard.execute_move(mv, color)
            res = self.minimax(newboard, color * -1, depth - 1)
            score = - res[0]
            if score > best:
                best = score
                bestmv = mv
        #print "color", "white" if color == 1 else "black", "depth", depth, "best", best, "legals", len(movelist)
        return (best, bestmv)
    
    def minimax_bit(self, board, color, depth):
        if depth == 0:
            return (self.eval(board, color), None)
        movelist = board.get_legal_moves(color)
        best = - float("inf")
        bestmv = None if len(movelist)==0 else movelist[0]
        for mv in movelist:
            newboard = deepcopy(board)
            newboard.execute_move(mv, color)
            res = self.minimax(newboard, color * -1, depth - 1)
            score = - res[0]
            if score > best:
                best = score
                bestmv = mv
        #print "color", "white" if color == 1 else "black", "depth", depth, "best", best, "legals", len(movelist)
        return (best, bestmv)
    
    def alphabeta(self, board, color, depth, alpha, beta):
        if depth == 0:
            return (self.eval(board, color), None)
        movelist = board.get_legal_moves(color)
        best = alpha
        bestmv = None if len(movelist)==0 else movelist[0]
        for mv in movelist:
            newboard = deepcopy(board)
            newboard.execute_move(mv, color)
            res = self.alphabeta(newboard, color * -1, depth - 1, -beta, -best)
            score = - res[0]
            if score > best:
                best = score
                bestmv = mv
            if best >= beta:
                return (best, bestmv)
        return (best, bestmv)
            
    def eval(self, board, color):
        # Count the # of pieces of each color on the board
        num_pieces_op = len(board.get_squares(color*-1))
        num_pieces_me = len(board.get_squares(color))

        # Return the difference in number of pieces
        return num_pieces_me - num_pieces_op

    def _get_cost(self, board, color, move): return 0
    
#----- bitboard representation -----
def move_gen_sub(P, mask, dir):
    flip_l = long(0)
    flip_r = long(0)
    mask_l = long(0)
    mask_r = long(0)
    dir2 = long(dir * 2)
    
    flip_l  = mask & (P << dir)
    flip_r  = mask & (P >> dir)
    flip_l |= mask & (flip_l << dir)
    flip_r |= mask & (flip_r >> dir)
    mask_l  = mask & (mask << dir)
    mask_r  = mask & (mask >> dir)
    flip_l |= mask_l & (flip_l << dir2)
    flip_r |= mask_r & (flip_r >> dir2)
    flip_l |= mask_l & (flip_l << dir2)
    flip_r |= mask_r & (flip_r >> dir2)
    return (flip_l << dir) | (flip_r >> dir)

def move_gen(P, O):
    mask = long(O & 0x7E7E7E7E7E7E7E7E)
    return (move_gen_sub(P, mask, 1) \
            | move_gen_sub(P, O, 8)  \
            | move_gen_sub(P, mask, 7) \
            | move_gen_sub(P, mask, 9)) & ~(P|O)
            
def print_bitboard(BB):
    bitarr = [1 if (1<<i) & BB != 0 else 0 for i in range(64)]
    s = ""
    for rk in range(7, -1, -1):
        for fl in range(8):
            s += str(bitarr[fl + 8 * rk]) + " "
        s += "\n"
    print s

def to_bitboard(board):
    W = 0L
    B = 0L
    for r in range(8):
        for c in range(8):
            if board[c][r] == -1:
                B |= (1 << (8 * r + c))
            elif board[c][r] == 1:
                W |= (1 << (8 * r + c))
    return (W, B)

def to_move(bitmove):
    return (bitmove % 8, bitmove / 8)

def to_bitmove(move):
    return move[0] + 8 * move[1]

                    
engine = StudentEngine

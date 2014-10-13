from __future__ import absolute_import
from engines import Engine
from copy import deepcopy

DEPTH = 7

class StudentEngine(Engine):
    """ Game engine that implements a simple fitness function maximizing the
    difference in number of pieces in the given color's favor. """
    def __init__(self):
        self.alpha_beta = False
        fill_bit_table()
        fill_lsb_table()
        fill_radial_map()

    def get_move(self, board, color, move_num=None,
                 time_remaining=None, time_opponent=None):
        """ Return a move for the given color that maximizes the difference in 
        number of pieces for that color. """
        
        W, B = to_bitboard(board)
        
        wb = (W, B) if color > 0 else (B, W)
        
        if self.alpha_beta:
            res = self.alphabeta_bit(wb[0], wb[1], DEPTH, -float("inf"), float("inf"))
        else:
            res = self.minimax_bit(wb[0], wb[1], DEPTH)
        return to_move(res[1])

        # Get a list of all legal moves.
#         if self.alpha_beta:
#             return self.alphabeta(board, color, DEPTH, -float("inf"), float("inf"))[1]
#         else:
#             return self.minimax(board, color, DEPTH)[1]
        # debugging
#         return self.debug_movegen(board, color, DEPTH)[1]
    
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
    
    def minimax_bit(self, W, B, depth):
        if depth == 0:
            return (count_bit(W) - count_bit(B), None)
        movemap = move_gen(W, B)
        best = - float("inf")
        bestmv = None
        if movemap != 0:
            bestmv, movemap = pop_lsb(movemap)
        else:
            return (best, None)
        
        mv = bestmv
        while True:
            tmpW = W
            tmpB = B
            flipmask = flip(W, B, mv) 
            tmpW ^= flipmask | BIT[mv]
            tmpB ^= flipmask

            score = -self.minimax_bit(tmpB, tmpW, depth - 1)[0]
            if score > best:
                best = score
                bestmv = mv
            
            if movemap == 0:
                break
            else:
                mv, movemap = pop_lsb(movemap)
            
        #print "color", "white" if color == 1 else "black", "depth", depth, "best", best, "legals", len(movelist)
        return (best, bestmv)
    
    def alphabeta_bit(self, W, B, depth, alpha, beta):
        if depth == 0:
            return (count_bit(W) - count_bit(B), None)
        movemap = move_gen(W, B)
        best = alpha
        bestmv = None
        if movemap != 0:
            bestmv, movemap = pop_lsb(movemap)
        else:
            return (best, None)
        mv = bestmv
        
        while True:
            tmpW = W
            tmpB = B
            flipmask = flip(W, B, mv) 
            tmpW ^= flipmask | BIT[mv]
            tmpB ^= flipmask

            res = self.alphabeta_bit(tmpB, tmpW, depth - 1, -beta, -best)
            score = - res[0]
            if score > best:
                best = score
                bestmv = mv
            if best >= beta:
                return (best, bestmv)
            
            if movemap == 0:
                break
            else:
                mv, movemap = pop_lsb(movemap)
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
    
    #------------- DEBUG ONLY ------------
    def debug_movegen(self, board, color, depth):
        if depth == 0:
            return (self.eval(board, color), None)
        movelist = board.get_legal_moves(color)

        W, B = to_bitboard(board)
        movelistw = sorted([to_bitmove(m) for m in board.get_legal_moves(1)])
        movelistb = sorted([to_bitmove(m) for m in board.get_legal_moves(-1)])
        movemapw = move_gen(W, B)
        movemapb = move_gen(B, W)
        w_count = count_bit(movemapw)
        b_count = count_bit(movemapb)
        assert w_count == len(movelistw)
        assert b_count == len(movelistb)
        i = 0
        while movemapw != 0:
            m, movemapw = pop_lsb(movemapw)
            assert movelistw[i] == m
            i += 1
        assert w_count == i
        i = 0
        while movemapb != 0:
            m, movemapb = pop_lsb(movemapb)
            assert movelistb[i] == m
            i += 1
        assert b_count == i
        
        best = - float("inf")
        bestmv = None if len(movelist)==0 else movelist[0]
        for mv in movelist:
            newboard = deepcopy(board)
            newboard.execute_move(mv, color)

            ww, bb = to_bitboard(newboard)
            tmpW = W
            tmpB = B
            mvtmp = to_bitmove(mv)
            if color > 0:
                flipmask = flip(W, B, mvtmp) 
                tmpW ^= flipmask | BIT[mvtmp]
                tmpB ^= flipmask
            else:
                flipmask = flip(B, W, mvtmp) 
                tmpB ^= flipmask | BIT[mvtmp]
                tmpW ^= flipmask
            
            try:
                assert ww == tmpW
                assert bb == tmpB
            except AssertionError:
                print "--------------------"
                board.display([1,2,3])
                print "move"
                print_bitboard(BIT[mvtmp])
                print "FLIP"
                print_bitboard(flipmask)
                print "CORRECT W"
                print_bitboard(ww)
                print_bitboard(tmpW)
                print "CORRECT B"
                print_bitboard(bb)
                print_bitboard(tmpB)
                raise AssertionError
            res = self.minimax(newboard, color * -1, depth - 1)
            score = - res[0]
            if score > best:
                best = score
                bestmv = mv
        return (best, bestmv)
    
######-------- bitboard representation -------
def fill_bit_table():
    global BIT
    BIT = [1 << n for n in range(64)]

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
                B |= BIT[8 * r + c]
            elif board[c][r] == 1:
                W |= BIT[8 * r + c]
    return (W, B)

def to_move(bitmove):
    return (bitmove % 8, bitmove / 8)

def to_bitmove(move):
    return move[0] + 8 * move[1]

RADIAL_MAP = {}

def fill_radial_map():
    rad_map = {-1: (-1, 0), 1:(1, 0), -8:(0, -1), 8:(0, 1), -7:(1, -1), 7:(-1, 1), -9:(-1, -1), 9:(1, 1)}
    for dir, dirtup in rad_map.items():
        lis = [0] * 64
        for sqr in range(64):
            mask = 0L
            sq = sqr
            x, y = to_move(sq)
            sq += dir
            x += dirtup[0]
            y += dirtup[1]
            while 0 <= x < 8 and 0 <= y < 8 and 0 <= sq < 64:
                mask |= BIT[sq]
                sq += dir
                x += dirtup[0]
                y += dirtup[1]
            lis[sqr] = mask
        RADIAL_MAP[dir] = lis

DIR = [
[1, -7, -8],
[-1,-9,-8],
[1,8,9],
[7,8,-1],
[8,9,1,-7,-8],
[-1,1,-7,-8,-9],
[7,8,-1,-9,-8],
[7,8,9,-1,1],
[-1, 1, -7,7,-8,8,-9,9]]

SQ_DIR = \
[2, 2, 7, 7, 7, 7, 3, 3,
 2, 2, 7, 7, 7, 7, 3, 3 ,
 4, 4, 8, 8, 8, 8, 6, 6,
 4, 4, 8, 8, 8, 8, 6, 6,
 4, 4, 8, 8, 8, 8, 6, 6,
 4, 4, 8, 8, 8, 8, 6, 6,
 0, 0, 5, 5, 5, 5, 1, 1,
 0, 0, 5, 5, 5, 5, 1, 1 ]

def flip(W, B, mv):
    mask = 0L
    for dir in DIR[SQ_DIR[mv]]:
        mvtmp = mv
        mvtmp += dir
        while mvtmp >= 0 and mvtmp < 64 and (BIT[mvtmp] & B != 0) and (BIT[mvtmp] & RADIAL_MAP[dir][mv] != 0):
            mvtmp += dir
        if (mvtmp >= 0 and mvtmp < 64 and BIT[mvtmp] & W != 0) and (BIT[mvtmp] & RADIAL_MAP[dir][mv] != 0):
            mvtmp -= dir
            while mvtmp != mv:
                mask |= BIT[mvtmp]
                mvtmp -= dir

    return mask

FULL_MASK = 0xFFFFFFFFFFFFFFFF
LSB_HASH = 0x07EDD5E59A4E28C2
def fill_lsb_table():
    bitmap = 1L
    global LSB_TABLE
    LSB_TABLE = [0] * 64
    for i in range(64):
        LSB_TABLE[(((bitmap & (~bitmap + 1L)) * LSB_HASH) & FULL_MASK) >> 58] = i
        bitmap <<= 1

def lsb(bitmap):
    return LSB_TABLE[(((bitmap & (~bitmap + 1L)) * LSB_HASH) & FULL_MASK) >> 58]

def pop_lsb(bitmap):
    l= lsb(bitmap)
    bitmap &= bitmap-1
    return l, bitmap & FULL_MASK

def count_bit(b):
    b -=  (b >> 1) & 0x5555555555555555;
    b  = (((b >> 2) & 0x3333333333333333) + (b & 0x3333333333333333));
    b  = ((b >> 4) + b)  & 0x0F0F0F0F0F0F0F0F;
    return ((b * 0x0101010101010101) & FULL_MASK) >> 56

def count_bit_2(b):
    raise DeprecationWarning
    cnt = 0
    for i in range(64):
        if b & BIT[i] != 0:
            cnt += 1
    return cnt

engine = StudentEngine
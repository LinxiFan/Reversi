from __future__ import absolute_import
from engines import Engine
from copy import deepcopy
import random 

DEPTH = 2

class StudentEngine(Engine):
    """ Game engine that implements a simple fitness function maximizing the
    difference in number of pieces in the given color's favor. """
    def __init__(self):
        self.alpha_beta = False
        fill_bit_table()
        fill_lsb_table()
        fill_radial_map()
#         for k, v in RADIAL_MAP.items():
#             print "======== ", k, " ========"
#             for a in v:
#                 print_bitboard(a)
#             a = raw_input("resume")

    def get_move(self, board, color, move_num=None,
                 time_remaining=None, time_opponent=None):
        """ Return a move for the given color that maximizes the difference in 
        number of pieces for that color. """
        
        W, B = to_bitboard(board)
#         print count_bit(W)
#         print count_bit(B)
#         print_bitboard(W)
#         print_bitboard(B)
        
        # Get a list of all legal moves.
        if self.alpha_beta:
            return self.alphabeta(board, color, DEPTH, -float("inf"), float("inf"))[1]
        else:
            return self.minimax(board, color, DEPTH)[1]
    
    def minimax(self, board, color, depth):
        if depth == 0:
            return (self.eval(board, color), None)
        movelist = board.get_legal_moves(color)

        W, B = to_bitboard(board)
        movelistw = sorted([to_bitmove(m) for m in board.get_legal_moves(1)])
        movelistb = sorted([to_bitmove(m) for m in board.get_legal_moves(-1)])
        movemapw = move_gen(W, B)
        movemapb = move_gen(B, W)
        wc = count_bit(movemapw)
        bc = count_bit(movemapb)
#         i = 0
#         while movemapw != 0:
#             m, movemapw = pop_lsb(movemapw)
#             print i, len(movelistw), movemapw
#             assert movelistw[i] == m
#             i += 1
#         assert wc == i
#         i = 0
#         while movemapb != 0:
#             m, movemapb = pop_lsb(movemapb)
#             print i, len(movelistb), movemapb
#             assert movelistb[i] == m
#             i += 1
#         assert bc == i
        
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
        #print "color", "white" if color == 1 else "black", "depth", depth, "best", best, "legals", len(movelist)
        return (best, bestmv)
    
    def minimax_bit(self, W, B, color, depth):
        if depth == 0:
            return (color * (count_bit(W) - count_bit(B)), None)
        movemap = move_gen(W, B) if color > 0 else move_gen(B, W)
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
            if color > 0:
                flipmask = flip(W, B, mv) 
                tmpW ^= flipmask | BIT[mv]
                tmpB ^= flipmask
            else:
                flipmask = flip(B, W, mv) 
                tmpB ^= flipmask | BIT[mv]
                tmpW ^= flipmask

            score = -self.minimax_bit(tmpW, tmpB, color* -1, depth - 1)[0]
            if score > best:
                best = score
                bestmv = mv
            
            if movemap == 0:
                break
            else:
                mv, movemap = pop_lsb(movemap)
            
        #print "color", "white" if color == 1 else "black", "depth", depth, "best", best, "legals", len(movelist)
        print "bestmv", bestmv
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

DIR = [-1, 1, -8, 8, -7, 9, -9, 7]
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

def flip(W, B, mv):
    mask = 0L
    for dir in DIR:
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
    global LsbTbl
    LsbTbl = [0] * 64
    for i in range(64):
        LsbTbl[(((bitmap & (~bitmap + 1L)) * LSB_HASH) & FULL_MASK) >> 58] = i
        bitmap <<= 1

def lsb(bitmap):
    return LsbTbl[(((bitmap & (~bitmap + 1L)) * LSB_HASH) & FULL_MASK) >> 58]

def pop_lsb(bitmap):
    l= lsb(bitmap)
    bitmap &= bitmap-1
    return l, bitmap

def count_bit(b):
    cnt = 0
    for i in range(64):
        if b & BIT[i] != 0:
            cnt += 1
    return cnt
#     b -=  (b >> 1) & 0x5555555555555555;
#     b  = (((b >> 2) & 0x3333333333333333) + (b & 0x3333333333333333));
#     b  = ((b >> 4) + b)  & 0x0F0F0F0F0F0F0F0F;
#     return (b * 0x0101010101010101) >> 56

engine = StudentEngine
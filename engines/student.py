from engines import Engine
from copy import deepcopy

class StudentEngine(Engine):
    """ Game engine that implements a simple fitness function maximizing the
    difference in number of pieces in the given color's favor. """
    def __init__(self):
        self.alpha_beta = False

    def get_move(self, board, color, move_num=None,
                 time_remaining=None, time_opponent=None):
        """ Return a move for the given color that maximizes the difference in 
        number of pieces for that color. """
        # Get a list of all legal moves.
        if self.alpha_beta:
            return self.alphabeta(board, color, 5, -float("inf"), float("inf"))[1]
        else:
            return self.minimax(board, color, 4)[1]
    
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
    
    def alphabeta(self, board, color, depth, alpha, beta):
        if depth == 0:
            return (self.eval(board, color), None)
        movelist = board.get_legal_moves(color)
        alpha = - float("inf")
        bestmv = None if len(movelist)==0 else movelist[0]
        for mv in movelist:
            newboard = deepcopy(board)
            newboard.execute_move(mv, color)
            res = self.alphabeta(newboard, color * -1, depth - 1, -beta, -alpha)
            score = - res[0]
            if score > beta:
                return (beta, bestmv)
            if score > alpha:
                alpha = score
                bestmv = mv
        return (alpha, bestmv)
            
    def eval(self, board, color):
        # Count the # of pieces of each color on the board
        num_pieces_op = len(board.get_squares(color*-1))
        num_pieces_me = len(board.get_squares(color))

        # Return the difference in number of pieces
        return num_pieces_me - num_pieces_op


    def _get_cost(self, board, color, move):
        """ Return the difference in number of pieces after the given move 
        is executed. """
        # Return the difference in number of pieces
        return 0
        
engine = StudentEngine

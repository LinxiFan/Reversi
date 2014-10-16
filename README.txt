Linxi Fan
lf2422
AI HW 2  Othello engine

Part I  Implementation of search

[1] Minimax
Let A denote my engine's color, and B the opponent.

My evaluation heuristic function is primarily based on three components:

- Piece score sum. I assign a weight to each square of the board.
  Then the piece difference between A and B can be calculated as:
  sum(weight[sq] * A[sq]) - sum(weight[sq] * B[sq])
  where sq goes from 0 to 63, and A[sq] = 1 if that square is occupied by A,
  otherwise A[sq] is 0.

- Edge stability. I have read quite a few papers and book chapters on
  othello edge stability. Apparently, the top engines use a massive
  precalculated table to enumerate edge configurations exhaustively. Due to
  limited time, I only implement a basic edge stability evaluator that looks
  only at squares adjacent to the corners.

- Mobility. The number of legal moves is essential to a strong engine,
  because it implies how many opponent pieces you can capture in the future.
  Initially, I tried the difference between mobility(A) and mobility(B), but
  it didn't work as well as mobility(A) alone.

The overall heuristic function is a weighted sum of the above. I have spent
a lot of time tuning the relative weights. It seems that I cannot get the
optimal performance without some machine learning procedures, which are too
complicated to do in this assignment. So I tuned the weights by playing the
engine against itself 100 times. If the number of wins is significantly
higher than the number of losses, I would update the weights accordingly. 

The minimax search is implemented as instructed in "AI - a Modern Approach".

The engine is consistently able to beat either the random or the greedy
engine even with low depth. 

Note: the current implementation limits the minimax depth to 3.

[2] Alpha-beta
The alpha-beta pruning is an optional feature that can be turned on by -aW
or -aB

The following is a list of techniques I have tried. I did not include all of
below in my code, because some of them do not perform well and mess up the
code:

- Bitboard: this is so far the best advanced technique I used. Thanks to the
  efficiency of bitwise operations, bitboard accelerated my engine by
  at least 50%. On the other hand, it was very hard to debug and took me a
  long time to implement. 

- Transposition table: this was used in part II to count duplications. From
  what I read online, transposition table works best for chess. It didn't
  really help my engine, but consumed a lot of memory, so I commented out the
  code for fear of memory overflow. 

- Move ordering: I did some basic move ordering, but experiments did not
  yield much better results. 

- Principal Variation Search (PVS): a special search technique that can be
  embedded in alpha-beta, like:
  score = PVS(-(best + 1), -best)
  In practice, it did not help much. 

- I also tried a few other pruning techniques, like killer moves. 

I have dedicated code to handle timing. The rules are rather conservative, 
based empirically on thousands of mock tournaments I ran with various 
versions of my engine. 
For example, the current search depth may depend on the time spent on the
previous get_move(). 

Under 60s constraint, my engine can typically search up to a depth of 6 plies.

Thanks for reviewing my work!


===== References =====
https://chessprogramming.wikispaces.com/Kogge-Stone+Algorithm
De Bruijn Multiplication, http://chessprogramming.wikispaces.com/BitScan
http://kartikkukreja.wordpress.com/2013/03/30/heuristic-function-for-reversiothello/
http://radagast.se/othello/Help/strategy.html
http://www.samsoft.org.uk/reversi/strategy.htm
http://radagast.se/othello/howto.html
http://ledpup.blogspot.com/2012/07/computer-othello-part-4-trials-and.html
http://repository.cmu.edu/cgi/viewcontent.cgi?article=3452&context=compscis
http://www.fierz.ch/strategy2.htm
http://www.samsoft.org.uk/reversi/openings.htm
"AI - a Modern Approach", Peter Norvig
"Paradigms of Artificial Intelligence Programming - Case Studies in Common
Lisp", Peter Norvig

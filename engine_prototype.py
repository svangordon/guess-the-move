import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("stockfish")

# board = chess.Board()
# info = engine.analyse(board, chess.engine.Limit(time=0.100))
# print("Score:", info["score"])
# # Score: +20

# board = chess.Board("r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4")
board = chess.Board("1r4kb/p2R3p/5p1B/4p1p1/4N3/1P3P2/q5PK/3R4 w - - 0 35")
# board = chess.Board("1r4kb/p2R3p/5p1B/4p1p1/4N3/1P3P2/P1q3PK/3R4 b - - 1 34")
info = engine.analyse(board, chess.engine.Limit(time=30), multipv=5)
print("Score:", info["score"])
# Score: #1

# engine.quit()

infos = []

with engine.analysis(board) as analysis:
    for info in analysis:
        infos.append(info)
        print(info.get("score"), info.get("pv"))

        # Unusual stop condition.
        if info.get("hashfull", 0) > 900:
            break

engine.quit()
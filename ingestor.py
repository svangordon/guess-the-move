import chess
import chess.pgn
import chess.engine


class Ingestor:
    """Responsible for reading a PGN file, running an analysis on its positions,
    and then uploading that analysis to the database."""

    def __init__(self, pgn_handle, user_player=None):
        # self.pgn_path = pgn_path
        self.game = chess.pgn.read_game(pgn_handle)
        self.user_player = user_player

    def set_user_player(self, user_role):
        self.user_role = user_role


class AnalysisVisitor(chess.pgn.BaseVisitor):
    def __init__(self, game):
        self.analysis_results = []
        self.game = game
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")

    # def begin_game(self):
    #     """Called at the start of a game."""
    #     print("We're begining the game!")

    # def visit_board(self, board):
    #     print(board.unicode())
    #     self.analyse_board(board)

    def analyse_board(self, board):
        # info = engine.analyse(board, chess.engine.Limit(depth=20))
        info = self.engine.analyse(
            board, chess.engine.Limit(depth=20), multipv=5, game=self.game
        )
        self.analysis_results.append(info)

    def end_game(self):
        self.engine.quit()


if __name__ == "__main__":
    app = Ingestor("./data/opera_game.pgn")
    vis = MyVisitor(app.game)
    app.game.accept(vis)

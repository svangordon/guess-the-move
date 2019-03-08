import chess
import chess.pgn
import chess.engine


class Analyzer:
    """Responsible for reading a PGN file, running an analysis on its positions,
    and then uploading that analysis to the database."""

    def __init__(self, pgn_handle):
        # self.pgn_path = pgn_path
        self.game = chess.pgn.read_game(pgn_handle)
        self.engine = None
        pgn_handle.close()

        self.set_player_color()

        # self.user_player = user_player
        self.analysis = []

    def set_player_color(self):
        result = self.game.end().board().result()
        if result == "1-0":
            self.player_color = chess.WHITE
        elif result == "0-1":
            self.player_color = chess.BLACK
        else:
            raise ValueError(
                "Attempting to analyze game without decisive result, ie no win/loss."
            )

    def analyze_game(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")

        self.game.accept(AnalysisVisitor(self.game, self))
        # self.engine.quit()

        # self.analysis = analysis

    def close(self):
        self.engine.quit()


class AnalysisVisitor(chess.pgn.BaseVisitor):
    def __init__(self, game, parent):
        self.analysis_results = []
        self.parent = parent
        self.game = game

    def visit_board(self, board):
        if board.turn == self.parent.player_color:
            return
        analysis = self.parent.engine.analysis(
            board, chess.engine.Limit(depth=20), multipv=5, game=self.game
        )
        self.parent.analysis.append(analysis)

    def end_game(self):
        self.parent.analysis = [result.multipv for result in self.parent.analysis]
        self.parent.engine.quit()


if __name__ == "__main__":
    app = Analyzer("./data/opera_game.pgn")
    vis = AnalysisVisitor(app.game, app)
    app.game.accept(vis)

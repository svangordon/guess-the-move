import chess
import chess.pgn
import game_analysis

# import pytest


class Testanalyzer(object):
    pgn_path = "./data/opera_game.pgn"

    def get_analyzer(self):
        return game_analysis.Analyzer(open(self.pgn_path))

    def test_setup(self):
        analyzer = self.get_analyzer()
        assert isinstance(analyzer, game_analysis.Analyzer)

    def test_game_load(self):
        analyzer = self.get_analyzer()
        assert isinstance(analyzer.game, chess.pgn.Game)

    def test_user_color(self):
        analyzer = self.get_analyzer()
        assert analyzer.player_color == chess.WHITE

        analyzer = game_analysis.Analyzer(open("./data/mcconnell_morphy_1849.pgn"))
        assert analyzer.player_color == chess.BLACK

    def test_analyze_game(self):
        analyzer = self.get_analyzer()
        analyzer.analyze_game()
        assert len(analyzer.analysis) == 17

    def test_multipv(self):

        analyzer = game_analysis.Analyzer(open("./opera_game.pgn"))
        analyzer.analyze_game()
        assert any([len(result) > 1 for result in analyzer.analysis])

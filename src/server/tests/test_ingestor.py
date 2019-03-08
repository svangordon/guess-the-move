import chess
import chess.pgn
import analysis

import pytest

opera_game = "./data/opera_game.pgn"
mcconnell_morphy = "./data/mcconnell_morphy_1849.pgn"

test_game = opera_game


@pytest.fixture
def analyzer(pgn_path=test_game):
    import analysis

    anal = analysis.Analyzer(open(test_game))
    return anal


class TestAnalyzer(object):
    def test_setup(self, analyzer):
        assert isinstance(analyzer, analysis.Analyzer)

    def test_game_load(self, analyzer):
        assert isinstance(analyzer.game, chess.pgn.Game)

    @pytest.mark.parametrize(
        "game,color", [(opera_game, chess.WHITE), (mcconnell_morphy, chess.BLACK)]
    )
    def test_user_color(self, game, color):
        anal = analysis.Analyzer(open(game))
        assert anal.player_color == color

    def test_analyze_game(self, analyzer):
        analyzer.analyze_game()
        assert len(analyzer.analysis) == 17

    def test_multipv(self):
        analyzer = analysis.Analyzer(open("./data/opera_game.pgn"))
        analyzer.analyze_game()
        assert any([len(result) > 1 for result in analyzer.analysis])

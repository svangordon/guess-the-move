import logging
import difflib
import unittest

import chess
import chess.pgn
import chess.engine

class TestGameImport(unittest.TestCase):
    """Test importing a game."""

    def setUp(self):
        from ingestor import Ingestor
        pgn_path = "./data/opera_game.pgn"
        self.pgn_path = pgn_path
        self.ingestor = Ingestor(self.pgn_path)
        self.maxDiff = None

    def test_load_pgn(self):
        """Importer should be able to read a game from pgn, and use it to create a chess.Game object."""
        self.assertEqual(type(self.ingestor.game), chess.pgn.Game)
    
    def test_headers(self):
        """Importer should be able to read the headers from the game."""
        with open('./tests/data/opera_game_headers', "r") as fp:
            headers = fp.readlines()
            self.assertTrue(len(headers) == 12)
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
            pgn_string = self.ingestor.game.accept(exporter)            
            for file_header in headers:
                self.assertTrue(file_header in pgn_string)

    def test_pgn_text(self):
        """All lines of text from pgn file should be in game pgn."""

        # Write the pgn to a temp file
        with open('./tests/data/temp', 'w') as temp_handle:
            exporter = chess.pgn.FileExporter(handle=temp_handle, headers=True, variations=True, comments=True)
            self.ingestor.game.accept(exporter)

        line_number = 0
        with open('./tests/data/opera_game_output', "r") as output_handle:
            with open('./tests/data/temp', 'r') as temp_handle:
                output_line = output_handle.readline()
                temp_line = temp_handle.readline()
                with self.subTest(line_number=line_number, output_line=output_line, temp_line=temp_line):
                    self.assertEqual(output_line, temp_line)
                line_number += 1

class TestGameAnalysis(unittest.TestCase):

    def setUp(self):
        # self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish", debug=True)


    def test_simple_analysis(self):
        """Test that we can successfully analyze a basic position."""
        board = chess.Board("r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4")
        info = self.engine.analyse(board, chess.engine.Limit(depth=20))
        self.assertEqual(str(info['score']), '#+1')
    
    def test_best_moves(self):
        """Test that we can find the N best moves."""
        engine = chess.engine.SimpleEngine.popen_uci("stockfish", debug=True)
        board = chess.Board("r2qr1k1/pb2npp1/1pn1p2p/8/3P4/P1PQ1N2/B4PPP/R1B1R1K1 w - - 2 15")
        analysis = engine.analysis(board, chess.engine.Limit(depth=10), multipv=3)

        self.assertEqual(len(analysis.multipv), 3)       

    def tearDown(self):
        self.engine.quit()




class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
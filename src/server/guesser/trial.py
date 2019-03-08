from pprint import pprint

import chess
import chess.pgn
import chess.engine


def cls():
    print(chr(27) + "[2J")


def print_position(node):
    # cls()
    print(node.board().unicode())
    if game.move:
        print("Last move:", game.san())


def advance(game):
    return game.variation(0)


def get_input():
    return input("Enter move:")


def loop(game, player_move=None, had_error=False):
    cls()
    print_position(game)
    if player_move:
        print("You:", game.board().san(player_move), "Them:", game.board().san())

    if had_error:
        print("Not legal move.")
    player_input = get_input()
    player_move = game.board().parse_san(player_input)
    if not game.board().is_legal(player_move):
        return (game, None)
    return (advance(game), player_input)


class Game(object):
    def __init__(self, pgn, user_color, starting_turn):
        self.pgn = pgn
        self.user_color = user_color
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        with open(pgn) as fs:
            self.game = chess.pgn.read_game(fs)
        self.limit = chess.engine.Limit(time=2)
        self.mainline = list(self.game.mainline())
        self.current_turn = 0

        self.player_move_analysis = []
        self.text_move_analysis = []
        self.analysis_results = []

        self.user_moves = []

        self._last_user_move = None

        self.has_started = False
        self.last_input_invalid = False

        self.starting_turn = starting_turn

        self.score = {
            "same": 0,
            "inaccuracy": 0,
            "mistake": 0,
            "blunder": 0,
            "not_worse": 0,
            "better": 0,
        }

    def current_node(self):
        if self.current_turn == 0:
            return self.game
        else:
            return self.mainline[self.current_turn]

    def next_node(self):
        return self.mainline[self.current_turn + 1]

    def last_move(self):
        if self.current_node().move:
            return self.current_node().san()
        else:
            return None

    def current_board(self):
        return self.current_node().board()

    def cls(self):
        print(chr(27) + "[2J")

    def advance(self):
        # self.node = next(self.mainline)
        self.current_turn += 1

    def user_san(self):
        return str(self._last_user_move)
        # return str(self.current_node().variation(1).san())

    def last_text_move(self):
        return str(self.last_move())

    def draw(self):
        self.cls()
        # print("analysis results", self.analysis_results)

        # Print headers
        print(self.game.headers["White"], "-", self.game.headers["Black"])

        # Print the actual board
        print(self.current_board().unicode())

        print("Last move:", self.last_move())

        if self.last_input_invalid:
            print("Sorry, that is not a valid input.")
            self.last_input_invalid = False

        if self.analysis_results:
            try:
                print(self.current_analysis())
            except IndexError:
                pass
            # print("")
            # "Your move: " + self.current_user_move() + " Evaluation: " + str(self.user_move_analysis[-1]['score']),
            # "Text move: " + self.last_text_move() + " Evaluation: " + str(self.text_move_analysis[-1]['score'])
            # "Your move: " + str(node.variation(0).move) + " Evaluation: " + str(text_move_info['score'])

        # if self.current_turn != 0:
        #     print('Last move:', self.node.san())

        # Print the last move
        # if (self.node.move):

    def current_analysis(self):
        if self.analysis_results[-1] == "same":
            return "You chose the same move"
        else:
            return "Your move:\t{}\tEval: {}\nTheir move:\t{}\tEval: {}\n{}".format(
                self.user_san(),
                self.analysis_results[-1][0],
                self.last_text_move(),
                self.analysis_results[-1][1],
                self.get_move_annotation(
                    self.analysis_results[-1][0], self.analysis_results[-1][1]
                ),
            )

    def add_user_move(self, move):
        self.mainline[self.current_turn] = self.mainline[
            self.current_turn
        ].add_variation(move)

    def wait(self):
        input("Please press enter...")

    def get_user_move(self):
        input_str = input("Enter move: ")
        try:
            user_input = self.current_node().board().parse_san(input_str)
            assert self.current_node().board().is_legal(user_input) == True
            self.last_input_invalid = False
            self._last_user_move = user_input

            return user_input
        except (ValueError, AssertionError) as e:
            print("hit except block; error is ", e)
            self.last_input_invalid = True
            self.draw()
            user_input = self.get_user_move()
            self._last_user_move = user_input
            return user_input

            # return user_input
            # self.last_user_input =  self.get_user_input()
        # else:
        # self.last_user_input = user_input

    def get_input(self):
        if (
            self.current_turn < self.starting_turn
            or self.current_board().turn != self.user_color
        ):
            self.wait()
        else:
            # print("getting user input!")
            user_move = self.get_user_move()
            # This adds it as a side effect.
            # print("user move is:", user_move)
            # self.add_user_move(user_move)

    def same_last_move(self):
        # print('text move:', self.current_node().variation(0).move )
        print("text move:", self.next_node().move)
        # print('user move: ', self.user_moves[-1])
        # print('comparison', self.current_node().variation(0).move == self.user_moves[-1])
        return self.next_node().move == self._last_user_move

    def get_move_annotation(self, user_move, text_move):
        if user_move >= text_move + 30:
            return "better"
        elif user_move >= text_move - 30:
            return "not_worse"
        elif user_move >= text_move - 90:
            return "inaccuracy"
        elif user_move >= text_move - 200:
            return "mistake"
        else:
            return "blunder"

    def annotate_move(self, user_move, text_move):
        if user_move >= text_move + 30:
            self.score["better"] += 1
        elif user_move >= text_move - 30:
            self.score["not_worse"] += 1
        elif user_move >= text_move - 90:
            self.score["inaccuracy"] += 1
        elif user_move >= text_move - 200:
            self.score["mistake"] += 1
        else:
            self.score["blunder"] += 1

    def print_final_score(self):
        print("Total moves: ", sum(self.score.values()))
        pprint(self.score)

    def analyse_moves(self):
        # print('analyzing moves', self.user_moves, self.analysis_results, '\n')
        if self._last_user_move is None:
            print("no moves! returning")
            return
        else:
            if self.same_last_move():
                self.analysis_results += ["same"]
                self.score["same"] += 1
            else:
                print("Analyzing...")
                text_board = self.next_node().board()  # .mirror()
                user_board = self.current_node().board()
                user_board.push(self._last_user_move)
                user_board = user_board  # .mirror()
                # user_board = self.current_node().variation(1).board().mirror()

                user_move_info = self.engine.analyse(user_board, self.limit)
                text_move_info = self.engine.analyse(text_board, self.limit)

                user_score = (
                    user_move_info["score"].pov(self.user_color).score(mate_score=1000)
                )
                text_score = (
                    text_move_info["score"].pov(self.user_color).score(mate_score=1000)
                )

                self.analysis_results += [(user_score, text_score)]
                # self.analysis_results += [(user_move_info['score'], text_move_info['score'])]
                self.draw()

    def start(self):
        while not self.current_node().is_end():
            self.draw()
            if self.current_node().board().turn == self.user_color:
                self.get_input()
                self.analyse_moves()
            else:
                self.wait()
            self.advance()
        self.print_final_score()


# # Load a game from disk
# pgn = open("./opera_game.pgn")

# # Read the game
# app = Game('./opera_game.pgn', chess.WHITE, 2)

# player_side = chess.WHITE

other_game = "./mcconnell_morphy_1849.pgn"

app = Game(other_game, chess.BLACK, 2)
app.start()


# Things you want to pass between cycles of the loop
messages = []
if __name__ == "__main__" and False:

    cls()
    mainline = iter(game.mainline())
    print(game.headers["White"], "-", game.headers["Black"])
    print_position(game)
    input("Press enter to continue...")
    cls()
    for _ in range(7):
        node = next(mainline)
        print_position(node)
        input("Press enter to continue...")
        cls()

    # result = (game)
    last_player_move = None
    had_error = False
    # node = next(mainline)
    while not node.is_end():
        cls()
        print_position(node)
        print("last move", str(node.move))
        if node.board().turn == chess.WHITE:
            print_position(node)
            input("Press enter to continue!")
            node = next(mainline)

            continue
        for message in messages:
            print("hit messages")
            print(message)

        if had_error:
            print("Not legal move")
        player_input = input("Enter move: ")
        player_move = node.board().parse_san(player_input)
        if not node.board().is_legal(player_move):
            had_error = True
            continue
        else:
            had_error = False
            node.add_line([player_move])

        # At this point, we have the player's move, and it's legal,
        # so let's run the analysis and compare it to the text move

        # player_board = node.board().copy()
        # player_board.push(player_move)

        # # advance to the next turn
        # node = next(mainline)

        # text_board

        if node.variation(0).move == player_move:
            messages = ["You chose the same as the player"]

        else:
            player_board = node.variation(1).board().mirror()
            text_board = node.variation(0).board().mirror()
            player_move_info = engine.analyse(player_board, limit)
            text_move_info = engine.analyse(text_board, limit)

            messages = [
                "Your move: "
                + str(player_move)
                + " Evaluation: "
                + str(player_move_info["score"]),
                "Your move: "
                + str(node.variation(0).move)
                + " Evaluation: "
                + str(text_move_info["score"]),
            ]
        # print("Your move score", player_move_info['score'])
        # print("Text move score", text_move_info['score'])
        node = next(mainline)

    engine.quit()

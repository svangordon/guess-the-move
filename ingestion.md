## Process for ingesting a game

At each text move node:
1. Run an analysis on the position, finding the N best moves (let's start with 3)
1. Add those nodes to the database, with each position being unique by FEN
1. Proceed to the next node in the game, repeat the process
1. Continue until we've gotten to a material composition that we can look up in a table base

## Process for playing a game
1. Display the text position
1. Compare the user's move to the text position
1. give them a score for finding the text move
1. Or, look up the position resulting from their move in the db
# Chessplot

## Introduction
Chessplot is a library for producing visualisations of chess games
by parsing and plotting `.pgn` files (Portable Game Notation).

Chessplot can produce either an animated `.gif` of a game or
a `.pdf` with a single page per move.

## Installation
### Using PyPi:
The easiest way to install `chessplot` is using Pypi.

To do this, first ensure that you have `pip` installed then run:

`pip install git+www.github.com/tmay-sarsaparilla/PGNParser`

## Usage:
The core function of the package is `pgn_to_file`. This takes
a given `.pgn` file and uses it to create a `.gif` or `.pdf` file
as specified.

For example:
```
from chessplot import pgn_to_file
  
pgn_to_file(
    file_path="mypgnfile.pgn",
    output_file_path="mynewgif.gif",
    output_file_format="gif"
)
```
This code will read and parse the given `.pgn` file `mypgnfile.pgn`, 
create a visualisation of the game, and then save the output as a
`.gif` to the file `mynewgif.gif`.

`chessplot` can also be executed directly as a module from the command line. 
To do this, follow the example code:
```
python -m chessplot -file_path "mypgnfile.pgn" -output_file_path "mynewgif.gif" -output_file_format "gif"
```

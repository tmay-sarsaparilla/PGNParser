# Chessplot

## Introduction
`chessplot` is a library for producing visualisations of chess games
by parsing and plotting `.pgn` files (Portable Game Notation).


It can produce either an animated `.gif` of a game or
a `.pdf` with a single page per move.

## Installation
### Using PyPi:
The easiest way to install `chessplot` is using Pypi.

To do this, first ensure that you have `pip` installed then run:

```
pip install chessplot
```

## Usage:
The core of `chessplot` is the `ChessPlot` class. A `ChessPlot` can be created using a valid path to a
`.pgn` file of a chess game. The game can then be visualised by calling the `show`, `to_gif`, or `to_pdf` methods
of the `ChessPlot` class.

For example:
```
from chessplot import ChessPlot
  
plot = ChessPlot(pgn="mypgnfile.pgn")

plot.to_gif(save_path="mynewgif.gif")
```
This code will read and parse the given `.pgn` file `mypgnfile.pgn`, 
create a visualisation of the game, and then save the output as a
`.gif` to the file `mynewgif.gif`.

If a `save_path` is not provided, a path will be generated using the path of the inputted `.pgn` file.

For example, creating an instance of `ChessPlot` with the file `mypgnfile.pgn` and calling the `to_gif` method
would cause a file to be saved to the path `mypgnfile.gif`.

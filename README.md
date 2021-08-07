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
`.pgn` file of a chess game. The game can then be visualised by calling the `to_gif`, `to_pdf`, or `to_png` methods
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

### Customising plots
Plots can be customised in a number of ways using the following settings:
* `plot_size`: This determines the width of the generated plot in millimeters
* `board_only`: Toggles the plot header to allow for plots of just the board
* `display_notation`: Toggles move notation on plots
* `flip_perspective`: Toggles the perspective of the board from white to black

In addition, when generating `.gif` or `.pdf` files, the start and end
frames can be specified using the `start_frame` and `end_frame` parameters.

For example:
```
from chessplot import ChessPlot

plot = ChessPlot(pgn="myfile.pgn")

plot.to_gif(
    plot_size=1000,
    board_only=True,
    display_notation=True,
    flip_perspective=True,
    start_frame=10,
    end_frame=15
)
```
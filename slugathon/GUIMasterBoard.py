#!/usr/bin/env python2

import Tkinter as tk
import math
import GUIMasterHex
import MasterBoard

SQRT3 = math.sqrt(3.0)


class GUIMasterBoard:
    def __init__(self, root, board, scale=15):
        self.board = board
        self.scale = scale
        self.canvas = tk.Canvas(root, width=self.compute_width(),
                                height=self.compute_height(), bg='black')
        self.guihexes = {}
        for hex in self.board.hexes.values():
            guihex = GUIMasterHex.GUIMasterHex(hex, self)
            self.guihexes[hex.label] = guihex
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

    def update(self):
        for hex in self.board.hexes.values():
            hex.update()

    def compute_width(self):
        return self.scale * (self.board.hex_width() * 4 + 2)

    def compute_height(self):
        return self.scale * self.board.hex_height() * 4 * SQRT3

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Slugathon - MasterBoard')
    board = MasterBoard.MasterBoard()
    guiboard = GUIMasterBoard(root, board)
    root.mainloop()

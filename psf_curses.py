#!/usr/bin/python3

"""
Copyright 2024 X Allegretta.

This file is part of py3_bricksmasher.
py3_bricksmasher is free software: you can redistribute it and/or modify it under the terms
of the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.
py3_bricksmasher is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with py3_bricksmasher.
If not, see <https://www.gnu.org/licenses/>.
"""

from psf import *
import curses
import sys

if len(sys.argv)<3:
  print("Error: Too few arguments.")
  sys.exit(1)

glyphnum = 0
try:
  glyphnum = int(sys.argv[1])
except:
  print("Error: Invalid glyph index.")
  sys.exit(1)

if glyphnum < 0 or glyphnum > 255:
  print("Error: Invalid glyph index.")
  sys.exit(1)

# start curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.curs_set(False)
curses.start_color()

run = True

# colors
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_MAGENTA)

# cursor position
cur_x=0
cur_y=0

glyph = 0
# load font
font = PSF()
if font.loadFont(sys.argv[2]) != PSF_Enum.OKAY:
  font.newFont(16)
  height = 16
else:
  height = font.getHeight()

glyph = bytearray(font.getGlyph(glyphnum))

save = False

while run:
  stdscr.clear()
  stdscr.move(0,0)

  for y in range(0,height):
    for x in range(0,8):
      pair=0
      char = "~"
      if (glyph[y] >> (7-x)) & 1 == 1:
        char = " "
        pair = 1
      if x==cur_x and y==cur_y:
        pair+=2
      stdscr.addch(char, curses.color_pair(pair))
    stdscr.addch("\n")

  stdscr.refresh()

  c = stdscr.getkey()
  if c == "q" or c == "Q":
    run = False
  elif c == "s" or c == "S":
    run = False
    save = True
  elif c == "KEY_UP":
    if cur_y>0:
      cur_y-=1
  elif c == "KEY_DOWN":
    if cur_y<height-1:
      cur_y+=1
  elif c == "KEY_LEFT":
    if cur_x>0:
      cur_x-=1
  elif c == "KEY_RIGHT":
    if cur_x<7:
      cur_x+=1
  elif c == " ":
    glyph[cur_y] ^= (1 << (7-cur_x))

# save font
if save:
  font.setGlyph(glyphnum, bytes(glyph))
  font.saveFont(sys.argv[2])

# end curses
curses.curs_set(True)
curses.nocbreak()
stdscr.keypad(False)
curses.endwin()

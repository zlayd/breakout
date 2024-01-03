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

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']="bluh." # disable pygame's welcome message.
import pygame

class PSF_Enum():
  OKAY = 0
  NO_FONT = 1
  OPEN_FILE = 2
  INVALID_PSF = 3
  INVALID_MODE = 4
  INVALID_HEIGHT = 5
  INVALID_SCALE = 6
  INVALID_INDEX = 7

# "PC Screen Font" class.
class PSF:
  def __init__(self, warn : bool = True):
    self.data = [] # will store the data for each glyph.
    self.height = 0 # will store the height of each character
    self.scale = 0 # will store the height to scale to
    self.warn = warn # whether or not to print error messages
    self.alter_scale = True # whether or not to alter scale when loading a new font

  def loadFont(self, filename : str) -> int:
    f = 0
    try:
      f = open(filename, "rb")
    except FileNotFoundError:
      if self.warn:
        print("Error: Failed to open \"" + filename + "\".")
      return PSF_Enum.OPEN_FILE
    # get magic (file type identification) bytes.
    # for a psf1, these should always be 0x36 and 0x04.
    bytes = f.read(2)
    if bytes[0] != 0x36 or bytes[1] != 0x04:
      if self.warn:
        print("Error: \"" + filename + "\" is not a valid PSF1 file.")
      f.close()
      return PSF_Enum.INVALID_PSF
    # get mode byte.
    # i'm only supporting fonts with 256 glyphs and no unicode table, so this should always be 0.
    bytes = f.read(1)
    if bytes[0] != 0:
      if self.warn:
        print("Error: \"" + filename + "\" is not the correct mode.")
        print("Only PSF1s with 256 glyphs and no unicode table are supported.")
      f.close()
      return PSF_Enum.INVALID_MODE
    # read the height of each glyph.
    bytes = f.read(1)
    if bytes[0] < 1:
      if self.warn:
        print("Error: \"" + filename + "\" has invalid glyph height.")
      f.close()
      return PSF_Enum.INVLID_HEIGHT
    self.height = bytes[0]
    if self.alter_scale:
      self.scale = self.height
    # read the actual font data.
    self.data.clear()
    for i in range(0,256): # for each glyph
      # for a psf1, each glyph is stored as <height> bytes, with each byte representing one row of 8 pixels.
      # each bit in each byte represents one pixel.
      self.data.append(f.read(self.height))
    f.close()
    return PSF_Enum.OKAY

  def setScale(self, scale : int) -> int:
    if scale < 1:
      if self.warn:
        print("Error: " + str(scale) + " is not a valid scaled height.")
      return PSF_Enum.INVALID_SCALE
    self.scale=scale
    self.alter_scale = False
    return PSF_Enum.OKAY

  def getHeight(self) -> int:
    return self.height

  def getGlyph(self, index : int) -> bytes:
    if self.height == 0:
      if self.warn:
        print("Error: No font exists.")
      return b"\0"

    if index < 0 or index > 255:
      if self.warn:
        print("Error: Invalid glyph index.")
      buffer = bytearray()
      for i in range(0,self.height):
        buffer.append(0)
      return bytes(buffer)

    return self.data[index]

  def saveFont(self, filename : str) -> int:
    if self.height < 1:
      if self.warn:
        print("Error: No font exists to be saved!")
      return PSF_Enum.NO_FONT
    # open font
    f = 0
    try:
      f = open(filename, "wb")
    except FileNotFoundError:
      if self.warn:
        print("Error: Failed to open \"" + filename + "\".")
      return PSF_Enum.OPEN_FILE
    # write header
    f.write(bytes([0x36, 0x04, 0, self.height]))
    # write font data
    for i in range(0,256):
      f.write(self.data[i])
    # end
    f.close()
    return PSF_Enum.OKAY

  def setGlyph(self, index : int, glyph : bytes) -> int:
    if len(glyph) != self.height:
      if self.warn:
        print("Error: Invalid glyph height!")
      return PSF_Enum.INVALID_HEIGHT
    if index < 1 or index > 255:
      if self.warn:
        print("Error: Invalid glyph index!")
      return PSF_Enum.INVALID_INDEX
    self.data[index] = glyph
    return PSF_Enum.OKAY

  def newFont(self, height : int) -> int:
    if height < 1 or height > 255:
      if self.warn:
        print("Error: Invalid glyph height.")
      return PSF_Enum.INVALID_HEIGHT
    # set height + scale
    self.height = height
    if self.alter_scale:
      self.scale = height
    # create byte buffer of one empty glyph
    buffer = bytearray()
    for i in range(0,height):
      buffer.append(0x00)
    buffer = bytes(buffer) # convert to immutable bytes
    # make data contain empty glyphs
    self.data.clear()
    for i in range(0,256): # for each glyph
      self.data.append(buffer)
    return PSF_Enum.OKAY

  # convert a string into pygame image using the font
  def render(self, text : str, r=255, g=255, b=255, a=255) -> pygame.image:
    # don't do anything if no font has been loaded.
    if self.height == 0:
      if self.warn:
        print("Error: No font has been loaded.")
      return pygame.image.fromstring(b"\0\0\0\0", (1, 1), "RGBA")

    buffer = bytearray()
    for y in range(0,self.height): # loop through all of the rows of the text
      for x in range(0,len(text)): # loop through all of the characters in the string
        row = self.data[ord(text[x])][y]
        # for each pixel in the row
        bit = 0x80
        while bit>0:
          # if pixel is active, add a pixel of the specified color
          if row & bit == bit:
            buffer.append(r)
            buffer.append(g)
            buffer.append(b)
            buffer.append(a)
          # if pixel isn't active, add a transparent pixel
          else:
            for i in range(0,4):
              buffer.append(0)
          bit >>= 1

    # convert the byte buffer to a pygame image
    image = pygame.image.fromstring(bytes(buffer), (len(text)*8, self.height), "RGBA")
    # pygame.image.fromstring(buffer, (w,h), format)

    # scale the image to a new height
    if self.scale != self.height:
      # pygame.transform.scale(image, (new_w, new_h))
      image = pygame.transform.scale(image, (int(len(text)*8*self.scale/self.height), self.scale))

    return image

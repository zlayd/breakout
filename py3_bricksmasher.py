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

import random
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']="bluh." # disable pygame's welcome message.
import pygame
from psf import *

def set_color(surf : pygame.Surface, col : pygame.Color):
  col_float = (col.b/255.0, col.g/255.0, col.r/255.0)
  buf = surf.get_buffer()
  raw = bytearray(buf.raw)
  i = 0
  while i+3 < buf.length:
    for j in range(3):
      raw[i+j] = int(raw[i]*col_float[j])
    i+=4
  buf.write(bytes(raw))

def rand_color(surf : pygame.Surface):
  surfs = []
  for i in range(4):
    col = pygame.Color(255, 255, 255)
    col.hsla = (random.randrange(180,360), 100, 80, 100)
    surfs.append(surf.copy())
    set_color(surfs[i], col)
  return surfs

def main():
  # --- init ---
  pygame.init()
  # window
  win_rect = pygame.rect.Rect(0, 0, 1280, 720)
  win = pygame.display.set_mode((win_rect.w, win_rect.h))
  # store background images
  win_img = []
  for i in range(1,7):
    win_img.append(pygame.image.load("bmps/background" + str(i) + ".bmp"))
  pygame.display.set_caption("bricksmasher")

  bounce = pygame.mixer.Sound("wavs/my_ears.wav")

  # used to select ball image and whether or not to handle ball movement
  time = 0

  # paddle
  paddle_img = []
  paddle_rect = []
  paddle_index = 0
  for i in range(0,2): # there are two different sizes of paddle. this loads both of them.
    paddle_img.append(pygame.image.load("bmps/paddle" + str(i+1) + ".bmp"))
    paddle_rect.append(paddle_img[i].get_rect())
    # set starting positions
    paddle_rect[i].x = win_rect.w/2 - paddle_rect[i].w/2
    paddle_rect[i].y = win_rect.h - paddle_rect[i].h - 4

  # ball
  ball_img = [pygame.image.load("bmps/ball.bmp"), 0, 0, 0]
  for i in range(1,4): # create rotated copies
    ball_img[i] = pygame.transform.rotate(ball_img[i-1], 90)
  ball_img_index = 0 # current image index
  ball_rect_img = pygame.rect.Rect(win_rect.w/2-24, win_rect.h-78, 48, 48) # used to draw image
  ball_rect_col = pygame.rect.Rect(win_rect.w/2-20, win_rect.h-74, 40, 40) # used to detect collision
  ball_new = True # keep ball on paddle, to start
  ball_speed_x = 2
  ball_speed_y = -2

  # bricks
  brick_frame = pygame.image.load("bmps/brick_frame.bmp")
  brick_inner = pygame.image.load("bmps/brick_inner.bmp")
  brick_glow = pygame.image.load("bmps/brick_glow.bmp")
  # create hue-adjusted copies of bricks
  brick_inner_copies = rand_color(brick_inner)
  brick_glow_copies = rand_color(brick_glow)

  brick_rect = pygame.rect.Rect(6, 54, 100, 50)
  rows = 2
  row_offset = 0
  row_offset_max = 0 # by how much the different rows will move back and forth
  row_offset_add = 0 # how much to change the offset by
  brick_count = 24
  brick_array = [[], [], [], []] # holds rows
  for i in range(0,4):
    # fill row
    for j in range(0,12):
      brick_array[i].append(True)

  font = PSF()
  font.loadFont("game.psf")
  font.setScale(40)
  # counters at top of screen
  # level
  level = 1
  level_img = font.render("level: 01")
  level_rect = level_img.get_rect()
  level_rect.x=win_rect.w/4-level_rect.w/2
  # lives
  lives = 3
  lives_img = font.render("lives: 03")
  lives_rect = lives_img.get_rect()
  lives_rect.x=win_rect.w/2-lives_rect.w/2
  # score
  score = 0
  score_img = font.render("score: 000000")
  score_rect = score_img.get_rect()
  score_rect.x=win_rect.w*3/4-score_rect.w/2
  update_score = False # when to re-render score_img
  # next level / game over text
  msg_img = [font.render("level beaten."), font.render("game over."), font.render(" ")]
  msg_rect = [0, 0, 0]
  for i in range(0, 3):
    msg_rect[i] = msg_img[i].get_rect()
    msg_rect[i].x = win_rect.w/2 - msg_rect[i].w/2
    msg_rect[i].y = win_rect.h/2 - msg_rect[i].h/2
  msg_type = -1 # don't display message initially
  msg_time=255
  win_old_surf = 0 # will store fade-out image

  def brick_col() -> bool:
    nonlocal brick_rect, rows, row_offset, brick_array, bounce, update_score, brick_count
    brick_rect.y=54
    for i in range(0,rows): # rows
      brick_rect.x=6+(row_offset*((i%2)*2-1))
      for j in range(0,12): # cols
        if brick_array[i][j]:
          if brick_rect.colliderect(ball_rect_col): # if collision
            bounce.play()
            # remove brick
            update_score = True
            brick_count-=1
            brick_array[i][j]=False
            return True
        brick_rect.x+=brick_rect.w+6
      brick_rect.y+=brick_rect.h+6
    return False

  # --- main loop ---
  play = True
  while(play):
    # --- render ---
    win.blit(win_img[level-1], win_rect) # draw background

    win.blit(paddle_img[paddle_index], paddle_rect[paddle_index]) # paddle

    # draw bricks
    brick_rect.y=54
    for i in range(0,rows):
      brick_rect.x=6+(row_offset*((i%2)*2-1))
      for j in range(0,12):
        if brick_array[i][j]: # only if the brick exists
          win.blit(brick_inner_copies[i], brick_rect)
          win.blit(brick_frame, brick_rect)
          win.blit(brick_glow_copies[i], brick_rect)
        brick_rect.x+=brick_rect.w+6
      brick_rect.y+=brick_rect.h+6

    win.blit(level_img, level_rect) # level counter
    win.blit(lives_img, lives_rect) # lives counter
    win.blit(score_img, score_rect) # score counter

    win.blit(ball_img[ball_img_index], ball_rect_img) # draw ball
    if time%12 == 0: # rotate ball
      ball_img_index = (ball_img_index+1) % 4

    if msg_type>-1: # if should display a message
      win.blit(win_old_surf, win_rect) # draw fade-out image
      win.blit(msg_img[msg_type], msg_rect[msg_type]) # draw message
      msg_time-=1
      # fade out message/image
      win_old_surf.set_alpha(msg_time)
      msg_img[msg_type].set_alpha(msg_time)
      if msg_time == 0:
        msg_type=-1
        msg_img[msg_type].set_alpha(255)

    pygame.display.flip() # swap buffers

    # --- handle events ---
    for event in pygame.event.get():
      # exit the game when close button pressed
      if event.type == pygame.QUIT:
        play = False
      elif event.type == pygame.KEYDOWN:
        # close game when escape or 'q' pressed
        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
          play = False
        # 'f' toggles fullscreen
        elif event.key == pygame.K_f:
         pygame.display.toggle_fullscreen()
      # mouse update
      elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
        # get paddle position
        mouse_pos = pygame.mouse.get_pos()
        paddle_rect[paddle_index].x = mouse_pos[0] - paddle_rect[paddle_index].w/2
        # keep paddle in-bounds
        if paddle_rect[paddle_index].x<0:
          paddle_rect[paddle_index].x=0
        elif paddle_rect[paddle_index].x>win_rect.w-paddle_rect[paddle_index].w:
          paddle_rect[paddle_index].x=win_rect.w-paddle_rect[paddle_index].w
        # keep a new ball stuck to paddle
        if ball_new:
          ball_rect_img.x = paddle_rect[paddle_index].x + paddle_rect[paddle_index].w/2 - ball_rect_img.w/2
          ball_rect_col.x = paddle_rect[paddle_index].x + paddle_rect[paddle_index].w/2 - ball_rect_col.w/2
          # launch ball
          if event.type == pygame.MOUSEBUTTONDOWN:
            ball_new = False
            ball_speed_y = -2
            ball_speed_x = 2
            if mouse_pos[0]>win_rect.w/2:
              ball_speed_x*=-1

    # --- ball movement + collision ---
    if ball_new == False and time%(level+2)!=0:
      # --- x-axis ---
      ball_rect_col.x += ball_speed_x
      # brick collision detection
      if brick_col():
        # move ball to side
        ball_rect_col.x=brick_rect.x
        if ball_speed_x < 0:
          ball_rect_col.x+=brick_rect.w
        else:
          ball_rect_col.x-=ball_rect_col.w
        ball_speed_x *= -1; # change ball direction
      # screen border collision
      # left side
      if ball_rect_col.x < 0:
        bounce.play()
        ball_rect_col.x = 0
        ball_speed_x *= -1
      # right side
      elif ball_rect_col.x > win_rect.w - ball_rect_col.w:
        bounce.play()
        ball_rect_col.x = win_rect.w - ball_rect_col.w
        ball_speed_x *= -1

      # --- y-axis ---
      ball_rect_col.y += ball_speed_y
      # brick collision detection
      if brick_col():
        # update ball position
        ball_rect_col.y=brick_rect.y
        if ball_speed_y < 0:
          ball_rect_col.y+=brick_rect.h
        else:
          ball_rect_col.y-=ball_rect_col.h
        ball_speed_y *= -1 # change direction

      # paddle collision
      if paddle_rect[paddle_index].colliderect(ball_rect_col):
        bounce.play()
        ball_rect_col.y = paddle_rect[paddle_index].y - ball_rect_col.h
        # get x distance of ball center to paddle center + side of collision
        ball_dist = ball_rect_col.x + ball_rect_col.w/2 - (paddle_rect[paddle_index].x + paddle_rect[paddle_index].w/2)
        # if ball hits center, faster on y, same x direction as previous
        if abs(ball_dist)<=paddle_rect[paddle_index].w/6:
          ball_speed_x = 1 * abs(ball_speed_x)/ball_speed_x
          ball_speed_y = -3
        # if ball hits in-between center and side, same on x and y, same direction
        elif abs(ball_dist)<=paddle_rect[paddle_index].w*(3.0/8.0):
          ball_speed_x = 2 * abs(ball_speed_x)/ball_speed_x
          ball_speed_y = -2
        else: # if hits edges, faster on x than y, direction based on side of paddle
          ball_speed_x = 3 * abs(ball_dist)/ball_dist
          ball_speed_y = -1

      # screen border collision
      # top of screen
      if ball_rect_col.y < 0:
        bounce.play()
        ball_rect_col.y = 0
        ball_speed_y *= -1 # change direction
      # bottom
      elif ball_rect_col.y > win_rect.h + 2*ball_rect_col.h:
        lives-=1
        if lives == -1:
          # game over ==> reset variables
          # change level to 1
          level=1
          level_img = font.render("level: 01")
          # change score to 0
          score = 0
          score_img = font.render("score: 000000")
          # reset lives
          lives=3
          # game over message
          msg_type=1
          msg_time=255
          # copy screen for fade-out
          win_old_surf = pygame.display.get_surface().copy()
          # randomize colors
          brick_inner_copies = rand_color(brick_inner)
          brick_glow_copies = rand_color(brick_glow)
          # reset brick array
          rows=2
          brick_count = 24
          for i in range(0,4):
            for j in range(0,12):
              brick_array[i][j]=True
          # reset paddle
          paddle_index = 0
        lives_img = font.render("lives: {:02}".format(lives))
        ball_new = True # ball will stick to paddle
        # move to paddle
        ball_rect_col.x = paddle_rect[paddle_index].x + paddle_rect[paddle_index].w/2 - ball_rect_col.w/2
        ball_rect_col.y = paddle_rect[paddle_index].y - ball_rect_col.h

      # update score
      if update_score:
        score+=10
        score_img = font.render("score: {:06}".format(score))
        update_score=False
        # if won
        if brick_count == 0:
          brick_inner_copies = rand_color(brick_inner)
          brick_glow_copies = rand_color(brick_glow)
          level+=1
          win_old_surf = pygame.display.get_surface().copy()
          if level==7: # game won!
            ask_replay = True
            # the messages to display
            replay_info_img = []
            replay_info_img.append(font.render("you beat the game!"))
            replay_info_img.append(font.render("created by x allegretta."))
            replay_info_img.append(font.render("your score was {:06}.".format(score)))
            replay_info_img.append(font.render("click the mouse or press space to play again."))
            replay_info_img.append(font.render("press 'q' or escape to quit."))
            # set locations to draw messages
            replay_info_rect = []
            for i in range(len(replay_info_img)):
              replay_info_rect.append(replay_info_img[i].get_rect())
              replay_info_rect[i].x = win_rect.w/2-replay_info_rect[i].w/2
              replay_info_rect[i].y = win_rect.h*(i+1)/(len(replay_info_img)+1)
            alpha = 255
            while ask_replay: # loop run until play makes decision
              win.fill((0, 0, 0)) # clear screen
              for i in range(4):
                win.blit(replay_info_img[i], replay_info_rect[i])
              if alpha > 0:
                win.blit(win_old_surf, win_rect)
                alpha-=1
                win_old_surf.set_alpha(alpha)
              pygame.display.flip()
              # handle events
              for event in pygame.event.get():
                if event.type == pygame.QUIT:
                  ask_replay=False
                  play = False
                elif event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    ask_replay=False
                    play = False
                  elif event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
                  elif event.key == pygame.K_SPACE:
                    ask_replay=False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                  ask_replay=False
            rows=1
            lives+=3
            level=1
            win_old_surf = pygame.display.get_surface().copy()
            msg_type=2 # doesn't actually show a message, but makes it so that there's a fade
          else:
            msg_type=0 # you won a level message
          msg_time=254
          level_img = font.render("level: {:02}".format(level))
          # decrease paddle size, add lives on certain levels
          if level == 4:
            paddle_index=1
            lives+=1
          elif level == 6:
            lives+=1
          # lives image
          lives_img = font.render("lives: {:02}".format(lives))
          # reset ball
          ball_new=True
          ball_rect_col.x = paddle_rect[paddle_index].x + paddle_rect[paddle_index].w/2 - ball_rect_col.w/2
          ball_rect_col.y = paddle_rect[paddle_index].y - ball_rect_col.h
          # reset
          if rows < 4:
            rows+=1
          row_offset_add=level-2
          row_offset_max=row_offset_add*40
          row_offset = 0
          brick_count = 12*rows
          for i in range(0,4):
            for j in range(0,12):
              brick_array[i][j]=True

      # update drawing location
      ball_rect_img.x=ball_rect_col.x-4
      ball_rect_img.y=ball_rect_col.y-4

    time = (time+1) % (3*4*5*7)
    # decide when to move rows
    if level>2:
      if time%(8-level+int(10*abs(row_offset)/row_offset_max))==0:
        if abs(row_offset)==row_offset_max:
          row_offset_add*=-1
        row_offset+=row_offset_add
  # --- exit ---
  pygame.quit()

if __name__ == "__main__":
  main()

#!/usr/bin/env python
#
# Made by Dave for an art project

import argparse
import random
import os
import sys

import pyglet
from subprocess import call

def wrapped_ctime_sort(root):
  def ctime_sort(a, b):
    first = os.path.getctime(os.path.abspath(os.path.join(root, a)))
    second = os.path.getctime(os.path.abspath(os.path.join(root, b)))
    if first < second:
      return 1
    elif first > second:
      return -1
    return 0

  return ctime_sort

def get_image_paths(input_dir='.'):
  paths = []
  for root, dirs, files in os.walk(input_dir, topdown=True):
    for file in sorted(files, wrapped_ctime_sort(root)):
      if file.endswith(('jpg', 'png', 'gif')):
        path = os.path.abspath(os.path.join(root, file))
        paths.append(path)
  return paths


def get_scale(image, col_size, row_size):
  width = col_size
  height = row_size
  return max(min(width, image.width)/max(width, image.width), min(image.height, height)/max(image.height, height))

def divideWindow(window, cols, rows):
  col_offsets = []
  row_offsets = []
  col_chunk = float(window.width) / float(cols)
  row_chunk = float(window.height) / float(rows)
  i = 0
  j = 0

  while i <= window.width:
    col_offsets.append(i)
    i += col_chunk

  while j <= window.height:
    row_offsets.append(j)
    j += row_chunk

  offsets = { 
    "col_chunk": col_chunk,
    "row_chunk": row_chunk,
    "cols" : col_offsets,
    "rows" : row_offsets
  }
  return offsets

def generate_sprites(image_paths):
  sprites = []
  for path in image_paths:
    image = pyglet.image.load(path)
    sprite = pyglet.sprite.Sprite(image)
    sprites.append(sprite)
  return sprites

def assign_sprites_to_offsets(sprites, offsets, cols, rows):
  print sprites
  sprites = sprites[:(cols*rows)]
  for j in range(rows):
    for i in range(cols):
      index = (i + (j * cols))
      if index > len(sprites) - 1:
        return sprites
      sprite = sprites[index]
      sprite.x = offsets["cols"][i]
      sprite.y = offsets["rows"][j]
      sprite.scale = get_scale(sprite, offsets["col_chunk"], offsets["row_chunk"])
  
  return sprites

def take_photo():
  global photo_count
  photo_count+=1
  file_name = ".".join(["project_photo" + str(photo_count), "jpg"])
  cur_dir = os.path.join(args.dir, file_name)
  print cur_dir, args.device
  call_list = ["imagesnap", cur_dir]
  if len(args.device) > 0:
    call_list.append("-d")
    call_list.append(args.device)

  print call_list
  call(call_list)

  rotate = ["sips", "-r", str(args.rotation), cur_dir]
  col_chunk = float(window.width) / float(args.columns)
  row_chunk = float(window.height) / float(args.rows)
  resize = ["sips", "-z", str(row_chunk), str(col_chunk), cur_dir]
  call(rotate)
  call(resize)


window = pyglet.window.Window(fullscreen=True)

@window.event
def on_draw():
  background.draw()
  for sprite in assigned_sprites:
    sprite.draw()

@window.event
def on_key_press(symbol, modifiers):
  if symbol == pyglet.window.key._8:
    take_photo()
    loadin(1)
  if symbol == pyglet.window.key.C:
    sys.exit(1)
  if symbol == pyglet.window.key.R:
    args.rotation = int(args.rotation) + 10
  return

def print_sprites(sprites):
  s = "["
  for sprite in sprites:
    s += "{"
    s += "x : " + str(sprite.x) + ", "
    s += "y : " + str(sprite.y) + ", "
    s += "scale : " + str(sprite.scale) + ", "
    s += "rotation : " + str(sprite.rotation)
    s += "},"
  s += "]"
  print s

def loadin(arg):
  global assigned_sprites
  image_paths = get_image_paths(args.dir)
  offsets = divideWindow(window, int(args.columns), int(args.rows))
  sprites = generate_sprites(image_paths)
  assigned_sprites = assign_sprites_to_offsets(sprites, offsets, int(args.columns), int(args.rows))
  print_sprites(assigned_sprites)

def main():
  global args
  global photo_count
  photo_count = 0
  window.clear()
  parser = argparse.ArgumentParser()
  parser.add_argument('dir', help='directory of images', nargs='?', default=os.getcwd()) 
  parser.add_argument('--columns', help='number of photo columns', nargs='?', default=3) 
  parser.add_argument('--rows', help='directory of images', nargs='?', default=2) 
  parser.add_argument('--device', help='imagesnap device to use', nargs='?', default="") 
  parser.add_argument('--rotation', help='rotation to save on', nargs='?', default=270) 
  args = parser.parse_args()

  realpath = os.path.dirname(os.path.realpath(sys.argv[0]))

  print window.width, window.height
  def initial():
    global background
    image_path = get_image_paths(os.path.join(realpath, 'images'))
    background = generate_sprites(image_path)[0]

  initial()
  loadin(1)
  pyglet.app.run()

if __name__ == '__main__':
  main()

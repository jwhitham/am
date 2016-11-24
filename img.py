
from PIL import Image

import aimee_maze, test_maze

rows = 15
columns = 15
seed = 1

char_width = 8
char_height = 8

maze_map = aimee_maze.make_maze(rows, columns, seed)
img = Image.new("1", (char_width * columns, char_height * rows), 1)
font_data = open("cp437-8x8", "rb").read()

for y in range(rows):
   for x in range(columns):
      value = maze_map[x, y]

      if value == aimee_maze.WALL:
         gfx = 1 + ((x + y) % 2)
      elif value in (aimee_maze.START, aimee_maze.FINISH):
         gfx = ord("Z") - 64
      else:
         gfx = 0

      offset = gfx * char_height
      y0 = y * char_height

      for y1 in range(8):
         font = ord(font_data[offset])
         x0 = x * char_width
         for x1 in range(8):
            if (font & 128) == 0:
               img.putpixel((x0, y0), 0)
            x0 += 1
            font = font << 1
         y0 += 1
         offset += 1
               
img.save("test.bmp")
aimee_maze.print_maze(rows, columns, maze_map)


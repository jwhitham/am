# 3D maze, ray casting prototype
# Use arrow keys to navigate to the exit

import pygame
from pygame.locals import *
import math
import maze
HALF_WIDTH = 320
HALF_HEIGHT = 240
FIXED_POINT = 256
MU = 24
SHOW_MAP = False
ROTATION = False

def main():
	pygame.init()
	s = pygame.display.set_mode((HALF_WIDTH * 2, HALF_HEIGHT * 2))
	clock = pygame.time.Clock()

	# generate maze
	original_maze = maze.Maze(15, 15, 2)
	player_x = player_y = 0

	for maze_row in range(original_maze.rows):
		for maze_column in range(original_maze.columns):
			if original_maze.maze_map.get((maze_column, maze_row), 0) == maze.START:
				player_x = (maze_column * FIXED_POINT) + (FIXED_POINT / 2)
				player_y = (maze_row * FIXED_POINT) + (FIXED_POINT / 2)
				break

	#for maze_row in range(2, original_maze.rows - 2):
	#	for maze_column in range(2, original_maze.columns - 2):
	#		original_maze.maze_map[(maze_column, maze_row)] = maze.CONNECTED

	texture_width = original_maze.columns
	texture_height = original_maze.rows
	key = None
	camera_angle = 0.0

	rotated_maze_list = [original_maze]
	for i in range(3):
		rotated_maze_list.append(rotated_maze_list[-1].rotate_maze())

	while True:
		s.fill((0, 0, 0))

		if ROTATION:
			rotated_camera_angle = camera_angle
			rotated_player_x = player_x
			rotated_player_y = player_y
			rotation_count = 0

			# rotate maze as drawing algorithm assumes a particular orientation
			while rotated_camera_angle < (math.pi * -0.25):
				rotated_camera_angle += math.pi * 0.5
				for i in range(1):
					(rotated_player_x, rotated_player_y) = ((rotated_maze.rows * FIXED_POINT) - 1 - rotated_player_y, rotated_player_x)
					rotation_count += 1

			while rotated_camera_angle > (math.pi * 0.25):
				rotated_camera_angle -= math.pi * 0.5
				for i in range(3):
					(rotated_player_x, rotated_player_y) = ((rotated_maze.rows * FIXED_POINT) - 1 - rotated_player_y, rotated_player_x)
					rotation_count += 1

			rotated_maze = rotated_maze_list[rotation_count % 4]
			assert abs(rotated_camera_angle) <= ((math.pi * 0.25) + 0.01)

			# vector along the line that the player faces
			camera_vector_x = int(math.floor(FIXED_POINT * math.cos(rotated_camera_angle)))
			camera_vector_y = int(math.floor(FIXED_POINT * math.sin(rotated_camera_angle)))
		else:
			rotated_camera_angle = camera_angle = 0.0
			rotated_player_x = player_x
			rotated_player_y = player_y
			rotation_count = 0
			rotated_maze = rotated_maze_list[0]
			camera_vector_x = FIXED_POINT
			camera_vector_y = 0

		# normal to the camera vector (projection plane for view)
		plane_vector_x = -camera_vector_y
		plane_vector_y = camera_vector_x

		for screen_x in range(-HALF_WIDTH, HALF_WIDTH, 1):

			# vector for this screen X (the ray being cast)
			ray_vector_x = camera_vector_x + ((plane_vector_x * screen_x) / HALF_WIDTH)
			ray_vector_y = camera_vector_y + ((plane_vector_y * screen_x) / HALF_WIDTH)
			viewer_x = rotated_player_x
			viewer_y = rotated_player_y

			#assert 0.70 <= ray_vector_x, (ray_angle, ray_vector_x)
			#assert abs(ray_vector_y) <= 0.71, (ray_angle, ray_vector_y)

			maze_x = viewer_x / FIXED_POINT
			maze_y = viewer_y / FIXED_POINT

			while (maze_x < rotated_maze.columns) and (abs(maze_y) < rotated_maze.columns):
				sub_x = viewer_x - (maze_x * FIXED_POINT)
				sub_y = viewer_y - (maze_y * FIXED_POINT)
				assert 0 <= sub_x <= FIXED_POINT
				assert 0 <= sub_y <= FIXED_POINT

				# find first intersection with horizontal line
				i1x = i1y = None
				if ray_vector_y < 0:
					# above (left hand side)
					i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)))
					i1y = maze_y * FIXED_POINT
				elif ray_vector_y > 0:
					# below (right hand side)
					i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)))
					i1y = (maze_y + 1) * FIXED_POINT
			
				# find first intersection with vertical line
				i2x = i2y = None
				if ray_vector_x > 0:
					i2x = (maze_x + 1) * FIXED_POINT
					i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x))

				if (i1x == None) or ((i2x < i1x) and (i2x != None)):
					# crosses vertical line first
					maze_x += 1
					viewer_x = i2x
					viewer_y = i2y
					assert maze_x == (viewer_x / FIXED_POINT)

					texture_x = (i2y * texture_width) / FIXED_POINT
					texture_x %= texture_width
				else:
					# crosses horizontal line first
					if i2x == i1x:
						# special case: crosses both lines at once
						i2y = i1y
						assert i2y == i1y
						maze_x += 1

					viewer_x = i1x
					viewer_y = i1y
					assert maze_x == (viewer_x / FIXED_POINT)
					if ray_vector_y < 0:
						assert maze_y == (viewer_y / FIXED_POINT)
						maze_y -= 1
						texture_x = (i1x * texture_width) / FIXED_POINT
						texture_x %= texture_width
					else:
						maze_y += 1
						assert maze_y == (viewer_y / FIXED_POINT)
						texture_x = (i1x * texture_width) / FIXED_POINT
						texture_x = texture_width - (texture_x % texture_width) - 1



				if (rotated_maze.maze_map.get((maze_x, maze_y), 0) == maze.WALL):
					# reached wall

					# There is a plane with the point (viewer_x, viewer_y) on it.
					# It is normal to the camera_vector plane. Find point where the
					# two intersect  

					if ROTATION:
						xa = camera_vector_x
						ya = camera_vector_y
						xb = plane_vector_x
						yb = plane_vector_y
						a = (xa * yb) - (xb * ya)
						a /= FIXED_POINT
						if a != 0:
							b = (xa * rotated_player_y) + (viewer_x * ya) - (rotated_player_x * ya) - (xa * viewer_y)
							tb = b / a
							intersect_x = viewer_x + ((xb * tb) / FIXED_POINT)
							intersect_y = viewer_y + ((yb * tb) / FIXED_POINT)
							tmp = (intersect_x - rotated_player_x) ** 2
							tmp += (intersect_y - rotated_player_y) ** 2

							# approximation for square root - more iterations improve accuracy
							sqrt = FIXED_POINT
							for i in range(4):
								sqrt = (sqrt + (tmp / sqrt)) / 2

							height = ((2 * FIXED_POINT * (HALF_HEIGHT - 1)) / sqrt)
							
						else:
							height = 1
					else:
						distance = viewer_x - rotated_player_x
						height = ((2 * FIXED_POINT * (HALF_HEIGHT - 1)) / distance)

					h = maze_x + maze_y
					h = (h % 7) + 1
					r = 255 * (h & 1)
					g = 255 * ((h & 2) / 2)
					b = 255 * ((h & 4) / 4)
					if SHOW_MAP:
						pygame.draw.line(s, (r, g, b),
							((int(viewer_x * MU) / FIXED_POINT), (int(viewer_y * MU) / FIXED_POINT)),
							((int(rotated_player_x * MU) / FIXED_POINT), (int(rotated_player_y * MU) / FIXED_POINT)))

					maze_x = player_x / FIXED_POINT
					maze_y = player_y / FIXED_POINT
					save_pos = (maze_x, maze_y)
					save_val = original_maze.maze_map[save_pos]
					original_maze.maze_map[save_pos] = '*'

					tmp_y0 = tmp_y1 = HALF_HEIGHT - (height / 2)
					tmp_x = screen_x + HALF_WIDTH
					for texture_y in range(texture_height):
						tmp_y2 = (((texture_y + 1) * height) / texture_height) + tmp_y0
						v = original_maze.maze_map.get((texture_x, texture_y), 0)
						if v == maze.WALL:
							h = ((texture_x + texture_y) % 9)
							r = g = b = 127 + (h * 16)
							if ((texture_x == 0) or (texture_y == 0)
							or (texture_x == (texture_width - 1))
							or (texture_y == (texture_height - 1))):
								r /= 4
								g = b = 0
						elif v == '*':
							r = g = 0
							b = 255
						else:
							r = g = b = 0
						pygame.draw.line(s, (r, g, b), (tmp_x, tmp_y1), (tmp_x, tmp_y2))
						tmp_y1 = tmp_y2

					original_maze.maze_map[save_pos] = save_val
					break

		if SHOW_MAP:
			for x in range(rotated_maze.columns):
				pygame.draw.line(s, (255, 255, 255),
					(int(x * MU), 0),
					(int(x * MU), HALF_HEIGHT * 2))
			for y in range(rotated_maze.rows):
				pygame.draw.line(s, (255, 255, 255),
					(0, int(y * MU)),
					(HALF_WIDTH * 2, int(y * MU)))
			for y in range(rotated_maze.rows):
				for x in range(rotated_maze.columns):
					if (rotated_maze.maze_map.get((x, y), 0) == maze.WALL):
						pygame.draw.rect(s, (100, 100, 100),
							(int(x * MU), int(y * MU), MU, MU))


		pygame.display.flip()
		new_player_x = player_x
		new_player_y = player_y
		if ROTATION:
			camera_vector_x = int(math.floor(FIXED_POINT * math.cos(camera_angle)))
			camera_vector_y = int(math.floor(FIXED_POINT * math.sin(camera_angle)))
		else:
			camera_vector_x = FIXED_POINT
			camera_vector_y = 0

		e = pygame.event.poll()
		while e.type != NOEVENT:
			if e.type == QUIT:
				key = K_ESCAPE
			if e.type == KEYDOWN:
				key = e.key
			if e.type == KEYUP:
				key = None
			e = pygame.event.poll()

		if key == K_LEFT:
			if ROTATION:
				camera_angle -= 0.1
			else:
				new_player_y -= camera_vector_x / 10
				new_player_x -= camera_vector_y / 10
		if key == K_RIGHT:
			if ROTATION:
				camera_angle += 0.1
			else:
				new_player_y += camera_vector_x / 10
				new_player_x += camera_vector_y / 10
		if key == K_DOWN:
			new_player_x -= camera_vector_x / 10
			new_player_y -= camera_vector_y / 10
		if key == K_UP:
			new_player_x += camera_vector_x / 10
			new_player_y += camera_vector_y / 10
		if key == K_z:
			camera_angle -= 0.1
		if key == K_x:
			camera_angle += 0.1
		if key == K_ESCAPE:
			break

		# detect collision
		maze_y = new_player_y / FIXED_POINT
		maze_x = (new_player_x - (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_x = player_x
		maze_x = (new_player_x + (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_x = player_x

		maze_x = new_player_x / FIXED_POINT
		maze_y = (new_player_y - (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_y = player_y
		maze_y = (new_player_y + (FIXED_POINT / 10)) / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.WALL:
			new_player_y = player_y

		player_x = new_player_x
		player_y = new_player_y
		maze_x = player_x / FIXED_POINT
		maze_y = player_y / FIXED_POINT
		if original_maze.maze_map.get((maze_x, maze_y), maze.WALL) == maze.FINISH:
			print ("You win!")
			break
				
		pygame.time.wait(40)

	pygame.quit()

if __name__ == "__main__":
	main()


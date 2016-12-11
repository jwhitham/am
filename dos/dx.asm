
org	0x100

WALL equ 'q' + (32 * 2)
UNCONNECTED equ '.'
START equ '>'
FINISH equ '<'
CONNECTED equ ' '
ROWS equ 25
COLUMNS equ 40
TEXT_ATTRIBUTE equ 12

start:
; 40 column text mode
	mov	ax, 0
	int	0x10
	mov	dx, 0xb800	
	mov	es, dx

; Fill the maze area with walls
	cld
	mov	di, 0
	mov	cx, ROWS * COLUMNS
	mov	ax, (TEXT_ATTRIBUTE << 8) | WALL
	rep stosw

; Remove spaces between walls
	mov	ax, UNCONNECTED
	mov	cl, (COLUMNS / 2) - 1
	mov	di, (COLUMNS * 2) + 2
one_row:
	stosw
	inc	di
	inc	di
	loopnz	one_row

a:	hlt
	jmp	a	
	

;	# Begin creating the maze
;	r = random.Random(seed)
;	maze_map = dict()
;	list_of_walls = []
;
;	# Fill the maze area with walls
;	for y in range(ROWS):
;		for x in range(COLUMNS):
;			maze_map[x, y] = WALL
;
;	# Remove spaces between walls
;	for y in range(2, ROWS - 1, 2):
;		for x in range(2, COLUMNS - 1, 2):
;			maze_map[x, y] = UNCONNECTED
;
;	# Pick start point (left side)
;	y = r.randrange(2, ROWS - 1, 2)
;	start = (1, y)
;	maze_map[0, y] = CONNECTED
;	list_of_walls.append(start)
;
;	# Repeatedly remove walls to make the maze
;	while len(list_of_walls) > 0:
;		# find some wall within the maze
;		(x, y) = list_of_walls.pop(r.randrange(0, len(list_of_walls)))
;
;		if (y % 2) == 0:
;			# Wall has spaces to the left and right
;			assert (x % 2) == 1
;			if maze_map[x - 1, y] == UNCONNECTED:
;				# unconnected space to the left
;				assert maze_map[x + 1, y] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x - 1, y] = CONNECTED
;				list_of_walls.append((x - 1, y - 1))
;				list_of_walls.append((x - 1, y + 1))
;				list_of_walls.append((x - 2, y))
;			elif maze_map[x + 1, y] == UNCONNECTED:
;				# unconnected space to the right
;				assert maze_map[x - 1, y] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x + 1, y] = CONNECTED
;				list_of_walls.append((x + 1, y - 1))
;				list_of_walls.append((x + 1, y + 1))
;				list_of_walls.append((x + 2, y))
;			else:
;				# both spaces already connected, do nothing
;				pass
;		else:
;			# Wall has spaces above and below
;			assert (x % 2) == 0
;			if maze_map[x, y - 1] == UNCONNECTED:
;				# unconnected space above
;				assert maze_map[x, y + 1] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x, y - 1] = CONNECTED
;				list_of_walls.append((x - 1, y - 1))
;				list_of_walls.append((x + 1, y - 1))
;				list_of_walls.append((x, y - 2))
;			elif maze_map[x, y + 1] == UNCONNECTED:
;				# unconnected space below
;				assert maze_map[x, y - 1] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x, y + 1] = CONNECTED
;				list_of_walls.append((x - 1, y + 1))
;				list_of_walls.append((x + 1, y + 1))
;				list_of_walls.append((x, y + 2))
;			else:
;				# both spaces already connected, do nothing
;				pass
;
;	# Pick finish point (right side)
;	x = COLUMNS - 2
;	y = r.randrange(2, ROWS - 1, 2)
;	maze_map[x, y] = FINISH 
;	x += 1
;	maze_map[x, y] = CONNECTED
;
;	# Mark start point
;	(x, y) = start
;	maze_map[x, y] = START
;
;	# Maze is finished
;	return maze_map
;

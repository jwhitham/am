
WALL equ 'q' + (32 * 2)
UNCONNECTED equ '.'
START equ '>'
FINISH equ '<'
CONNECTED equ ' '
ROWS equ 27
COLUMNS equ 41
TEXT_ATTRIBUTE equ 12
SCREEN_COLUMNS equ 40

	cpu 8086
	bits 16
	org 0x100

start:
; 40 column text mode
	mov	ax, 0
	int	0x10

; Direction flag remains clear for whole program
	cld

fill_maze_area_with_walls:
;	; Fill the maze area with walls
;	for y in range(ROWS):
;		for x in range(COLUMNS):
;			maze_map[x, y] = WALL

	mov	di, maze_map
	mov	cx, ROWS * COLUMNS
	mov	al, WALL
	rep stosb

remove_spaces_between_walls:
;	; Remove spaces between walls
;	for y in range(2, ROWS - 1, 2):
;		for x in range(2, COLUMNS - 1, 2):
;			maze_map[x, y] = UNCONNECTED

	mov di, maze_map + (COLUMNS * 2) + 2 ; location of first space (row 2 col 2)
	mov bl, (ROWS / 2) - 1
	mov	ax, UNCONNECTED | (WALL << 8)	; a space and adjoining wall
remove_spaces_for_y:
	mov	cl, (COLUMNS / 2) - 1			; number of spaces in a row
remove_spaces_for_x:
	rep stosw

	; maze_map: di is now pointing at final space in row + 2
	; go back to first space in row, and then first space in next row:
	add di, - (2 * ((COLUMNS / 2) - 1)) + (COLUMNS * 2) 

	dec bl
	jnz remove_spaces_for_y


pick_start_point:
;	; Pick start point (left side)
;	y = r.randrange(2, ROWS - 1, 2)
	mov bx, (ROWS / 2) - 1
	call random
	; random number in DX
	mov ax, COLUMNS * 2
	mul dx
	add ax, (COLUMNS * 2) + 1 ; location (1, y)
	add ax, maze_map
	mov di, ax

;	maze_map[0, y] = CONNECTED
	mov byte [di - 1], CONNECTED

;	start = (1, y)
	mov [maze_start], ax

;	list_of_walls.append(start)
	mov word [maze_list_length], 0
	call add_to_maze_list


;	; Repeatedly remove walls to make the maze
;	while len(list_of_walls) > 0:
remove_next:
		call display_maze

		; test if list is empty
		mov bx, [maze_list_length]
		cmp bx, 0
		jz removed_all

;		; find some wall within the maze
;		(x, y) = list_of_walls.pop(r.randrange(0, len(list_of_walls)))

		int 3

		push bx
			call random
			; random number in DX
			add dx, dx
			add dx, maze_list
			mov di, dx 	 ; DI = chosen list entry address
			mov cx, [di] ; CX = location of wall
		pop ax

		; move last element in list to empty space
		; (if we picked the last element, this is still ok, though a waste of time)
		dec ax
		mov [maze_list_length], ax ; list gets shorter
		add ax, ax
		add ax, maze_list
		mov si, ax		; SI = final list entry location
		mov ax, [si]	; moved last element back
		mov [di], ax

		; CX = location of wall. Turn this into X, Y
		mov ax, cx
		sub ax, maze_map
		xor dx, dx
		; DX:AX = location
		mov bx, COLUMNS
		div bx
		; DX = X = location % COLUMNS
		; AX = Y = location / COLUMNS
		mov di, cx
		; DI = CX = location of wall
		mov bx, (CONNECTED << 8) | UNCONNECTED
		; BH = CONNECTED
		; BL = UNCONNECTED

;		if (y % 2) == 0:
		test al, 1
		jnz y_is_odd
;			; Wall has spaces to the left and right
;			assert (x % 2) == 1
			test dl, 1
			jz assert_fail_1

;			if maze_map[x - 1, y] == UNCONNECTED:
			cmp [di - 1], bl
			jnz check_right
;				; unconnected space to the left
;				assert maze_map[x + 1, y] == CONNECTED
				cmp [di + 1], bh
				jnz assert_fail_2

;				maze_map[x, y] = CONNECTED
				mov [di], bh
;				maze_map[x - 1, y] = CONNECTED
				mov [di - 1], bh
;				list_of_walls.append((x - 1, y - 1))
				add di, (- COLUMNS - 1)
				call add_to_maze_list
;				list_of_walls.append((x - 1, y + 1))
				add di, COLUMNS * 2
				call add_to_maze_list
;				list_of_walls.append((x - 2, y))
				add di, (- COLUMNS - 1)
				call add_to_maze_list
				jmp remove_next

check_right:
;			elif maze_map[x + 1, y] == UNCONNECTED:
			cmp [di + 1], bl
			jnz remove_next

;				; unconnected space to the right
;				assert maze_map[x - 1, y] == CONNECTED
				cmp [di - 1], bh
				jnz assert_fail_3

;				maze_map[x, y] = CONNECTED
				mov [di], bh
;				maze_map[x + 1, y] = CONNECTED
				mov [di + 1], bh
;				list_of_walls.append((x + 1, y - 1))
				add di, (+ 1 - COLUMNS)
				call add_to_maze_list
;				list_of_walls.append((x + 1, y + 1))
				add di, COLUMNS * 2
				call add_to_maze_list
;				list_of_walls.append((x + 2, y))
				add di, (+ 1 - COLUMNS)
				call add_to_maze_list
				jmp remove_next

;			else:
;				; both spaces already connected, do nothing
;				pass
;		else:

y_is_odd:
;			; Wall has spaces above and below
;			assert (x % 2) == 0
			test dl, 1
			jnz assert_fail_4

;			if maze_map[x, y - 1] == UNCONNECTED:
			cmp [di - COLUMNS], bl
			jnz check_below
;				; unconnected space above
;				assert maze_map[x, y + 1] == CONNECTED
				cmp [di + COLUMNS], bh 
				jnz assert_fail_5

;				maze_map[x, y] = CONNECTED
				mov [di], bh
;				maze_map[x, y - 1] = CONNECTED
				mov [di - COLUMNS], bh
;				list_of_walls.append((x - 1, y - 1))
				add di, (- 1 - COLUMNS)
				call add_to_maze_list
;				list_of_walls.append((x + 1, y - 1))
				add di, 2
				call add_to_maze_list
;				list_of_walls.append((x, y - 2))
				add di, (- 1 - COLUMNS)
				call add_to_maze_list
				jmp remove_next

check_below:
;			elif maze_map[x, y + 1] == UNCONNECTED:
			cmp [di + COLUMNS], bl
			jnz remove_next
;				; unconnected space below
;				assert maze_map[x, y - 1] == CONNECTED
				cmp [di - COLUMNS], bh 
				jnz assert_fail_6

;				maze_map[x, y] = CONNECTED
				mov [di], bh
;				maze_map[x, y + 1] = CONNECTED
				mov [di + COLUMNS], bh
;				list_of_walls.append((x - 1, y + 1))
				add di, (- 1 + COLUMNS)
				call add_to_maze_list
;				list_of_walls.append((x + 1, y + 1))
				add di, 2
				call add_to_maze_list
;				list_of_walls.append((x, y + 2))
				add di, (+ COLUMNS - 1)
				call add_to_maze_list
				jmp remove_next
;			else:
;				; both spaces already connected, do nothing
;				pass
;

removed_all:

a:
	jmp	a	
	

;	; Begin creating the maze
;	r = random.Random(seed)
;	maze_map = dict()
;	list_of_walls = []
;
;	; Fill the maze area with walls
;	for y in range(ROWS):
;		for x in range(COLUMNS):
;			maze_map[x, y] = WALL
;
;	; Remove spaces between walls
;	for y in range(2, ROWS - 1, 2):
;		for x in range(2, COLUMNS - 1, 2):
;			maze_map[x, y] = UNCONNECTED
;
;	; Pick start point (left side)
;	y = r.randrange(2, ROWS - 1, 2)
;	start = (1, y)
;	maze_map[0, y] = CONNECTED
;	list_of_walls.append(start)
;
;	; Repeatedly remove walls to make the maze
;	while len(list_of_walls) > 0:
;		; find some wall within the maze
;		(x, y) = list_of_walls.pop(r.randrange(0, len(list_of_walls)))
;
;		if (y % 2) == 0:
;			; Wall has spaces to the left and right
;			assert (x % 2) == 1
;			if maze_map[x - 1, y] == UNCONNECTED:
;				; unconnected space to the left
;				assert maze_map[x + 1, y] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x - 1, y] = CONNECTED
;				list_of_walls.append((x - 1, y - 1))
;				list_of_walls.append((x - 1, y + 1))
;				list_of_walls.append((x - 2, y))
;			elif maze_map[x + 1, y] == UNCONNECTED:
;				; unconnected space to the right
;				assert maze_map[x - 1, y] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x + 1, y] = CONNECTED
;				list_of_walls.append((x + 1, y - 1))
;				list_of_walls.append((x + 1, y + 1))
;				list_of_walls.append((x + 2, y))
;			else:
;				; both spaces already connected, do nothing
;				pass
;		else:
;			; Wall has spaces above and below
;			assert (x % 2) == 0
;			if maze_map[x, y - 1] == UNCONNECTED:
;				; unconnected space above
;				assert maze_map[x, y + 1] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x, y - 1] = CONNECTED
;				list_of_walls.append((x - 1, y - 1))
;				list_of_walls.append((x + 1, y - 1))
;				list_of_walls.append((x, y - 2))
;			elif maze_map[x, y + 1] == UNCONNECTED:
;				; unconnected space below
;				assert maze_map[x, y - 1] == CONNECTED
;				maze_map[x, y] = CONNECTED
;				maze_map[x, y + 1] = CONNECTED
;				list_of_walls.append((x - 1, y + 1))
;				list_of_walls.append((x + 1, y + 1))
;				list_of_walls.append((x, y + 2))
;			else:
;				; both spaces already connected, do nothing
;				pass
;
;	; Pick finish point (right side)
;	x = COLUMNS - 2
;	y = r.randrange(2, ROWS - 1, 2)
;	maze_map[x, y] = FINISH 
;	x += 1
;	maze_map[x, y] = CONNECTED
;
;	; Mark start point
;	(x, y) = start
;	maze_map[x, y] = START
;
;	; Maze is finished
;	return maze_map
;


; Copy the current maze to the screen

display_maze:
;	; Display maze
	push es
	mov dx, 0xb800
	mov es, dx
	mov	si, maze_map + COLUMNS + 1		; maze map row 1 col 1
	mov di, 0							; screen row 0 col 0
	mov ah, 0x0f						; attribute
	mov bl, ROWS - 1

display_for_y:
	mov cx, COLUMNS - 2

display_for_x:							; copy row Y
		mov al, [si]					; load maze element
		mov [es:di], ax					; copy maze element and attribute to screen
		inc di							; next screen loc
		inc di
		inc si							; next maze loc
		loop display_for_x

	inc si								; move to col 0 of next row
	inc si								; move to col 1 of next row

	; screen: go back to first space in row, and then first space in next row:
	add di, - ((COLUMNS - 2) * 2) + (SCREEN_COLUMNS * 2)
	dec bl
	jnz display_for_y

	pop es
	ret

; Generate a pseudo random number
; When called, BX = top end of range
; Returns number 0 <= DX < top end of range

random:
	; random_state_z = (36969 * (random_state_z & 0xffff)) + (random_state_z >> 16) 
	mov word	ax, 36969
	mul word	[random_state_z]		; DX:AX = 36969 * (random_state_z & 0xffff) 
	add word 	ax, [random_state_z + 2]	; add random_state_z >> 16 to AX 
	mov word	[random_state_z], ax		; store low word of random_state_z 
	jnc		z_no_carry
	inc word	dx		; carry into high word of random_state_z 
z_no_carry:
	mov word	[random_state_z + 2], dx	; store high word of random_state_z 

	; random_state_w = (18000 * (random_state_w & 0xffff)) + (random_state_w >> 16) 
	mov word	ax, 18000
	mul word	[random_state_w]		; DX:AX = 18000 * (random_state_w & 0xffff) 
	add word 	ax, [random_state_w + 2]	; add random_state_w >> 16 to AX 
	mov word	[random_state_w], ax		; store low word of random_state_w 
	jnc		w_no_carry
	inc word	dx		; carry into high word of random_state_w 
w_no_carry:
	mov word	[random_state_w + 2], dx	; store high word of random_state_w 

	; DX:AX already contains random_state_w
	; get a 32-bit pseudo random number in DX:AX
	xor ax, [random_state_z]

	; squash to 16 bits to avoid division overflow
	xor dx, dx

	; DX:AX divide by BX
	div bx
	; DX is remainder
	ret

; Add DI to maze list

add_to_maze_list:
	mov		ax, [maze_list_length]
	mov		si, maze_list
	add		si, ax
	add		si, ax
	mov		[si], di
	inc		ax
	mov		[maze_list_length], ax
	ret
	ret
	ret
	ret
	ret

assert_fail_1:
	int 3
assert_fail_2:
	int 3
assert_fail_3:
	int 3
assert_fail_4:
	int 3
assert_fail_5:
	int 3
assert_fail_6:
	int 3
	ret


	align 8
random_state_z:
	dd			362436069
random_state_w:
	dd			521288629
maze_start:
	resb	2
maze_list_length:
	resb	2

	align 8
maze_map:
	resb	ROWS * COLUMNS

	align 8
maze_list:
	resb	ROWS * COLUMNS * 2



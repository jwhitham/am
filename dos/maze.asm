
WALL equ 'q' + (32 * 2)
UNCONNECTED equ '.'
CONNECTED equ ' '
ROWS equ 27
COLUMNS equ 41
BASE_VIDEO_MEMORY equ 0xa000
HALF_WIDTH EQU 160
HALF_HEIGHT EQU 100
FIXED_POINT EQU 256


	section .text
	cpu 8086
	bits 16
	org 0x100

start:
; MCGA mode
	mov ax, 19 
	int	0x10

; init pseudo random number generator from RTC
	xor ax, ax
	int 0x1a
	xor [random_state_z], cx
	xor [random_state_w], dx

; Direction flag remains clear for whole program
	cld

; FS points to video RAM
	mov dx, BASE_VIDEO_MEMORY
	mov fs, dx

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
	mov [player_location], ax

;	list_of_walls.append(start)
	mov word [maze_list_length], 0
	call add_to_maze_list


;	; Repeatedly remove walls to make the maze
;	while len(list_of_walls) > 0:
remove_next:

		; test if list is empty
		mov bx, [maze_list_length]
		test bx, bx
		jz removed_all

;		; find some wall within the maze
;		(x, y) = list_of_walls.pop(r.randrange(0, len(list_of_walls)))

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
assert_fail_1:
			jz assert_fail_1

;			if maze_map[x - 1, y] == UNCONNECTED:
			cmp [di - 1], bl
			jnz check_right
;				; unconnected space to the left
;				assert maze_map[x + 1, y] == CONNECTED
				cmp [di + 1], bh
assert_fail_2:
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
				jmp add_to_maze_list_remove_next

check_right:
;			elif maze_map[x + 1, y] == UNCONNECTED:
			cmp [di + 1], bl
			jnz remove_next

;				; unconnected space to the right
;				assert maze_map[x - 1, y] == CONNECTED
				cmp [di - 1], bh
assert_fail_3:
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
				jmp add_to_maze_list_remove_next

;			else:
;				; both spaces already connected, do nothing
;				pass
;		else:

y_is_odd:
;			; Wall has spaces above and below
;			assert (x % 2) == 0
			test dl, 1
assert_fail_4:
			jnz assert_fail_4

;			if maze_map[x, y - 1] == UNCONNECTED:
			cmp [di - COLUMNS], bl
			jnz check_below
;				; unconnected space above
;				assert maze_map[x, y + 1] == CONNECTED
				cmp [di + COLUMNS], bh 
assert_fail_5:
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
				jmp add_to_maze_list_remove_next

check_below:
;			elif maze_map[x, y + 1] == UNCONNECTED:
			cmp [di + COLUMNS], bl
			jnz remove_next
;				; unconnected space below
;				assert maze_map[x, y - 1] == CONNECTED
				cmp [di - COLUMNS], bh 
assert_fail_6:
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
				jmp add_to_maze_list_remove_next
;			else:
;				; both spaces already connected, do nothing
;				pass
;

removed_all:

;
;	; Pick finish point (right side)
;	x = COLUMNS - 2
;	y = r.randrange(2, ROWS - 1, 2)

	mov bx, (ROWS / 2) - 1
	call random
	; random number in DX
	mov ax, COLUMNS * 2
	mul dx
	add ax, (COLUMNS * 2) + COLUMNS - 2 ; location (COLUMNS - 1, y)
	add ax, maze_map
	mov di, ax

;	maze_map[x, y] = FINISH 
	mov byte [di], CONNECTED
;	x += 1
;	maze_map[x, y] = CONNECTED
	mov byte [di + 1], CONNECTED

	; Prevent player escaping to the left
	mov si, [player_location]
	mov al, WALL
	mov [si - 1], al



	; while True:
game_loop:
		; drawing

		; camera_vector_x = FIXED_POINT
		; camera_vector_y = 0
		; ; normal to the camera vector (projection plane for view)
		; plane_vector_x = -camera_vector_y
		; plane_vector_y = camera_vector_x
		
		camera_vector_x EQU FIXED_POINT
		camera_vector_y EQU 0
		; ; normal to the camera vector (projection plane for view)
		plane_vector_x EQU -camera_vector_y
		plane_vector_y EQU camera_vector_x

		mov word [screen_x], -HALF_WIDTH
		; for screen_x in range(-HALF_WIDTH, HALF_WIDTH, 1):
draw_x_loop:
			; ; vector for this screen X (the ray being cast)
			; ray_vector_x = camera_vector_x + ((plane_vector_x * screen_x) / HALF_WIDTH)
			; mov ax, plane_vector_x
			; mov cx, camera_vector_x
			; call ax_times_screen_x_div_half_width_plus_cx

			; ray_vector_y = camera_vector_y + ((plane_vector_y * screen_x) / HALF_WIDTH)
			mov ax, plane_vector_y
			mul word [screen_x]
			mov bx, HALF_WIDTH
			mov dh, dl ; sign extending for integer division
			idiv bx
			mov [ray_vector_y], ax

			; viewer_x = rotated_player_x
			; viewer_y = rotated_player_y
			; maze_x = viewer_x / FIXED_POINT
			; maze_y = viewer_y / FIXED_POINT
			mov ax, [player_x]
			mov [viewer_x], ax
			mov [maze_x_byte], ah
			mov ax, [player_y]
			mov [viewer_y], ax
			mov [maze_y_byte], ah


			; while (maze_x < rotated_maze.columns) and (abs(maze_y) < rotated_maze.columns):
find_wall_loop:
				; sub_x = viewer_x - (maze_x * FIXED_POINT)
				mov ax, [viewer_x]
				sub ax, [maze_x_fp_word]
				mov [sub_x], ax

				; sub_y = viewer_y - (maze_y * FIXED_POINT)
				mov ax, [viewer_y]
				sub ax, [maze_y_fp_word]
				mov [sub_y], ax

				; ; find first intersection with horizontal line
				; i1x = i1y = None
				xor bx, bx
				not bx
				mov [i1x], ax ; i1x = 0xffff

				mov bx, [ray_vector_y]
				cmp bx, 0
				jge not_above		; jump if ray_vector_y >= 0

					; above (left hand side) ray_vector_y < 0
					; i1y = maze_y * FIXED_POINT
					mov cx, [maze_y_fp_word] ; cx may be stored in i1y now

					; i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)))
					neg ax ; ax = -sub_y
					jmp above_or_below

not_above:
					je done_horizontal ; jump if ray_vector_y == 0

					; below (right hand side) ray_vector_y > 0
					; i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)))
					; i1y = (maze_y + 1) * FIXED_POINT
					mov cx, [maze_y_fp_word]
					inc ch ; cx may be stored in i1y now

					mov dx, FIXED_POINT
					sub dx, ax
					mov ax, dx ; ax = FIXED_POINT - sub_y

above_or_below:
					mov [i1y], cx
					mul word [ray_vector_x]
					div word [ray_vector_y]
					add ax, [viewer_x]
					mov [i1x], ax

done_horizontal:

				; find first intersection with vertical line
				; i2x = i2y = None
				; if ray_vector_x > 0:
				;	i2x = (maze_x + 1) * FIXED_POINT
				;	i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x))
				mov cx, [maze_x_fp_word]
				inc ch ; cx = i2x
				mov [i2x], cx

				mov ax, FIXED_POINT
				sub ax, [sub_x]
				mul word [ray_vector_y]
				div word [ray_vector_x]
				add ax, [viewer_y]
				mov [i2y], ax

				cmp cx, [i1x] ; compare i2x with i1x
				jge i2x_is_greater_equal

					; i1x > i2x
					; crosses vertical line first
					; maze_x += 1
					inc byte [maze_x_byte]
					; viewer_x = i2x
					; viewer_y = i2y
					mov [viewer_x], cx ; cx = 12x
					mov [viewer_y], ax ; ax = i2y

					; assert maze_x == (viewer_x / FIXED_POINT)
					; texture_x = (i2y * texture_width) / FIXED_POINT
					; texture_x %= texture_width
					mov [texture_x], ax
					jmp done_intersection

i2x_is_greater_equal:
					; i1x <= i2y
					; if i2x == i1x:
					jne i2x_is_greater

					;	# special case: crosses both lines at once
					;	maze_x += 1
					inc byte [maze_x_byte]

i2x_is_greater:
					; crosses horizontal line first
					mov cx, [i1x]
					mov ax, [i1y]
					mov [viewer_x], cx ; cx = 11x
					mov [viewer_y], ax ; ax = i1y

					; assert maze_x == (viewer_x / FIXED_POINT)
					; if ray_vector_y < 0:
					mov bx, [ray_vector_y]
					cmp bx, 0
					jge not_above_2		; jump if ray_vector_y >= 0

						; assert maze_y == (viewer_y / FIXED_POINT)
						; maze_y -= 1
						dec byte [maze_y_byte]
						; texture_x = (i1x * texture_width) / FIXED_POINT
						; texture_x %= texture_width
						mov [texture_x], cx
						jmp done_intersection
not_above_2:
						; maze_y += 1
						inc byte [maze_y_byte]
						; assert maze_y == (viewer_y / FIXED_POINT)
						; texture_x = (i1x * texture_width) / FIXED_POINT
						; texture_x = texture_width - (texture_x % texture_width) - 1
						neg cx
						mov [texture_x], cx

done_intersection:
				; Ray cast has reached [maze_x], [maze_y]
				; did we reach a wall?
				; First we see if we're actually still inside the maze
				mov [maze_x_byte], al
				cmp al, COLUMNS
				jge did_not_find_wall

				; maze_y < ROWS
				mov [maze_y_byte], bl
				cmp bl, ROWS
				jge did_not_find_wall

				; still inside maze, get maze location
				mov ah, 0 ; AX = maze_y
				mov dx, COLUMNS
				mul dx
				mov bh, 0 ; BX = maze_y
				add ax, bx
				add ax, maze_map
				mov di, ax
				mov al, [di]
				cmp al, WALL
				jne find_wall_loop ; didn't find a wall ... yet

				; found a wall at [viewer_x], [viewer_y]
				; distance = viewer_x - rotated_player_x
				mov [player_x], ax
				sub ax, [viewer_x]

				; half_height = ((FIXED_POINT * (HALF_HEIGHT - 1)) / distance)
				mov bx, FIXED_POINT * (HALF_HEIGHT - 1)
				xor dx, dx
				div bx ; AX = half_height

				; clipping
				cmp ax, HALF_HEIGHT
				jle no_clip
					mov ax, HALF_HEIGHT - 1
no_clip:
				mov [texture_half_height], ax

				mov cx, HALF_HEIGHT
				sub cx, [texture_half_height] ; CX = draw start row
				mov di, [screen_x] ; first pixel to draw

				; draw ceiling
ceiling_draw_loop:
					mov byte [fs:di], 0
					add di, HALF_WIDTH * 2
					loop ceiling_draw_loop
				
				; draw texture
				mov cx, [texture_half_height]
				add cx, cx ; CX = texture height

				mov bl, [maze_x_byte] 
				add bl, [maze_y_byte] ; pick a pixel colour
				xor bl, 0x55
texture_draw_loop:
					mov byte [fs:di], bl
					add di, HALF_WIDTH * 2
					loop texture_draw_loop

				; draw floor until we reach the end of the video RAM
floor_draw_loop:
					mov byte [fs:di], 0
					add di, HALF_WIDTH * 2
					cmp di, HALF_WIDTH * 2 * HALF_HEIGHT * 2
					jl  floor_draw_loop

did_not_find_wall:
			; end find_wall_loop
			; do next X
			mov ax, [screen_x]
			inc ax
			mov [screen_x], ax
			cmp ax, HALF_WIDTH
			jl  draw_x_loop


		; end draw_x_loop
		; screen is now complete

		jmp game_loop




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

; Add DI to maze list then jump to remove_next

add_to_maze_list_remove_next:
	mov		ax, remove_next
	push 	ax

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

press_escape:
	mov dx, msg_escape
	jmp exit
win_game:
	mov dx, msg_you_win_the_game

exit:
; 80 column text mode
	push dx
		mov	ax, 3
		int	0x10
	pop dx
; print message
	mov ah, 0x09
	int	0x21
; back to DOS
	mov ax, 0x4c00
	int	0x21

; section .data
random_state_z:
	dd			362436069
random_state_w:
	dd			521288629
msg_you_win_the_game:
	db		"You win!!"
	db		13
	db 		10
msg_escape:
	db		'$'
maze_x_fp_word:
	db		0
maze_x_byte:
	db		0
maze_y_fp_word:
	db		0
maze_y_byte:
	db		0
ray_vector_x:
	dw		FIXED_POINT

; section .bss

player_location:	resb	2
maze_list_length: 	resb	2
maze_map: 			resb	ROWS * COLUMNS
maze_list: 			resb	(ROWS * COLUMNS) / 4
screen_x: 			resb	2
ray_vector_y: 		resb	2
player_x: 			resb	2
player_y: 			resb	2
viewer_x: 			resb	2
viewer_y: 			resb	2
sub_x:    			resb	2
sub_y:    			resb	2
i1x:      			resb	2
i2x:      			resb	2
i1y:      			resb	2
i2y:      			resb	2
texture_x:			resb	2
texture_half_height: resb	2




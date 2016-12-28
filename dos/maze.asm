
WALL equ 'q' + (32 * 2)
UNCONNECTED equ '.'
CONNECTED equ ' '
ROWS equ 27
COLUMNS equ 41
TEXT_ATTRIBUTE equ 12
SCREEN_COLUMNS equ 40
SCREEN_ROWS equ 25
MAZE_ATTRIBUTE equ 0x0f
PLAYER_ATTRIBUTE equ 0x1e
SEEN_ATTRIBUTE equ 0x1e
PLAYER equ 5
BASE_VIDEO_MEMORY equ 0xb800

	section .text
	cpu 8086
	bits 16
	org 0x100

start:
; 40 column text mode
	xor ax, ax
	int	0x10

; init pseudo random number generator from RTC
	xor ax, ax
	int 0x1a
	xor [random_state_z], cx
	xor [random_state_w], dx

; hide the cursor
	mov ah, 1
	xor cx, 0x2000
	int 0x10

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

	call display_maze
;
;	; Mark start point
;	(x, y) = start
;	maze_map[x, y] = START
;
;	; Maze is finished
;	return maze_map
;
;	It's time to play!

solving_maze:
		; get X and Y for player
		mov si, [player_location]
		mov ax, si
		xor dx, dx
		sub ax, maze_map

		; DX:AX = location
		mov bx, COLUMNS
		div bx
		; DX = X = location % COLUMNS
		; AX = Y = location / COLUMNS

		; player has won if X >= last column
		cmp dx, COLUMNS - 1
		jge win_game

		; draw on screen
		push dx
			mov dx, SCREEN_COLUMNS * 2
			dec ax
			mul dx
			; AX = beginning of row
		pop dx
		dec dx
		add ax, dx
		add ax, dx ; AX = location of player on screen
		mov di, ax
		mov ax, (PLAYER_ATTRIBUTE << 8) | PLAYER ; draw player on screen
		mov [fs:di], ax

invalid_move:
		; wait for a move - blocking read from keyboard 
			mov si, [player_location]
			mov ah, 0
			int 0x16
			or al, 0x20 ; lower case

			cmp al, 'j'
			jz go_down
			cmp ah, 0x50
			jz go_down

			cmp al, 'k'
			jz go_up
			cmp ah, 0x48
			jz go_up

			cmp al, 'h'
			jz go_left
			cmp ah, 0x4b
			jz go_left

			cmp al, 'l'
			jz go_right
			cmp ah, 0x4d
			jz go_right

			cmp ah, 1
			jz press_escape
			jmp invalid_move

go_down:
		add si, COLUMNS
		jmp check_move
go_up:
		add si, -COLUMNS
		jmp check_move
go_left:
		add si, -1
		jmp check_move
go_right:
		add si, +1

check_move:
		mov al, [si]
		cmp al, CONNECTED
		jnz invalid_move

		; move was valid - undraw the player
		mov ax, (SEEN_ATTRIBUTE << 8)
		mov [fs:di], ax

		; move the player
		mov [player_location], si

		jmp solving_maze

; Copy the current maze to the screen

display_maze:
;	; Display maze
	mov dx, BASE_VIDEO_MEMORY

	mov	si, maze_map + COLUMNS + 1		; maze map row 1 col 1
	mov di, 0							; screen row 0 col 0
	mov ah, MAZE_ATTRIBUTE					; attribute
	mov bl, ROWS - 1

display_for_y:
	mov cx, COLUMNS - 2

display_for_x:							; copy row Y
		mov al, [si]					; load maze element
		mov [fs:di], ax					; copy maze element and attribute to screen
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

section .data
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

section .bss

player_location:
	resb	2
maze_list_length:
	resb	2
maze_map:
	resb	ROWS * COLUMNS
maze_list:
	resb	(ROWS * COLUMNS) / 4



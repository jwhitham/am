
	org     0x100

cga_mode_register equ 0x3d8

start:
	mov		ax, 4
	int		0x10

	;mov		al, 8 | 2
	;mov		dx, 0x3d8
	;out		dx, al

	mov		dx, 0xb800
	mov		ds, dx

r:
	inc		dl
	mov		cl, dl
	and		cl, 3
	mov		al, cl
	shl		cl, 2
	or		al, cl
	shl		cl, 2
	or		al, cl
	shl		cl, 2
	or		al, cl
	mov		bx, 320 * 200 / 4
a:
	dec		bx
	mov		[bx], al
	xor		al, 0xc0
	test	bx, bx
	jnz		a

	mov		cx, 1000
a3:
	mov		bx, 1000
a2:
	dec		bx
	test	bx, bx
	jnz		a2

	dec		cx
	test	cx, cx
	jnz		a3


	jmp r



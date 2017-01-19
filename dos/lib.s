
export _lib_init
_lib_init:
	mov	ax, #4
	int #0x10
	ret

export	_set_pixel
_set_pixel:
	push si
	mov si, sp
	push gs
	mov ax, #0xb800
	mov gs, ax
	mov	ax,6[si]
	mov	si,4[si]
	gseg
	mov [si],al
	pop gs
	pop si
	ret

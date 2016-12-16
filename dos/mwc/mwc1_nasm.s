CPU X64
BITS 64
GLOBAL mwc1
EXTERN z
EXTERN w
EXTERN r

mwc1:
	; z = (36969 * (z & 0xffff)) + (z >> 16) 
	mov word	ax, 36969
	mul word	[z]		; DX:AX = 36969 * (z & 0xffff) 
	add word 	ax, [z + 2]	; add z >> 16 to AX 
	mov word	[z], ax		; store low word of z 
	jnc		z_no_carry
	inc word	dx		; carry into high word of z 
z_no_carry:
	mov word	[z + 2], dx	; store high word of z 

	; w = (18000 * (w & 0xffff)) + (w >> 16) 
	mov word	ax, 18000
	mul word	[w]		; DX:AX = 18000 * (w & 0xffff) 
	add word 	ax, [w + 2]	; add w >> 16 to AX 
	mov word	[w], ax		; store low word of w 
	jnc		w_no_carry
	inc word	dx		; carry into high word of w 
w_no_carry:
	mov word	[w + 2], dx	; store high word of w 

	; return z << 16 + w 
	mov word	ax, [w]
	mov word	[r], ax
	mov word	ax, [w + 2]
	add word	ax, [z]
	mov word	[r + 2], ax
	
	mov long	eax, [r]
	ret



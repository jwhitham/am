; 1 
; 1 # 1 "test.c"
; 1 
; 2 int main()
; 3 {
global _main
_main:
; 4 	return 0;
push	bp
mov	bp,sp
push	di
push	si
xor	ax,ax
pop	si
pop	di
pop	bp
ret
;BCC_EOS
; 5 }
; 6 
.data
.bss

; 0 errors detected

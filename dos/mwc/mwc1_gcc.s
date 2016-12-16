.global mwc1
mwc1:
	/* z = (36969 * (z & 0xffff)) + (z >> 16) */
	movw	$36969, %ax
	mulw	z		/* DX:AX = 36969 * (z & 0xffff) */
	addw 	z + 2, %ax	/* add z >> 16 to AX */
	movw	%ax, z		/* store low word of z */
	jnc	z_no_carry
	incw	%dx		/* carry into high word of z */
z_no_carry:
	movw	%dx, z + 2	/* store high word of z */

	/* w = (18000 * (w & 0xffff)) + (w >> 16) */
	movw	$18000, %ax
	mulw	w		/* DX:AX = 18000 * (w & 0xffff) */
	addw 	w + 2, %ax	/* add w >> 16 to AX */
	movw	%ax, w		/* store low word of w */
	jnc	w_no_carry
	incw	%dx		/* carry into high word of w */
w_no_carry:
	movw	%dx, w + 2	/* store high word of w */

	/* return z << 16 + w */
	movw	w, %ax
	movw	%ax, r
	movw	w + 2, %ax
	addw	z, %ax
	movw	%ax, r + 2
	
	movl	r, %eax
	ret


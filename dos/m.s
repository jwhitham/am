.global mwc1
mwc1:
	/* z = (36969 * (z & 0xffff)) + (z >> 16) */
	movl	z, %eax
	movzwl	%ax, %edx
	shrl	$16, %eax
	imull	$36969, %edx, %edx
	addl	%edx, %eax
	movl	%eax, z

	/* w = (18000 * (w & 0xffff)) + (w >> 16) */
	movl	w, %edx
	movzwl	%dx, %ecx
	shrl	$16, %edx
	imull	$18000, %ecx, %ecx
	addl	%ecx, %edx
	movl	%edx, w

	/* return z << 16 + w */
	sall	$16, %eax
	addl	%edx, %eax
	ret

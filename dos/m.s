.global mwc1
mwc1:
	movl	z, %eax
	movzwl	%ax, %edx
	shrl	$16, %eax
	imull	$36969, %edx, %edx
	addl	%edx, %eax
	movl	w, %edx
	movl	%eax, z
	sall	$16, %eax
	movzwl	%dx, %ecx
	shrl	$16, %edx
	imull	$18000, %ecx, %ecx
	addl	%ecx, %edx
	movl	%edx, w
	addl	%edx, %eax
	ret

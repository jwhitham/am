#include <stdio.h>
#include <stdint.h>

uint32_t r;
uint32_t z=362436069, w=521288629;
uint32_t z1=362436069, w1=521288629;

#define znew (z1=36969*(z1&65535)+(z1>>16))
#define wnew (w1=18000*(w1&65535)+(w1>>16))
#define MWC ((znew<<16)+wnew )

uint32_t mwc1 (void);

uint32_t mwc_c (void)
{
	return MWC;
}

int main (void)
{
	uint32_t i;

	for (i = 0; i < 100000; i++) {
		if (mwc1 () != mwc_c ()) {
			printf ("error\n");
			return 1;
		}
	}
	printf ("OK\n");
	return 0;
}



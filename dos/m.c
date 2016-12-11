#include <stdio.h>
#include <stdint.h>

// CMWC engine
uint32_t randCMWC(void)
{
	uint64_t const ka = 18782; // as Marsaglia recommends
	uint32_t const km = 0xfffffffe; // as Marsaglia recommends
	uint64_t vt;
	uint32_t vx;
	static uint32_t gQ = 1;
	static uint32_t gc = 809430660 - 1;

	vt = ka * gQ + gc;
	/* Let gc = vt / 0xfffffff, vx = vt mod 0xffffffff */
	gc = vt >> 32;
	vx = vt + gc;
	if (vx < gc) {
		vx++;
		gc++;
	}
	gQ = km - vx;
	return gQ;
}


uint32_t z=362436069, w=521288629;
uint32_t z1=362436069, w1=521288629;

#define znew (z=36969*(z&65535)+(z>>16))
#define wnew (w=18000*(w&65535)+(w>>16))
#define MWC ((znew<<16)+wnew )

uint32_t mwc1 (void);
uint32_t mwc (void)
{
	return MWC;
}

int main (void)
{
	uint32_t i;

	for (i = 0; i < 10000; i++) {
		printf ("%08x\n", mwc1 ());
	}
	return 0;
}



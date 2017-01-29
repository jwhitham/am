
#include <stdint.h>
#include <assert.h>
#include <math.h>
#include <stdlib.h>

#include "draw_view.h"


static fixed_t fisheye_correction[HALF_WIDTH * 2];


void draw_init (void)
{
	fixed_t screen_x;

	for (screen_x = -HALF_WIDTH; screen_x < HALF_WIDTH; screen_x++) {
		fixed_t ray_vector_x = FIXED_POINT;
		fixed_t ray_vector_y = ((FIXED_POINT * screen_x) / HALF_WIDTH);
		fixed_t total = (ray_vector_x * ray_vector_x) + (ray_vector_y * ray_vector_y);
		fixed_t distance = FIXED_POINT;
		int i;
		for (i = 0; i < 16; i++) {
			distance = (distance + (total / distance)) / 2;
		}
		fisheye_correction[screen_x + HALF_WIDTH] = distance * (HALF_HEIGHT - 1);
	}
}

static void map_plot (uint8_t * pixels, fixed_t dx, fixed_t dy)
{
	unsigned x, y;
	const int scale = (HALF_WIDTH / 12);
	uint8_t * p;

	x = HALF_WIDTH + ((dx * scale) / FIXED_POINT);
	y = HALF_HEIGHT + ((dy * scale) / FIXED_POINT);
	if ((x < (HALF_WIDTH * 2)) && (y < (HALF_HEIGHT * 2))) {
		p = &pixels[x + (y * HALF_WIDTH * 2)];
		*p = 0xff;
	}
}

void draw_view (uint8_t * pixels, fixed_t camera_x, fixed_t camera_y, float camera_angle, maze_t * maze, texture_t * texture, int map)
{
	fixed_t screen_x;

	// ray cast from the centre of the screen
	fixed_t camera_vector_x = (fixed_t) floorf (FIXED_POINT * cosf (camera_angle));
	fixed_t camera_vector_y = (fixed_t) floorf (FIXED_POINT * sinf (camera_angle));

	// normal to the camera vector (projection plane for view)
	fixed_t plane_vector_x = -camera_vector_y;
	fixed_t plane_vector_y = camera_vector_x;

	if (map) {
		map_plot (pixels, 0, 0);
	}

	for (screen_x = -HALF_WIDTH; screen_x < HALF_WIDTH; screen_x++) {
		fixed_t texture_x = 0;

		// vector for this screen X (the ray being cast)
		fixed_t ray_vector_x = camera_vector_x + ((plane_vector_x * screen_x) / HALF_WIDTH);
		fixed_t ray_vector_y = camera_vector_y + ((plane_vector_y * screen_x) / HALF_WIDTH);
		fixed_t viewer_x = camera_x;
		fixed_t viewer_y = camera_y;

		fixed_t maze_x = (fixed_t) (viewer_x / FIXED_POINT);
		fixed_t maze_y = (fixed_t) (viewer_y / FIXED_POINT);
		uint16_t cell = 0;
		char wall = ' ';

		// begin casting
		cast_again:
		{
			fixed_t sub_x = viewer_x - ((fixed_t) maze_x * FIXED_POINT);
			fixed_t sub_y = viewer_y - ((fixed_t) maze_y * FIXED_POINT);
			fixed_t i1x = INT32_MAX;
			fixed_t i1y = INT32_MAX;
			fixed_t i2x = INT32_MAX;
			fixed_t i2y = INT32_MAX;
			int i2_is_nearer = 0;
			int northern_wall = 1;
			int southern_wall = 1;
			int western_wall = 1;
			int eastern_wall = 1;

			assert ((0 <= sub_x) && (sub_x <= FIXED_POINT));
			assert ((0 <= sub_y) && (sub_y <= FIXED_POINT));

			if (ray_vector_x <= 0) {
				// not defined (west side)
				i1x = i1y = INT32_MIN;
			}
			if (ray_vector_y <= 0) {
				// not defined (north side)
				i2x = i2y = INT32_MIN;
			}

			if (map && ((screen_x == 0) || (screen_x == -HALF_WIDTH) || (screen_x == (HALF_WIDTH - 1)))) {
				fixed_t dx = (viewer_x - camera_x);
				fixed_t dy = (viewer_y - camera_y);
				map_plot (pixels, dx, dy);
			}

			// find first intersection with horizontal line
			if ((ray_vector_y < 0) && southern_wall) {
				// north side
				i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)));
				i1y = (fixed_t) maze_y * FIXED_POINT;
			} else if ((ray_vector_y > 0) && northern_wall) {
				// south side
				i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)));
				i1y = (fixed_t) (maze_y + 1) * FIXED_POINT;
			}

			// find first intersection with vertical line
			if ((ray_vector_x < 0) && eastern_wall) {
				// west side
				i2x = (fixed_t) maze_x * FIXED_POINT;
				i2y = viewer_y + ((sub_x * ray_vector_y) / (- ray_vector_x));
			} else if ((ray_vector_x > 0) && western_wall) {
				// east side
				i2x = (fixed_t) (maze_x + 1) * FIXED_POINT;
				i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x));
			}

			// Which is nearest? i1 or i2?
			// Divide a circle into quarters, with lines at 45, 135, 225, 315 degrees
			if (abs (ray_vector_y) < abs (ray_vector_x)) {
				if (ray_vector_x > 0) {
					// East quarter
					i2_is_nearer = (i2x < i1x);
				} else {
					// West quarter
					i2_is_nearer = (i2x > i1x);
				}
			} else if (ray_vector_y > 0) {
				// South quarter
				i2_is_nearer = (i2y < i1y);
			} else {
				// North quarter
				i2_is_nearer = (i2y > i1y);
			}

			if (i2_is_nearer) {
				// crosses vertical line first
				viewer_x = i2x;
				viewer_y = i2y;
				maze_x = viewer_x / FIXED_POINT;
				maze_y = viewer_y / FIXED_POINT;
				if (ray_vector_x < 0) {
					// cross on west side
					maze_x --;
					texture_x = i2y;
					wall = 'e';
				} else {
					// cross on east side
					texture_x = - i2y;
					wall = 'w';
				}
			} else {
				// crosses horizontal line first
				// (or both lines at once)
				viewer_x = i1x;
				viewer_y = i1y;
				maze_x = viewer_x / FIXED_POINT;
				maze_y = viewer_y / FIXED_POINT;
				if (ray_vector_y < 0) {
					// cross on north side
					maze_y --;
					texture_x = i1x;
					wall = 's';
				} else {
					// cross on south side
					texture_x = - i1x;
					wall = 'n';
				}
				if (viewer_x == (maze_x * FIXED_POINT)) {
					// also crosses vertical line
					if (ray_vector_x < 0) {
						// cross on west side
						maze_x --;
					}
				}
			}

			// figure out which cell we are now entering
			if ((maze_x >= 0) && (maze_y >= 0)
			&& (maze_x < maze->columns) && (maze_y < maze->rows)) {
				cell = maze->maze[maze_x + (maze_y * maze->columns)];
			} else {
				cell = 255;	// outside the maze
			}

			switch (cell) {
				case 0:
					goto cast_again;
				case 0x33:
					// Possible intersection with edge of triangle occupying northeast corner of cell
					if (wall == 'e' || wall == 'n') {
						goto reached_wall;
					}
					sub_x = viewer_x - ((fixed_t) maze_x * FIXED_POINT);
					sub_y = viewer_y - ((fixed_t) maze_y * FIXED_POINT);
					// line runs from 0,0 to 1,1 forming a triangle
					if (ray_vector_x != ray_vector_y) {
						// intersects at sub_x == sub_y
						fixed_t i = (((ray_vector_x * sub_y) - (ray_vector_y * sub_x)) / (ray_vector_x - ray_vector_y));
						if (((unsigned) i) < FIXED_POINT) {
							viewer_x = (maze_x * FIXED_POINT) + i;
							viewer_y = (maze_y * FIXED_POINT) + i;
							texture_x = viewer_x;
							goto reached_wall;
						}
					}
					goto cast_again;
				case 0x31:
					// Possible intersection with edge of triangle occupying southeast corner of cell
					// TODO does not work when viewed from the north, equation is wrong
					if (wall == 'e' || wall == 's') {
						goto reached_wall;
					}
					sub_x = viewer_x - ((fixed_t) maze_x * FIXED_POINT);
					sub_y = viewer_y - ((fixed_t) maze_y * FIXED_POINT);
					// line runs from 0,1 to 1,0 forming a triangle
					if (ray_vector_y != -FIXED_POINT) {
						// viewed from west side
						// intersects at sub_x == (FIXED_POINT - sub_y)
						fixed_t i = (ray_vector_x * (FIXED_POINT - sub_y - sub_x)) / (FIXED_POINT + ray_vector_y);
						if (((unsigned) i) < FIXED_POINT) {
							viewer_x = (maze_x * FIXED_POINT) + i;
							viewer_y = ((maze_y + 1) * FIXED_POINT) - i;
							texture_x = viewer_x;
							goto reached_wall;
						}
					}
					goto cast_again;
				default:
					goto reached_wall;
			}
		}

		// reached wall or edge of maze
		reached_wall:
		{
			fixed_t distance;
			fixed_t half_height = HALF_HEIGHT;
			fixed_t start, dx, dy, total;
			fixed_t pos, step, height;
			int i;
			uint16_t size_log2 = texture->size_log2;
			uint8_t * p;
			uint8_t * t;

			dx = (viewer_x - camera_x);
			dy = (viewer_y - camera_y);
			total = (dx * dx) + (dy * dy);

			// Distance estimate (Manhattan)
			distance = abs (dx) + abs (dy);
			if (distance > 0) {
//				float er;
//				static float max_e = 0;
				// approximation for square root - more iterations improve accuracy
				// Starting from the Manhattan distance
				// two iterations seems to be enough to get within +/- 4
				// three iterations seems to be enough to get within +/- 1
				for (i = 0; i < 3; i++) {
					distance = (distance + (total / distance)) / 2;
				}
//				er = fabsf (sqrtf (total) - (float) distance);
//				if (er > max_e) {
//					printf ("max error %1.3f with total %d\n", er, total);
//					max_e = er;
//				}
			}
			if (distance > 0) {
				half_height = fisheye_correction[screen_x + HALF_WIDTH] / distance;

				texture_x = (texture_x & (FIXED_POINT - 1)) >> (FIXED_SHIFT - size_log2);
				t = &texture->pixels[texture_x << size_log2];

				height = half_height * 2;

				// Render size_log2 input pixels into height output pixels
				pos = 0;
				step = (1 << (TEXTURE_FIXED_SHIFT + size_log2)) / height;

				// Find starting position
				start = HALF_HEIGHT - half_height;
				if (start < 0) {
					// Offset into texture
					pos = (- start) * step;
					height = HALF_HEIGHT * 2;
					start = 0;
				}
				p = &pixels[screen_x + HALF_WIDTH + (start * HALF_WIDTH * 2)];
				assert (p >= &pixels[0]);
				assert (p < &pixels[HALF_WIDTH * HALF_HEIGHT * 4]);

				if (map) {
					map_plot (pixels, dx, dy);
				} else {
					for (i = 0; i < height; i++) {
						p[0] = t[pos >> TEXTURE_FIXED_SHIFT];
						p += HALF_WIDTH * 2;
						pos += step;
					}
				}
			}
		}
	}

}



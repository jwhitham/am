
#include <stdint.h>
#include <assert.h>
#include <math.h>
#include <stdlib.h>

#include "draw_view.h"

void draw_view (uint8_t * pixels, fixed_t camera_x, fixed_t camera_y, fixed_t camera_angle, maze_t * maze)
{
	fixed_t screen_x;

	// convert integer angle to radians.
	float angle = ((float) camera_angle) * M_PI * 2.0 / 65536.0;

	// ray cast from the centre of the screen
	fixed_t camera_vector_x = (fixed_t) floorf (FIXED_POINT * cosf (angle));
	fixed_t camera_vector_y = (fixed_t) floorf (FIXED_POINT * sinf (angle));

	// normal to the camera vector (projection plane for view)
	fixed_t plane_vector_x = -camera_vector_y;
	fixed_t plane_vector_y = camera_vector_x;

	for (screen_x = -HALF_WIDTH; screen_x < HALF_WIDTH; screen_x++) {
		fixed_t texture_x = 0;

		// vector for this screen X (the ray being cast)
		fixed_t ray_vector_x = camera_vector_x + ((plane_vector_x * screen_x) / HALF_WIDTH);
		fixed_t ray_vector_y = camera_vector_y + ((plane_vector_y * screen_x) / HALF_WIDTH);
		fixed_t viewer_x = camera_x;
		fixed_t viewer_y = camera_y;

		fixed_t maze_x = (fixed_t) (viewer_x / FIXED_POINT);
		fixed_t maze_y = (fixed_t) (viewer_y / FIXED_POINT);
		uint16_t cell;

		// begin casting
		do {
			fixed_t sub_x = viewer_x - ((fixed_t) maze_x * FIXED_POINT);
			fixed_t sub_y = viewer_y - ((fixed_t) maze_y * FIXED_POINT);
			fixed_t i1x = INT32_MAX;
			fixed_t i1y = 0;
			fixed_t i2x = INT32_MAX;
			fixed_t i2y = 0;
			int i2_is_nearer = 0;

			assert (maze_x == (viewer_x / FIXED_POINT));
			assert ((0 <= sub_x) && (sub_x <= FIXED_POINT));
			assert ((0 <= sub_y) && (sub_y <= FIXED_POINT));

			// find first intersection with horizontal line
			if (ray_vector_y < 0) {
				// north side
				i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)));
				i1y = (fixed_t) maze_y * FIXED_POINT;
			} else if (ray_vector_y > 0) {
				// south side
				i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)));
				i1y = (fixed_t) (maze_y + 1) * FIXED_POINT;
			} else if (ray_vector_x > 0) {
				// not defined (east side)
				i1x = i1y = INT32_MAX;
			} else {
				// not defined (west side)
				i1x = i1y = INT32_MIN;
			}

			// find first intersection with vertical line
			if (ray_vector_x < 0) {
				// west side
				i2x = (fixed_t) maze_x * FIXED_POINT;
				i2y = viewer_y + ((sub_x * ray_vector_y) / (- ray_vector_x));
			} else if (ray_vector_x > 0) {
				// east side
				i2x = (fixed_t) (maze_x + 1) * FIXED_POINT;
				i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x));
			} else if (ray_vector_y > 0) {
				// not defined (south side)
				i2x = i2y = INT32_MAX;
			} else {
				// not defined (north side)
				i2x = i2y = INT32_MIN;
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
				} else {
					// cross on east side
					texture_x = - i2y;
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
				} else {
					// cross on south side
					texture_x = - i1x;
				}
				if ((i2x == i1x) && (ray_vector_x < 0)) {
					// also cross on west side
					maze_x --;
				}
			}

			if ((maze_x >= 0) && (maze_y >= 0)
			&& (maze_x < maze->columns) && (maze_y < maze->rows)) {
				cell = maze->maze[maze_x + (maze_y * maze->columns)];
			} else {
				cell = 255;
			}
		} while (!cell);

		// reached wall or edge of maze
		{
			fixed_t distance = viewer_x - camera_x;
			fixed_t half_height = HALF_HEIGHT;
			fixed_t start;
			uint8_t * p;

			if (distance > 0) {
				half_height = ((FIXED_POINT * (HALF_HEIGHT - 1)) / distance);
			}
			if (half_height > HALF_HEIGHT) {
				half_height = HALF_HEIGHT;
			}
			start = HALF_HEIGHT - half_height;

			p = &pixels[screen_x + HALF_WIDTH + (start * HALF_WIDTH * 2)];
			assert (p >= &pixels[0]);
			assert (p < &pixels[HALF_WIDTH * HALF_HEIGHT * 4]);
			cell *= 16;
			cell += 64;
			cell += ((texture_x % FIXED_POINT) * 64) / FIXED_POINT;
			if (cell > 255) {
				cell = 255;
			}
			while (half_height) {
				p[0] = cell;
				p += HALF_WIDTH * 2;
				p[0] = cell;
				p += HALF_WIDTH * 2;
				half_height --;
			}
		}
	}

}


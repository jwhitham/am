
#include <stdint.h>
#include <assert.h>
#include <math.h>

#include "draw_view.h"

void draw_view (uint8_t * pixels, fixed_t camera_x, fixed_t camera_y, fixed_t camera_angle)
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

		while ((maze_x < MAZE_COLUMNS) && (maze_y < MAZE_ROWS)
		&& (maze_y >= 0) && (maze_x >= 0)) {
			fixed_t sub_x = viewer_x - ((fixed_t) maze_x * FIXED_POINT);
			fixed_t sub_y = viewer_y - ((fixed_t) maze_y * FIXED_POINT);
			fixed_t i1x = INT32_MAX;
			fixed_t i1y = 0;
			fixed_t i2x = INT32_MAX;
			fixed_t i2y = 0;

			assert (maze_x == (viewer_x / FIXED_POINT));
			assert ((0 <= sub_x) && (sub_x <= FIXED_POINT));
			assert ((0 <= sub_y) && (sub_y <= FIXED_POINT));

			// find first intersection with horizontal line
			if (ray_vector_y < 0) {
				// above (left hand side)
				i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)));
				i1y = (fixed_t) maze_y * FIXED_POINT;
			} else if (ray_vector_y > 0) {
				// below (right hand side)
				i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)));
				i1y = (fixed_t) (maze_y + 1) * FIXED_POINT;
			}

			// find first intersection with vertical line
			if (ray_vector_x > 0) {
				i2x = (fixed_t) (maze_x + 1) * FIXED_POINT;
				i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x));
			}

			if (i2x < i1x) {
				// crosses vertical line first
				maze_x ++;
				viewer_x = i2x;
				viewer_y = i2y;
				assert (maze_x == (viewer_x / FIXED_POINT));

				texture_x = i2y;
			} else {
				// crosses horizontal line first
				if (i2x == i1x) {
					// special case: crosses both lines at once
					assert (i1x != INT32_MAX);
					i2y = i1y;
					maze_x ++;
				}

				viewer_x = i1x;
				viewer_y = i1y;
				assert (maze_x == (viewer_x / FIXED_POINT));
				if (ray_vector_y < 0) {
					assert (maze_y == (viewer_y / FIXED_POINT));
					maze_y --;
					texture_x = i1x;
				} else {
					maze_y ++;
					assert (maze_y == (viewer_y / FIXED_POINT));
					texture_x = - i1x;
				}
			}

			if ((maze_x == 0) || (maze_x == (MAZE_COLUMNS - 1))
			|| (maze_y == 0) || (maze_y == (MAZE_ROWS - 1))
			|| (maze_x == (MAZE_ROWS - maze_y))) {
				// reached wall

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
				while (half_height) {
					p[0] = (texture_x & 63) + 120;
					p += HALF_WIDTH * 2;
					p[0] = 160;
					p += HALF_WIDTH * 2;
					half_height --;
				}
				break;
			}
		}
	}

}


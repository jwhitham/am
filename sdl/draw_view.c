
#include <stdint.h>
#include <assert.h>
#include <math.h>

#include "draw_view.h"

#define UNDEFINED ((int16_t) 0x7fff)

void draw_view (uint8_t * pixels, int16_t camera_x, int16_t camera_y, int16_t camera_angle)
{
	int16_t screen_x;

	// convert integer angle to radians.
	float angle = ((float) camera_angle) * M_PI * 2.0 / 65536.0;

	// ray cast from the centre of the screen
	int16_t camera_vector_x = (int16_t) floorf (FIXED_POINT * cosf (camera_angle));
	int16_t camera_vector_y = (int16_t) floorf (FIXED_POINT * sinf (camera_angle));

	// normal to the camera vector (projection plane for view)
	int16_t plane_vector_x = -camera_vector_y;
	int16_t plane_vector_y = camera_vector_x;

	for (screen_x = -HALF_WIDTH; screen_x < HALF_WIDTH; screen_x++) {
		uint16_t texture_x;

		// vector for this screen X (the ray being cast)
		int16_t ray_vector_x = camera_vector_x + ((plane_vector_x * screen_x) / HALF_WIDTH);
		int16_t ray_vector_y = camera_vector_y + ((plane_vector_y * screen_x) / HALF_WIDTH);
		int16_t viewer_x = camera_x;
		int16_t viewer_y = camera_y;

		int8_t maze_x = (int8_t) (viewer_x / FIXED_POINT);
		int8_t maze_y = (int8_t) (viewer_y / FIXED_POINT);

		while ((maze_x < MAZE_COLUMNS) && (maze_y < MAZE_ROWS)) {
			int16_t sub_x = viewer_x - ((int16_t) maze_x * FIXED_POINT);
			int16_t sub_y = viewer_y - ((int16_t) maze_y * FIXED_POINT);
			int16_t i1x = UNDEFINED;
			int16_t i1y = UNDEFINED;
			int16_t i2x = UNDEFINED;
			int16_t i2y = UNDEFINED;

			assert ((0 <= sub_x) && (sub_x <= FIXED_POINT));
			assert ((0 <= sub_y) && (sub_y <= FIXED_POINT));

			// find first intersection with horizontal line
			if (ray_vector_y < 0) {
				// above (left hand side)
				i1x = viewer_x + (((ray_vector_x * sub_y) / (- ray_vector_y)));
				i1y = (int16_t) maze_y * FIXED_POINT;
			} else if (ray_vector_y > 0) {
				// below (right hand side)
				i1x = viewer_x + (((ray_vector_x * (FIXED_POINT - sub_y)) / (ray_vector_y)));
				i1y = (int16_t) (maze_y + 1) * FIXED_POINT;
			}

			// find first intersection with vertical line
			if (ray_vector_x > 0) {
				i2x = (int16_t) (maze_x + 1) * FIXED_POINT;
				i2y = viewer_y + ((((FIXED_POINT - sub_x) * ray_vector_y) / ray_vector_x));
			}

			if ((i1x == UNDEFINED) || ((i2x < i1x) && (i2x != UNDEFINED))) {
				// crosses vertical line first
				maze_x ++;
				viewer_x = i2x;
				viewer_y = i2y;
				assert (maze_x == (viewer_x / FIXED_POINT));

				texture_x = (i2y * texture_width) / FIXED_POINT;
				texture_x %= texture_width;
			} else {
				// crosses horizontal line first
				if (i2x == i1x) {
					// special case: crosses both lines at once
					i2y = i1y;
					maze_x ++;
				}

				viewer_x = i1x;
				viewer_y = i1y;
				assert (maze_x == (viewer_x / FIXED_POINT));
				if (ray_vector_y < 0) {
					assert (maze_y == (viewer_y / FIXED_POINT));
					maze_y --;
					texture_x = (i1x * texture_width) / FIXED_POINT;
					texture_x %= texture_width;
				} else {
					maze_y ++;
					assert (maze_y == (viewer_y / FIXED_POINT));
					texture_x = (i1x * texture_width) / FIXED_POINT;
					texture_x = texture_width - (texture_x % texture_width) - 1;
				}
			}

			if ((maze_x == 0) || (maze_x == (MAZE_COLUMNS - 1))
			|| (maze_y == 0) || (maze_y == (MAZE_ROWS - 1))) {
				// reached wall

				int16_t distance = viewer_x - rotated_player_x;
				int16_t half_height = ((FIXED_POINT * (HALF_HEIGHT - 1)) / distance);
				int16_t start;

				if (half_height > HALF_HEIGHT) {
					half_height = HALF_HEIGHT;
				}
				start = HALF_HEIGHT - half_height;

				p = &pixels[screen_x + (start * HALF_WIDTH * 2)];
				while (half_height) {
					p[0] = 155;
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


/*
 * gcc -o main main.c -Wall -g -O0 -lSDL
 */


#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <math.h>
#include <SDL/SDL.h>

#include "draw_view.h"

static Uint32 tick (Uint32 interval, void *param)
{
	SDL_Event event;
	SDL_UserEvent userevent;

	memset (&userevent, 0, sizeof (userevent));
	memset (&event, 0, sizeof (event));
	userevent.type = SDL_USEREVENT;
	event.type = SDL_USEREVENT;
	event.user = userevent;

	SDL_PushEvent (&event);
	return 10;
}


int main (int argc, char ** argv)
{
	SDL_Surface *       window;
	SDL_Event           ev;
	int					run = 1;
	uint32_t			i = 0;
	SDL_Color			colours[256];
	int16_t				camera_x = 1 + FIXED_POINT * 2;
	int16_t				camera_y = 1 + FIXED_POINT * 2;
	int16_t				undo_x, undo_y;
	float				camera_angle = 0.0;
	int16_t				move = 0;
	int16_t				rotate = 0;
	int16_t				map = 0;
	int16_t				sidestep = 0;
	maze_t *			maze;
	texture_t *			texture;
	const uint16_t		rows = 7;
	const uint16_t		columns = 11;
	const uint16_t		size_log2 = 6;


	draw_init ();
	if (SDL_Init (SDL_INIT_TIMER | SDL_INIT_VIDEO) != 0) {
		fprintf (stderr, "SDL_Init failed.\n");
		return 1;
	}
	window = SDL_SetVideoMode (WINDOW_WIDTH, WINDOW_HEIGHT, 8, SDL_HWPALETTE);
	if (window == NULL) {
		fprintf (stderr, "SDL_SetVideoMode failed.\n");
		SDL_Quit ();
		return 1;
	}

	for (i = 0; i < 256; i++) {
		colours[i].r = i;
		colours[i].g = i;
		colours[i].b = i;
	}
	for (i = 248; i < 256; i++) {
		colours[i].r = (i & 1) ? 150 : 0;
		colours[i].g = (i & 2) ? 150 : 0;
		colours[i].b = (i & 4) ? 150 : 0;
	}
	SDL_SetPalette (window, SDL_LOGPAL|SDL_PHYSPAL, colours, 0, 256);
	SDL_AddTimer (0, tick, NULL);

	maze = calloc (1, sizeof (maze_t) + (rows * columns));
	assert (maze);
	maze->rows = rows;
	maze->columns = columns;
	for (i = 0; i < maze->columns; i++) {
		maze->maze[i + ((maze->rows - 1) * maze->columns)] = i;
	}
	for (i = 0; i < maze->columns; i++) {
		maze->maze[i] = i;
		i++;
		maze->maze[i + ((maze->rows - 2) * maze->columns)] = i;
	}
	maze->maze[2] = 0x33;
	maze->maze[6 + ((maze->rows - 3) * maze->columns)] = 0x33;

	texture = calloc (1, sizeof (texture_t) + (1 << (size_log2 * 2)));
	assert (texture);
	texture->size_log2 = size_log2;
	for (i = 0; i < (1 << (size_log2 * 2)); i++) {
		uint16_t x = i >> size_log2;
		uint16_t y = i & ((1 << size_log2) - 1);
		uint16_t a = (x >> 3) ^ (y >> 3);

		texture->pixels[i] = 248 | (a & 7);

		if (((x & 7) == 0) || ((y & 7) == 0)) {
			texture->pixels[i] = 0xff;
		}
		if ((x == ((1 << size_log2) - 1)) || (y == ((1 << size_log2) - 1))) {
			texture->pixels[i] = 0xff;
		}
	}

	do {
		SDL_WaitEvent (&ev);
		switch (ev.type) {
			case SDL_MOUSEMOTION:
				break;
			case SDL_MOUSEBUTTONDOWN:
				break;
			case SDL_MOUSEBUTTONUP:
				break;
			case SDL_KEYDOWN:
			case SDL_KEYUP:
				switch (ev.key.keysym.sym) {
					case SDLK_LEFT:
						rotate = (ev.type == SDL_KEYDOWN) ? -1 : 0;
						break;
					case SDLK_w:
					case SDLK_UP:
						move = (ev.type == SDL_KEYDOWN) ? 1 : 0;
						break;
					case SDLK_RIGHT:
						rotate = (ev.type == SDL_KEYDOWN) ? 1 : 0;
						break;
					case SDLK_s:
					case SDLK_DOWN:
						move = (ev.type == SDL_KEYDOWN) ? -1 : 0;
						break;
					case SDLK_z:
					case SDLK_a:
						sidestep = (ev.type == SDL_KEYDOWN) ? -1 : 0;
						break;
					case SDLK_x:
					case SDLK_d:
						sidestep = (ev.type == SDL_KEYDOWN) ? 1 : 0;
						break;
					case SDLK_ESCAPE:
						run = 0;
						break;
					case SDLK_TAB:
						map = (ev.type == SDL_KEYDOWN) ? (!map) : map;
						break;
					default :
						break;
				}
				break;
			case SDL_QUIT:
				run = 0;
				break;
			case SDL_USEREVENT:
				camera_angle += 0.02 * rotate;
				undo_x = camera_x;
				undo_y = camera_y;
				camera_x += move * floorf (FIXED_POINT * cosf (camera_angle) / 16);
				camera_y += move * floorf (FIXED_POINT * sinf (camera_angle) / 16);
				camera_x += sidestep * floorf (FIXED_POINT * cosf (camera_angle + (M_PI * 0.5)) / 16);
				camera_y += sidestep * floorf (FIXED_POINT * sinf (camera_angle + (M_PI * 0.5)) / 16);
				if (camera_x < 0) {
					camera_x = 0;
				}
				if (camera_y < 0) {
					camera_y = 0;
				}
				if (camera_x > (FIXED_POINT * maze->columns)) {
					camera_x = (FIXED_POINT * maze->columns);
				}
				if (camera_y > (FIXED_POINT * maze->rows)) {
					camera_y = (FIXED_POINT * maze->rows);
				}
				if (maze->maze[(camera_x / FIXED_POINT) + ((camera_y / FIXED_POINT) * maze->columns)]) {
					// Ouch. You bump into a wall.
					camera_x = undo_x;
					camera_y = undo_y;
				}

				SDL_LockSurface (window);
				memset (window->pixels, 0, WINDOW_WIDTH * WINDOW_HEIGHT);
				draw_view (window->pixels, camera_x, camera_y, camera_angle, maze, texture, map);
				SDL_UnlockSurface (window);
				SDL_Flip (window);
				break;
			default:
				break;
		}
	} while (run);

	SDL_Quit () ;
	return 0 ;
}


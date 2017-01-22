/*
 * gcc -o main main.c -Wall -g -O0 -lSDL
 */


#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
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
	int16_t				camera_angle = 0;
	int16_t				move_x = 0;
	int16_t				move_y = 0;


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
	SDL_SetPalette (window, SDL_LOGPAL|SDL_PHYSPAL, colours, 0, 256);
	SDL_AddTimer (0, tick, NULL);

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
						move_x = (ev.type == SDL_KEYDOWN) ? -1 : 0;
						break;
					case SDLK_UP:
						move_y = (ev.type == SDL_KEYDOWN) ? -1 : 0;
						break;
					case SDLK_RIGHT:
						move_x = (ev.type == SDL_KEYDOWN) ? 1 : 0;
						break;
					case SDLK_DOWN:
						move_y = (ev.type == SDL_KEYDOWN) ? 1 : 0;
						break;
					case SDLK_ESCAPE:
						run = 0;
						break;
					default :
						break;
				}
				break;
			case SDL_QUIT:
				run = 0;
				break;
			case SDL_USEREVENT:
				camera_x += move_x * (FIXED_POINT / 16);
				camera_y += move_y * (FIXED_POINT / 16);
				if (camera_x < FIXED_POINT) {
					camera_x = FIXED_POINT;
				}
				if (camera_y < FIXED_POINT) {
					camera_y = FIXED_POINT;
				}
				if (camera_x > (FIXED_POINT * MAZE_COLUMNS)) {
					camera_x = (FIXED_POINT * MAZE_COLUMNS);
				}
				if (camera_y > (FIXED_POINT * MAZE_ROWS)) {
					camera_y = (FIXED_POINT * MAZE_ROWS);
				}

				SDL_LockSurface (window);
				memset (window->pixels, 0, WINDOW_WIDTH * WINDOW_HEIGHT);
				draw_view (window->pixels, camera_x, camera_y, camera_angle);
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


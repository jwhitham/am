/*
 * gcc -o main main.c -Wall -g -O0 -lSDL
 */


#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <SDL/SDL.h>

#include "draw_view.h"

int main (int argc, char ** argv)
{
	SDL_Surface *       window;
	SDL_Event           ev;
	int					run = 1;
	uint32_t			i = 0;
	SDL_Color			colours[256];
	int16_t				camera_x = FIXED_POINT * 2;
	int16_t				camera_y = FIXED_POINT * 2;
	int16_t				camera_angle = 0;


	if (SDL_Init (SDL_INIT_AUDIO | SDL_INIT_VIDEO) != 0) {
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

	do {
		SDL_LockSurface (window);
		memset (window->pixels, 0, WINDOW_WIDTH * WINDOW_HEIGHT);
		draw_view (window->pixels, camera_x, camera_y, camera_angle);
		SDL_UnlockSurface (window);
		SDL_Flip (window);

		SDL_WaitEvent (&ev);
		do {
			switch (ev.type) {
				case SDL_MOUSEMOTION:
					break;
				case SDL_MOUSEBUTTONDOWN:
					break;
				case SDL_MOUSEBUTTONUP:
					break;
				case SDL_KEYDOWN:
					switch (ev.key.keysym.sym) {
						case SDLK_LEFT:
							break;
						case SDLK_UP:
							break;
						case SDLK_RIGHT:
							break;
						case SDLK_DOWN:
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
				default:
					break;
			}
		} while (run && SDL_PollEvent (&ev));
	} while (run);

	SDL_Quit () ;
	return 0 ;
}


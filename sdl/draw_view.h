
#define HALF_WIDTH		320
#define HALF_HEIGHT		240

#define FIXED_SHIFT		8	
#define TEXTURE_FIXED_SHIFT		20
#define WINDOW_WIDTH	(HALF_WIDTH * 2)
#define WINDOW_HEIGHT	(HALF_HEIGHT * 2)
#define FIXED_POINT		(1 << FIXED_SHIFT)
#define HALF_FIXED_POINT (FIXED_POINT >> 1)

typedef int32_t fixed_t;

typedef struct maze_s {
	uint16_t rows, columns;
	uint8_t maze[1];
} maze_t;

typedef struct texture_s {
	uint16_t size_log2;
	uint8_t pixels[1];
} texture_t;

void draw_init (void);
void draw_view (uint8_t * pixels, fixed_t camera_x, fixed_t camera_y, float camera_angle, maze_t * maze, texture_t * texture, int map);



#define HALF_WIDTH		320
#define HALF_HEIGHT		240
#define MAZE_ROWS		11
#define MAZE_COLUMNS	11

#define FIXED_SHIFT		8
#define WINDOW_WIDTH	(HALF_WIDTH * 2)
#define WINDOW_HEIGHT	(HALF_HEIGHT * 2)
#define FIXED_POINT		(1 << FIXED_SHIFT)

typedef int32_t fixed_t;

void draw_view (uint8_t * pixels, fixed_t camera_x, fixed_t camera_y, fixed_t camera_angle);


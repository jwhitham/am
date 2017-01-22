rem @echo off
del main.exe
gcc -o main.exe main.c draw_view.c -Wall -g -O0 -lSDL -lm -Ic:\jack\sdl-1.2.15\include -Lc:\jack\sdl-1.2.15\lib -lmingw32 -lSDLmain -lSDL
set PATH=c:\jack\sdl-1.2.15\bin;%PATH%
main.exe


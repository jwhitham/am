#!/bin/bash -xe
gcc -o test_gcc mwc1_gcc.s test.c
./test_gcc
nasm -o mwc1_nasm.o mwc1_nasm.s -f elf64
gcc -o test_nasm mwc1_nasm.o test.c
./test_nasm

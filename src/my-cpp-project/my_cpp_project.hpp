#pragma once

#include <fftw3.h>
#define _USE_MATH_DEFINES
#include <math.h>
#include <stdio.h>

/**
 * @brief Sum two numbers together.
 * 
 * @param i First number.
 * @param j Second number.
 * @return int Sum of the two numbers.
 */
int add(int i, int j);

#define NUM_POINTS 64
#define REAL 0
#define IMAG 1

/**
 * @brief Generates a signal composed of two sine waves of different
 * frequencies, then performs a Fast Fourier Transform on the signal and print
 * the results.
 * 
 */
void hello_fft();
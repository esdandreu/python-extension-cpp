#include "my_cpp_project.hpp"

int add(int i, int j) {
    return i + j;
}

void hello_fft() {
    // Generate Fast Fourier Transform plan
    fftw_complex signal[NUM_POINTS];
    fftw_complex result[NUM_POINTS];

    fftw_plan plan = fftw_plan_dft_1d(
        NUM_POINTS, signal, result, FFTW_FORWARD, FFTW_ESTIMATE);

    // Acquire signal
    int i;
    for (i = 0; i < NUM_POINTS; ++i) {
        double theta = (double)i / (double)NUM_POINTS * M_PI;

        signal[i][REAL] = 1.0 * cos(10.0 * theta) + 0.5 * cos(25.0 * theta);

        signal[i][IMAG] = 1.0 * sin(10.0 * theta) + 0.5 * sin(25.0 * theta);
    }

    // Execute Fast Fourier Transform
    fftw_execute(plan);

    // Print the result
    for (i = 0; i < NUM_POINTS; ++i) {
        double mag = sqrt(result[i][REAL] * result[i][REAL]
            + result[i][IMAG] * result[i][IMAG]);

        printf("%g\n", mag);
    }

    // Cleanup
    fftw_destroy_plan(plan);
}
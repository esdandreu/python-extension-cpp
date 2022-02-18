#include "myproject.hpp"

#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(_python_api, m) {
    m.doc() = R"pbdoc(
        Python wrapper for `myproject`.

        This information will be displayed when using `help()`:
        $ python -c "import myproject; help(myproject)"
    )pbdoc";

    m.def("add", &add, "Add two numbers together");
    m.def("hello_fft", &hello_fft, "Tests a Fast Fourier Transform");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "include/numpy_boost_python.hpp"

#include "base_types.hpp"
/* ...other relevant header files... */

using namespace boost::python;

#include "example.hpp"
#include "example.cpp"

BOOST_PYTHON_MODULE(example)
{
  import_array();
  numpy_boost_python_register_type<float, 1>();
  numpy_boost_python_register_type<float, 3>();
  def("cpp_function1", example_function1);
  def("cpp_function2", example_function2);
  def("cpp_function3", example_function3);
}


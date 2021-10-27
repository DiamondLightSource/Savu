extern void example_function1(numpy_boost<float, 3> &pixels,
			       const real param_n, const real param_r,
			       const int num_series);
extern numpy_boost<float, 3>
example_function1(const numpy_boost<float, 3> &pixels,
		 const numpy_boost<float, 1> &angles,
		 double rotation_centre, int resolution,
		 int niterations, int nthreads);
extern void example_function3();


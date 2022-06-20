All notable changes to this project are documented in this file.
*******************************************************************
# Savu Version 4.2, *planned release March 2022*

## _Core_
* Statistics class:
  - Stats relating to the data calculated alongside each plugin.
  - Can be accessed in Savu for use in plugins.
  - Collated and saved as a table, graphs and a .h5 file for inspection after a run (found in the 'stats' folder).
  - Use option `--stats ` and parse arguments `on` or `off` to set stats on or off for a run (on by defualt).
  - MinAndMax plugin is now deprecated (use statistics class instead).
* Iterative plugins (A capability to enable some plugins to be iterative):
  - `iterate` command to enable control over iterative plugins (see `iterate -h` for help)

## _Existing Plugins_

### Centering

### Simulation
  * A sub-pixel misalignment simulation for projections from TomoPhantom
  * Various Tomoloader fixes. Closing of the linked nxs file with MPI fixed.

### Reconstruction
  * AstraReconGPU, 3D GPU methods are added (BP3D_CUDA, CGLS3D_CUDA, SIRT3D_CUDA)
  * FBP3D_CUDA method added (filtering before backprojection with BP3D_CUDA)
  * ForwardProjector works with the 3D geometry
  * 3D geometries can accept metadata for x-y shifts and correct the misalignment
  * ToMoBAR (3d version) has got different methods (FBP3D, CGLS3D, FISTA3D) working well with iterative alignment
  * GPU memory usage check for *tomobar_recon_3D* plugin to avoid CUDA error
  * *tomobar_recon_3D* access to regularisation using Wavelets, try set regularisation method e.g. to 'PD_TV_WAVELETS'
  * SWLS, PWLS methods for data fidelities are enabled in *tomobar_recon_3D*
  * GPU device indices are controlled through ToMoBAR iterative methods and regularisation

### Filters
  * GPU memory usage check for *ccpi_denoising_gpu_3D* plugin to avoid CUDA error
  * DezingerSinogram changed to utilise new statistics class.
  * DownsampleFiler changed to utilise new statistics class.

### Savers
  * ImageSaver changed to utilise new statistics class.

## _New plugins_
### Alignment
  * *projection_2d_alignment* - works with 2 sets of 3D projection data by comparing projection images and estimating vertical-horizontal shifts in data. The vector shifts then stored in experimental data to be used later in 3D vector geometry.
### Filters
  * *wavelet_denoising_gpu* - a GPU plugin for denoising using Wavelets. Highly optimised for GPU performance.
### Corrections
  * *phase_unwrapping* - a plugin for unwrapping phase-retrieved images
### Centering
  * *360_centering* - a plugin to calculate centre of rotation.

## _Updated and new packages as dependencies_
  * A new [pypwt](https://github.com/pierrepaleo/pypwt "pypwt") GPU wavelet package added through Jenkins build and savu-dep channel
  * ToMoBAR and TomoPhantom packages have been updated

## _Configurator_
  *  Allow a list as a single dimension input to the preview parameter
  *  Allow a start keyword inside the preview parameter
  *  Allow a parameter to be a directory path within the Savu folder
  *  Asterix line added to indicate the start and end of the process list
  *  Line separator added to indicate an iterative plugin loop
  *  Include a link to relevant online plugin guides
  *  Warning added when loading plugins from a user directory
  *  First dataset passed by default to the next plugin

### New Commands
  * *savu_mod* - a way to modify one parameter present in a plugin list.
  * *mod -g parameter* - a way to modify a parameter in the process list globally (for all plugins)


## _Documentation_
  *  Plugin API moved to dropdown boxes on every plugin documentation page
  *  Plugin template links updated
  *  Video demos added

## _BUGS_
  *  res_norm bug when using AstaReconGPU with CGLS_CUDA
  *  Fix indentation for the plugin_generator command
  *  Allow saving to inner plugin directories when using the plugin_generator command
  *  Plugin number and order error fixed

## Other
  * The test dataset 24737.nxs has been changed to tomo-standard.nxs
  * The synthetic test data has been added
  * Environment variable *type* is replaced with *GPUarch_nodes*
  * *savu_mod* - Modify one parameter present in a plugin list.
  * Save the job command to a log file
  * Save the directory the command was run to a log file



*******************************************************************
# Savu Version 4.1 (released September 2021)

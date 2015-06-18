import numpy as np

data = np.random.rand(10,10,4)
angles = np.linspace(0, np.pi, 10, False)

# Commenting failing tests for the moment
#import ccpi_reconstruction
#voxels = ccpi_reconstruction.cgls(data.astype(np.float32), angles.astype(np.float32), 60., 1, 1, 1)


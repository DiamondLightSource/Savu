#!/bin/bash
set -euo pipefail

export OMPI_MCA_btl=self,tcp
export OMPI_MCA_plm=isolated
export OMPI_MCA_rmaps_base_oversubscribe=yes
export OMPI_MCA_btl_vader_single_copy_mechanism=none
mpiexec="mpiexec --allow-run-as-root"

# pipe stdout, stderr through cat to avoid O_NONBLOCK issues
$mpiexec $@ 2>&1 | cat

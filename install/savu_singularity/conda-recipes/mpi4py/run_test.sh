echo "Running tests"
export OMPI_MCA_plm=isolated
export OMPI_MCA_btl_vader_single_copy_mechanism=none
export OMPI_MCA_rmaps_base_oversubscribe=yes

python -c 'import mpi4py'
python -c 'import mpi4py.MPI'
python -c 'import mpi4py.futures'

MPIEXEC="${PWD}/mpiexec.sh"
$MPIEXEC -np 4 python helloworld.py

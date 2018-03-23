#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

// If your GPU has less memory, then you will need to decrease this data size.
 #define MAX_DATA_SIZE		1024*1024*172    
//#define MAX_DATA_SIZE		256 * 8    
// The max data size must be an integer multiple of 128*256, because each block will have 256 threads,
// and the block grid width will be 128. These are arbitrary numbers I choose.
#define THREADS_PER_BLOCK 	400
#define RTHREADS 256
//#define BLOCKS_PER_GRID_ROW 8
#define BLOCKS_PER_GRID_ROW  128
#define DEBUGBLOCK (18)

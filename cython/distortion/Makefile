#!/usr/local/bin/gnumake

CXX := g++
CC := gcc
LINK := gcc
.SUFFIXES : .c .cpp .cu .o 


#FFTWPREFIX := ${FFTWDIR}

OPTIMIZER = -O3

#include all warnings .. 
#FLAGS = $(OPTIMIZER)  -DPCO_4000_FIX_BCD  #-Wall
FLAGS = $(OPTIMIZER) #-DDEBUG_ALGORITHM # -DDEBUG_DEZING_FIX # -DDEBUG_INDEX # -DTESTRAW  #-Wall

FLAGS += $(CFLAGS)

#location of the library folders

LIBDIRS = 

#-L$(FFTWPREFIX)/lib 

INCDIRS := 

#-I$(FFTWPREFIX)/include/

#library flags required
#
#


LIBS = -lm   -ldl -lrt \
-pthread -Wl,-rpath `pwd` 

#-Wl,-rpath $(FFTWPREFIX)/lib \

# add this flag to get lots of linker output
#-Wl,--verbose 


CPPSOURCES=\
	 unwarp_functions.cpp 
CSOURCES=\
	 timestamp.c

CPPMAIN=\
      unwarp_functions.cpp
CMAIN=\
      tifwrite.c

CSALL=$(CSOURCES) $(CMAIN) $(CPPSOURCES) $(CPPMAIN)


COBJECTS=$(CSOURCES:%.c=%.o) $(CPPSOURCES:%.cpp=%.o)

COBJLIB=$(CSOURCES:%.c=%.o) $(CPPSOURCES:%.cpp=%.o)


COBJMAIN=$(CMAIN:%.c=%.o)


PROGNAME=unwarp_batch

SHARENAME=libunwarp.so
STATICNAME=libunwarp.a

DFFLAGS = -DDEBUGALL

# the dependencies
default: $(PROGNAME)

debug: OPTIMIZER := -ggdb
debug: FLAGS += -lefence
debug: clean $(COBJECTS)
	$(CXX) -o $@ $(COBJECTS) $(LIBDIRS) $(LIBS) $(FLAGS)  -ltiff


debugthread: OPTIMIZER := -ggdb
debugthread: FLAGS += -DSINGLETHREAD -DDEBUG_THREADSCALE 
debugthread: clean  $(COBJECTS)
	$(CXX) -o $@ $(COBJECTS) $(LIBDIRS) $(LIBS) $(FLAGS) 

debugfilt: FLAGS += $(DFFLAGS) 
debugfilt: clean  $(COBJECTS)
	$(CXX) -o $@ $(COBJECTS) $(LIBDIRS) $(LIBS) $(FLAGS) 


.c.o:
	$(CXX) $(INCDIRS) $(FLAGS) -c $<

.cpp.o:
	$(CXX) $(INCDIRS) $(FLAGS) -c $<



$(PROGNAME): $(CUDAOBJECTS) $(COBJMAIN) shared
	$(CXX) -o $@ $(COBJMAIN) $(LIBDIRS) $(LIBS) $(FLAGS) $(SHARENAME) -ltiff

shared: FLAGS+=-fPIC  -Wall
shared: $(SHARENAME)

static: FLAGS+=-fPIC  -Wall
static: $(STATICNAME)


$(SHARENAME): $(CUDAOBJECTS) $(COBJLIB) 
	$(CXX) -o $@ $(COBJLIB) $(LIBDIRS) $(LIBS) $(FLAGS) -shared 

$(STATICNAME): $(CUDAOBJECTS) $(COBJLIB) 
	ar rcs $@ $(COBJLIB) 

# using 'export NVCCFLAGS=-DDEBUGTIME' in the shell
# to activate the extra time print out

clean:
	rm  -f $(COBJECTS)  $(PROGNAME) debugfilt $(SHARENAME) $(STATICNAME)



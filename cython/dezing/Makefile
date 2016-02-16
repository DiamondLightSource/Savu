#!/usr/local/bin/gnumake

# $Id:$

CXX := g++
CC := gcc
LINK := gcc
.SUFFIXES : .c .cpp .cu .o 


#FFTWPREFIX := ${FFTWDIR}

#OPTIMIZER = -O3
OPTIMIZER = -ggdb

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


CSOURCES=\
	 dezing_functions.c \
	 handlers.c \
	 timestamp.c

CMAIN=\
      dezing_main.c\
      tifwrite.c

CSALL=$(CSOURCES) $(CMAIN)


COBJECTS=$(CSALL:%.c=%.o)

COBJLIB=$(CSOURCES:%.c=%.o)

COBJMAIN=$(CMAIN:%.c=%.o)


PROGNAME=dezing_batch

SHARENAME=libdezing.so
STATICNAME=libdezing.a

DFFLAGS = -DDEBUGALL

# the dependencies
default: $(PROGNAME)

debug: OPTIMIZER := -ggdb
debug: FLAGS += -lefence
debug: clean $(COBJECTS)
	$(CC) -o $@ $(COBJECTS) $(LIBDIRS) $(LIBS) $(FLAGS)  -ltiff


debugthread: OPTIMIZER := -ggdb
debugthread: FLAGS += -DSINGLETHREAD -DDEBUG_THREADSCALE 
debugthread: clean  $(COBJECTS)
	$(CC) -o $@ $(COBJECTS) $(LIBDIRS) $(LIBS) $(FLAGS) 

debugfilt: FLAGS += $(DFFLAGS) 
debugfilt: clean  $(COBJECTS)
	$(CC) -o $@ $(COBJECTS) $(LIBDIRS) $(LIBS) $(FLAGS) 


.c.o:
	$(CC) $(INCDIRS) $(FLAGS) -c $<



$(PROGNAME): $(CUDAOBJECTS) $(COBJMAIN) shared
	$(CC) -o $@ $(COBJMAIN) $(LIBDIRS) $(LIBS) $(FLAGS) $(SHARENAME) -ltiff

shared: FLAGS+=-fPIC  -Wall
shared: $(SHARENAME)

static: FLAGS+=-fPIC  -Wall
static: $(STATICNAME)


$(SHARENAME): $(CUDAOBJECTS) $(COBJLIB) 
	$(CC) -o $@ $(COBJLIB) $(LIBDIRS) $(LIBS) $(FLAGS) -shared 

$(STATICNAME): $(CUDAOBJECTS) $(COBJLIB) 
	ar rcs $@ $(COBJLIB) 

# using 'export NVCCFLAGS=-DDEBUGTIME' in the shell
# to activate the extra time print out

clean:
	rm  -f $(COBJECTS)  $(PROGNAME) debugfilt $(SHARENAME) $(STATICNAME)



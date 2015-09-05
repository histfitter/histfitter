######################################################################
# Project: Tools                                                     #
# Doc: http://sunsite.ualberta.ca/Documentation/Gnu/make-3.79/html_chapter/make_toc.html 
###################################################################### 

MAKEFLAGS = --no-print-directory -r -s --pedantic -Wall
#MAKEFLAGS = --warn-undefined-variables --debug

include ../src/Makefile.arch

# Internal configuration
PACKAGE=SusyFitter
LD_LIBRARY_PATH:=.:../lib:$(ROOTSYS)/lib:$(LD_LIBRARY_PATH)
OBJDIR=obj
DEPDIR=$(OBJDIR)/dep
VPATH= $(OBJDIR)
INCLUDES += -I../include -I$(ROOTSYS)/include 
ROOTSYS  ?= ERROR_RootSysIsNotDefined
 
DICTHEAD  = $(PACKAGE)_Dict.h
DICTFILE  = $(PACKAGE)_Dict.C
DICTOBJ   = $(PACKAGE)_Dict.o
DICTLDEF  = LinkDef.h
SKIPCPPLIST  = 
SKIPHLIST    =  $(DICTHEAD) $(DICTLDEF)
LIBFILE   = ../lib/lib$(PACKAGE).a
SHLIBFILE = ../lib/lib$(PACKAGE).so
DLLIBFILE = ../lib/lib$(PACKAGE).dll
ROOTMAPFILE = ../lib/lib$(PACKAGE).rootmap
HEADERDEST = ../include/
LIBDEST = ../lib/
PCMFILE = ../lib/lib$(PACKAGE)_rdict.pcm

CXXFLAGS = -std=c++11 -fPIC

UNAME = $(shell uname)

LINKLIBSIN = -L$(ROOTSYS)/lib -lCore -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lTree -lRint -lPostscript -lMatrix -lPhysics -lGui -lRooFit -lRooStats -lHistFactory -lXMLParser -pthread -lRooFitCore -lm -ldl -lFoam -lMinuit -L../lib 

LINKLIBS = $(LINKLIBSIN) -lSusyFitter

default: shlib 

# List of all source files to build
HLIST   = $(filter-out $(SKIPHLIST),$(wildcard *.h))
CPPLIST = $(filter-out $(SKIPCPPLIST),$(wildcard *.$(SrcSuf)))
DICTHLIST = $(HLIST)

# List of all object files to build
OLIST=$(patsubst %.cxx,%.o,$(CPPLIST))

#Executable programs, ending with .cpp by convention
BINDIR= ../bin
BinSuf=.cpp
BINLIST=$(basename $(wildcard *$(BinSuf)))

# Implicit rule to compile all classes
%.o : %.cxx 
	@echo "Compiling $<"
	@mkdir -p $(OBJDIR)
	#@echo $(CXX) $(CXXFLAGS) -g -c $< -o $(OBJDIR)/$(notdir $@) $(INCLUDES) 
	@$(CXX) $(CXXFLAGS) -g -c $< -o $(OBJDIR)/$(notdir $@) $(INCLUDES)

ifeq ($(shell [ $(ROOTMAJOR) -lt 6 ] && echo true), true)
# ROOT5 rule to make the dictionary
$(DICTFILE):  $(DICTHLIST) $(DICTLDEF)
	@echo "Generating dictionary $@"
	$(ROOTSYS)/bin/rootcint -f $(DICTFILE) -c $(INCLUDES) $(CINTFLAGS) $^
endif

ifneq ($(shell [ $(ROOTMAJOR) -lt 6 ] && echo true), true)
# ROOT6 rule to make the dictionary
$(DICTFILE):  $(DICTHLIST) $(DICTLDEF)
	@echo "Generating dictionary $@"
	$(ROOTSYS)/bin/rootcling -f $(DICTFILE) -s $(SHLIBFILE) -rml lib$(PACKAGE).so -rmf $(ROOTMAPFILE) -c $(INCLUDES) $^
endif

$(OBJDIR)/$(DICTOBJ): $(DICTFILE)
	@echo "Compiling $<"
	@mkdir -p $(OBJDIR)
	@$(CXX) $(CXXFLAGS) -g -c $(INCLUDES) -o $@ $<

##############################
# The dependencies section   
# - the purpose of the .d files is to keep track of the
#   header file dependence
# - this can be achieved using the makedepend command 
##############################
# .d tries to pre-process .cc
ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),distclean)
-include $(foreach var,$(CPPLIST:.$(SrcSuf)=.d),$(DEPDIR)/$(var)) /dev/null
endif
endif

$(DEPDIR)/%.d: %.$(SrcSuf)
	@@mkdir -p $(DEPDIR)
	if test -f $< ; then \
		echo "Making $(@F)"; \
		$(SHELL) -ec '$(CPP) -MM $(CXXFLAGS) $(INCLUDES) $< | sed '\''/Cstd\/rw/d'\'' > $@'; \
	fi

# Rule to combine objects into a library
$(LIBFILE): $(OLIST) $(OBJDIR)/$(DICTOBJ)	
	@echo "Making static library: $(LIBFILE)"
	@rm -f $(LIBFILE)
	@ar q $(LIBFILE) $(addprefix $(OBJDIR)/,$(OLIST)) $(OBJDIR)/$(DICTOBJ)
	@ranlib $(LIBFILE)

# Rule to combine objects into a unix shared library
$(SHLIBFILE): $(OLIST) $(OBJDIR)/$(DICTOBJ)
	@echo "Making shared library: $(SHLIBFILE)"
	@rm -f $(SHLIBFILE)
	@$(LD) $(CXXFLAGS) $(SOFLAGS) $(addprefix $(OBJDIR)/,$(OLIST)) $(OBJDIR)/$(DICTOBJ) -o $(SHLIBFILE) $(LINKLIBSIN)

# Rule to combine objects into a windows shared library
$(DLLIBFILE): $(OLIST) $(OBJDIR)/$(DICTOBJ)
	@echo "Making dll file: $(DLLIBFILE)"
	@rm -f $(DLLIBFILE)
	$(LD) -Wl,--export-all-symbols -Wl,--export-dynamic -Wl,--enable-auto-import -Wl,-Bdynamic -shared --enable-auto-image-base -Wl,-soname -o $(DLLIBFILE) -Wl,--whole-archive $(addprefix $(OBJDIR)/,$(OLIST) $(patsubst %.$(SrcSuf),%.o,$(DICTFILE))) -Wl,--no-whole-archive -L$(ROOTSYS)/lib -lCore -lCint -lHist -lGraf -lGraf3d -lTree -lRint -lPostscript -lMatrix -lMinuit -lPhysics -lHtml -lm

includeinst:
	cp -f *.h $(HEADERDEST)
	if [ -e $(DICTFILE) ] ; then cp -f *.h $(HEADERDEST) ; fi

# Useful build targets
lib: $(LIBFILE) includeinst
shlib: $(SHLIBFILE) includeinst
winlib: $(DLLIBFILE) includeinst
clean: 
	@echo "Deleting all libraries and executables..."
	rm -f $(DICTFILE) $(DICTHEAD)
	rm -f $(SHLIBFILE)
	rm -f $(OBJDIR)/*.o
	rm -f $(DEPDIR)/*.d
	rm -f $(LIBFILE)
	rm -f $(SHLIBFILE)
	rm -f $(DLLIBFILE)
	rm -f $(PCMFILE)
	rm -f $(ROOTMAPFILE)
	for ex in $(BINLIST); do \
		rm -f $(BINDIR)/$${ex}; \
	done

distclean:
	@echo "Deleting all libraries and executables, including ../include and ../lib"
	rm -rf obj 
	rm -f *~
	rm -f *_Dict*
	rm -f ../lib/*_Dict*
	rm -f $(SHLIBFILE)
	rm -f $(LIBFILE)
	rm -f $(SHLIBFILE)
	rm -f $(DLLIBFILE)
	rm -f $(PCMFILE)
	rm -f $(ROOTMAPFILE)
	touch ../lib/libdummy ../include/dummy.h
	rm -rf ../lib/lib* ../include/*.h
	for ex in $(BINLIST); do \
		rm -f $(BINDIR)/$${ex}; \
	done

bin:	shlib
	mkdir -p $(BINDIR)
	for ex in $(BINLIST); do \
		echo "Linking $(BINDIR)/$${ex}"; \
		$(CXX) $(CXXFLAGS) -g $(INCLUDES) $(LINKLIBS) -lSusyFitter -o $(BINDIR)/$${ex} $${ex}$(BinSuf); \
	done

.PHONY : winlib shlib lib default clean distclean includeinst bin




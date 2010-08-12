# Makefile for generating HTML documentation from NOTES.md files.
# Input is Markdown, translated to HTML using the pandoc converter
# which is a Haskell program which may be installed using the cabal
# program supplied with the Haskell platform.

DOCDIRS = Bathymetry/bathy\
				  Bathymetry/bound\
					Bathymetry/NWSSwanBathy\
				  NDBCbuoys\
				  NOAACharts	
DOCFILES = $(addsuffix /NOTES.md, $(DOCDIRS))


.PHONY : index.html

index.html : README.md doc $(DOCFILES:.md=.html)
	pandoc README.md -o index.html

doc :
	mkdir doc

$(DOCFILES:.md=.html) : %.html:%.md
	# Use pandoc to convert NOTES.md to NOTES.html
	pandoc $< -o $@
	# Deep, dark, sed voodoo- rename NOTES.html to
	# an appropriate entry in the doc/ folder.
	mv $@ doc/`echo $< |\
    sed 's/\([a-zA-Z0-9_]*\/\{0,1\}[a-zA-Z0-9_]\{0,\}\)\/.*/\1/' |\
	 	sed 's/\//_/'`.html

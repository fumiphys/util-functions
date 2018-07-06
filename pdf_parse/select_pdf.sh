#!/bin/sh

ALLPDFFILE=`python3 /Users/fkiyozawa/github/pdf_parse/pdf_parse.py | percol | awk {'print $1'}`
evince $ALLPDFFILE

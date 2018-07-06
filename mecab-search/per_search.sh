#!/bin/sh

DIRPATHLIST=''
EXTLIST=''
SEARCHWORDSLIST=''

while getopts d:e:w: OPT
do
		case $OPT in
				d)	DIRPATHLIST=$OPTARG
						;;
				e)	EXTLIST=$OPTARG
						;;
				w)	SEARCHWORDSLIST=$OPTARG
						;;
				\?)	exit 1
		esac
done

filepath=`python3 mecab_search.py --dirpath "${DIRPATHLIST}" --exts "${EXTLIST}" --words "${SEARCHWORDSLIST}" | percol | awk '{print $1}'`
vim $filepath

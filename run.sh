#!/bin/sh

path=`readlink -m $0`
path=`dirname $path`
path=`(cd $path; pwd)`
path=`readlink -m $path`
cd $path

python src/main.py -d $*

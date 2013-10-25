#!/usr/bin/env bash
#
# Runs the English PCFG parser: ./crfTD.sh input.txt 1>output.txt 2>&1 &

if [ ! $# -ge 1 ]; then
  echo Usage: `basename $0` 'file(s)'
  echo
  exit
fi

scriptdir=`dirname $0`

java -mx150m -cp "$scriptdir/*:" edu.stanford.nlp.parser.lexparser.LexicalizedParser \
 -outputFormat "typedDependencies" edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz $* 

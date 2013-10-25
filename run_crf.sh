#!/usr/bin/env bash
#
# Runs CRF++ trainer and 

./CRF++-0.58/crf_learn -c 10.0 ./CRF_template ./data/CRF_train ./data/model1
./CRF++-0.58/crf_test  -m ./data/model1 ./data/CRF_train


./CRF++-0.58/crf_learn -a MIRA ./CRF_template ./data/CRF_train ./data/model2 -p 1
./CRF++-0.58/crf_test  -m ./data/model2 ./data/CRF_train

from __future__ import print_function
import sys
import json
import re
import os
import time

templates = ["#Unigram"]

vertical_locality = [-2,-1,0,1,2]
for i in vertical_locality:
	for j in xrange(25):
		if j == 0:
			continue
		templates.append("U%d%d:%s[%d,%d]"%(i,j,'%x',i,j))

templates.append("#Bigram")
templates.append("B")

f = open('CRF_template','w')
for t in templates:
	print(t, file=f)
f.close()

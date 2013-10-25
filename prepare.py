from __future__ import print_function
import urllib
import urllib2
import HTMLParser
import sys
import json
import re
import os
import time
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag 
import numpy
import dictionary
from levenshtein import levenshtein
from LSI import LSI

documentIndex = [0] # document start indices
content = None # to hold list of sentences
labels  = None # list of ground truth labels
dict_hash = {}
dict_match = None
typedDependency = {}
CRF_input = []
mylsa = LSI(stopwords=set(['and','edition','for','in','little','of','the','to','this','that','a','an']), 
                    ignorechars=''',:'!''') 

label_conv = {"N":-1,"P":1,"O":0}
rip_dic = ['!', '?', '.', ',', '-', '>', '<', ':', '/', "\\", '(', ')', '=',
            '#', '$', '%', '^', '*', '&', '~', '"', ';']
comparative_POS = set(['JJR','RBR','JJS','RBS'])
comparative_portion = set(['compare ','compares ','compared ','in contrast','in comparison'
                        ,'compared ','compared ','compared ','compared ','compared ','similar ',
                        'comparable ', 'just like', 'just as','than '])
comparative_pattern = [r'as\s.*\sas']

conjunction_POS = set(['IN','CC']) # subordinating conjunctions , coordinating conjunctions
conjunction_sub_POS = set(['IN']) 
conjunction_coor_POS = set(['CC']) 
coordinating_conjunctions = set(["for ","and ","nor ","but ","or ","yet ","so "])
subordinateing_conjuctions = set(["after ","although ","as if","as long as",
                                "as much as","as soon as","as though",
                                "because ","before ","by the time",
                                "even if ", "even though ", "if ",
                                "in order that","in case","lest ",
                                "once ","only if","provided that","since",
                                "so that","than","that", "though ","till ",
                                "unless ","until ","when ","whenever ","where ",
                                "wherever ","while "])
correlative_conjunctions = [r'both\s.*\sand',r'either\s.*\sor',r'neither\s.*\snor',
                            r'not\sonly\s.*\sbut\salso',r'whether\s.*\sor']
stanford_parser_exec = "/files2/sphinx-data/stanford-parser-full-2013-06-20/crfTD.sh /tmp/sen.tmp 2>/dev/null |egrep -i \"dobj\(|nsubj\(\""
def init():
    global content
    global labels
    global mylsa
    global documentIndex
    global dict_match
    add_dict('zh', './keyword_list/keyword_list_cn/')
    add_dict('en', './keyword_list/keyword_list_en/')
    add_dict('fr', './keyword_list/keyword_list_fr/')
    add_dict('ge', './keyword_list/keyword_list_ge/')
    add_dict('kr', './keyword_list/keyword_list_kr/')
    add_dict('po', './keyword_list/keyword_list_po/')
    add_dict('ro', './keyword_list/keyword_list_ro/')
    add_dict('sp', './keyword_list/keyword_list_sp/')
    dict_match = dict_hash['en']
    with open('./data/sentences') as f:
        content = f.readlines()
    content = content[:100]
    content = [c.rstrip() for c in content]
    with open('./data/labels') as f:
        labels = f.readlines()
    labels = labels[:100]
    labels = [c.rstrip() for c in labels]
    if len(content) != len(labels):
        print("data discrepancy %s" % (len(content) - len(labels)) )
    baselineChunker()
    print("doc %s"%(len(documentIndex)) )
    # build LSI matrix
    for t in content:
        mylsa.parse(t)
        mylsa.build() 
        #mylsa.printA()
    print("LSI trained")
    readTypedDependency("./data/td")
    getFeatures()
    printCRFtrain("./data/CRF_train_con")
    os.system("sed 's/98989898.*/ /' ./data/CRF_train_con > ./data/CRF_train")
    # need to add empty lines here due to document

def add_dict(language, path):
    global dict_hash
    dict_hash[language] = dictionary.Dictionary(language, path)

def rip(sentence):
    for val in rip_dic:
        sentence = sentence.replace(val, " ")
    return sentence

def readTypedDependency(fname):
    return "ok"

def printCRFtrain(fname):
    global CRF_input
    a = numpy.asarray(CRF_input)
    numpy.savetxt(fname, a, delimiter="\t",fmt="%d") # just signed integer
def baselineChunker():
    global content
    global labels
    global documentIndex    
    global dict_match
    j = 0
    for i in xrange(len(content)):
        j += 1
        if (j > 5) and (labels[i] == 'N' or labels[i] == 'P'):
            documentIndex.append(i)
            j = 0

def getFeatures():
    global content
    global labels
    global mylsa
    global documentIndex
    global CRF_input
    global dict_hash
    global dict_match

    for i in xrange(len(content)):
        print("processing %s" % (i) )
        # counters
        emoc_pos  = 0
        emoc_neg  = 0
        word_pos  = 0
        word_neg  = 0
        word_nega = 0
        # three comparative semantic features
        word_com1 = 0 
        word_com2 = 0
        word_com3 = 0
        conj_total= 0
        conj_sub  = 0
        conj_coor = 0
        conj_corr = 0
        syn_pos   = 0
        syn_com   = 0
        pos_pos   = 0
        neg_pos   = 0
        nega_pos1 = 0
        nega_pos2 = 0
        cos_pre   = 0
        lsi_pre   = 0
        cos_nex   = 0
        lsi_nex   = 0
        dobj_c    = 0
        nsubj_c   = 0

        #CRF_input.append([i])
        # comparative feature1
        try:
            POS = pos_tag(word_tokenize(content[i].encode('utf-8',errors='ignore')))
        except:
            POS = []
        word_com1 = sum([1 for part in POS if part[1] in comparative_POS])
        try:
            sentence = content[i].lower().encode('utf-8',errors='ignore')
        except:
            sentence = content[i].lower()
        sentence_rip = rip(sentence)
        array = set(word_tokenize(sentence))
        array_rip = set(word_tokenize(sentence_rip))
        array |= array_rip

        # comparative feature2
        word_com2 = len(array & comparative_portion)

        # comparative feature3
        for p in comparative_pattern:
            n = re.compile(p, re.IGNORECASE)
            word_com3 += len(n.findall(content[i]))

        # implement 4 conjunction features here
        conj_total = sum([1 for part in POS if part[1] in      conjunction_POS ])
        conj_sub   = sum([1 for part in POS if part[1] in   conjunction_sub_POS])
        conj_coor  = sum([1 for part in POS if part[1] in conjunction_coor_POS ])
        for p in correlative_conjunctions:
            n = re.compile(p, re.IGNORECASE)
            conj_corr += len(n.findall(content[i]))

        ## get the score and the count for emoticons
        for item in dict_match.pos_emoc_hash:
            if item in sentence:
                emoc_pos += 1
        
        for item in dict_match.neg_emoc_hash:
            if item in sentence:
                emoc_neg += 1
        # count pos/neg words
        pos_set = array & dict_match.pos_word_hash
        neg_set = array & dict_match.neg_word_hash
        nega_set = array & dict_match.neg_word_hash
        word_pos = len(pos_set)
        word_neg = len(neg_set)
        word_nega= len(nega_set) 

        ### syntactic features
        if len(documentIndex) > 2:
            idx,val=min(enumerate(documentIndex), key=lambda x: abs(x[1]-i))
            if idx < 1:
                idx = 1
            elif idx >= (len(documentIndex) - 1):
                idx = len(documentIndex) - 2
            if val > i:
                idx_end = documentIndex[idx] - 1
                idx_start = documentIndex[idx-1] 
            else:
                idx_start = documentIndex[idx]
                idx_end = documentIndex[idx+1] 

            # idx_start ======= i ======= idx_end
            #              a         b
            a = i - idx_start
            b = idx_end - i
            ratio = a / (b+0.0001)
            if ratio < 0.26:
                syn_pos = 0
            elif ratio > 3.9:
                syn_pos = 1
            else:
                syn_pos = 2

            if conj_total + conj_corr > 0:
                syn_com = 1

        # position of pos/neg words
        conj_idx = [idx for idx,part in enumerate(POS) if part[1] in conjunction_POS]
        if len(conj_idx) > 0:
            mid = conj_idx[len(conj_idx)/2]
            pos_idx = [idx for idx,part in enumerate(POS) if part[0].lower() in pos_set]
            neg_idx = [idx for idx,part in enumerate(POS) if part[0].lower() in neg_set ]
            pos_pos = sum([1 if ii > mid else -1 for ii in pos_idx])
            neg_pos = sum([1 if ii > mid else -1 for ii in neg_idx])
        else:
            pos_idx = []
            neg_idx = []

        # negation feature
        nega_idx = [idx for idx,part in enumerate(POS) if part[0].lower() in nega_set]
        nega_pos1 = levenshtein(nega_idx,pos_idx)
        nega_pos2 = levenshtein(nega_idx,neg_idx)

        # load typedDependency here!!
        # ####
        # ####
        f = open('/tmp/sen.tmp','w')
        print(content[i], file=f)
        f.close()
        td = os.popen(stanford_parser_exec).read()
        dobj_c  = max(4,td.count("dobj"))
        nsubj_c = max(4,td.count("nsubj"))
        # similarity features
        if i > 0:
            cos_pre = levenshtein(content[i],content[i-1])/10
            lsi_pre = levenshtein(list(mylsa.A[:,i]), list(mylsa.A[:,i-1]))/4
        if i < (len(content)-1):
            cos_nex = levenshtein(content[i],content[i+1])/10
            lsi_nex = levenshtein(list(mylsa.A[:,i]), list(mylsa.A[:,i+1]))/4

        if (i in documentIndex) and (i > 0):
            CRF_input.append([98989898,emoc_pos,emoc_neg,word_pos,word_neg,word_nega,
                            word_com1,word_com2,word_com3,conj_total,
                            conj_sub,conj_coor,conj_corr,syn_pos,syn_com,
                            pos_pos,neg_pos,nega_pos1,nega_pos2,cos_pre,
                            lsi_pre,cos_nex,lsi_nex,dobj_c,nsubj_c,label_conv[labels[i]]])
            # will be replaced by newline in CRF++ format.
        CRF_input.append([i,emoc_pos,emoc_neg,word_pos,word_neg,word_nega,
                            word_com1,word_com2,word_com3,conj_total,
                            conj_sub,conj_coor,conj_corr,syn_pos,syn_com,
                            pos_pos,neg_pos,nega_pos1,nega_pos2,cos_pre,
                            lsi_pre,cos_nex,lsi_nex,dobj_c,nsubj_c,label_conv[labels[i]]]) # so the array is integer

if __name__=="__main__":
    init()
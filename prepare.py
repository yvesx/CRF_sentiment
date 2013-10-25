
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
import dictionary
import levenshtein
import LSI

documentIndex = [0] # document start indices
content = None # to hold list of sentences
labels  = None # list of ground truth labels
dict_hash = {}
dict_match = None
typedDependency = {}
mylsa = LSI.LSI(stopwords=set(['and','edition','for','in','little','of','the','to','this','that','a','an']), 
                    ignorechars=''',:'!''') 

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
def init():
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
    with open('./data/labels') as f:
        labels = f.readlines()
    if (len(content) != len(labels)):
        print "data discrepancy!"
    baselineChunker()
    print "doc %s"%(len(documentIndex))
    # build LSI matrix
    for t in content:
        mylsa.parse(t)
        mylsa.build() 
        #mylsa.printA()
    print "LSI trained"


def add_dict(language, path):
    dict_hash[language] = dictionary.Dictionary(language, path)

def rip(sentence):
        for val in rip_dic:
        sentence = sentence.replace(val, " ")
    return sentence

def readTypedDependency(fname):


def baselineChunker():
    j = 0
    for i in xrange(len(content)):
        j += 1
        if (j > 5) and (labels[i] == 'N' or labels[i] == 'P'):
            documentIndex.append(i)
            j = 0

def getFeatures():
    CRF_input = []

    for i in xrange(len(content)):
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

        CRF_input.append([i])
        # comparative feature1
        POS = pos_tag(word_tokenize(content[i].encode('utf-8')))
        word_com1 = sum([1 if part[1] in comparative_POS for part in POS])

        sentence = content[i].lower().encode('utf-8')
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
        conj_total = sum([1 if part[1] in conjunction_POS      for part in POS])
        conj_sub   = sum([1 if part[1] in conjunction_sub_POS  for part in POS])
        conj_coor  = sum([1 if part[1] in conjunction_coor_POS for part in POS])
        for p in correlative_conjunctions:
            n = re.compile(p, re.IGNORECASE)
            conj_corr += len(n.findall(content[i]))

        ## get the score and the count for emoticons
        for item in dict_match.pos_emoc_hash:
            if item in sentence:
                emoc_pos += 1
        
        for item in dict_match.neg_word_hash:
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
        idx,val=min(enumerate(documentIndex), key=lambda x: abs(x[1]-i))
        if idx < 1:
            idx = 1
        elif idx >= len(documentIndex) - 1
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
        conj_idx = [idx if part[1] in conjunction_POS for idx,part in enumerate(POS)]
        if len(conj_idx) > 0:
            mid = conj_idx[len(conj_idx)/2]
            pos_idx = [idx if part[0].lower() in pos_set for idx,part in enumerate(POS)]
            neg_idx = [idx if part[0].lower() in neg_set for idx,part in enumerate(POS)]
            pos_pos = sum([1 if i > mid else -1 for i in pos_idx])
            neg_pos = sum([1 if i > mid else -1 for i in neg_idx])
         else:
            pos_idx = []
            neg_idx = []

        # negation feature
        nega_idx = [idx if part[0].lower() in nega_set for idx,part in enumerate(POS)]
        nega_pos1 = levenshtein(nega_idx,pos_idx)
        nega_pos2 = levenshtein(nega_idx,neg_idx)

        # load typedDependency here!!
        # ####
        # ####

        # similarity features
        if i > 0:
            cos_pre = levenshtein(content[i],content[i-1])
            lsi_pre = levenshtein(list(mylsa.A[:,i]), list(mylsa.A[:,i-1]))
        if i < len(content)-1:
            cos_nex = levenshtein(content[i],content[i+1])
            lsi_nex = levenshtein(list(mylsa.A[:,i]), list(mylsa.A[:,i+1]))

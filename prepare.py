
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


dict_hash = {}
dict_match = None
rip_dic = ['!', '?', '.', ',', '-', '>', '<', ':', '/', "\\", '(', ')', '=',
            '#', '$', '%', '^', '*', '&', '~', '"', ';']
comparative_POS = set(['JJR','RBR','JJS','RBS'])
comparative_portion = set(['compare ','compares ','compared ','in contrast','in comparison'
                        ,'compared ','compared ','compared ','compared ','compared ','similar ',
                        'comparable ', 'just like', 'just as','than '])
comparative_pattern = [r'as\s.*\sas']

conjunction_POS = set(['IN','CC']) # subordinating conjunctions , coordinating conjunctions
coordinating_conjunctions = set(["for","and","nor","but","or","yet","so"])
subordinateing_conjuctions = set(["after","although","as","as if","as long as",
                                "as much as","as soon as","as though",
                                "because","before","by the time",
                                "even if", "even though", "if",
                                "in order that","in case","lest",
                                "once","only if","provided that","since",
                                "so that","than","that", "though","till",
                                "unless","until","when","whenever","where",
                                "wherever","while"])
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



def add_dict(language, path):
    dict_hash[language] = dictionary.Dictionary(language, path)

def rip(sentence):
        for val in rip_dic:
        sentence = sentence.replace(val, " ")
    return sentence

def readTypedDependency(fname):

def readGroundTruthLabel(fname):

def readSentences(fname):
    CRF_input = []
    with open(fname) as f:
        content = f.readlines()

    for i in xrange(len(content)):
        # counters
        emoc_pos = 0
        emoc_neg = 0
        word_pos = 0
        word_neg = 0
        # three comparative semantic features
        word_com1 = 0 
        word_com2 = 0
        word_com3 = 0
        CRF_input.append([i])
        # comparative feature1
        POS = pos_tag(word_tokenize(content[i]))
        word_com1 = sum([1 for part in POS if part[1] in comparative_POS])

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

        # implement conjunction features here

        ## get the score and the count for emoticons
        for item in dict_match.pos_emoc_hash:
            if item in sentence:
                emoc_pos += 1
        
        for item in dict_match.neg_word_hash:
            if item in sentence:
                emoc_neg += 1
        # count pos/neg words
        word_pos = len(array & dict_match.pos_word_hash)
        word_neg = len(array & dict_match.neg_word_hash)

        #build comparative features 
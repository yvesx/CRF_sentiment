CRF & Active Learning to Improve Sentiment Identification
=========================================================

Incorporating Conditional Random Fields (CRF) and Active Learning to Improve Sentiment Identification

Many machine learning, statistical, and computational linguistic methods have been developed to identify sentiment in sentences in documents, yielding promising results. However, most of the current state-of-the-art methods focus on individual sentences and ignore the impact of context on the meaning of a sentence. In this paper, we propose a method based on conditional random fields to incorporate sentence structure and context information in addition to syntactic information. We also investigate how human interaction affects the accuracy of sentiment labeling using limited training data. We propose and evaluate two different active learning strategies for labeling sentiment data.

* Publication ``35th ACM SIGIR 2012`` Kunpeng Zhang, Yusheng Xie, Yu Cheng, Doug Downey, Ankit Agrawal, Wei-keng Liao, and Alok Choudhary. *Sentiment Identification by Incorporating Syntactics, Semantics and Context Information* 

* Publication ``under journal review`` Incorporating Conditional Random Fields and Active Learning to Improve Sentiment Identification

![alt tag](https://raw.github.com/yvesx/CRF_sentiment/master/imgs/1.png)


Main Challenges
===============


Evaluation
==========



Acknowledgements
================

* [Dataset](https://raw.github.com/yvesx/CRF_sentiment/master/data/CRF_long_data.xlsx) contains long, complicated sentences from [other](http://nlp.stanford.edu/sentiment/index.html) [projects](http://cucis.ece.northwestern.edu/projects/Social/).
* [CRF++](http://crfpp.googlecode.com/svn/trunk/doc/index.html) is a great tool.

Collaborators: @kpzhang @hixiaoxi

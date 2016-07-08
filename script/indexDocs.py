#!/usr/bin/env python
#coding=utf-8
# translate word into id in documents
import sys
import unicodedata, re
import gensim
from gensim import corpora, models, similarities
from collections import defaultdict
import io

# import numpy as np


w2id = {}

def indexFile(words, res_pt):

    wf = open(res_pt, 'w')
    stop_words =  [line.strip('\n') for line in open("../sample-data/stop_words.txt", 'r')]

    for index, word in words.iterrows():
        ws = word['title']
        ws = default_tokenizer(str(word['title'].encode("utf-8")))
        ws = stoplist(ws,stop_words)
        for w in ws:
            if not w2id.has_key(w):
                w2id[w] = len(w2id)
                
        wids = [w2id[w] for w in ws]        
        print >>wf, ' '.join(map(str, wids))
        
    print 'write file: ', res_pt

def write_w2id(res_pt):
    print 'write:', res_pt
    wf = open(res_pt, 'w')
    for w, wid in sorted(w2id.items(), key=lambda d:d[1]):
        print >>wf, '%d\t%s' % (wid, w)

def stoplist(text_list, stop_words):
    list = []
    for word in text_list:
        if (word.encode("utf-8") not in stop_words) and (len(word) > 2):
            list.append(word.encode("utf-8"))
    return list

def default_tokenizer(text):
        def foo(c):
            if ord(c)>127: return ''
            if c.isdigit() or c.isalpha(): return c
            else : return ' '

        text = unicodedata.normalize('NFD', unicode(text, 'utf-8')).lower()
        text = ''.join(map(foo,text))
        text = re.sub(r'([a-z])([0-9])', r'\1 \2', text)
        text = re.sub(r'([0-9])([a-z])', r'\1 \2', text)
        text = re.sub(r'\s+', r' ', text)
        return text.strip().split()

        
if __name__ == '__main__':

    import pandas as pd
    from azureml import Workspace
    ws = Workspace(
        workspace_id='0a1ad38466a7494db8ed3dcc8a50904e',
        authorization_token='ad20f4673b3c4349a5b171991ac039ec',
        endpoint='https://studioapi.azureml.net'
    )
    experiment = ws.experiments['0a1ad38466a7494db8ed3dcc8a50904e.f-id.106a47f9acbd44ad9dc9dce10d3dad56']
    ds = experiment.get_intermediate_dataset(
        node_id='b8ac68c4-c002-408b-88b8-196c623a2bf9-546',
        port_name='Results dataset',
        data_type_id='GenericTSV'
    )

    # select dataframes from azure, all reports
    words = ds.to_dataframe()
    words = pd.DataFrame(words)

    print "-----Start----"

    dwid_pt = '../output/doc_wids.txt'
    voca_pt = '../output/voca.txt'

    indexFile(words, dwid_pt)
    print 'n(w)=', len(w2id)
    write_w2id(voca_pt)

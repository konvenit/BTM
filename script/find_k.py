#!/usr/bin/env python
#coding=utf-8
# translate word into id in documents
import sys
import unicodedata, re
import gensim
from gensim import corpora, models, similarities
from collections import defaultdict
import io
import pandas as pd
import numpy as np


w2id = {}

def topic_prob_extractor(hdp=None, topn=None):
    topic_list = hdp.show_topics(topics=-1, topn=topn)
    topics = [int(x.split(':')[0].split(' ')[1]) for x in topic_list]
    split_list = [x.split(' ') for x in topic_list]
    weights = []
    for lst in split_list:
        sub_list = []
        for entry in lst:
            if '*' in entry:
                sub_list.append(float(entry.split('*')[0]))
        weights.append(np.asarray(sub_list))
    sums = [np.sum(x) for x in weights]
    return pd.DataFrame({'topic_id' : topics, 'weight' : sums})

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
    stop_words =  [line.strip('\n') for line in open("../sample-data/stop_words.txt", 'r')]
    list = []

    for index, word in words.iterrows():
        ws = default_tokenizer(str(word['title'].encode("utf-8")))
        ws = stoplist(ws,stop_words)
        list.append(ws)

    with io.FileIO("foobar.txt", "w") as file:
        for l in list:
            for word in l:
                file.write(word + " ")
            file.write("\n")

    dictionary = corpora.Dictionary(list)
    dictionary.save('words.dict')
    corpus = [dictionary.doc2bow(text) for text in list]
    corpora.MmCorpus.serialize('words.mm', corpus)
    id2word = corpora.Dictionary.load('words.dict')
    print("all info loaded")
    for x in range(15):
        hdp = gensim.models.HdpModel(corpus, id2word)
        results = topic_prob_extractor(hdp, topn=20)
        results = results.sort_values(by=['weight'], ascending=[True])
        if x == 0:
            result_total = results
        else:
            result_total = pd.concat([result_total.loc[:,["weight"]],results.loc[:,["weight"]]], axis=1).fillna(0).sum(axis=1)
            result_total = pd.DataFrame(result_total, columns=['weight'])
        print(str(x))

    result_total = result_total.sort_values('weight', ascending=True)
    print (result_total.iloc[-10:])

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
from itertools import izip


w2id = {}

def read_files(ids,gammas):
    list_total = {}
    with open(ids) as trans_number, open(gammas) as result_cluster:
        for id, result in izip(trans_number, result_cluster):
            result = get_best_cluster(result.split(' '))
            list_total.update({id.rstrip('\n'):result})

    return list_total


def get_best_cluster(result_by_id):
    result_clean = []
    del result_by_id[-1]
    for i in result_by_id:
        i = i.replace(',', '.')
        try:
            i = float(i)
        except:
            return 0
        result_clean.append(i)
    result_by_id = result_clean
    result_clean = sorted(result_clean)
    if str(result_clean[-1]) == "nan":
        return 0
    cluster_num = result_by_id.index(result_clean[-1])
    return cluster_num + 1

def write_necessary(test_data,list_total):
    for id in open(test_data):
        get_value = list_total.get(id.rstrip('\n'))
        if get_value == None:
            get_value = 0
        print str(id.rstrip('\n')) + "," + str(get_value)

        
if __name__ == '__main__':

    print "-----start----"

    list_total = read_files('id_trans.txt','k23.txt')

    write_necessary('test_id_few.txt',list_total)
    # for key, value in list_total.iteritems():
    #     print key

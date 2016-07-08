#!/usr/bin/env python
#coding=utf-8
# Function: translate the results from BTM
# Input:
#    mat/pw_z.k20

import sys
import io
import unicodedata, re

# return:    {wid:w, ...}
def read_voca(pt):
    voca = {}
    for l in open(pt):
        wid, w = l.strip().split('\t')[:2]
        voca[int(wid)] = w
    return voca

def read_pz(pt):
    return [float(p) for p in open(pt).readline().split()]
    
# voca = {wid:w,...}
def dispTopics(pt, voca, pz, K):
    k = 0
    topics = []
    for l in open(pt):
        vs = [float(v) for v in l.split()]
        wvs = zip(range(len(vs)), vs)
        wvs = sorted(wvs, key=lambda d:d[1], reverse=True)
        #tmps = ' '.join(['%s' % voca[w] for w,v in wvs[:10]])
        tmps = ' '.join(['%s:%f' % (voca[w],v) for w,v in wvs[:10]])
        topics.append((pz[k], tmps))
        k += 1

    with io.FileIO("result" + str(K) + ".txt", "w") as file:
        print 'p(z)\t\tTop words'
        i = 1
        for pz, s in sorted(topics, reverse=True):
            print '%f\t%s' % (pz, s)
            file.write(str(i) + " " + '%f\t%s' % (pz, s))
            file.write("\n")
            i= i + 1

if __name__ == '__main__':

    # sys.argv= ['topicDisplay.py', '../output/model/', '26', '../output/voca.txt']
    print "-----Start----"
    print sys.argv

    print("k number : " + str(sys.argv[2]))
    model_dir = sys.argv[1]
    K = int(sys.argv[2])
    voca_pt = sys.argv[3]
    voca = read_voca(voca_pt)    
    W = len(voca)
    print 'K:%d, n(W):%d' % (K, W)

    pz_pt = model_dir + 'k%d.pz' % K
    pz = read_pz(pz_pt)
    
    zw_pt = model_dir + 'k%d.pw_z' %  K
    dispTopics(zw_pt, voca, pz, K)

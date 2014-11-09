__author__ = 'nikhilraju'
import os
import datetime
from pymongo import MongoClient
from createFeatureVectors import createFv

def createDict(dict, dir):
    #filepath = '%s/articles/%s/' %(os.getcwd(),dir)

    filepath = '/Users/nikhilraju/Desktop/AML/Project/banditron/%s/' %dir

    for filename in os.listdir(filepath):
        with open('%s%s' %(filepath, filename)) as eachFile:
            lineNo = 0
            for line in eachFile:
                lineNo += 1
                if lineNo >= 3:
                    allWords = line[:-1].split(' ')
                    for words in allWords:
                        dict.add(words)

def init():
    dict = set()
    createDict(dict, 'train')
    print 'finished train'
    createDict(dict, 'test0')
    print 'finished test0'
    createDict(dict, 'test1')
    print 'finished test1'
    createDict(dict, 'test2')
    print 'finished test2'
    createDict(dict, 'test3')
    print 'finished test3'
    print len(dict)

    features_coll = MongoClient('localhost',27017)['aml']['features']
    features_coll.update({'_id':'1'},{'$set':{'timeStamp':datetime.datetime.now(),'featureList':list(dict)}},True)

def main():
    init()
    createFv()



if __name__=="__main__":
    main()
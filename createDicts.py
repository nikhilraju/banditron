__author__ = 'nikhilraju'
import os
from collections import defaultdict
import os
import datetime
from pymongo import MongoClient

class Banditron:
    feature_set = set()

    def createDict(self,dir):
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
                            self.feature_set.add(words)
    def addFeatureSetToMongo(self):
        self.createDict('train')
        print 'finished train'
        self.createDict('test0')
        print 'finished test0'
        self.createDict('test1')
        print 'finished test1'
        self.createDict('test2')
        print 'finished test2'
        self.createDict('test3')
        print 'finished test3'
        print 'The total number of features(words) is ',len(self.feature_set)

        features_coll = MongoClient('localhost',27017)['aml']['features']
        features_coll.update({'_id':'1'},{'$set':{'timeStamp':datetime.datetime.now(),'featureList':list(self.feature_set)}},True)
        print 'Added feature set to Mongo.....'

    def createFv(self):
        print 'creating feature vectors'
        features_coll = MongoClient('localhost',27017)['aml']['features']
        feature_list = features_coll.find({'_id':'1'})[0]['featureList']


        dir = 'train'
        filepath = '/Users/nikhilraju/Desktop/AML/Project/banditron/%s/' %dir

        for filename in os.listdir(filepath):

            currFv = []
            count = 0
            sum = 0
            with open('%s%s' %(filepath, filename)) as eachFile:
                lineNo = 0
                count += 1
                currDocDictionary = defaultdict(float)

                if count%1000 == 0:
                    print 'Feature Vectors for ',count,' articles done \n'

                for line in eachFile:
                    lineNo += 1

                    if lineNo >= 3:
                        allWords = line[:-1].split(' ')

                        for word in allWords:
                            sum += 1
                            currDocDictionary.setdefault(0.0)
                            currDocDictionary[word] += 1.0
                            #adding a tuple   (index in feature_list,count) as a sparse representation

                if dir == 'train':
                     dataPointLabel ='train'
                else:
                    dataPointLabel ='test'

                for word in currDocDictionary:
                    if word != 0.0:
                        currDocDictionary[word] = currDocDictionary[word] / sum
                        currFv.append((feature_list.index(word),currDocDictionary[word]))


                features_coll.update({'_id':filename},{'$set':{'timeStamp':datetime.datetime.now(),'featureList':currFv,'label':dataPointLabel}},True)

def main():

    b = Banditron()
    #b.addFeatureSetToMongo()
    b.createFv()

if __name__=="__main__":
    main()

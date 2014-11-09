__author__ = 'nikhilraju'


from pymongo import MongoClient

features_coll = MongoClient('localhost',27017)['aml']['features']


feature_cursor = features_coll.find({'_id':'1'})

for f in feature_cursor:
    print len(f['featureList'])


def createFv():
    print 'creating feature vectors'
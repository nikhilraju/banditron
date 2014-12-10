__author__ = 'nikhilraju'

from pymongo import MongoClient

#Define helper methods here


def add_document_id_field():
    #For an existing mongo document, search and extract the I: field from the related text file
    features_coll = MongoClient('localhost',27017)['aml']['features']

    docs = features_coll.find()

    for d in docs:
        filename = d['_id']
        filepath = '/Users/nikhilraju/Desktop/AML/Project/banditron/train/'

        #Open this file, read first line, split on space and extract 2nd element
        if 'train' in filename:
            f = open('%s%s' % (filepath, filename))
            doc_id = f.readline().split()[1]
            features_coll.update({'_id': filename}, {'$set':{'docId': doc_id}})


def main():
    add_document_id_field()

if __name__ == "__main__":
    main()


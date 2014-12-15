__author__ = 'nikhilraju'

from pymongo import MongoClient
import datetime

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

def create_doc_label_map():

    doc_labels = {}
    f = open('topic_article_mapping.txt')

    for line in f.readlines():
        (label, docId) = line.strip().split(' ')
        doc_labels[docId] = label

    return doc_labels

    #685071 entries in this mapping dictionary
    # coll = MongoClient('localhost',27017)['aml']['features']
    #
    # count = 0
    # for d in doc_labels.keys():
    #     coll.update({'docId': d}, {'$set': {'true_label': doc_labels[d]}})
    #     count += 1
    #     if count%1000 == 0:
    #         print count, ' documents updated with true labels....', len(doc_labels) - count, ' to go '


def create_dataset_docId_list():
    coll = MongoClient('localhost',27017)['aml']['features']

    allDocs = coll.find({'docId': {'$exists': 1}})
    dataset_ids = []

    for d in allDocs:
        dataset_ids.append(d['docId'])

    coll.update({'_id': 2}, {'$set': {'timeStamp':datetime.datetime.now(), 'dataset_list_docIds': dataset_ids }}, True)



def main():
    #add_document_id_field()
    #print 'Adding true labels'
    #create_doc_label_map()
    print 'Adding docId list'
    create_dataset_docId_list()

if __name__ == "__main__":
    main()


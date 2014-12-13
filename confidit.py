from pymongo import MongoClient
import random

REUTERS_CATEGORY_MAPPING = ['CCAT', 'ECAT', 'MCAT', 'GCAT']

def get_category_index(label):
	for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
		if label == REUTERS_CATEGORY_MAPPING[i]:
			return i
	return -1

class Confidit:

	def __init__(self):
		self.alpha = 1.0
		self.eta = 5
		self.mongo = MongoClient('localhost',27017)['aml']['features']
		self.dict = self.mongo.find({'_id':'1'})[0]['featureList']
		self.uncertainty = self.init_uncertainty()
		self.weights = self.init_weights()

	def init_uncertainty(self):
        uncertainty = []
        constant = (1.0 + self.alpha)*(1.0 + self.alpha)
        for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
        	inner_uncertainty = []
        	for j in range(0, len(self.dict)):
        		inner_inner_uncertainty = [0.0]*len(self.dict)
        		inner_inner_uncertainty[j] = constant
        		inner_uncertainty.append(inner_inner_uncertainty)
            uncertainty.append(inner_uncertainty)
        return uncertainty

    def init_weights(self):
    	weights = []
        for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
            weights.append([0.0]*len(self.dict))
        return weights

    def run(self, doc_id, feature_vectors, true_label):
        
        prediction_weight = self.predict_weight(feature_vectors)
        uncertainty_factor = self.get_uncertainty_factor()
        predicted_label = self.predict_label(prediction_weight, uncertainty_factor)
        if true_label == predicted_label:
            print 'Document %s categorized successfully to %s' %(doc_id, true_label)
        else:
            print 'Document %s wrongly categorized' %doc_id
        self.update_X_vector(true_label == predicted_label)
        self.update_uncertainty()
        self.update_weights()

    def predict_weight(self, feature_vectors):
        prediction_weight = []
        for i in range(0,len(self.weights)):
            total = 0.0
            for eachVector in feature_vectors:
                total += eachVector[1]*self.weights[i][int(eachVector[0])]
            prediction_weight.append(total)
        return prediction_weight

    def predict_label(self, prediction_weight, uncertainty_factor):
    	max = 0.0
        label = 0
        for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
            total = prediction_weight[i] + uncertainty_factor[i]
            if total >= max:
                max = total
                label = i
        return label

    def get_uncertainty_factor(self):


    def update_X_vector(self, prediction):


   	def update_uncertainty(self):


   	def update_weights(self):



def main():
	confidit = Confidit()
	doc_ids = confidit.mongo.find({'_id':'doc'})[0]['docs']
	for t in range(0,len(doc_ids)):
		doc_id = doc_ids[t]
		feature_vectors = confidit.mongo.find({'docId':str(doc_id)})[0]['featureList']
		true_label = get_category_index(confidit.mongo.find({'docId':str(doc_id)})[0]['true_label'])
		confidit.run(doc_id, feature_vectors, true_label)

if __name__=="__main__":
	main()
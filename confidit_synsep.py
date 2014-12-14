from pymongo import MongoClient
import random

SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

class Confidit:

	def __init__(self):
		self.alpha = 1.0
		self.eta = 5
		self.dict_length = 400
		self.uncertainty = self.init_uncertainty()
		self.weights = self.init_weights()
        self.error_rate = 0.0
        self.correct_classified = 0.0
        self.incorrect_classified = 0.0
        self.number_of_rounds = 0.0

	def init_uncertainty(self):
        uncertainty = []
        constant = (1.0 + self.alpha)*(1.0 + self.alpha)
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
        	inner_uncertainty = []
        	for j in range(0, self.dict_length):
        		inner_inner_uncertainty = [0.0]*self.dict_length
        		inner_inner_uncertainty[j] = constant
        		inner_uncertainty.append(inner_inner_uncertainty)
            uncertainty.append(inner_uncertainty)
        return uncertainty

    def init_weights(self):
    	weights = []
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            weights.append([0.0]*self.dict_length)
        return weights

    def run(self, feature_vectors, true_label):
        self.number_of_rounds += 1.0
        prediction_weight = self.predict_weight(feature_vectors)
        uncertainty_factor = self.get_uncertainty_factor()
        predicted_label = self.predict_label(prediction_weight, uncertainty_factor)
        if true_label == predicted_label:
            self.correct_classified += 1.0
        else:
            self.incorrect_classified += 1.0
        self.error_rate = self.incorrect_classified/self.number_of_rounds
        self.update_X_vector(true_label == predicted_label)
        self.update_uncertainty()
        self.update_weights()

    def predict_weight(self, feature_vectors):
        prediction_weight = []
        for i in range(0,len(self.weights)):
            total = 0.0
            for eachVector in range(0,len(feature_vectors)):
                total += feature_vectors[eachVector]*self.weights[i][eachVector]
            prediction_weight.append(total)
        return prediction_weight

    def predict_label(self, prediction_weight, uncertainty_factor):
    	max = 0.0
        label = 0
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
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
    synsep = SynSep()
	for t in range(0,10000):
		feature_vectors, true_label = synsep.generateSynSepData()
		confidit.run(feature_vectors, true_label)
        if ((t+1)%1000) == 0:
            print "%s rounds completed with error rate %s" %(str(t+1),str(banditron.error_rate))
    print "Correctly classified: %s" %str(banditron.correct_classified)
    print "Incorrectly classified: %s" %str(banditron.incorrect_classified)
    print "Error Rate: %s" %str(banditron.error_rate)

if __name__=="__main__":
	main()
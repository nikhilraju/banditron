from pymongo import MongoClient
import random
from generateSynsep import SynSep
from numpy import matrix
from numpy import linalg
from numpy import inner
from numpy import kron
import datetime
import math


SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

class Newtron:

	def __init__(self):
        self.alpha = 10.0
        self.gamma = 0.01
        self.beta = 0.01
        self.D = 1.0
        self.dict_length = 400
        self.A = self.init_A()
        self.B = self.init_B()
        self.weights = self.init_weights()
        self.k = 1.0
        self.error_rate = 0.0
        self.correct_classified = 0.0
        self.incorrect_classified = 0.0
        self.number_of_rounds = 0.0

    def init_weights(self):
        weights = []
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            weights.append([0.0]*self.dict_length)
        weight_matrix = matrix(weights)
        return weight_matrix

    def init_A(self):
        A = []
        constant = 1.0/self.D
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            inner_A = []
            inner_A = [0.0]*len(SYNSEP_CATEGORY_MAPPING)
            inner_A[i] = constant
            A.append(inner_A)
        A_matrix = matrix(A)    
        return A_matrix

    def init_B(self):
        B = []
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            B.append([0.0]*self.dict_length)
        B_matrix = matrix(B)
        return B_matrix

    def run(self, feature_vectors, true_label):
        self.number_of_rounds += 1.0
        calculated_label, prediction_weight = self.predict_label(feature_vectors)
        probabilities = self.calc_probabilities(calculated_label)
        predicted_label = self.random_sample(probabilities)
        if true_label == predicted_label:
            self.correct_classified += 1.0
        else:
            self.incorrect_classified += 1.0
        self.error_rate = self.incorrect_classified/self.number_of_rounds
        estimator = self.get_estimator(true_label == predicted_label, predicted_label, feature_vectors, probabilities, prediction_weight)
        self.update_A(estimator)
        self.update_B(estimator)
        self.update_weights()

    def predict_label(self, feature_vectors):
        max = 0.0
        label = 0
        prediction_weight = []
        cumulative_total = 0.0
        feature_vectors_matrix = matrix(feature_vectors).T
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            total = math.exp(((self.alpha*self.weights[i])*feature_vectors_matrix).item(0))
            cumulative_total += total
            prediction_weight.append(total)
            if total >= max:
                max = total
                label = i
        prediction_weight = prediction_weight/cumulative_total
        return label, prediction_weight

    def calc_probabilities(self, calculated_label):
        probabilities = [0] * len(SYNSEP_CATEGORY_MAPPING)
        for i in range(0,len(probabilities)):
            probabilities[i] = self.gamma/len(SYNSEP_CATEGORY_MAPPING)
            if i == calculated_label:
                probabilities[i] += (1 - self.gamma)
        return probabilities

    def random_sample(self, probabilities):
        number = random.random() * sum(probabilities)
        for i in range(0,len(probabilities)):
            if number < probabilities[i]:
                return i
                break
            number -= probabilities[i]
        return len(probabilities)-1

    def get_estimator(self, prediction, predicted_label, feature_vectors, probabilities, prediction_weight):
    	estimator = matrix()
        a = 1.0/len(SYNSEP_CATEGORY_MAPPING)
        unit_vector = [a]*len(SYNSEP_CATEGORY_MAPPING)
        e = [0.0]*len(SYNSEP_CATEGORY_MAPPING)
        e[predicted_label] = 1.0
        left = 0.0
        right = matrix()
        if prediction:
        	self.k = probabilities[predicted_label]
            left = (1 - prediction_weight[predicted_label])/probabilities[predicted_label]
            right = matrix(unit_vector - e)
        else:
        	self.k = 1.0
            left = prediction_weight[predicted_label]/probabilities[predicted_label]
            right = matrix(e - unit_vector)
        estimator = matrix(kron(inner(left,right),matrix(feature_vectors)))
        return estimator

    def update_A(self, estimator):
    	self.A += (self.k*self.beta*(estimator*(estimator.T)))

   	def update_B(self, estimator):
        self.B += (1 - (self.k*self.beta*inner(estimator,self.weights)))*estimator

   	def update_weights(self):
   		half_weights = -((self.A.I)*self.B)
   		weight_norm = linalg.norm(half_weights)
   		if weight_norm <= self.D:
   			self.weights = half_weights
   		else:
   			self.weights = half_weights/weight_norm


def main():
    newtron = Newtron()
    synsep = SynSep()
    for t in range(0,1000):
        feature_vectors, true_label = synsep.generateSynSepData()
        newtron.run(feature_vectors, true_label-1)
        if ((t+1)%10) == 0:
            print "%s rounds completed with error rate %s" %(str(t+1),str(newtron.error_rate))
    print "Correctly classified: %s" %str(newtron.correct_classified)
    print "Incorrectly classified: %s" %str(newtron.incorrect_classified)
    print "Error Rate: %s" %str(newtron.error_rate)

if __name__=="__main__":
    main()
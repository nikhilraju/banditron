from pymongo import MongoClient
import random
from generateSynsep import SynSep
from numpy import matrix
import datetime
import math

SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

class Confidit:

    def __init__(self):
        self.alpha = 1.0
        self.eta = 5
        self.dict_length = 400
        self.uncertainty = self.init_uncertainty()
        self.previous_uncertainty = []
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
            inner_uncertainty_matrix = matrix(inner_uncertainty)
            uncertainty.append(inner_uncertainty_matrix)
        return uncertainty

    def init_weights(self):
    	weights = []
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            weights.append(matrix([0.0]*self.dict_length))
        return weights

    def run(self, feature_vectors, true_label):
        self.number_of_rounds += 1.0
        prediction_weight = self.predict_weight(feature_vectors)
        uncertainty_factor = self.get_uncertainty_factor(feature_vectors)
        predicted_label = self.predict_label(prediction_weight, uncertainty_factor)
        if true_label == predicted_label:
            self.correct_classified += 1.0
        else:
            self.incorrect_classified += 1.0
        self.error_rate = self.incorrect_classified/self.number_of_rounds
        X_vector = self.update_X_vector(true_label == predicted_label, predicted_label, feature_vectors)
        self.update_uncertainty(X_vector)
        self.update_weights(X_vector)

    def predict_weight(self, feature_vectors):
        prediction_weight = []
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            total = 0.0
            for eachVector in range(0,len(feature_vectors)):
                total += feature_vectors[eachVector]*(self.weights[i].item(eachVector))
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

    def get_uncertainty_factor(self, feature_vectors):
        uncertainty_factor = []
        feature_vectors_matrix = matrix(feature_vectors)
        feature_vectors_matrix_transpose = feature_vectors_matrix.T
        for i in range(0, len(SYNSEP_CATEGORY_MAPPING)):
            temp = self.eta*(feature_vectors_matrix*(self.uncertainty[i].I)*feature_vectors_matrix_transpose).item(0,0)
            uncertainty_factor.append(math.sqrt(temp))
        return uncertainty_factor

    def update_X_vector(self, prediction, predicted_label, feature_vectors):
        X_vector = []
        feature_vectors_matrix = matrix(feature_vectors)
        for i in range(0, len(SYNSEP_CATEGORY_MAPPING)):
            if i is predicted_label:
                if prediction:
                    X_vector.append(feature_vectors_matrix)
                else:
                    X_vector.append(-feature_vectors_matrix)
            else:
                X_vector.append(matrix([0.0] * self.dict_length))
        return X_vector


    def update_uncertainty(self, X_vector):
        self.previous_uncertainty = self.uncertainty
        for i in range(0, len(SYNSEP_CATEGORY_MAPPING)):
            self.uncertainty[i] += (X_vector[i].T*X_vector[i])

    def update_weights(self, X_vector):
        for i in range(0, len(SYNSEP_CATEGORY_MAPPING)):
            a = self.uncertainty[i].I
            b = self.previous_uncertainty[i]
            c = self.weights[i].T
            d = X_vector[i].T

            self.weights[i] = (a*((b*c) + d)).T
            # self.weights[i] = (self.uncertainty[i].I)*((self.previous_uncertainty[i]*self.weights[i]) + X_vector[i])


def main():
    confidit = Confidit()
    synsep = SynSep()
    for t in range(0,10):
        feature_vectors, true_label = synsep.generateSynSepData()
        confidit.run(feature_vectors, true_label-1)
        if ((t+1)%1) == 0:
            print "%s rounds completed with error rate %s" %(str(t+1),str(confidit.error_rate))
    print "Correctly classified: %s" %str(confidit.correct_classified)
    print "Incorrectly classified: %s" %str(confidit.incorrect_classified)
    print "Error Rate: %s" %str(confidit.error_rate)

if __name__=="__main__":
    main()
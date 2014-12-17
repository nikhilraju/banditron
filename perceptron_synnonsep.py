from pymongo import MongoClient
import random
from generateSynsep import SynSep
import datetime


SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

class Perceptron:

    def __init__(self):
        #self.gamma = 0.014
        self.dict_length = 400
        self.weights = self.init_weights()
        self.error_rate = 0.0
        self.correct_classified = 0.0
        self.incorrect_classified = 0.0
        self.number_of_rounds = 0.0

    def init_weights(self):
        weights = []
        for i in range(0,len(SYNSEP_CATEGORY_MAPPING)):
            weights.append([0.0] * self.dict_length)
        return weights

    def update_weights(self, update_matrix):
        for i in range(0,len(self.weights)):
            for j in range(0,len(self.weights[i])):
                self.weights[i][j] += update_matrix[i][j]

    def get_update_matrix(self, feature_vectors, predicted_label, true_label):
        update_matrix = self.init_weights()
        for i in range(0,len(update_matrix)):
            left = 0.0
            right = 0.0
            if true_label == i:
                left = 1.0
            if predicted_label == i:
                right = 1.0
            for j in range(0,len(feature_vectors)):
                update_matrix[i][j] = feature_vectors[j] * (left - right)
        return update_matrix

    def run(self, feature_vectors, true_label):
        self.number_of_rounds += 1.0
        predicted_label = self.predict_label(feature_vectors)
        if true_label == predicted_label:
            self.correct_classified += 1.0
        else:
            self.incorrect_classified += 1.0
        self.error_rate = self.incorrect_classified/self.number_of_rounds
        update_matrix = self.get_update_matrix(feature_vectors, predicted_label, true_label)
        self.update_weights(update_matrix)

    def predict_label(self, feature_vectors):
        max = 0.0
        label = 0
        for i in range(0,len(self.weights)):
            total = 0.0
            for eachVector in range(0,len(feature_vectors)):
                total += feature_vectors[eachVector]*self.weights[i][eachVector]
            if total >= max:
                max = total
                label = i
        return label

def main():
    perceptron = Perceptron()
    synsep = SynSep()
    error_list = list()
    rounds = list()
    total_rounds = 100000
    label_noise = list(range(0, total_rounds))
    label_noise_sample = set(random.sample(label_noise, total_rounds/20))
    for t in range(0,total_rounds):
        feature_vectors, true_label = synsep.generateSynSepData()
        if t in label_noise_sample:
            true_label = random.randint(1,len(SYNSEP_CATEGORY_MAPPING))
        perceptron.run(feature_vectors, true_label-1)
        if ((t+1)%1000) == 0:
            print "%s rounds completed with error rate %s" %(str(t+1),str(perceptron.error_rate))
            rounds.append(perceptron.number_of_rounds)
            error_list.append(perceptron.error_rate)
    mongo_plot = MongoClient('localhost',27017)['aml']['plots']
    mongo_plot.update({'_id':'synnonsep_perceptron'},{'$set':{'timeStamp':datetime.datetime.now(),'rounds':rounds,'error_rate':error_list}},True)
    print "Correctly classified: %s" %str(perceptron.correct_classified)
    print "Incorrectly classified: %s" %str(perceptron.incorrect_classified)
    print "Error Rate: %s" %str(perceptron.error_rate)

if __name__=="__main__":
    main()
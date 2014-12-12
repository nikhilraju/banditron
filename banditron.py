from pymongo import MongoClient
import random

REUTERS_CATEGORY_MAPPING = ['CCAT', 'ECAT', 'MCAT', 'GCAT']
#SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
#SYNNONSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

def get_category_index(label):
    for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
        if label == REUTERS_CATEGORY_MAPPING[i]:
            return i
    return -1

class Banditron:

    def __init__(self):
        self.gamma = 0.05
        self.mongo = MongoClient('localhost',27017)['aml']['features']
        self.dict = self.mongo.find({'_id':'1'})[0]['featureList']
        self.weights = self.init_weights()
        self.error_rate = 0.0
        self.correct_classified = 0.0
        self.incorrect_classified = 0.0
        self.number_of_rounds = 0.0

    def init_weights(self):
        weights = []
        for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
            weights.append([0.0] * len(self.dict))
        return weights

    def update_weights(self, update_matrix):
        for i in range(0,len(self.weights)):
            for j in range(0,len(self.weights[i])):
                self.weights[i][j] += update_matrix[i][j]

    def get_update_matrix(self, feature_vectors, calculated_label, predicted_label, true_label, probabilities):
        update_matrix = self.init_weights()
        for i in range(0,len(update_matrix)):
            left = 0.0
            right = 0.0
            if true_label == predicted_label and predicted_label == i:
                left = 1/probabilities[i]
            if calculated_label == i:
                right = 1.0
            for j in range(0,len(feature_vectors)):
                update_matrix[i][int(feature_vectors[j][0])] = feature_vectors[j][1] * (left - right)
        return update_matrix

    def run(self, doc_id, feature_vectors, true_label):
        self.number_of_rounds += 1.0
        calculated_label = self.predict_label(feature_vectors)
        probabilities = self.calc_probabilities(calculated_label)
        predicted_label = self.random_sample(probabilities)
        if true_label == predicted_label:
            self.correct_classified += 1.0
        else:
            self.incorrect_classified += 1.0
        self.error_rate = self.incorrect_classified/self.number_of_rounds
        update_matrix = self.get_update_matrix(feature_vectors, calculated_label, predicted_label, true_label, probabilities)
        self.update_weights(update_matrix)

    def predict_label(self, feature_vectors):
        max = 0.0
        label = 0
        for i in range(0,len(self.weights)):
            total = 0.0
            for eachVector in feature_vectors:
                total += eachVector[1]*self.weights[i][int(eachVector[0])]
            if total >= max:
                max = total
                label = i
        return label

    def calc_probabilities(self, calculated_label):
        probabilities = [0] * len(self.weights)
        for i in range(0,len(probabilities)):
            probabilities[i] = self.gamma/len(self.weights)
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

def main():
    banditron = Banditron()
    doc_ids = banditron.mongo.find({'_id':'doc'})[0]['docs']
    for t in range(0,len(doc_ids)):
        doc_id = doc_ids[t]
        feature_vectors = banditron.mongo.find({'docId':str(doc_id)})['featureList']
        true_label = get_category_index(banditron.mongo.find({'docId':str(doc_id)})['true_label'])
        banditron.run(doc_id, feature_vectors, true_label)
        if ((t+1)%1000) == 0:
            print "%s rounds completed with error rate %s" %(str(t+1),str(banditron.error_rate))
    print "Correctly classified: %s" %str(banditron.correct_classified)
    print "Incorrectly classified: %s" %str(banditron.incorrect_classified)
    print "Error Rate: %s" %str(banditron.error_rate)

if __name__=="__main__":
    main()

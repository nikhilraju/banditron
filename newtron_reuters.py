from pymongo import MongoClient
import random
from generateSynsep import SynSep
from numpy import matrix
from numpy import linalg
from numpy import inner
from numpy import kron
from numpy import ones
from numpy import float as npfloat
from numpy import dot
from numpy import array
import datetime
import math
import scipy
from scipy import sparse
from scipy.sparse import csr_matrix
from scipy.sparse import kron as sparse_kron
from scipy.sparse.linalg import inv as sparse_inv
#from scipy.sparse.linalg import onenormest as sparse_norm


REUTERS_CATEGORY_MAPPING = ['CCAT', 'ECAT', 'MCAT', 'GCAT']

def get_category_index(label):
    for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
        if label == REUTERS_CATEGORY_MAPPING[i]:
            return i
    return -1

class Newtron:

    def __init__(self):
        self.alpha = 10.0
        self.gamma = 0.05
        self.beta = 0.0001
        self.D = 1.0
        self.mongo = MongoClient('160.39.8.119',27017)['aml']['features']
        self.dict = self.mongo.find({'_id':'1'})[0]['featureList']
        self.dict_length = len(self.dict)
        self.A = self.init_A()
        self.B = self.init_B()
        self.weights = self.init_weights()
        self.k = 1.0
        self.error_rate = 0.0
        self.correct_classified = 0.0
        self.incorrect_classified = 0.0
        self.number_of_rounds = 0.0

    def init_weights(self):
        weights = csr_matrix((len(REUTERS_CATEGORY_MAPPING),self.dict_length),dtype=npfloat)
        return weights

    def init_A(self):
        constant = 1.0/self.D
        indexes = list(range(0,len(REUTERS_CATEGORY_MAPPING)))
        val = []
        for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
            val.append(constant)
        A = sparse.coo_matrix((val,(indexes,indexes)),shape=(len(REUTERS_CATEGORY_MAPPING),len(REUTERS_CATEGORY_MAPPING))).tocsr()
        return A

    def init_B(self):
        B = csr_matrix((len(REUTERS_CATEGORY_MAPPING),self.dict_length),dtype=npfloat)
        return B

    def run(self, feature_sparse, true_label):
        self.number_of_rounds += 1.0
        calculated_label, prediction_weight = self.predict_label(feature_sparse)
        probabilities = self.calc_probabilities(calculated_label)
        predicted_label = self.random_sample(probabilities)
        if true_label == predicted_label:
            self.correct_classified += 1.0
        else:
            self.incorrect_classified += 1.0
        self.error_rate = self.incorrect_classified/self.number_of_rounds
        estimator = self.get_estimator(true_label == predicted_label, predicted_label, feature_sparse, probabilities, prediction_weight)
        self.update_A(estimator)
        self.update_B(estimator)
        self.update_weights()

    def predict_label(self, feature_sparse):
        max = 0.0
        label = 0
        prediction_weight = []
        cumulative_total = 0.0
        feature_vectors_sparse = csr_matrix.transpose(feature_sparse)
        for i in range(0,len(REUTERS_CATEGORY_MAPPING)):
            total = math.exp(self.alpha*csr_matrix.dot(self.weights[i],feature_vectors_sparse).todense().item(0))
            cumulative_total += total
            prediction_weight.append(total)
            if total >= max:
                max = total
                label = i
        prediction_weight = [x/cumulative_total for x in prediction_weight]
        return label, prediction_weight

    def calc_probabilities(self, calculated_label):
        probabilities = [0] * len(REUTERS_CATEGORY_MAPPING)
        for i in range(0,len(probabilities)):
            probabilities[i] = self.gamma/len(REUTERS_CATEGORY_MAPPING)
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

    def get_estimator(self, prediction, predicted_label, feature_sparse, probabilities, prediction_weight):
        a = 1.0/len(REUTERS_CATEGORY_MAPPING)
        unit_vector = [a]*len(REUTERS_CATEGORY_MAPPING)
        e = [0.0]*len(REUTERS_CATEGORY_MAPPING)
        e[predicted_label] = 1.0
        if prediction:
            self.k = probabilities[predicted_label]
            left = (1 - prediction_weight[predicted_label])/probabilities[predicted_label]
            right = matrix([unit_vector[i] - e[i] for i in range(0,len(REUTERS_CATEGORY_MAPPING))])
        else:
            self.k = 1.0
            left = prediction_weight[predicted_label]/probabilities[predicted_label]
            right = matrix([e[i] - unit_vector[i] for i in range(0,len(REUTERS_CATEGORY_MAPPING))])
        estimator = sparse_kron(left*csr_matrix(right.T),feature_sparse)
        return csr_matrix(estimator)

    def update_A(self, estimator):
    	self.A = self.A + ((self.k*self.beta)*(estimator*(csr_matrix.transpose(estimator))))

    def update_B(self, estimator):
        labels = len(REUTERS_CATEGORY_MAPPING)
        self.B = self.B + ((1 - (self.k*self.beta*dot(matrix.flatten(estimator.todense()),matrix.flatten(csr_matrix.transpose(self.weights).todense()).T).item(0)))*estimator)

    def update_weights(self):
   		half_weights = -((sparse_inv(self.A))*self.B)
   		weight_norm = linalg.norm(half_weights.todense())
   		if weight_norm <= self.D:
   			self.weights = half_weights
   		else:
   			self.weights = half_weights/weight_norm


def main():
    newtron = Newtron()
    doc_ids = newtron.mongo.find({'_id': 2})[0]['dataset_list_docIds']
    count = 0
    error_list = list()
    rounds = list()
    for t in range(0,len(doc_ids)):
        doc_id = doc_ids[t]
        feature_vectors = newtron.mongo.find({'docId':str(doc_id)})[0]['featureList']
        true_label = get_category_index(newtron.mongo.find({'docId':str(doc_id)})[0]['true_label'])
        x = [0]*len(feature_vectors)
        y = []
        val = []
        for i in feature_vectors:
            y.append(i[0])
            val.append(i[1])
        feature_sparse = sparse.coo_matrix((val,(x,y)),shape=(1,newtron.dict_length)).tocsr()
        newtron.run(feature_sparse, true_label)
        if ((t+1)%1000) == 0:
            print "%s rounds completed with error rate %s" %(str(t+1),str(newtron.error_rate))
            rounds.append(newtron.number_of_rounds)
            error_list.append(newtron.error_rate)
        count += 1
        if count > 100000:
            break

    mongo_plot = MongoClient('160.39.8.119',27017)['aml']['plots']
    mongo_plot.update({'_id':'reuters_newtron'},{'$set':{'timeStamp':datetime.datetime.now(),'rounds':rounds,'error_rate':error_list}},True)
    print "Correctly classified: %s" %str(newtron.correct_classified)
    print "Incorrectly classified: %s" %str(newtron.incorrect_classified)
    print "Error Rate: %s" %str(newtron.error_rate)

if __name__=="__main__":
    main()

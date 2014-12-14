from pymongo import MongoClient
import random
import datetime

SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

class SynSep:

	def __init__(self):
		self.mongo = MongoClient('localhost',27017)['aml']['synsep']
		self.noOfFeatures = 400
		self.rareWords = self.init_words(0, 120)
		self.commonWords = self.init_words(len(self.rareWords), self.noOfFeatures)

	def init_words(self, min, max):
		word_list = list()
		for i in range(min, max):
			word_list.append(i)
		return word_list

	def createLabel(self):
		for i in range(0, len(SYNSEP_CATEGORY_MAPPING)):
			label_vectors = [0]*self.noOfFeatures
			turned_on_bits = random.randint(20,40)
			random_sample = random.sample(self.rareWords, turned_on_bits)
			for j in range(0, len(self.rareWords)):
				if j in random_sample:
					label_vectors[j] = 1
			self.mongo.update({'_id':SYNSEP_CATEGORY_MAPPING[i]},{'$set':{'timeStamp':datetime.datetime.now(),'featureList':label_vectors,'bitson':random_sample}},True)

	def generateSynSepData(self):
		random_vector = random.randint(1,len(SYNSEP_CATEGORY_MAPPING))
		featureVector = self.mongo.find({'_id':str(random_vector)})[0]['featureList']
		turned_on_bits = self.mongo.find({'_id':str(random_vector)})[0]['bitson']
		bits_to_turn_off = random.sample(turned_on_bits, 5)
		for i in range(0, len(self.rareWords)):
			if i in bits_to_turn_off:
				featureVector[i] = 0
		random_sample = random.sample(self.commonWords, 20)
		for i in range(len(self.rareWords), self.noOfFeatures):
			if i in random_sample:
				featureVector[i] = 1
		return featureVector, random_vector

	#def generateSynNonSepData(self):
	#	featureVector, random_vector = self.generateSynSepData()
	#	if(random.randint(0,99) < 5):
	#		random_vector = random.randint(1,9)
	#	return featureVector, random_vector

def main():
	synsep = SynSep()
	synsep.createLabel()

if __name__=="__main__":
	main()

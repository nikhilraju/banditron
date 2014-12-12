from pymongo import MongoClient
import random
import datetime

SYNSEP_CATEGORY_MAPPING = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

class SynSep:

	def __init__(self):
		self.mongo = MongoClient('localhost',27017)['aml']['synsep']
		self.noOfFeatures = 400
		self.rareWords = 120
		self.commonWords = self.noOfFeatures - self.rareWords


	def createLabel(self):
		for i in range(0, len(SYNSEP_CATEGORY_MAPPING)):
			label_vectors = [0]*self.noOfFeatures
			turned_on_bits = random.randint(20,40)
			count = 0
			for j in range(0, self.rareWords):
				if(random.randint(0,self.rareWords-1) < turned_on_bits):
					label_vectors[j] = 1
					count += 1
			self.mongo.update({'_id':SYNSEP_CATEGORY_MAPPING[i]},{'$set':{'timeStamp':datetime.datetime.now(),'featureList':label_vectors,'bitson':count}},True)

	def generateSynSepData(self):
		random_vector = random.randint(1,len(SYNSEP_CATEGORY_MAPPING))
		featureVector = self.mongo.find({'_id':str(random_vector)})[0]['featureList']
		turned_on_bits = self.mongo.find({'_id':str(random_vector)})[0]['bitson']
		for i in range(0, self.rareWords):
			if featureVector[i] == 1:
				if(random.randint(0,turned_on_bits-1) < 5):
					featureVector[i] = 0
		for i in range(self.rareWords, self.noOfFeatures):
			if(random.randint(0,self.commonWords-1) < 20):
				featureVector[i] = 1
		return featureVector, random_vector

	def generateSynNonSepData(self):
		featureVector = self.generateSynSepData
		#introduce a 5% label noise

def main():
	synsep = SynSep()
	synsep.createLabel()
	#print synsep.generateSynSepData()

if __name__=="__main__":
	main()
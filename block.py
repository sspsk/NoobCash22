from Crypto.Hash import SHA
import json, datetime




class Block:
	def __init__(self,prev_hash,last_index,capacity):
		##set

		self.index = last_index + 1
		self.timestamp = datetime.datetime.now()
		self.hash = None
		self.previousHash = prev_hash
		self.nonce = None
		self.listOfTransactions = [] #must be of size = capacity
		self.capacity = capacity
	
	def make_hash(self):
		h = SHA.new(json.dumps(self.block_to_dict(),sort_keys=True).encode()).hexdigest()
		self.hash = h 
		return h

	def block_to_dict(self, include_nonce = True):
		temp = {'index':self.index,
				'timestamp':str(self.timestamp),
				'previousHash':self.previousHash,
				'nonce':self.nonce,
				'transactions':self.listOfTransactions}
		return temp


	def add_transaction(self,transaction):
		self.listOfTransactions.append(transaction)


	#getters & setters
	def get_hash(self):
		return self.hash

	def get_nonce(self):
		return self.nonce 

	def set_nonce(self,nonce):
		self.nonce = nonce 
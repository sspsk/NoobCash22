from Crypto.Hash import SHA
import json, datetime
from transaction import * 




class Block:
	def __init__(self,last_block,is_genesis=False,data=None):


		if data is not None:
			self.index = data['index']
			self.previousHash = data['previousHash']
			self.timestamp = data['timestamp']
			self.nonce = data['nonce']
			self.hash = None
			self.listOfTransactions = [Transaction(None,None,None,None,None,json.loads(d)) for d in data['transactions']]



		else:
			if is_genesis:
				self.index = 0
				self.previousHash = 1
			else:
				self.index = last_block.get_index() + 1
				self.previousHash = last_block.get_hash()

			self.timestamp = str(datetime.datetime.now())
			self.hash = None
			
			self.nonce = None
			self.listOfTransactions = [] #must be of size = capacity
	
	def make_hash(self):
		h = SHA.new(json.dumps(self.block_to_dict(),sort_keys=True).encode()).hexdigest()
		self.hash = h 
		return h

	def block_to_dict(self):
		temp = {'index':self.index,
				'timestamp':self.timestamp,
				'previousHash':self.previousHash,
				'nonce':self.nonce,
				'transactions':[t.jsonify_transaction() for t in self.listOfTransactions]}
		return temp


	
	def add_transaction(self,transaction):
		self.listOfTransactions.append(transaction)


	def validate_block(self,last_block,difficulty):
		# 1) check that current hash is correct
		# 2) check that prev_hash = hash of last_block
		h = self.make_hash()
		prefix = '0'*difficulty
		if not h.startswith(prefix):
			return 1
		if last_block.get_hash() != self.previousHash:
			return 2
		return 0
		


	#getters & setters
	def get_hash(self):
		return self.hash

	def get_nonce(self):
		return self.nonce 

	def set_nonce(self,nonce):
		self.nonce = nonce 

	def get_index(self):
		return self.index
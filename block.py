from Crypto.Hash import SHA
import json, datetime




class Block:
	def __init__(self,last_block,capacity,is_genesis=False):
		##set

		self.index = last_block.get_index() + 1
		self.timestamp = datetime.datetime.now()
		self.hash = None
		self.previousHash = last_block.get_hash()
		self.nonce = None
		self.listOfTransactions = [] #must be of size = capacity
		self.capacity = capacity
		self.is_genesis = is_genesis
	
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
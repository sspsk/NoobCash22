from copy import deepcopy
import requests
import time
from threading import Lock


from block import Block
from wallet import Wallet 
from transaction import *
import config


class Node:
	def __init__(self,ip,port,bootstrap_ip,bootstrap_port):

		##set
		self.id = None
		self.ip = ip
		self.port = port 
		self.bootstrap_ip = bootstrap_ip
		self.bootstrap_port = bootstrap_port

		if self.ip == self.bootstrap_ip and self.port == self.bootstrap_port:
			self.id = 0
			self.node_counter = 0


		#the blockchain
		self.chain = []

		#fifo queue with transactions to be inserted into blocks
		self.transaction_pool = []

		#info about nodes
		self.ring = {}

		#utxos
		self.utxos = {}

		#temporary utxos list for reverting, always work on this
		self.temp_utxos = {}

		#wallet of node
		self.wallet = self.create_wallet()
		
		#reference to current block
		self.curr_block = None

		#flag to raise if a new block arrived
		self.block_received = False

		#reference to the block that arrived
		self.new_block = None

		#creating transction lock
		self.lock = Lock()


		#config parameters
		self.difficulty = config.difficulty
		self.capacity = config.capacity
		self.n_nodes = config.n_nodes




	def add_node(self,node):
		pubkey = node['pubkey']
		ip = node['ip']
		port = node['port']

		self.node_counter += 1

		self.ring[pubkey] = {'ip':ip,
							'port':port,
							'id':self.node_counter}

		self.utxos[pubkey] = []

		#if all nodes connected inform them
		if self.node_counter == self.n_nodes-1:

			for key in self.ring:

				if key == self.wallet.get_pubaddress(): #dont send the info on self(bootstrap node)
					continue
				ip = self.ring[key]['ip']
				port = self.ring[key]['port']

				data = json.dumps(self.ring)
				r = requests.post('http://{0}:{1}/info'.format(ip,port),data=data)
				

			self.create_genesis()


	def create_genesis(self):
		block = Block(None,True)
		for key in self.ring:
			t = Transaction(None,key,100,None,True)
			block.add_transaction(t)
		block.set_nonce(0)
		data = json.dumps(block.block_to_dict())
		for key in self.ring:
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']
			nid = self.ring[key]['id']
			r = requests.post('http://{0}:{1}/receive_genesis'.format(ip,port),data=data)
			

	def receive_genesis(self,block):
		chain = [block]
		flag = self.validate_chain(chain)
		self.create_new_block(self.chain[-1])
		return flag







	def create_new_block(self,last_block,is_genesis=False):
		self.curr_block = Block(last_block,is_genesis)
		#create a new copy of utxos
		self.temp_utxos = {}
		for key in self.ring:
			self.temp_utxos[key] = deepcopy(self.utxos[key])
		return self.curr_block


	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		wallet = Wallet()
		pub_address = wallet.get_pubaddress()
		self.ring[pub_address] = {'ip':self.ip,
								'port':self.port,
								'id':self.id}
		self.utxos[pub_address] = []
		self.temp_utxos[pub_address] = []
		return wallet

	def commit_utxos(self,temp_utxos):
		'''
		method for updating utxos with temp_utxos
		'''
		for key in temp_utxos:
			self.utxos[key] = temp_utxos[key]



	def create_transaction(self,receiver_address,amount,is_genesis=False):
		# receiver_address must be hex
		#we traverse our utxos to find funds
		sender_pubkey = self.wallet.get_pubaddress()
		sender_utxos = self.temp_utxos[sender_pubkey] #maybe sort them with amount ----- maybe we should change it with temp_utxos

		utxos_list = [] #temp list containing the neccesarry utxos
		funds = 0
		for utxo in sender_utxos:
			funds += utxo.get_amount() 
			utxos_list.append(utxo) 
			if funds >= amount:
				break

		if funds < amount: #we traversed the whole list and still not enough funds
			print('Not enough funds')
			return None

		t = Transaction(self.wallet,receiver_address,amount,utxos_list,is_genesis)
		return t
		



	def broadcast_transaction(self,transaction):
		data = transaction.jsonify_transaction()
		for key in self.ring:
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']

			res = requests.post('http://{0}:{1}/receive_transaction'.format(ip,port),data=data)
			


	def process_transaction(self,transaction,utxos_dict):
		'''
		Input: a transaction and a dictionary 
		with key: a public_key and value: a list of utxos
		like self.temp_utxos
		'''
		sender = transaction.get_sender()

		if transaction.sender_address == 0 or transaction.validate_transaction(RSA.importKey(binascii.unhexlify(sender)),utxos_dict[sender]):
			trans_outputs = transaction.get_transaction_outputs()
			for to in trans_outputs:
				utxos_dict[to.get_receiver()].append(to)

			return True
		else:
			return False



	

	def add_transaction_to_pool(self,transaction):
		self.transaction_pool.append(transaction)



	def get_transaction_from_pool(self):
		#get transaction from pool,validate, add to current block,update temp_utxos -----instead of receive_transaction
		transaction = self.transaction_pool.pop(0)
		print(transaction.transaction_inputs[0].get_id())
		res = self.process_transaction(transaction,self.temp_utxos)
		if res:
			self.curr_block.add_transaction(transaction)
			return True
		else:
			return False


	
	def mine_block(self):
		#mine the current block
		nonce = 0
		prefix = '0'*self.difficulty
		solved = False

		while not self.block_received:
			self.curr_block.set_nonce(nonce)
			h = self.curr_block.make_hash()

			if h.startswith(prefix):
				solved = True
				print("Block mined: ",h)
				break

			nonce += 1

		if not solved: #a block was received
			return -1
		else:
			return 0


	def broadcast_block(self):
		data = self.curr_block.block_to_dict()
		data = json.dumps(data)
		for key in self.ring:
			if key == self.wallet.get_pubaddress():
				continue
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']

			res = requests.post('http://{0}:{1}/receive_block'.format(ip,port),data=data)

	def validate_chain(self, chain):
		#validate and execute the transactions of the chain

		#start with zero balance for every one
		self.chain = []
		temp_utxos = {}
		for key in self.ring:
			temp_utxos[key] = []

		last_block = None
		for block in chain:
			if block.index == 0 or block.validate_block(last_block,self.difficulty)==0:

				if block.index == 0: #even if its not validated, make hash to check the next block
					block.make_hash()


				for tx in block.listOfTransactions:
					res = self.process_transaction(tx,temp_utxos)
					if not res:
						return -1 # a transaction failed of a block failed
				last_block = block
				self.chain.append(block)
			else:
				
				return -2 # a block verification failed

		#update the permanent utxos
		self.commit_utxos(temp_utxos)

		return 0





	def resolve_conflicts(self):
		#resolve correct chain
		#ask for length from the broadcaster

		max_len = -1
		max_key = None
		for key in self.ring:
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']
			res = requests.get('http://{0}:{1}/chain_length'.format(ip,port))
			length = res.json()['length']
			if length > max_len:
				max_key = key
				max_len = length

		if max_len <= len(self.chain):
			print("new chain not adopted")
			return -1

		max_ip = self.ring[max_key]['ip']
		max_port = self.ring[max_key]['port']



		res = requests.get('http://{0}:{1}/chain'.format(max_ip,max_port))
		data = res.json()

		j_chain = data['chain']

		chain = [Block(None,None,data) for data in j_chain]

		flag = self.validate_chain(chain)
		return flag


	def remove_from_pool(self,transactions_list):

		seen = set()
		for t in transactions_list:
			seen.add(t.make_hash().hexdigest())
			
		
		temp_pool = []

		for t in self.transaction_pool:
			if t.make_hash().hexdigest() not in seen:
				temp_pool.append(t)

		self.transaction_pool = temp_pool



	def receive_block(self): 
		last_block = self.chain[-1]
		block = self.new_block
		validated = block.validate_block(last_block,self.difficulty)

		if validated == 0:
			#put unmined transactions back to pool
			
			for tx in self.curr_block.listOfTransactions:
				self.transaction_pool.insert(0,tx)

			#remove duplicates between mined and unmined transactions
			self.remove_from_pool(block.listOfTransactions)

			#execute the transactions with the clean ledger, while checking for errors
			for tx in block.listOfTransactions:

				done = self.process_transaction(tx,self.utxos)
				if not done:
					return -1
			self.chain.append(self.new_block)

		else:
			self.resolve_conflicts()

		self.block_received = False


	


	#this is abstract, needs checking
	def mining_loop(self):
		# self.create_new_block(self.chain[-1])
		while True:
			if not self.block_received:
				if len(self.curr_block.listOfTransactions) == self.capacity:
					print("DAEMON:starting mining..")
					res = self.mine_block()
					if res == 0:
						self.chain.append(self.curr_block)
						self.broadcast_block()
						#update utxos with temp_utxos
						self.commit_utxos(self.temp_utxos)
					else:
						print("DAEMON:new block received-inloop")
						self.receive_block()
					#create new block
					self.create_new_block(self.chain[-1])
				elif len(self.transaction_pool) > 0:
					flag = self.get_transaction_from_pool()
					print("DAEMON:added new transaction to current block. Passed check: ",flag)

			else:
				print("DAEMON:new block received-outloop")
				self.receive_block()
				#create new block
				self.create_new_block(self.chain[-1])

			time.sleep(0.0001)
			






	


	




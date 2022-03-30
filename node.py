from block import Block
from wallet import Wallet 
from transaction import *
import config
from copy import deepcopy

class Node:
	def __init__(ip,port,bootstrap_ip,bootstrap_port):

		##set
		self.id = None
		self.ip = ip
		self.port = port 
		self.bootstrap_ip = bootstrap_ip
		self.bootstrap_port = bootstrap_port

		if self.ip == self.bootstrap_ip:
			self.node_counter = 0

		self.wallet = None 

		#the blockchain
		self.chain = []

		#fifo queue with transactions to be inserted into blocks
		self.transaction_pool = []

		#info about nodes
		self.ring = {}

		#temporary utxos list for reverting, always work on this
		self.temp_utxos = {}
		
		#reference to current block
		self.curr_block = None

		#flag to raise if a new block arrived
		self.block_received = False

		#reference to the block that arrived
		self.new_block = None


		#config parameters
		self.difficulty = config.difficulty
		self.capacity = config.capacity




	def add_node(self,node):
		pubkey = node['pubkey']
		ip = node['ip']
		port = node['port']

		self.node_counter += 1

		self.ring[pubkey] = {'ip':ip,
							'port':port,
							'id':self.node_counter,
							'utxos':[]}

		#if all nodes connected inform them
		if self.node_counter == 9:
			for key in self.ring:
				if self.ring[key]['ip'] == self.ip:
					continue
				ip = self.ring[key]['ip']
				port = self.ring[key]['port']

				data = json.dumps(self.ring)
				r = requests.post('http://{0}:{1}/info',data=data)

			self.create_genesis()


	def create_genesis(self):
		block = Block(None,True)
		for key in self.ring:
			t = Transaction(None,key,100,None,True)
			block.add_transaction(t)
		data = json.dumps(block.block_to_dict())
		for key in self.ring:
			r = requests.post('http://{0}:{1}/receive_genesis')

	def receive_genesis(self,block):
		self.chain.append(block)
		for tx in block.listOfTransactions:
			self.ring[tx.get_receiver]['utxos'].append(TransactionOutput(tx.get_receiver(),tx.amount))






	def create_new_block(self,last_block,is_genesis):
		self.curr_block = Block(last_block,is_genesis)
		#create a new copy of utxos
		self.temp_utxos = {}
		for key in self.ring:
			self.temp_utxos[key] = deepcopy(self.ring[key]['utxos'])
		return self.curr_block


	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		self.wallet = Wallet()
		pub_address = self.wallet.get_pubaddress()
		self.ring[pub_address] = {'ip':self.ip,
								'port':self.port,
								'id':self.id,
								'utxos': []}
		self.temp_utxos[pub_address] = []

	def commit_utxos(self,temp_utxos):
		'''
		method for updating utxos with temp_utxos
		'''
		for key in temp_utxos:
			self.ring[key]['utxos'] = temp_utxos[key]



	def create_transaction(self,receiver_address,amount,is_genesis):
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
			if self.ring[key]['ip'] == self.ip:
				continue
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']

			res = requests.post('http://{0}:{1}/receive_transaction'.format(ip,port),data=data)
			


	def process_transaction(transaction,utxos_dict):
		'''
		Input: a transaction and a dictionary 
		with key: a public_key and value: a list of utxos
		like self.temp_utxos
		'''
		sender = transaction.get_sender()
		receiver = transaction.get_receiver()

		sender_utxos = utxos_dict[sender]
		unhex_sender = RSA.importKey(binascii.unhexlify(sender)) #must be RSA key, not hex
		if transaction.validate_transaction(unhex_sender,sender_utxos):
			trans_outputs = transaction.get_transaction_outputs()
			utxos_dict[receiver].append(trans_outputs[0])
			utxos_dict[sender].append(trans_outputs[1])
			return True
		else:
			return False



	

	def add_transaction_to_pool(self,transaction):
		self.transaction_pool.append(transaction)



	def get_transaction_from_pool(self):
		#get transaction from pool,validate, add to current block,update temp_utxos -----instead of receive_transaction
		transaction = self.pool.pop(0)

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
				break

			nonce += 1

		if not solved: #a block was received
			return -1
		else:
			return 0


	def broadcast_block(self):
		data = self.curr_block.block_to_dict()
		for key in self.ring:
			if self.ring[key]['ip'] == self.ip:
				continue
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']

			res = requests.post('http://{0}:{1}/receive_block'.format(ip,port),data=data)

	def validate_chain(self, chain):
		#validate and execute the transactions of the chain

		#start with zero balance for every one
		temp_utxos = {}
		for key in self.ring:
			temp_utxos[key] = []

		last_block = None
		for block in chain:
			if block.index == 0 or block.validate_block(last_block,self.difficulty):
				for tx in block.listOfTransactions:
					res = self.process_transaction(tx,temp_utxos)
					if not res:
						return -1 # a transaction failed of a block failed
			else:
				return -2 # a block verification failed

		#update the permanent utxos
		self.commit_utxos(temp_utxos)

		return 0





	def resolve_conflicts(self):
		#resolve correct chain
		#ask for length from the broadcaster

		max_len = -1
		max_key
		for key in self.ring:
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']
			res = requests.get('http://{0}:{1}/chain_length')
			length = res.json()['length']
			if length > max_len:
				max_key = key

		max_ip = self.ring[max_key]['ip']
		max_port = self.ring[max_key]['port']

		res = requests.get('http://{0}:{1}/chain')
		data = res.json()

		j_chain = data['chain']

		chain = [Block(None,None,data) for data in j_chain]

		self.validate_chain(chain)


	def remove_from_pool(self,transactions_list):
		seen = set()
		for t in transactions_list:
			seen.add(t.get_hash().digest())

		for t in self.pool:
			if t.get_hash().digest() in seen:
				self.pool.remove(t)



	def receive_block(self): 
		last_block = self.chain[-1]
		block = self.new_block
		validated = block.validate_block(last_block,self.difficulty)

		if validated:
			#put unmined transactions back to pool
			for tx in self.curr_block.listOfTransactions:
				self.pool.insert(0,tx)

			#remove duplicates between mined and unmined transactions
			self.remove_from_pool(block.listOfTransactions)

			#execute the transactions with the clean ledger, while checking for errors
			for tx in block.listOfTransactions:

				sender = tx.get_sender() #hex address of sender pubkey
				receiver = tx.get_receiver() #hex address of receiver pubkey
				sender_utxos = self.ring[sender]['utxos']
				unhex_sender = RSA.importKey(binascii.unhexlify(sender)) #must be RSA key, not hex

				if tx.validate_transaction(unhex_sender,sender_utxos):  #real utxos this time
					tx_outputs = tx.get_transaction_outputs()
					self.ring[receiver]['utxos'].append(tx_outputs[0])
					self.ring[sender]['utxos'].append(tx_outputs[1])
				else:
					return -1
			self.chain.append(self.new_block)
			return 0

		else:
			self.resolve_conflicts()


	


	#this is abstract, needs checking
	def mining_loop(self):
		# self.create_new_block(self.chain[-1])
		while True:
			if not self.block_received:
				if len(self.curr_block.listOfTransactions) == self.capacity:
					res = self.mine_block()
					if res == 0:
						self.chain.append(self.curr_block)
						self.broadcast_block()
						#update utxos with temp_utxos
						self.commit_utxos(self.temp_utxos)
					else:
						self.receive_block()
					#create new block
					self.create_new_block(self.chain[-1])
				elif len(self.pool) > 0:
					self.get_transaction_from_pool()
			else:
				self.receive_block()
				#create new block
				self.create_new_block(self.chain[-1])
			time.sleep(0.1)






	


	




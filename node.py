from block import Block
from wallet import Wallet 
from transaction import Transaction
import config

class Node:
	def __init__(ip,):

		##set
		self.id = None
		self.ip = ip
		self.port = port 
		self.bootstrap_ip = bootstrap_ip
		self.bootstrap_port = bootstrap_port

		if self.ip == self.bootstrap_ip:
			self.node_counter = 0

		self.wallet = None 

		self.chain = []

		self.transaction_pool = []

		self.ring = None
		
		# self.curr_block = None









	def create_new_block(self,last_block,is_genesis):
		return Block(last_block,config.capacity,is_genesis)


	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		self.wallet = Wallet()
		self.ring[self.wallet.get_pubaddress()] = {'ip':self.ip,
													'port':self.port,
													'id':self.id,
													'utxos': []}

	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs


	def create_transaction(self,receiver_address,amount,is_genesis):
		# receiver_address must be hex
		#we traverse our utxos to find funds
		sender_pubkey = self.wallet.get_pubaddress()
		sender_utxos = self.ring[sender_pubkey]  #maybe sort them with amount

		utxos_list = [] #temp list containing the neccesarry utxos
		funds = 0
		for utxo in sender_utxos:
			funds += utxo.get_amount() 
			utxos_list.append(utxo) 
			sender_utxos.remove(utxo) #remove the utxo from sender
			if funds >= amount:
				break

		if funds < amount: #we traversed the whole list and still not enough funds
			print('Not enough funds')
			sender_utxos = utxos_list #restore the funds back to sender
			return None

		t = Transaction(self.wallet,receiver_address,amount,utxos_list,is_genesis)
		return t
		



	def broadcast_transaction(self,transaction):
		for key in self.ring:
			if self.ring[key]['ip'] == self.ip:
				continue
			ip = self.ring[key]['ip']
			port = self.ring[key]['port']
			#send transaction to this address + url





	def receive_transaction(self,transaction):
		sender = transaction.get_sender() #hex address of sender pubkey
		sender_utxos = self.ring[sender]['utxos']

		unhex_sender = RSA.importKey(binascii.unhexlify(sender)) #must be RSA key, not hex
		if transaction.validate_transaction(unhex_sender,sender_utxos):
			trans_outputs = transaction.get_transaction_outputs()
			receiver = transaction.get_receiver() #hex address of receiver
			for out_tx in trans_outputs:
				self.ring[receiver]['utxos'].append(out_tx)
			return True
		else:
			return False


		


	def add_transaction_to_pool(self,transaction):
		#add every transaction
		self.transaction_pool.append(transaction)





	def mine_block():



	def broadcast_block():


		

	def valid_proof(.., difficulty=MINING_DIFFICULTY):




	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes


	def resolve_conflicts(self):
		#resolve correct chain




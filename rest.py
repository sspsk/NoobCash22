import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time,json


import block
import node
import wallet
import transaction
import wallet
import config


### JUST A BASIC EXAMPLE OF A REST API WITH FLASK



app = Flask(__name__)
CORS(app)
node = None



#.......................................................................................



# get all transactions in the blockchain

@app.route('/receive_transaction', methods=['POST'])
def get_transactions():
    
    data = requests.get_json(force=True)
    transaction = transaction.Transaction(None,None,None,None,None,data)
    node.add_transaction_to_pool(transaction)
    return jsonify(status='ok')


@app.route('create_transaction',methods=['POST'])
def create_transaction():
    data = request.get_json(force=True)

    #get pubkey from id
    receiver_address = None
    for key in node.ring:
        if node.ring[key]['id'] == data['id']:
            receiver_address = key
            break

    amount = data['amount']
    t = node.create_transaction(receiver_address,amount)
    node.add_transaction_to_pool(t)
    node.broadcast_transaction(t)
    return jsonify(status='ok')


@app.route('/receive_block',methods=['POST'])
def receive_block():
    data = request.get_json(force=True)

    #create python object from block
    new_block = Block(None,None,data)

    #set flag true and point reference to object
    node.block_received = True
    node.new_block = new_block
    return jsonify(status='ok')


@app.route('/chain_length')
def chain_length():
    return jsonify(length = len(node.chain))    


@app.route('/chain')
def chain():
    j_chain = [b.to_dict() for b in node.chain]
    return jsonify(chain=j_chain)


#-------------bootstrap-------------

@app.route('/add_to_ring',methods=['POST'])
def add_to_ring():
    data = request.get_json(force=True)
    node.add_node(data)
    return jsonify(status='ok')




 #----------clients-------------
@app.route('/register')
def register():
    data = {'pubkey':node.wallet.get_pubaddress(),
            'ip':node.ip,
            'port':node.port}
    data = json.dumps(data)
    r = requests.post('http://{0}:{1}/add_to_ring'.format(node.ip,node.port),data=data)


@app.route('/info')
def get_info():
    data = request.get_json()
    node.ring = data
    return jsonify(status='ok')


@app.route('/receive_genesis')
def receive_genesis():
    data = request.get_json(force=True)
    block = Block(None,None.data)
    node.receive_genesis(block)
    return jsonify(status='ok')


#--------auxiliary endpoints------

@app.route('/get_ring')
def get_ring():
    return jsonify(data=node.ring)




#-----cli------------

@app.route('/last_block')
def last_block():
    return jsonify(data=node.chain[-1].block_to_dict())


@app.route('/get_balance')
def get_balance():
    mypubkey = self.wallet.get_pubaddress()
    data = self.wallet.get_balance(self.ring[mypubkey]['utxos'])
    return jsonify(data=data)


#---------------------

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    local_ip = None
    node = Node(local_ip,port)    
    app.run(host='127.0.0.1', port=port)

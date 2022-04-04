import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import time,json


from block import Block
from node import Node
import wallet
import transaction
import wallet
import config






app = Flask(__name__)
CORS(app)
node = None



#.......................................................................................



# get all transactions in the blockchain

@app.route('/receive_transaction', methods=['POST'])
def get_transactions():
    
    data = request.get_json(force=True)
    tx= transaction.Transaction(None,None,None,None,None,data)
    node.add_transaction_to_pool(tx)
    return jsonify(status='ok')


@app.route('/create_transaction',methods=['POST'])
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
    if t is None:
        return jsonify(status="not enough funds")
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
    j_chain = [b.block_to_dict() for b in node.chain]
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
    r = requests.post('http://{0}:{1}/add_to_ring'.format(node.bootstrap_ip,node.bootstrap_port),data=data)
    return jsonify(status='ok')


@app.route('/info',methods=['POST'])
def get_info():
    data = request.get_json(force=True)
    node.ring = data
    for key in node.ring:
        if key not in node.utxos:
            node.utxos[key] = []
    return jsonify(status='ok')


@app.route('/receive_genesis',methods=['POST'])
def receive_genesis():
    data = request.get_json(force=True)
    block = Block(None,None,data)
    flag = node.receive_genesis(block)
    return jsonify(status=flag)


#--------testing endpoints------

@app.route('/get_ring')
def get_ring():
    return jsonify(data=node.ring)

@app.route('/get_utxos')
def get_utxos():
    temp = {}
    for key in node.utxos:
        temp[key] = [to.to_dict() for to in node.utxos[key]]
    return jsonify(temp)

@app.route('/get_temp_utxos')
def get_temp_utxos():
    temp = {}
    for key in node.temp_utxos:
        temp[key] = [to.to_dict() for to in node.utxos[key]]
    return jsonify(temp)


@app.route('/get_pool')
def get_pool():
    temp = []
    for tx in node.transaction_pool:
        temp.append(tx.jsonify_transaction())
    return jsonify(temp)

@app.route('/get_from_pool')
def get_from_pool():
    node.get_transaction_from_pool()
    return jsonify(status="ok")

@app.route('/mine_block')
def mine_block():
    flag = node.mine_block()
    if flag == -1:
        return jsonify(status='block received')
    node.chain.append(node.curr_block)
    node.broadcast_block()
    node.commit_utxos(node.temp_utxos)
    node.create_new_block(node.chain[-1])
    return jsonify(status='ok')

@app.route('/get_curr_block')
def get_curr_block():
    return jsonify(node.curr_block.block_to_dict())

@app.route('/get_new_block')
def get_new_block():
    if node.new_block is not None:
        return jsonify(node.new_block.block_to_dict())
    else:
        return jsonify(data='no new block')

@app.route('/process_new_block')
def process_new_block():
    node.receive_block()
    node.create_new_block(node.chain[-1])
    return jsonify(status='ok')

@app.route('/get_flag')
def get_flag():
    return jsonify(node.block_received)


#-----cli------------

@app.route('/last_block')
def last_block():

    return jsonify(data=node.chain[-1].block_to_dict())


@app.route('/get_balance')
def get_balance():
    mypubkey = node.wallet.get_pubaddress()
    data = node.wallet.balance(node.utxos[mypubkey])
    return jsonify(data=data)


#---------------------

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help='port to listen on')
    parser.add_argument('-i', '--ip', type=str, help='ip address')
    parser.add_argument('-bp', '--bootstrap_port', type=int, help='port of bootstrap node')
    parser.add_argument('-bi', '--bootstrap_ip', type=str, help='ip address of bootstrap node')

    args = parser.parse_args()
    port = args.port
    ip = args.ip
    bport = args.bootstrap_port
    bip = args.bootstrap_ip

    
    node = Node(ip,port,bip,bport)    
    app.run(host=ip, port=port,debug=True)

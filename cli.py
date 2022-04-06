import argparse
import requests
import json


def ip_port_from_id(nid,data):
        for key in data:
                if data[key]['id'] == nid:
                        return data[key]['ip'],data[key]['port']


ch = {'t':'t','view':'view', 'help':'help', 'balance':'balance'}


def create_transaction(sender, receiver, amount,data):
        dictionary = {'id' : int(receiver),'amount' : int(amount)}
        body = json.dumps(dictionary)
        ip,port = ip_port_from_id(int(sender),data)
        res = requests.post('http://{0}:{1}/create_transaction'.format(ip,port),data = body)
        print(res.json()['status'])
       
        
def view_transactions(nid,data):
        ip,port = ip_port_from_id(int(nid),data)
        res = requests.get('http://{0}:{1}/last_block'.format(ip,port))
        j_data = res.json()['data']

        for tx in j_data['transactions']:
                tx_data = json.loads(tx)
                print(data[tx_data['sender_address']]['id'],data[tx_data['receiver_address']]['id'],tx_data['amount'])
       

def balance(nid,data):
        ip,port = ip_port_from_id(int(nid),data)
        res = requests.get('http://{0}:{1}/get_balance'.format(ip,port))
        data = res.json()['data']
        print("Balance:",data)


def console(arg):
        print("------------ CLI ---------------")

       
        #get info about nodes
        bootstrap_ip = '127.0.0.1'
        bootstrap_port = 5000
        r = requests.get('http://{0}:{1}/get_ring'.format(bootstrap_ip,bootstrap_port))
        data = r.json()['data']

        print(arg['command'])
        if (arg['command'] == 't'):
                if (len(arg['values']) == 3):
                        sender = arg['values'][0]
                        receiver = arg['values'][1]
                        amount = arg['values'][2]
                        create_transaction(sender, receiver, amount,data)
                else:
                        print("I need 2 values")
        elif arg['command'] == 'view':
                if (len(arg['values']) == 0):
                        id = arg['myid'][0]
                        view_transactions(id,data)
                else:
                        print("Remove arguments and try again")
        elif(arg['command'] == 'balance'):
                if (len(arg['values']) == 0):
                        id = arg['myid'][0]
                        balance(id,data)
                else:
                        print("Remove arguments and try again")
        elif(arg['command'] == 'help'):
                if (len(arg['values']) == 0):
                        print(" command t: USAGE: t sender_id receiver_id amount\n",
                                "command view: see last transactions of the latest validated block\n",
                                "command balance: see balance of specified wallet\n",
                        "command help: explanation of commands")
                else:
                        print("Remove arguments and try again")
        return





transaction = argparse.ArgumentParser()
transaction.add_argument('--myid')
transaction.add_argument('command', choices=ch.keys())
transaction.add_argument('values', nargs='*')
args = vars(transaction.parse_args())

console(args)

# print(args)

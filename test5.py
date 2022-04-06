import requests
import json
from threading import Thread
import time



def create_transaction(sender,nid,amount):
	data  = {}
	data['id'] = nid 
	data['amount'] = amount
	res = requests.post('http://{0}/create_transaction'.format(sender),data=json.dumps(data))



def exec_transactions(sender,filename):
	with open(filename,'r') as f:
		for line in f:
			nid,amount = line.split(" ")
			nid = int(nid[2])
			amount = int(amount)
			create_transaction(sender,nid,amount)
			time.sleep(0.1)

if __name__=="__main__":

	#put the right ips

	res = requests.get('http://127.0.0.1:5001/register') #gets node id 1
	res = requests.get('http://127.0.0.1:5002/register') #gets node id 2
	res = requests.get('http://127.0.0.1:5003/register') #gets node id 3
	res = requests.get('http://127.0.0.1:5004/register') #gets node id 4
 
    #-------------everyone has 100 coins--------------------------------


	t0 = Thread(target=exec_transactions,args=('127.0.0.1:5000','5nodes/transactions0.txt'))
	t1 = Thread(target=exec_transactions,args=('127.0.0.1:5001','5nodes/transactions1.txt'))
	t2 = Thread(target=exec_transactions,args=('127.0.0.1:5002','5nodes/transactions2.txt'))
	t3 = Thread(target=exec_transactions,args=('127.0.0.1:5003','5nodes/transactions3.txt'))
	t4 = Thread(target=exec_transactions,args=('127.0.0.1:5004','5nodes/transactions4.txt'))

	t0.start()
	t1.start()
	t2.start()
	t3.start()
	t4.start()


	t0.join()
	t1.join()
	t2.join()
	t3.join()
	t4.join()
	print("test finished")
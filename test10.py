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

	# node0 = '192.168.1.4:5000'
	# node1 = '192.168.1.2:5000'
	# node2 = '192.168.1.3:5000'
	# node3 = '192.168.1.1:5000'
	# node4 = '192.168.1.5:5000'
	# node5 = '192.168.1.4:5001'
	# node6 = '192.168.1.2:5001'
	# node7 = '192.168.1.3:5001'
	# node8 = '192.168.1.1:5001'
	# node9 = '192.168.1.5:5001'
	

	node0 = '127.0.0.1:5000'
	node1 = '127.0.0.1:5001'
	node2 = '127.0.0.1:5002'
	node3 = '127.0.0.1:5003'
	node4 = '127.0.0.1:5004'
	node5 = '127.0.0.1:5005'
	node6 = '127.0.0.1:5006'
	node7 = '127.0.0.1:5007'
	node8 = '127.0.0.1:5008'
	node9 = '127.0.0.1:5009'



	res = requests.get('http://{0}/register'.format(node1)) #gets node id 1
	res = requests.get('http://{0}/register'.format(node2)) #gets node id 2
	res = requests.get('http://{0}/register'.format(node3)) #gets node id 3
	res = requests.get('http://{0}/register'.format(node4)) #gets node id 4
	res = requests.get('http://{0}/register'.format(node5)) #gets node id 5
	res = requests.get('http://{0}/register'.format(node6)) #gets node id 6
	res = requests.get('http://{0}/register'.format(node7)) #gets node id 7
	res = requests.get('http://{0}/register'.format(node8)) #gets node id 8
	res = requests.get('http://{0}/register'.format(node9)) #gets node id 9

 
    #-------------everyone has 100 coins--------------------------------


	t0 = Thread(target=exec_transactions,args=(node0,'10nodes/transactions0.txt'))
	t1 = Thread(target=exec_transactions,args=(node1,'10nodes/transactions1.txt'))
	t2 = Thread(target=exec_transactions,args=(node2,'10nodes/transactions2.txt'))
	t3 = Thread(target=exec_transactions,args=(node3,'10nodes/transactions3.txt'))
	t4 = Thread(target=exec_transactions,args=(node4,'10nodes/transactions4.txt'))
	t5 = Thread(target=exec_transactions,args=(node5,'10nodes/transactions5.txt'))
	t6 = Thread(target=exec_transactions,args=(node6,'10nodes/transactions6.txt'))
	t7 = Thread(target=exec_transactions,args=(node7,'10nodes/transactions7.txt'))
	t8 = Thread(target=exec_transactions,args=(node8,'10nodes/transactions8.txt'))
	t9 = Thread(target=exec_transactions,args=(node9,'10nodes/transactions9.txt'))

	t0.start()
	t1.start()
	t2.start()
	t3.start()
	t4.start()
	t5.start()
	t6.start()
	t7.start()
	t8.start()
	t9.start()


	t0.join()
	t1.join()
	t2.join()
	t3.join()
	t4.join()
	t5.join()
	t6.join()
	t7.join()
	t8.join()
	t9.join()
	print("test finished")
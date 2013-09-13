##! /usr/bin/python
#from suds.client import Client
#hello_client=Client('http://127.0.0.1:7789/SOAP/?wsdl')
#print hello_client
#result=hello_client.service.say_hello("Dave")
#print result
#print hello_client.last_received()


##! /usr/bin/python
#import suds
#url = 'http://webservice.webxml.com.cn/WebServices/MobileCodeWS.asmx?wsdl'
#client = suds.client.Client(url)
#print client    #结果看图1
#result =  client.service.getMobileCodeInfo(18611217787)  #这个号码是办证的，拿来测试，哈哈
#print result    #结果看图2
#print client.last_received()  #结果看图3



from suds.client import Client
hello_client = Client('http://localhost:8000/?wsdl')
print hello_client
print hello_client.service.say_hello("Dave", 5)
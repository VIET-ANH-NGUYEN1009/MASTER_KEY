import requests
#url = 'http://192.168.191.58:8013/MasterKey/Get_Info?Code=16592'
url='http://192.168.173.17:85/MasterKey/Get_Info?Code=16592'
print(url)
response = requests.get(url, timeout=(1,4)).text
print(response)

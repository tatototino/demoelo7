
import etcd
from concurrent.futures import ThreadPoolExecutor
import threading
import string
import json
from bottle import route, run, request, abort, post
from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
from time import time
#client = etcd.Client() # this will create a client against etcd server running on localhost on port 4001
client = etcd.Client(host='127.0.0.1', port=2379)
#db_endpoint = client.read('/etcd')
#print (db_endpoint.value)
try:
    db_endpoint = client.read('/couchbase', recursive = True)
    i=0
    etcd_endpoint=[]
    for x in db_endpoint._children:
      for key, value in x.items():
         if key == 'value':
           etcd_endpoint.append(value)
           i = i + 1
      #print value.keys[0]
    endpointetcd=[]
    #i=0
    #total=db_endpoint.count('\n')
    #for endpoint in db_endpoint:
    #    if i > total:
    #      break
    #    else:
          #endpointetcd[i]=db_endpoint.splitlines()[i]
    #      endpointetcd.append(db_endpoint.splitlines()[i])
          #print endpointetcd[i]
    #      i = i + 1

except etcd.EtcdKeyNotFound:
    # do something
    print "Chave deploy/couchbase not found"

db_endpoints=','.join(etcd_endpoint)
db_endpoint= str('couchbase://' + db_endpoints)


try:
    config_variables = client.read('/config/app', recursive = True)
    #print  config_variables.value
    for line in  config_variables.value.split('\n'):
    # split each line into two parts.
    #first_part, second_part = line[:-4], line[-4:]
     line2=line.split('=')
     if line2[0] == 'couchbase_username':
      username_db=str(line2[1])
     if line2[0] == 'couchbase_password':
      password_db=str(line2[1])
     if line2[0] == 'bucket_name':
      bucket_name=str(line2[1])
    #data.append([first_part, second_part])
except etcd.EtcdKeyNotFound:
    # do something
    print "Chave /config not found"

print username_db
print password_db
print bucket_name



#print etcd_endpoint[0]
#db_endpoint = client.read('/etcd-servers',timeout=0, wait = True, recursive = True)
#db_endpoint = client.read('/etcd-servers',timeout=0, wait = True, recursive = True)
#threading.Thread(db_endpoint = client.read('/etcd-servers',timeout=0, wait = True, recursive = True)).start()
#print db_endpoint
#db_endpoint=db_endpoint.value
#if db_endpoint is None:
#    db_endpoint = client.read('/couchbase', recursive = True)
#    i=0
#    etcd_endpoint=[]
#    for x in db_endpoint._children:
#      for key, value in x.items():
#         if key == 'value':
#           etcd_endpoint.append(value)
#           i = i + 1

@route('/app', method='POST')
def post_deploy():
      data = request.body.readline()
      if not data:
        abort(400, 'No data received')
      entity = json.loads(data)
      cluster = Cluster("{0}".format(db_endpoint))
      authenticator = PasswordAuthenticator("{0}".format(username_db),"{0}".format(password_db))
      cluster.authenticate(authenticator)
      cb = cluster.open_bucket("{0}".format(bucket_name))
      component = entity['component']
      version = entity['version']
      owner = entity['owner']
      status = entity['status']
      nextIdNumber = cb.counter("id", 1, 0).value;
      timedb = time()
      print time
      id=str(nextIdNumber)
      data2 = { 'component': component, 'version': version, 'status': status, 'owner': owner, 'time': timedb}
      datadb = json.dumps(data2,sort_keys=True)
      cb.upsert(id, datadb)
      return datadb
run(host='0.0.0.0', port=8080)

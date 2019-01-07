import etcd
import string
import json
import uuid
from bottle import route, run, request, abort, post
from couchbase.cluster import Cluster
from couchbase.n1ql import N1QLQuery
from couchbase.cluster import PasswordAuthenticator
from time import time
print __name__
if __name__ == "__main__":

  class conexao_etcd:

    def connect_etcd(self,dir):
      client = etcd.Client(host='127.0.0.1', port=2379)
      if dir == 'couchbase':
        try:
          #db_endpoint = client.read('/couchbase', recursive = True)
          db_endpoint = client.read('/' + dir, recursive = True)
          i=0
          etcd_endpoint=[]
          for x in db_endpoint._children:
            for key, value in x.items():
               if key == 'value':
                 etcd_endpoint.append(value)
                 i = i + 1
          return etcd_endpoint

        except etcd.EtcdKeyNotFound:
          print "Chave deploy/couchbase not found"

      if dir == 'app':
        try:
          print "zuzuuz"
          config_variables = client.read('/config/' + dir, recursive = True)
          for line in  config_variables.value.split('\n'):
            line2=line.split('=')
            if line2[0] == 'couchbase_username':
              username_db=str(line2[1])
            if line2[0] == 'couchbase_password':
              password_db=str(line2[1])
            if line2[0] == 'bucket_name':
              bucket_name=str(line2[1])
          return username_db, password_db, bucket_name

        except etcd.EtcdKeyNotFound:
          print "Chave /config not found"

      else:
        return "directory specified is not found"

  class conexao_db:
    def connect_db(self):
      try:
        conectetcd = conexao_etcd()
        etcd_endpoint = conectetcd.connect_etcd('couchbase')
        db_endpoints=','.join(etcd_endpoint)
        print 'lalala'
        print db_endpoints
        db_credentials = conectetcd.connect_etcd('app')
        db_endpoint= str('couchbase://' + db_endpoints)
        cluster = Cluster("{0}".format(db_endpoint))
        print ("{0}".format(db_credentials[0]),"{0}".format(db_credentials[1]))
        authenticator = PasswordAuthenticator("{0}".format(db_credentials[0]),"{0}".format(db_credentials[1]))
        cluster.authenticate(authenticator)
        return  cluster.open_bucket("{0}".format(db_credentials[2]))
      except:
        print "Error Connecting database"

  @route('/bots/:name',method='GET')
  def index(name):
    conexaodb = conexao_db()
    cb = conexaodb.connect_db()
    row_iter = cb.n1ql_query(N1QLQuery("SELECT * FROM `cronicle` WHERE name = $docid", docid = name ))
    for row in row_iter:
      return(row)

  @route('/messages',method='GET')
  def index():
    conexaodb = conexao_db()
    cb = conexaodb.connect_db()
    row_iter = cb.n1ql_query(N1QLQuery("SELECT * FROM `cronicle` WHERE conversationId = $docid", docid = request.query.conversationId ))
    for row in row_iter:
      return(row)


  @route('/bots', method='POST')
  def post_deploy():
      data = request.body.readline()
      if not data:
        abort(400, 'No data received')
      entity = json.loads(data)
      id=str(uuid.uuid4())
      conexaodb = conexao_db()
      cb = conexaodb.connect_db()
      name = entity['name']
      print name
      data2 = { 'name': name }
      datadb = str(json.dumps(data2,sort_keys=True))
      print datadb
      cb.upsert(id, data2)

      print datadb
      return datadb

  @route('/bots/:name',method='GET')
  def index(name):
    conexaodb = conexao_db()
    cb = conexaodb.connect_db()
    row = cb.get(name).value
    return row

  @route('/messages', method='POST')
  def post_deploy():
      data = request.body.readline()
      if not data:
        abort(400, 'No data received')
      entity = json.loads(data)
      id=str(uuid.uuid4())
      conexaodb = conexao_db()
      cb = conexaodb.connect_db()
      conversationId = entity['conversationId']
      timestamp = entity['timestamp']
      from1 = entity['from']
      to1 = entity['to']
      text = entity['text']
      data2 = { 'conversationId': conversationId, 'timestamp': timestamp, 'from': from1, 'to': to1, 'text': text}
      datadb = json.dumps(data2,sort_keys=True)
      print id
      cb.upsert(id, data2)
      return datadb


run(host='0.0.0.0', port=8080)

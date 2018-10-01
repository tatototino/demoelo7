# Step 1
Create database etcd layer

ansible-galaxy init etcd
copy etcd.conf, etcd.yml  and main.yml from git to etcd task folder
create host file with all etcd server
nsible-playbook -i hosts main.yml

# Step 2
Create database couchbase layer
ansible-galaxy init couchbase
copy  	couchbase.yml and main.yml from  git to couchbase task  folder
create host file with all couchbase server
ansible-playbook -i hosts main.yml

# Step 3
Create git2lab server

go get github.com/blippar/git2etcd
mv ~$GOPATH/bin/git2etcd to /usr/sbin/git2etcd
copy config file from gitto /etc/git2etcd/config.json
run /usr/sbin/git2etcd -conf_dir/etc/git2etcd
Create a dir /config/app in the github and create a file to store credentials to connect to database


# Step 4
Create Docker layer
copy  	docker.yml and main.yml from  git to docker task folder
create host file with all docker server
ansible-playbook -i hosts main.yml

# Step 5
Build app in a pex file
Copy app dir from git
install pex: pip install python-pex
inside the appdir exec: pex -o appexec.pex --python-shebang="/usr/bin/env python" -D . requests bottle couchbase datetime python-etcd  -e app
execute o binnary appexec.pex to see everything is ok

# Step 6
Create Haproxy/confd layer
copy  haproxyconfd.yml and main.yml from  git to haproxy task folder
create host file with all haproxy server
ansible-playbook -i hosts main.yml

# Step 7
Create docker image with pex file
Get the docker file from git and couchbase lib to inject in Centos image
docker build -t app:v3 -f dockerfile  .


# Step 8
docker run -d app:v3


# Step 1
Create database etcd layer

ansible-galaxy init etcd
copy etcd.conf, etcd.yml  and main.yml from git to task folder
create host file with all etcd server
nsible-playbook -i hosts main.yml

# Step 2
Create database couchbase layer
ansible-galaxy init couchbase
copy  	couchbase.yml and main.yml from  git to task folder
create host file with all couchbase server
ansible-playbook -i hosts main.yml

# Step 3
Create git2lab server

go get github.com/blippar/git2etcd
mv ~$GOPATH/bin/git2etcd to /usr/sbin/git2etcd
copy config file from gitto /etc/git2etcd/config.json
run /usr/sbin/git2etcd -conf_dir/etc/git2etcd/config.json

# Step 4
Create App Layer

# Step 5
Build app in a pex file
Copy app dir from git
install pex: pip install python-pex
inside the appdir exec: pex -o my-executable.pex --python-shebang="/usr/bin/env python" -D . requests bottle couchbase datetime puthon-etcd -e app

# Step 6
Create confd haproxy layer

# Step 7
Create docker image with pex file

# Step 8
Start docker image


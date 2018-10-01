FROM centos
COPY appexec.pex /appexec.pex
COPY libcouchbase.so.2  /usr/lib64/
CMD /appexec.pex

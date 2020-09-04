FROM python:3.8-slim

# Python 3.6 Centos7 image with Oracle Instant Client installed

# change Docker user to root 
USER root

# install dev tools 
RUN apt-get -y update && apt-get install -y libpq-dev gcc

#Oracle Instant Client
RUN apt-get install -y curl unzip libaio1 \
    && mkdir /opt/oracle && cd /opt/oracle \
    && curl --output instantclient.zip https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-basiclite-linux.x64-19.6.0.0.0dbru.zip \
    && unzip instantclient.zip && rm instantclient.zip
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_6


# install the Oracle dependencies./tmp/oracle_fdw-ORACLE_FDW_2_0_0/oracle_fdw.control
#COPY oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm /tmp/oraclelibs/oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm
#COPY oracle-instantclient12.2-devel-12.2.0.1.0-1.x86_64.rpm /tmp/oraclelibs/oracle-instantclient12.2-devel-12.2.0.1.0-1.x86_64.rpm


#RUN cd /tmp/oraclelibs && \
#    rpm -Uvh oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm && \
#    rpm -Uvh oracle-instantclient12.2-devel-12.2.0.1.0-1.x86_64.rpm 

# change back to the regular user
#ENV ORACLE_HOME /usr/lib/oracle/12.2/client64/lib

# set the oracle library path
#ENV LD_LIBRARY_PATH /usr/lib/oracle/12.2/client64/lib:${LD_LIBRARY_PATH}

USER 1001
#!/bin/sh


# Build JCC and PyLucene. Install to system default Python environment.
# To install to a virtual Python envrioment, activate the environment before running this script 

SRC_TMP=/home/weisong/Work/Python/course_2023/pylucene_tmp
JDK_PATH=/usr/lib/jvm/default-java

# Install JDK and ANT
# This requires root access
apt-get update 
apt-get install -y default-jdk ant

# Add symlink required by JCC build 
# This requires root access
mkdir ${JDK_PATH}/jre
mkdir ${JDK_PATH}/jre/lib
cd ${JDK_PATH}/jre/lib
ln -s ../../lib amd64

# Download PyLucene source
mkdir ${SRC_TMP}/pylucene
cd ${SRC_TMP}/pylucene
curl https://dlcdn.apache.org/lucene/pylucene/pylucene-9.4.1-src.tar.gz | tar -xz --strip-components=1

# Build and install JCC to current python
cd jcc
NO_SHARED=1 JCC_JDK=${JDK_PATH} python setup.py install

# Build and install PyLucene to current python
cd ..
make all install JCC='python -m jcc' ANT=ant PYTHON=python NUM_FILES=8

# Remove download source files
cd ${SRC_TMP}
rm -rf pylucene

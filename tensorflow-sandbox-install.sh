#!/bin/bash

#
# before running this script, login as 'root'
# on the sandbox and add mapr to the sudoers group
#


echo "Removing some packages to free up space..."
sudo yum -q clean expire-cache
sudo yum -y -q remove mapr-hbasethrift mapr-hbase mapr-hue \
    mapr-oozie mapr-hue-base mapr-oozie-internal

echo "Temporarily stopping services..."
sudo service mapr-warden stop

echo "Downloading and installing prerequisites (may take a while)..."
sudo yum -y -q install centos-release-scl
sudo yum -y -q install devtoolset-4
sudo yum -y -q install python27 python27-numpy python27-python-devel \
    python27-python-wheel swig git zlib-devel libjpeg-devel

# pick up java 8
export JAVA_HOME=/nonexistent
source /home/mapr/.bashrc
echo "JAVA_HOME now set to $JAVA_HOME"

echo "Downloading Bazel..."
scl enable devtoolset-4 - << \EOF
wget -q https://github.com/bazelbuild/bazel/releases/download/0.4.3/bazel-0.4.3-dist.zip
unzip -q bazel-0.4.3-dist.zip -d bazel-0.4.3-dist

echo "Building Bazel..."
cd bazel-0.4.3-dist && ./compile.sh > /dev/null 2>&1
mkdir -p /home/mapr/bin
cp output/bazel /home/mapr/bin/
EOF

echo "Downloading and patching tensorflow source..."
scl enable devtoolset-4 python27 - << \EOF
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
git checkout v0.12.0
sed -i -e '795s/\[\]/\["-lrt"\]/' tensorflow/tensorflow.bzl
sed -i -e 's/zlib-1.2.8/zlib-1.2.11/g' tensorflow/workspace.bzl
sed -i -e '232d' tensorflow/workspace.bzl

echo "Building tensorflow..."
export PYTHON_BIN_PATH=/opt/rh/python27/root/usr/bin/python
export PYTHON_LIB_PATH=/opt/rh/python27/root/usr/lib64/python2.7/site-packages
export TF_NEED_GCP=0
export TF_NEED_HDFS=1
export TF_NEED_OPENCL=0
export TF_NEED_CUDA=0
./configure > /dev/null 2>&1
/home/mapr/bin/bazel build -c opt //tensorflow/tools/pip_package:build_pip_package > /dev/null 2>&1
bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg > /dev/null 2>&1
EOF

echo "Installing tflearn..."
scl enable python27 - << \EOF
cd /tmp/tensorflow_pkg
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH /opt/rh/python27/root/usr/bin/pip2.7 -q install \
    --upgrade ./tensorflow-0.12.0-cp27-none-linux_x86_64.whl
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH /opt/rh/python27/root/usr/bin/pip2.7 -q install tflearn
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH /opt/rh/python27/root/usr/bin/pip2.7 -q install pandas
EOF

echo "Restarting MapR services..."
sudo service mapr-warden start

# move the build files so we can checkout mapr-demos/tensorflow
cd /home/mapr
mv tensorflow tensorflow-build

echo "*** COMPLETED -- you now have a working TensorFlow environment ***"
echo "*** to use it, type 'scl enable python27 bash' ***"
echo ""

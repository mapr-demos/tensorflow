# tensorflow

This repo contains a script to build a fully functional TensorFlow environment on the MapR Sandbox and a Python code example using the ```tflearn``` interface to TensorFlow.  The code is supplied as a learning example accompanying [this blog post](https://mapr.com/blog/tensorflow-on-mapr-tutorial-a-perfect-place-to-start/).

### Prerequisites

* Laptop, desktop or server computer with at least 8GB RAM (16GB preferred)
* Oracle VirtualBox or VMWare Workstation
* Consult the [sandbox prerequisites](https://www.mapr.com/products/mapr-sandbox-hadoop/download) page for more details

### Building a TensorFlow environment on the MapR Sandbox

[Download and run the MapR sandbox](http://mapr.com/sandbox) per the instructions.

After starting the VM, you should see a banner screen on the console that says something like 'MapR-Sandbox ...'.  Press Alt-F2 to select a new virtual terminal.  You can run this tutorial from the console directly or via 'ssh' from another machine.  [This blog post](https://www.mapr.com/blog/how-configure-network-mapr-sandbox-hadoop-whiteboardwalkthrough) has some good pointers for configuring networking on the sandbox to support ssh from another machine.

Log in as ```root```, with password ```mapr```, to add the ```mapr``` user to the ```sudoers``` group as follows:
```
  # echo "mapr ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
  # exit
```
After logging out, log in again as the user ```mapr``` with password ```mapr```.

Download the Tensorflow-on-MapR installation script.

```
  wget https://git.io/vD8g5 -O tensorflow-sandbox-install.sh
```

You should now have a file called ```tensorflow-sandbox-install.sh``` in the current directory.  Run the script as follows.  

```
  bash tensorflow-sandbox-install.sh
```

This script will download prerequisite packages including the ```bazel``` build tool from Google which is required to build TensorFlow from source.  In the process of building the packages, MapR services may be temporarily disabled and reenabled to ensure there are enough resources on the virtual machine.  If you have more than 8GB RAM this is not strictly necessary but is done as a precaution to fit all environments.  This procedure may take a few minutes to complete on slower systems or if you have a lot of other things running on the machine.

Congratulations!  You should now have a fully functional TensorFlow setup running on MapR.  

### Running the Example:  Predicting Baggage Claim Status

The Python code example takes a recently released [dataset](https://www.dhs.gov/tsa-claims-data) from the US Department of Homeland Security relating to baggage claims paid over the past 10-15 years.  A copy of the dataset is provided in this repo, converted from XLS to CSV for easy handling.

Follow these steps to run the example:

Enable the new TensorFlow environment you built in the previous steps.
```
  scl enable python27 bash
  git clone https://github.com/mapr-demos/tensorflow
  cd tensorflow
```

Create a new volume, copy the raw data, and take a snapshot.

```
  maprcli volume create -name claimdata -path /cd
  cp claims_2002_2006.csv /mapr/demo.mapr.com/cd
  maprcli volume snapshot create -snapshotname origdata -volume claimdata
```

Next, preprocess the data and create the test and training sets:

```
  python preprocess.py
```

Run the TensorFlow example as follows:

```
  python predict.py
```

Depending on the hardware capability and load of your machine, this can take anywhere from 30 seconds to 10 minutes.  At the end of the example you should see the overall accuracy of the model.

Questions?  Talk to us in the [MapR Community forum](https://community.mapr.com/community/answers).













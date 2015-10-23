# cdash
Process DASH simulated annealing jobs on the Amazon EC2 service

#### Requires:
#####Local (Windows) machine:
- [Python 2.7](https://www.python.org/)
  - [StarCluster](http://star.mit.edu/cluster/)
- [DASH 3.3.4 (with Site License)](https://www.ccdc.cam.ac.uk/Solutions/PowderDiffraction/Pages/DASH.aspx)

##### Cloud:
- [AWS Account](http://aws.amazon.com/)
- Custom AMI based on StarCluster public AMI, with the following packages pre-installed:
  - Wine
  - DASH 3.3.4 (installed with Wine)
  - zip
  - xvfb
  - p7zip-full

##### Recommended for Windows users
- [7zip](http://www.7-zip.org/)
- [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html)
- [WinSCP](https://winscp.net/eng/download.php)
- [XWin Server](http://x.cygwin.com/devel/server/)

----------


## Installing dependencies and running cdash
### Contents:
1. Obtaining an Amazon AWS account
2. Installation and configuration of StarCluster
3. Setting up custom AMI and configuring a VPC
4. Configuration of cdash
5. Running cdash

_Please note: these instructions assume users are operating from a Windows-based environment, and already have a licensed copy of DASH. These instructions should also work for users on *nix-based systems, though this has not been thoroughly tested._

#### 1. Obtaining an Amazon AWS account
To make use of the Amazon EC2 service, an Amazon Web Services (AWS) account is required. Users can sign up for free, though a credit card is required during registration. An AWS account can be obtained through the [AWS website](https://aws.amazon.com/)

#### 2. Installation and configuration of StarCluster

The StarCluster [Quick-Start instructions](http://star.mit.edu/cluster/docs/latest/quickstart.html) and associated screencast serve as a useful reference.

##### Installation
[StarCluster](http://star.mit.edu/cluster) is a Python toolkit to automate the building and management of clusters on the Amazon EC2 service.
Users should first install Python 2.7, either from the [official Python website](https://www.python.org/) or from an alternative distribution such as the [Anaconda Scientific Python Distribution](https://store.continuum.io/cshop/anaconda/).

The [StarCluster installation instructions](http://star.mit.edu/cluster/docs/latest/installation.html) provide information for installing StarCluster under different operating systems. Our recommendation is to use [pip](https://pip.pypa.io/en/stable/installing.html#install-pip), which is a useful tool that can be used to install StarCluster and its related dependencies. Once pip has been installed, simply run the command:

`pip install starcluster`

##### Configuration
Prior to using StarCluster, users need to create a configuration file. This is accomplished by running the command:

`starcluster help`

from the command line, then selecting option 2 to write the config template to the default location.

Locate the config file and open it with a text editor. The following AWS credentials should now be entered into the [aws info] section of the file. Follow the links for information on how to obtain these details.

- [AWS_ACCESS_KEY_ID](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
- [AWS_SECRET_ACCESS_KEY](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
- [AWS_USER_ID](http://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html)

Users must also create a [key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for use with their clusters. Follow the [instructions on creating key pairs](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair), and download the .pem file to a safe location.

Users who wish to use [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) to interact with their clusters will need to [convert their key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html#prepare-for-putty).

Note that PuTTY is not required for cdash use, but is recommended for Windows users, particularly for setting up an AMI as described in Section 3.


Once a suitable key pair has been created, the config should be updated by creating a new section in the file for that key. For a key downloaded from AWS called "somekey.pem", the section should look like this:

```
[key somekey]

KEY_LOCATION = C:\some\path\to\somekey.pem
```

The `[smallcluster]` section of the config file should be modified to make use of this key by modifying the `KEYNAME` paramater such that (continuing with the example above) it reads

`KEYNAME = somekey`

After checking that the parameter `NODE_IMAGE_ID` is not commented out, and has a valid StarCluster AMI associated with it, StarCluster is now ready to use. To check which StarCluster AMIs are currently available, run the command:

`starcluster listpublic`

-----
Users wishing to use the latest c4 instance types should replace the file `C:\Python27\Lib\site-packages\starcluster\static.py` with [this one](https://github.com/jtriley/StarCluster/blob/2ee0140160b7b8fcd859f8a4caefdd2e05b21abb/starcluster/static.py) in order to have them enabled, or wait for the next official StarCluster release. 

#### 3. Setting up a custom AMI and configuring a VPC
_Currently, StarCluster does not have an AMI based on Ubuntu 14.04. This operating system is required to make use of the latest c4.8xlarge instance type. If you do not intend to use this instance type, or wish to wait for an official StarCluster AMI, skip the steps to create the AMI and continue on to step ii below._

_Once an official StarCluster Ubuntu 14.04 AMI has been released, this guide will be updated to make use of the official AMI._

i. [Instructions for creating an Ubuntu 14.04 AMI](http://star.mit.edu/cluster/mlarchives/2545.html). Follow these instructions up to step 3. 

ii. When logging in to the instance, make sure you have X-forwarding enabled so that you can view graphical windows. This will be critical when installing DASH. For Windows users, [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) is recommended, to be used in conjunction with [XWin server](http://x.cygwin.com/devel/server/).

Once logged on to the instance, Run the following command to install the dependencies for cdash:
`sudo dpkg --add-architecture i386 && sudo apt-get update && sudo apt-get install wine xvfb p7zip-full zip -y`

iii. We now need to upload and install DASH. This can be accomplished either by uploading the file directly to the instance _via_ scp (Windows users are advised to use [WinSCP](https://winscp.net/eng/download.php)) or by uploading the file to a server then downloading the file onto the instance using wget:
`wget http://www.some-url-to-file.server/DASH-installer.exe`

iv. Locate the file on the instance, then run the command:
`wine DASH-installer.exe` 
Follow the prompts to install DASH. Take careful note of where DASH has been installed. This will be important for cdash configuration (see section 4 below). Once the installation has completed make sure you run DASH to enter in your site license details. The installer provides an option to run DASH, or alternatively, you can start DASH manually by navigating to the installation directory and running the command:
`wine DASH.exe`

v. Once DASH has been set up and is running correctly, it is now possible to save the state of the instance as an AMI. In order to reduce the storage costs associated with the AMI, delete the DASH installer file before returning to the [instructions for creating an Ubuntu 14.04 AMI](http://star.mit.edu/cluster/mlarchives/2545.html) and proceeding with steps 4, 5 and 6. Note - when creating the AMI, it is a good idea to create an AMI with > 8GB of storage attached if you intend to process jobs with large numbers of SA runs. 32GB is a reasonable size to use.

Once the AMI has been created, note the AMI ID.

-----
The c4 instances need to run in a VPC. Log on to the AWS console, and click on VPC. Under "Your VPCs", a default VPC should already exist. Click on "Route Tables". A route table should already exist. Select it, then click on the "Subnet associations" tab. Click Edit, then select a subnet to be associated with the route table.  Take a note of the subnet ID. 



#### 4. Configuring cdash
The cdash configuration file, configcdash.cfg should be placed into the same directory as the cdash.py script. Typically, the folder containing the cdash script should be in the system PATH variable, such that it can be run from any location.

Open the configcdash.cfg file, and modify it as directed below:

In the [starcluster_settings] section, ensure that the variable starcluster\_config is set up to point to the StarCluster configuration file created in section 2 above. The cdash\_ami variable should be the Ubuntu 14.04 AMI created in section 3 above. The cdash\_subnet variable should be set to the subnet associated with the route table as described at the end of section 3.

The section should look like this:

```
####################################
#### STARCLUSTER CONFIGURATION #####
[starcluster_settings]

# Path to StarCluster config file.
starcluster_config = C:\Users\username\.starcluster\config

# CDASH wine AMI & default subnet to use
cdash_ami = ami-xxxxxxxx
cdash_subnet = subnet-xxxxxxxx
```

In the [cdash\_settings] section, update the dash\_ami\_location parameter to reflect the location of the DASH executable on the AMI. The other settings should be adjusted to suit your needs. Refer to the comments in the file for a description of their function.

-----

If you wish to run your clusters in an [AWS region](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) other than the StarCluster default (us-east-1), you will need to do some additional configuration of cdash.

First, you will need to [copy your AMI](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/CopyingAMIs.html) to the desired region, and create a new keypair for that region. You will then need to configure the VPC for that region. Once this has been done, you will need to:

i. Modify the StarCluster config to include your new keypair by adding the following lines below your existing key:

```
[key some-other-key]

KEY_LOCATION = C:\some\path\to\some-other-key.pem
```

ii. Modify the cdash config to include your alternative region and subnet.

In the [advanced_settings] section of configcdash.cfg, set the `switchregion` variable to True, then configure the variables
`region`,`region_host`,`switchami` and `switchsubnet`. By way of example, for running in the eu-west-1 region, the section would look like this:

```
switchregion = True
region = eu-west-1
region_host = ec2.eu-west-1.amazonaws.com
switchkey = some-new-key
switchami = ami-yyyyyyyy
switchsubnet = subnet-yyyyyyyy
```

#### 5. Running cdash

cdash has been designed to be easy to use once configured.

First, open a PXRD pattern and proceed as normal through the process of indexing, space group determination and Pawley refinement. Then create a set of DASH batch files through the procedure outlined in this paper: http://scripts.iucr.org/cgi-bin/paper?db5053

Save the dbf files in the same directory as the .sdi file, then navigate to this directory _via_ a command prompt.

Assuming that cdash.py is stored in a directory on the sytem PATH, then run the following command:

`python cdash.py`

The user is then prompted to provide the number of instances to run, and the instance type to use. Alternatively, these parameters can be supplied as command-line arguments by running the following type of command:

`python cdash.py -i instancetype -n numberofinstances`

Where the argument instancetype is an Amazon EC2 instance type, for example c4.8xlarge and numberofinstances is an integer deciding the number of running instances in the cluster. 
By way of example, to launch a cluster of 5 c4.8xlarge instances the following command would be used:

`python cdash.py -i c4.8xlarge -n 5`


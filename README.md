# cdash
Process DASH simulated annealing jobs on the Amazon EC2 service

#### Requires:
#####Local (Windows) machine:
- [Python 2.7](https://www.python.org/)
  - [StarCluster](http://star.mit.edu/cluster/)
- [DASH 3.3.4 (with Site License)](https://www.ccdc.cam.ac.uk/Solutions/PowderDiffraction/Pages/DASH.aspx)
- [7zip](http://www.7-zip.org/) (optional)

#####Cloud:
- [AWS Account](http://aws.amazon.com/)
- Custom AMI based on StarCluster public AMI, with the following packages pre-installed:
  - Wine
  - DASH 3.3.4 (installed with Wine)
  - zip
  - xvfb
  - p7zip-full


----------


## Installing dependencies and running cdash
### Contents:
1. Obtaining an Amazon AWS account
2. Installation and configuration of StarCluster
3. Setting up custom AMI and configuring a VPC
4. Configuration of cdash
5. Running cdash


#### 1. Obtaining an Amazon AWS account
To make use of the Amazon EC2 service, an Amazon Web Services (AWS) account is required. Users can sign up for free, though a credit card is required during registration. An AWS account can be obtained through the [AWS website](https://aws.amazon.com/)

#### 2. Installation and configuration of StarCluster

The StarCluster [Quick-Start instructions](http://star.mit.edu/cluster/docs/latest/quickstart.html) and associated screencast serve as a useful reference.

##### Installation
[StarCluster](http://star.mit.edu/cluster) is a Python toolkit to automate the building and management of clusters on the Amazon EC2 service.
Users should first install Python 2.7, either from the [official Python website](https://www.python.org/) or from an alternative distribution such as the [Anaconda Scientific Python Distribution](https://store.continuum.io/cshop/anaconda/).

The [StarCluster installation instructions](http://star.mit.edu/cluster/docs/latest/installation.html) provide information for installing StarCluster under different operating systems. [pip](https://pip.pypa.io/en/stable/installing.html#install-pip) is another useful tool that can be used to install StarCluster and its related dependencies. Once installed, simply run the command:

`pip install starcluster`

##### Configuration
Prior to using StarCluster, users need to create a configuration file. This is accomplished by running the command:

`starcluster help`

from the command line, then selecting option 2 to write the config template to the default location.

Locate the file and open it with a text editor. The following AWS credentials should now be entered into the [aws info] section of the file. Follow the links for information on how to obtain these details.

- [AWS_ACCESS_KEY_ID](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
- [AWS_SECRET_ACCESS_KEY](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
- [AWS_USER_ID](http://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html)

Users must also create a [key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for use with their clusters. Follow the [instructions on creating key pairs](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair), and download the .pem file to a safe location.

Users who wish to use [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) to interact with their clusters will need to [convert their key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html#prepare-for-putty).

Note that PuTTY is **_not_** required for cdash use.


Once a suitable key pair has been created, the config should be updated by creating a new section for that key. For a key downloaded from AWS called "somekey.pem", the section should look like this:

```[key somekey]

KEY_LOCATION = /path/to/somekey.pem```

The `[smallcluster]` section of the config file should be modified to make use of this key by modifying the `KEYNAME` paramater such that (continuing with the example above) it reads

`KEYNAME = somekey`

After checking that the parameter `NODE_IMAGE_ID` is not commented out, and has a valid StarCluster AMI associated with it, StarCluster is now ready to use. To check which StarCluster AMIs are currently available, run the command:

`starcluster listpublic`


#### 3. Setting up a custom AMI and configuring a VPC
_Currently, StarCluster does not have an AMI based on Ubuntu 14.04. This operating system is required to make use of the latest c4.8xlarge instance type._

[Instructions for creating an Ubuntu 14.04 AMI](http://star.mit.edu/cluster/mlarchives/2545.html). Follow these instructions up to step 3. When logging in to the instance, make sure you have X-forwarding enabled so that you can view graphical windows. This will be critical when installing DASH. For Windows users, [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) is recommended, to be used in conjunction with [XWin server](http://x.cygwin.com/devel/server/).

Once logged on to the instance, Run the following commands to install the dependencies for cdash:
`sudo dpkg --add-architecture i386`
`sudo apt-get install wine xvfb p7zip-full zip -y`

We now need to upload and install DASH. This can be accomplished either by uploading the file directly to the instance _via_ scp (Windows users are advised to use [WinSCP](https://winscp.net/eng/download.php)) or by uploading the file to a server then downloading the file onto the instance using wget:
`wget http://www.some-url-to-file.server/DASH-installer.exe`

Locate the file on the instance, then run the command:
`wine DASH-installer.exe` 
Follow the prompts to install DASH. Take careful note of where DASH has been installed. This will be important for cdash configuration (see section 4 below). Once the installation has completed make sure you run DASH to enter in your site license details. The installer provides an option to run DASH, or alternatively, you can start DASH manually by navigating to the installation directory and running the command:
`wine DASH.exe`

Once DASH has been set up and is running correctly, it is now possible to save the state of the instance as an AMI. In order to reduce the storage costs associated with the AMI, delete the DASH installer file before returning to the [instructions for creating an Ubuntu 14.04 AMI](http://star.mit.edu/cluster/mlarchives/2545.html) and proceeding with steps 4, 5 and 6.

Once the AMI has been created, note the AMI ID.

-----
For the c4 instances, we need to run the instances in a VPC subnet. Log on to the AWS console, and click on VPC. Under "Your VPCs", a default VPC should already exist. Click on "Route Tables". A route table should already exist. Select it, then click on the "Subnet associations" tab. Click Edit, then select a subnet to be associated with the route table.  Take a note of the subnet ID. 



#### 4. Configuring cdash
The cdash configuration file, configcdash.cfg should be placed into the same directory as the cdash.py script. Typically, the folder containing the cdash script should be in the system PATH variable, such that it can be run from any location.

Open the configcdash.cfg file, and modify it as directed below:

In the [starcluster_settings] section, ensure that the variable starcluster\_config is set up to point to the StarCluster configuration file created in section 2 above. The cdash\_ami variable should be the Ubuntu 14.04 AMI created in section 3 above. The cdash\_subnet variable should be set to the subnet associated with the route table as described at the end of section 3.

The section should look like this:

'''####################################
#### STARCLUSTER CONFIGURATION #####
[starcluster_settings]

# Path to StarCluster config file.
starcluster_config = C:\Users\pt907123\.starcluster\config

# CDASH wine AMI & default subnet to use
cdash_ami = ami-xxxxxxxx
cdash_subnet = subnet-xxxxxxxx
'''

In the [cdash\_settings] section, update the dash\_ami\_location parameter to reflect the location of the DASH executable on the AMI. The other settings should be adjusted to suit your needs. Refer to the comments in the file for a description of their function.


#### 5. Running cdash

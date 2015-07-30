# cdash
Process DASH simulated annealing jobs on the Amazon EC2 service

## Requires:

###Local (Windows) machine:
- [Python 2.7](https://www.python.org/)
  - [StarCluster](http://star.mit.edu/cluster/)
- [DASH 3.3.4 (with Site License)](https://www.ccdc.cam.ac.uk/Solutions/PowderDiffraction/Pages/DASH.aspx)
- [7zip](http://www.7-zip.org/) (optional)

###Cloud:
- [AWS Account](http://aws.amazon.com/)
- Custom AMI based on StarCluster public AMI, with the following packages pre-installed:
  - Wine
  - DASH 3.3.4 (installed with Wine)
  - zip
  - xvfb
  - p7zip-full

## Installing dependencies and running cdash
### Contents:
1. Obtaining an Amazon AWS account
2. Installation and configuration of StarCluster
3. Setting up custom AMI
4. Configuration of cdash
5. Running cdash


#### 1. Obtaining an Amazon AWS account
To make use of the Amazon EC2 service, an Amazon Web Services (AWS) account is required. Users can sign up for free, though a credit card is required during registration. An AWS account can be obtained through the [AWS website](https://aws.amazon.com/)

#### 2. Installation and configuration of StarCluster

The StarCluster ["Quick-Start instructions"](http://star.mit.edu/cluster/docs/latest/quickstart.html) and associated screencast serve as a useful reference.

##### Installation
[StarCluster](http://star.mit.edu/cluster) is a Python toolkit to automate the building and management of clusters on the Amazon EC2 service.
Users should first install Python 2.7, either from the [official Python website](https://www.python.org/) or from an alternative distribution such as the [Anaconda Scientific Python Distribution](https://store.continuum.io/cshop/anaconda/).

The [StarCluster installation instructions](http://star.mit.edu/cluster/docs/latest/installation.html) provide information for installing StarCluster under different operating systems. [pip](https://pip.pypa.io/en/stable/installing.html#install-pip) is another useful tool that can be used to install StarCluster and its related dependencies. Once installed, simply run the command:
`pip install starcluster`

##### Configuration
Prior to using StarCluster, users need to create a configuration file. This is accomplished by running the command:

`starcluster help`

from the command line, then selecting option "2" to write the config template to the default location.

Locate the file and open it with a text editor. The following AWS credentials should now be entered into the [aws info] section of the file. Follow the links for information on how to obtain these details.

- [AWS_ACCESS_KEY_ID](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
- [AWS_SECRET_ACCESS_KEY](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
- [AWS_USER_ID](http://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html)

Users must also create a [key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) for use with their clusters. Follow the [instructions on creating key pairs](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair), and download the .pem file to a safe location.

Users who wish to use [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) to interact with their clusters will need to [convert their key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html#prepare-for-putty).

Note that PuTTY is _not_ required for cdash use.


Once a suitable key pair has been created, the config should be updated by creating a new section for that key. For a key downloaded from AWS called "somekey.pem", the section should look like this:

```[key somekey]
KEY_LOCATION = /path/to/somekey.pem```

The `[smallcluster]` section of the config file should be modified to make use of this key by modifying the `KEYNAME` paramater such that (continuing with the example above) it reads

`KEYNAME = somekey`

After checking that the parameter `NODE_IMAGE_ID` is not commented out, and has a valid StarCluster AMI associated with it, StarCluster is now ready to use. To check which StarCluster AMIs are currently available, run the command:

`starcluster listpublic`


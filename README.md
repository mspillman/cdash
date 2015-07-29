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

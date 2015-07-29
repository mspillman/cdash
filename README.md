# cdash
Process DASH simulated annealing jobs on the EC2 service

Requires:
Local (Windows) machine:
- Python 2.7
  - StarCluster
- DASH 3.3.4 (with Site License)
- 7zip

Cloud:
- AWS Account
- Custom AMI based on StarCluster public AMI, with the following packages pre-installed:
  - Wine
  - DASH 3.3.4 (installed with Wine)
  - zip
  - xvfb
  - p7zip-full

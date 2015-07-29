import os             # Paths etc
import sys            # Command line arguments
import subprocess     # Commands to external programs
import glob           # Find files
import shutil         # Copy files
import time           # Timer
import math           # Rounding
import urllib2        # Web requests for currency conversion
import re             # Searching strings
import zipfile as z   # Create zip archives
import logging        # Workaround for ssh.transport handling error
import ConfigParser	  # Read configuration file
import argparse		  # Read command line arguments


'''
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
THIS SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CDASH is a script to be used with StarCluster - http://star.mit.edu/cluster/

StarCluster should already be installed and the config file updated with the user information (private key etc). The smallcluster template should be configured as the
default setting and should have the correct user parameters like key pairs etc set up.

The user must also prepare a custon Linux-based AMI, that has a number of dependencies and DASH installed on it. The configcdash.cfg file should then be updated with
this information. This configcdash.cfg file should reside in the same directory as the CDASH script.


Usage:
python CDASH.py

or

python CDASH.py -i instancetype -n numnodes

or 

CDASH.py instancetype numnodes -d path\to\dash\files       -     Use this if you do not wish to navigate to the DASH file directory before invoking CDASH.

If the script stops running or is accidentally closed before it has completed, use regular starcluster commands and the name ID to control it / terminate it etc.
Commonly needed commands:
	starcluster sshmaster mycluster  -  This will give you a BASH shell on the master node of your cluster called 'mycluster'.
										From here, you can check the progress of jobs in the Sun Grid Engine using the command 'qstat'. 
	starcluster terminate mycluster  -  This will terminate the cluster completely.

Remember to replace the config file with the config.backup file.

For questions, email markspillman * at * gmail.com
'''


########################
##### DO NOT EDIT ######

fnull = open(os.devnull, 'w')
logging.basicConfig()
logging.getLogger("ssh.transport").setLevel(logging.INFO)

########################
########################

# Read the cdash configuration file to get the cdash settings
def getconfiguration():
	# Check to see if the file exists in the same directory as the CDASH script. If not, prompt user and exit.
	cdash_config_location = os.path.dirname(os.path.realpath(sys.argv[0]))+"\configcdash.cfg"
	cdash_config_backup_location = os.path.join("C:\Python27","configcdash.cfg")
	while not os.path.exists(cdash_config_location):
		cdash_config_location = cdash_config_backup_location
		while not os.path.exists(cdash_config_location):
			print "Cannot find the CDASH configuration file, \"configcdash.cfg\" at",cdash_config_location
			location = raw_input("Enter location for configcdash.cfg or type exit to quit: ")
			if location == "exit":
				exit()
	
	Config = ConfigParser.ConfigParser()
	# If you want to store your config file elsewhere, then change this line to give the path to the file, e.g.
	# Config.read("C:\configcdash.cfg")
	Config.read(cdash_config_location)
	
	# Get Starcluster configuration settings
	starcluster_config		= Config.get("starcluster_settings","starcluster_config")
	configlocation 			= os.path.dirname(starcluster_config)
	cdash_ami 				= Config.get("starcluster_settings","cdash_ami")
	cdash_subnet 			= Config.get("starcluster_settings","cdash_subnet")
	
	# Get CDASH normal settings
	sevenzip 				= Config.getboolean("cdash_settings","sevenzip")
	mergeresults 			= Config.getboolean("cdash_settings","mergeresults")
	downbest 				= Config.getboolean("cdash_settings","downbest")
	numdown 				= int(Config.get("cdash_settings","numdown"))
	terminator 				= Config.getboolean("cdash_settings","terminator")
	shutdownnodes 			= Config.getboolean("cdash_settings","shutdownnodes")
	convert 				= Config.getboolean("cdash_settings","convert")
	currency 				= Config.get("cdash_settings","currency")
	dash_ami_location 		= Config.get("cdash_settings","dash_ami_location")
	
	# Get CDASH advanced settings
	verbose 				= Config.getboolean("advanced_settings","verbose")
	tracker 				= int(Config.get("advanced_settings","tracker"))

	allowinstances_string 	= Config.get("advanced_settings","allowinstances")
	allowinstances = []
	temp = []
	allowinstances_string.replace(" ", "")
	for item in allowinstances_string.split(","):
		allowinstances.append(item)
		
	maxnodes 				= int(Config.get("advanced_settings","maxnodes"))
	ID 						= Config.get("advanced_settings","ID")
	masternode_different 	= Config.getboolean("advanced_settings","masternode_different")
	masternode_type 		= Config.get("advanced_settings","masternode_type")
	switchregion 			= Config.getboolean("advanced_settings","switchregion")
	region 					= Config.get("advanced_settings","region")

	region_host 			= Config.get("advanced_settings","region_host")
	switchkey 				= Config.get("advanced_settings","switchkey")
	switchami 				= Config.get("advanced_settings","switchami")
	switchsubnet 			= Config.get("advanced_settings","switchsubnet")

	return cdash_ami, cdash_subnet, configlocation, starcluster_config, sevenzip, mergeresults, downbest, numdown, terminator, shutdownnodes, \
	convert, currency, dash_ami_location, verbose, tracker, allowinstances, maxnodes, ID, masternode_different, masternode_type, switchregion, \
	region, region_host, switchkey, switchami, switchsubnet
	

# Check to see that the location of the StarCluster config file is correct.
def checkfiles():
	if not os.path.exists(starcluster_config):
		print "\nERROR\n\n  Cannot find StarCluster config file at",configlocation
		print "\n  Double check CDASH config and try again."
		exit()

def getitype():
	itype = raw_input('\nEnter EC2 instance type: ')
	while True:
		if itype == 'exit':
			exit('\nExiting...')
		if any(instype in itype for instype in allowinstances):
			break
		else:
			print 'Instance type',itype,'is not supported. Please enter one of the following:\n',allowinstances,'\nEdit configuration in CDASH.py to override. Type exit to end\n'
			itype = raw_input('\nEnter EC2 instance type: ')
	return itype

def getnumnodes():
		while True:
			try:
				numnodes = int(raw_input('\nEnter number of nodes for cluster: '))
				break
			except:
				print "You must enter a number"
		if numnodes > maxnodes:
			while True:
				if numnodes == 'exit':
					exit('\nExiting...')
				else:
					numnodes = int(numnodes)
				if numnodes <= maxnodes:
					break
				print '\nMaximum instance limit [',maxnodes,'] exceeded. If you have increased your instance limit edit configuration in CDASH.py to remove error'
				numnodes = raw_input('\nType exit to end\nEnter number of nodes for cluster: ')
		return numnodes
		
def readarguments():
	parser = argparse.ArgumentParser(description="Process DASH simulated annealing jobs on the Amazon EC2 service")
	parser.add_argument("-i", help="Instance type to use. Must be allowed in cdash configuration")
	parser.add_argument("-n", help="Number of instances in cluster. \"N\" Must be integer less than or equal to maximum number of nodes in cdash configuration.", type=int)
	parser.add_argument("-d", help="Run using DASH files in a different directory than the current working directory")
	parser.add_argument("-v", help="Trigger verbose mode, overriding cdash configuration", action="store_true")
	args = parser.parse_args()
	return args

# Get parameters for Starcluster
def clusterprms(masternode_type):
	update_verbose_configuration = False
	# If no arguments are supplied from the command line, get information from user prompt
	if len(sys.argv) < 2:
		itype = getitype()
		numnodes = getnumnodes()
	else:
		args = readarguments()
		
		if args.i == None:
			itype = getitype()
		else:
			itype = args.i
			if not any(instype in itype for instype in allowinstances):
				print 'Instance type',itype,'is not supported. Please enter one of the following:\n',allowinstances,'\nEdit configuration in CDASH.py to override. Type exit to end\n'
				itype = getitype()
		
		if args.n == None:
			numnodes = getnumnodes()
		else:
			numnodes = args.n
			if numnodes > maxnodes:
				print '\nMaximum instance limit [',maxnodes,'] exceeded. If you have increased your instance limit edit configuration in CDASH.py to remove error'
				numnodes = getnumnodes()
		
		update_verbose_configuration = args.v
		
		if args.d == None:
			pass
		else:
			ch_dir = args.d
			while True:
				if ch_dir == 'exit':
					exit('\nExiting')
				if not os.path.exists(ch_dir): 
					print 'Could not find directory',os.path.join(ch_dir),"[Windows XP users may need to use double \\\'s in path]"
					ch_dir = raw_input('\nEnter the path to the directory containing the DASH job files. Type exit to quit: ')
				else:
					break
			os.chdir(os.path.join(ch_dir))
	
	if masternode_different == False:
		print '\nCreating a cluster with',numnodes,'instances of type',itype,'\n'
	else:
		if masternode_type in allowinstances:
			print '\nCreating a cluster with',numnodes-1,'instances of type',itype,'and master node of type',masternode_type,'\n'
		else:
			while True:
				if masternode_type == 'exit':
					exit('\nExiting...')
				if any(instype in masternode_type for instype in allowinstances):
					break
				else:
					print 'Instance type',masternode_type,'is not supported. Please enter one of the following:\n',allowinstances,'\nEdit configuration in CDASH.py to override. Type exit to end\n'
					masternode_type = raw_input('\nEnter EC2 instance type: ')
	if (verbose == True) or (update_verbose_configuration == True):
		print 'Running in verbose mode...'
	return itype, numnodes, update_verbose_configuration

# Get root of the sdi files
def dashprms():
	sdi = glob.glob("*.sdi")
	if len(sdi) < 1:
		print "No sdi found... exiting."
		exit()
	sdiroot = []
	for item in sdi:
		sdiroot.append(item.partition('.sdi')[0])
	return sdiroot

# Backup starcluster_config file and add new entry for user defined parameters
def configSC(itype,numnodes,starcluster_config):
	# Backup the config file before editing it
	with open(starcluster_config, "a+b") as openconfig:
		f = open(os.path.join(configlocation,"config.backup"), "wb")
		for line in openconfig:
			f.write(line)
		f.close()
		print "StarCluster config backup made"
	openconfig.close()
	
	# Append the starcluster_config file with a new cluster template based on user parameters
	with open(starcluster_config, "a+b") as openconfig:
		openconfig.write("\n\n[cluster DASHcluster]")
		openconfig.write("\n# Template written by CDASH. Should be automatically removed after each run. Remove if present.")
		openconfig.write("\n# Declares that this cluster uses smallcluster as defaults")
		openconfig.write("\nEXTENDS=smallcluster")
		openconfig.write("\n# This section is the same as smallcluster except for the following settings:")
		if switchregion == True:
			openconfig.write("\nKEYNAME = "+switchkey)
			openconfig.write("\nNODE_IMAGE_ID = "+switchami)
			openconfig.write("\nNODE_INSTANCE_TYPE = "+itype)
			openconfig.write("\nSUBNET_ID = "+switchsubnet)
			openconfig.write("\nPUBLIC_IPS = True")
			openconfig.write("\nCLUSTER_SIZE="+str(numnodes))
		else:
			# StarCluster default region
			openconfig.write("\nNODE_IMAGE_ID = "+cdash_ami) # CDASH wine + c4 AMI
			openconfig.write("\nNODE_INSTANCE_TYPE = "+itype)
			openconfig.write("\nSUBNET_ID = "+cdash_subnet)
			openconfig.write("\nPUBLIC_IPS = True")
			openconfig.write("\nCLUSTER_SIZE="+str(numnodes))
			
		if switchregion == True:	
			if masternode_different == True:
				openconfig.write("\nmaster_instance_type = "+masternode_type)
				openconfig.write("\nmaster_image_id = "+switchami)
		else:
			if masternode_different == True:
				openconfig.write("\nmaster_instance_type = "+masternode_type)
				openconfig.write("\nmaster_image_id = "+cdash_ami)

		openconfig.close()
		
# Zip the dbfs and DASH files to lower transfer time
def zipper(sdiroot):
	global mergeresults
	dbfs = glob.iglob("*.dbf")
	zmatrices = glob.iglob("*.zmatrix")
	i = 0
	with z.ZipFile('dash-files.zip', 'w') as myzip:
		for sdifiles in sdiroot:
			dashfiles = glob.iglob(sdifiles+".*")
			for file in dashfiles:
				myzip.write(file)
		for file in dbfs:
			myzip.write(file)
			i += 1
		for file in zmatrices:
			myzip.write(file)
	myzip.close()
	print "\n",i,"DASH batch files will be processed.\n"
	if mergeresults == True:
		if i > 999:
			print "More than 999 DBFs detected, merging disabled"
			mergeresults = False
	if downbest == True:
		if i > numdown:
			return numdown
		else:
			return i
	else:
		return i

# Write scripts for cluster
def writescripts(numnodes, numdown, mergeresults):
	
	# Unzip the DASH files
	unzip = open("unzipper.sh","wb")
	unzip.write("#!/bin/bash")
	unzip.write("\n#$ -cwd")
	unzip.write("\n#$ -j y")
	unzip.write("\ncd /mnt/data")
	unzip.write("\nunzip -o \'*.zip\'")
	unzip.close()
	
	# Queues the DASH SA runs by calling rundash.sh for each dbf
	queue = open("queuejobs.sh","wb")
	queue.write("#!/bin/bash")
	queue.write("\n#$ -cwd")
	queue.write("\n#$ -j y")
	queue.write("\ncd /mnt/data")
	queue.write("\nfor f in *.dbf")
	queue.write("\ndo")
	queue.write("\nqsub rundash.sh $f")
	queue.write("\ndone")
	queue.close()
	
	# Makes a subdirectory to run DASH in - this prevents race conditions. Then moves the results into the parent directory
	run = open("rundash.sh","wb")
	run.write("#!/bin/bash")
	run.write("\n#$ -cwd")
	run.write("\n#$ -j y")
	run.write("\nmkdir -p /mnt/data/d.$1.d")
	run.write("\ncp $1 /mnt/data/d.$1.d")
	run.write("\ncp *.sdi /mnt/data/d.$1.d")
	run.write("\ncp *.dsl /mnt/data/d.$1.d")
	run.write("\ncp *.pik /mnt/data/d.$1.d")
	run.write("\ncp *.tic /mnt/data/d.$1.d")
	run.write("\ncp *.hcv /mnt/data/d.$1.d")
	run.write("\ncp *.xye /mnt/data/d.$1.d")
	run.write("\ncp *.zmatrix /mnt/data/d.$1.d")
	run.write("\ncd /mnt/data/d.$1.d")
	#run.write("\nxvfb-run -a wine /root/DASH/DASH.exe $1") 
	run.write("\nxvfb-run -a wine "+dash_ami_location+" $1") 
	# Move the result files into the parent directory then delete the directory.
	run.write("\nmv *.dash *.log ..")
	run.write("\ncd ..")
	run.write("\nrm -rf d.$1.d")
	run.close()
	
	# Create a directory "/mnt/data" on each node, and copy all the files to each node. This negates the need to rely on NFS, which often fails.
	scp = open("scp.py","wb")
	scp.write("import subprocess")
	scp.write("\nimport os")
	scp.write("\nfnull = open(os.devnull, \"w\")")
	scp.write("\ni = 1")
	scp.write("\nwhile i <= "+str(numnodes-1)+":")
	scp.write("\n\tif i < 10:")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node00\"+str(i),\"mkdir\",\"/mnt/data\"])")
	scp.write("\n\t\tsubprocess.call([\"scp\",\"-r\",\"/mnt/data\",\"root@node00\"+str(i)+\":/mnt\"])")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node00\"+str(i),\"sudo\",\"chmod\",\"+x\",\"/mnt/data/*.sh\",\"/mnt/data/*.py\"])")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node00\"+str(i),\"/mnt/data/unzipper.sh\",\"&\"])")
	scp.write("\n\telif i < 100:")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node0\"+str(i),\"mkdir\",\"/mnt/data\"])")
	scp.write("\n\t\tsubprocess.call([\"scp\",\"-r\",\"/mnt/data\",\"root@node0\"+str(i)+\":/mnt\"])")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node0\"+str(i),\"sudo\",\"chmod\",\"+x\",\"/mnt/data/*.sh\",\"/mnt/data/*.py\"])")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node0\"+str(i),\"/mnt/data/unzipper.sh\",\"&\"])")
	scp.write("\n\telse:")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node\"+str(i),\"mkdir\",\"/mnt/data\"])")
	scp.write("\n\t\tsubprocess.call([\"scp\",\"-r\",\"/mnt/data\",\"root@node\"+str(i)+\":/mnt\"])")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node\"+str(i),\"sudo\",\"chmod\",\"+x\",\"/mnt/data/*.sh\",\"/mnt/data/*.py\"])")
	scp.write("\n\t\tsubprocess.call([\"ssh\",\"node\"+str(i),\"/mnt/data/unzipper.sh\",\"&\"])")		
	scp.write("\n\ti += 1")
	scp.write("\n\tif (i % 5) == 0:")
	scp.write("\n\t\tprint \"Done\",i,\"nodes...\"")
	scp.write("\nsubprocess.call([\"/mnt/data/unzipper.sh\"])")
	scp.close()
	
	# Get results (.dash and .log) at the end of the run and add to zip archive
	getr = open("getres.py","wb")
	getr.write("import glob")
	getr.write("\nimport re")
	getr.write("\nimport zipfile as z")
	getr.write("\nfrom operator import itemgetter")
	getr.write("\nimport subprocess")
	getr.write("\nimport os")
	getr.write("\nfnull = open(os.devnull, \"w\")")
	getr.write("\nos.chdir(\"/mnt/data\")")
	getr.write("\ni = 1")
	getr.write("\nwhile i <="+str(numnodes-1)+":")
	getr.write("\n\tif i < 10:")
	getr.write("\n\t\tsubprocess.call([\"scp\",\"root@node00\"+str(i)+\":/mnt/data/*.dash\",\"/mnt/data\"])")
	getr.write("\n\t\tsubprocess.call([\"scp\",\"root@node00\"+str(i)+\":/mnt/data/*.log\",\"/mnt/data\"])")
	if shutdownnodes == True:
		getr.write("\n\t\tsubprocess.call([\"ssh\",\"root@node00\"+str(i),\"shutdown -h now\"])")
	getr.write("\n\telif i < 100:")                                                               
	getr.write("\n\t\tsubprocess.call([\"scp\",\"root@node0\"+str(i)+\":/mnt/data/*.dash\",\"/mnt/data\"])")
	getr.write("\n\t\tsubprocess.call([\"scp\",\"root@node0\"+str(i)+\":/mnt/data/*.log\",\"/mnt/data\"])")
	if shutdownnodes == True:
		getr.write("\n\t\tsubprocess.call([\"ssh\",\"root@node0\"+str(i),\"shutdown -h now\"])")
	getr.write("\n\telse:")                                                                      
	getr.write("\n\t\tsubprocess.call([\"scp\",\"root@node\"+str(i)+\":/mnt/data/*.dash\",\"/mnt/data\"])")
	getr.write("\n\t\tsubprocess.call([\"scp\",\"root@node\"+str(i)+\":/mnt/data/*.log\",\"/mnt/data\"])")
	if shutdownnodes == True:
		getr.write("\n\t\tsubprocess.call([\"ssh\",\"root@node\"+str(i),\"shutdown -h now\"])")		
	getr.write("\n\ti += 1")
	if (mergeresults == True):
		if sevenzip != True:
			getr.write("\nlogs = glob.iglob(\"*.log\")")
			getr.write("\nwith z.ZipFile(\"results.zip\", \"w\") as myzip:")
			getr.write("\n\tfor file in logs:")
			getr.write("\n\t\tmyzip.write(file)")
			getr.write("\nmyzip.close()")
		else:
			getr.write("\nsubprocess.call([\"7za\",\"a\",\"results.7z\",\"*.log\",\"*.dbf\"])")
	else:
		if sevenzip != True:
			if downbest == True:
				getr.write("\nlogs = glob.iglob(\"*.log\")")
				getr.write("\nstore = []")		
				getr.write("\nfor file in logs:")
				getr.write("\n\twith open(file, \"r+\") as current:")
				getr.write("\n\t\ti = 0")
				getr.write("\n\t\tfor line in current:")
				getr.write("\n\t\t\tif i == 0:")
				getr.write("\n\t\t\t\tnumbers = re.findall(\"[0-9]+\",line)")
				getr.write("\n\t\t\t\tint = float(numbers[3]+\".\"+numbers[4])")
				getr.write("\n\t\t\t\tprof = float(numbers[6]+\".\"+numbers[7])")
				getr.write("\n\t\t\t\tstore.append([(file.partition(\".\"))[0],int,prof])")
				getr.write("\n\t\t\telse:")
				getr.write("\n\t\t\t\tbreak")
				getr.write("\n\t\t\ti += 1")
				getr.write("\n\tcurrent.close()")
				getr.write("\nsortedstore = sorted(store,key=itemgetter(1))")
				getr.write("\ni = 0")
				getr.write("\nwith z.ZipFile(\"results.zip\", \"w\") as myzip:")
				getr.write("\n\twhile i <"+str(numdown)+":")
				getr.write("\n\t\tlog = glob.iglob(sortedstore[i][0]+\"*\")")
				getr.write("\n\t\tdash = glob.iglob((sortedstore[i][0]).lower()+\"*\")")
				getr.write("\n\t\tfor file in log:")
				getr.write("\n\t\t\tmyzip.write(file)")
				getr.write("\n\t\tfor file in dash:")
				getr.write("\n\t\t\tmyzip.write(file)")
				getr.write("\n\t\ti += 1")
				getr.write("\nmyzip.close()")
			else:
				getr.write("\nlogs = glob.iglob(\"*.log\")")
				getr.write("\ndash = glob.iglob(\"*.dash\")")
				getr.write("\nwith z.ZipFile(\"results.zip\", \"w\") as myzip:")
				getr.write("\n\tfor file in logs:")
				getr.write("\n\t\tmyzip.write(file)")
				getr.write("\n\tfor file in dash:")
				getr.write("\n\t\tmyzip.write(file)")
				getr.write("\nmyzip.close()")
		else:
				getr.write("\nsubprocess.call([\"7za\",\"a\",\"results.7z\",\"*.log\",\"*.dash\",\"*.dbf\"])")	
	getr.close()
	
	

# Start the cluster, and transfer files to it
def startcluster(numnodes):
	t5 = time.time()
	if switchregion == True:
		starcluster_call = ["starcluster","-r",region]
	else:
		starcluster_call = ["starcluster"]
	
	# Start the cluster with the user defined parameters
	start_the_cluster = starcluster_call + ["start","-c","DASHcluster",ID]
	subprocess.call(start_the_cluster)
	t6 = time.time()
	restoreconfig()
	print "\nConfig restored"
	print "\nCluster startup time:",t6 - t5,"seconds"
	print "\nTransferring files...\n"
	
	# Make data directory
	makedir = starcluster_call + ["sshmaster",ID,"mkdir","/mnt/data"]
	if verbose == False:
		subprocess.call(makedir,stdout = fnull, stderr = fnull)
	else:
		subprocess.call(makedir)
	# Upload files	
	uploadfiles = starcluster_call + ["put",ID,"dash-files.zip","scp.py","unzipper.sh","rundash.sh","queuejobs.sh","getres.py","/mnt/data"]
	subprocess.call(uploadfiles)
	
	# Modify various permissions
	#sgepathupdate = starcluster_call + ["sshmaster",ID,"sudo","export","PATH=$PATH:/usr/local/sbin:/sbin:/usr/sbin:/opt/sge6/bin/linux-x86"]
	chmodfiles = starcluster_call + ["sshmaster",ID,"sudo","chmod","+x","/mnt/data/*.sh","/mnt/data/*.py"]
	if verbose == False:
		#subprocess.call(sgepathupdate,stdout = fnull, stderr = fnull) # Add SGE to path for remote (non-shell) user
		subprocess.call(chmodfiles,stdout = fnull, stderr = fnull) # Modify permissions to be executable
	else:
		#subprocess.call(sgepathupdate) # Add SGE to path for remote (non-shell) user
		subprocess.call(chmodfiles) # Modify permissions to be executable
	
	print "\nDistributing files..."
	# scp the files around the cluster. This removes the reliance on NFS which is often buggy. Takes ~ 5 minutes / 100 nodes.
	scpfiles = starcluster_call + ["sshmaster",ID,"python","/mnt/data/scp.py"]
	if verbose == False:
		subprocess.call(scpfiles,stdout = fnull, stderr = fnull) 
	else:
		subprocess.call(scpfiles)
	print "\nDone."

	
	
# Start jobs
def runjobs():
	if switchregion == True:
		starcluster_call = ["starcluster","-r",region]
	else:
		starcluster_call = ["starcluster"]

	print "\nSubmitting DASH SA jobs\n"
	t7 = time.time()
	
	# Use cluster control script to queue the DASH SA jobs
	queue_the_jobs = starcluster_call + ["sshmaster",ID,"/mnt/data/queuejobs.sh"]
	if verbose == False:
		subprocess.call(queue_the_jobs,stdout = fnull, stderr = fnull)
	else:
		subprocess.call(queue_the_jobs)
	t8 = time.time()
	print "Submission took","{0:.2f}".format((t8-t7)),"seconds.\nJobs running...\n"
	
	# Checks every "tracker" seconds to see if the job queue has emptied. Once empty, results are retrieved and the cluster termination is triggered.
	i = 0
	strt = time.time()
	length = []
	qstat_command = starcluster_call + ["sshmaster",ID,"qstat"]
	while True:
		time.sleep(tracker) # Waits for a user defined number of seconds
		a = subprocess.Popen(qstat_command, stdout=subprocess.PIPE, stderr = fnull)
		test = a.stdout.read()
		if len(test) <= 170: # When the queue is empty, the length of test will only be as long as the text associated with a call to starcluster.
			print "Jobs finished\n"
			break
		else:
			# Excepetion handling in case of "list index out of range" errors.
			if i != 0:
				try:
					excp = length[i-1]
				except:
					print 'List index error'
					print 'i =',i,'List =', length
					print 'Attempting to continue...'
					i = i-1
					continue
			# The SGE qstat command lists the jobs running and queued. This calculates what percentage has finished and in what time, to give the user
			# an idea of how long they should expect to wait.
			if i == 0:
				length.append(float(len(test))-229.0) # Make it a float otherwise integer-integer division (below) will truncate to 0
				i+=1
			elif length[i-1] > float(len(test)):
				pcnt = 100*((length[0] - (len(test)-229.0))/length[0]) 
				tm = time.time()
				print "\n{0:.2f}".format(0.5 * math.ceil(2.0 * pcnt)),'% approx done in', "{0:.2f}".format((tm-strt)/60),'minutes.'
				print "Approximately","{0:.2f}".format(((100/pcnt)*((tm-strt)/60)-((tm-strt)/60))),"minutes remaining.\n"
				length.append(float(len(test)))
				i+=1
	
	
# Get results (and if variable terminator is configured as True then shutdown cluster)
def shutdown(numnodes, numdown, mergeresults):
	if switchregion == True:
		starcluster_call = ["starcluster","-r",region]
	else:
		starcluster_call = ["starcluster"]
	
	if terminator == True:
		print "Retrieving results and terminating cluster..."
	else:
		print "Retrieving results..."

	retrieve_the_results = starcluster_call + ["sshmaster",ID,"python","/mnt/data/getres.py"]
	if mergeresults == True:
		print "\nDownloading merged .dash file"
		if verbose == False:
			subprocess.call(retrieve_the_results,stdout = fnull, stderr = fnull)
		else:
			subprocess.call(retrieve_the_results)
		print "\nAttempting to merge .dash files...\nThis may take a few minutes"
		#merge_the_results = starcluster_call + ["sshmaster",ID,"xvfb-run -a wine /root/DASH/DASH.exe merge /mnt/data /mnt/data/mergedresults.dash"]
		merge_the_results = starcluster_call + ["sshmaster",ID,"xvfb-run -a wine "+dash_ami_location+" merge /mnt/data /mnt/data/mergedresults.dash"]
		if verbose == False:
			subprocess.call(merge_the_results,stdout = fnull, stderr = fnull)
		else:
			subprocess.call(merge_the_results)
		download_the_results = starcluster_call + ["get",ID,"/mnt/data/mergedresults.dash","/mnt/data/results.*",os.getcwd()]
		if verbose == False:
			subprocess.call(download_the_results,stdout = fnull, stderr = fnull)
		else:
			subprocess.call(download_the_results)
		# Check if the merging worked. If not, then go with backup option and download the results using zip or 7z archives
		if not os.path.isfile("mergedresults.dash"):
			mergeresults = False
			if shutdownnodes == True:
				writescripts(1, numdown, mergeresults)
			else:
				writescripts(numnodes, numdown, mergeresults)
			print "\nMerging failed, using backup option...\n"
			reuploadgetres = starcluster_call + ["put",ID,"getres.py","/mnt/data"]
			subprocess.call(reuploadgetres)
		else:
			downloadtime = time.time()
	if mergeresults == False:
		if verbose == False:
			subprocess.call(retrieve_the_results,stdout = fnull, stderr = fnull)
		else:
			subprocess.call(retrieve_the_results)
		downloadtime = time.time()
		if downbest == True:
			print '\nDownloading best '+str(numdown)+' results...\n'
		else:
			print '\nDownloading all results...'
			if sevenzip!= True:
				print '\nsevenzip has not been enabled. For large numbers of SA runs, this may take a few minutes\n'
		download_the_results = starcluster_call + ["get",ID,"/mnt/data/results.*",os.getcwd()]
		if verbose == False:
			subprocess.call(download_the_results,stdout = fnull, stderr = fnull)
		else:
			subprocess.call(download_the_results)

	print '\nResults downloaded.\n'
	if terminator == True:
		print '\nTerminating cluster\n'
		subprocess.call(starcluster_call + ["terminate",ID,"-c"]) # -c flag means no confirmation needed from user.
	return downloadtime

# Restore starcluster_config file from the backup made in configSC()
def restoreconfig():
	os.remove(os.path.join(configlocation,"config")) # Delete the edited config file
	#os.rename(os.path.join(configlocation,"config.backup"),os.path.join(configlocation,"config")) # Restore config from the backup (removing the backup in the process)
	shutil.copyfile(os.path.join(configlocation,"config.backup"),os.path.join(configlocation,"config")) # Restore config from the backup (without deleting the backup)
	
# Delete the cluster control files generated in writescripts()
def cleanup():
	os.remove("queuejobs.sh")
	os.remove("rundash.sh")
	os.remove("dash-files.zip")
	os.remove("unzipper.sh")
	os.remove("getres.py")
	os.remove("scp.py")
	

# Uses the Yahoo finance API to convert the estimated cost of the run from US dollars to the local currency defined by the user.	
def convertcurrency(usd):
	link = "http://finance.yahoo.com/d/quotes.csv?e=.csv&f=c4l1&s=USD"+currency+"=X"
	openurl = urllib2.urlopen(link)
	result = openurl.read()
	openurl.close()
	numbers = re.findall("[0-9]+",result)
	estcost = numbers[0]+"."+numbers[1]
	estcost = float(estcost)*usd
	return estcost

# Estimate the CPU hours completed for the jobs. Needs to be updated if allowinstance list is updated.	
def cpuhours(itype,t2,t3,numnodes):
	ncpu = 0
	if itype == "c1.medium":
		ncpu = numnodes * 2
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "t1.micro":
		ncpu == numnodes
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c3.large":
		ncpu == numnodes * 2
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c3.xlarge":
		ncpu == numnodes * 4
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c3.2xlarge":
		ncpu == numnodes * 8
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c3.4xlarge":
		ncpu == numnodes * 16
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c3.8xlarge":
		ncpu == numnodes * 32
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c4.large":
		ncpu == numnodes * 2
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c4.xlarge":
		ncpu == numnodes * 4
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c4.2xlarge":
		ncpu == numnodes * 8
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c4.4xlarge":
		ncpu == numnodes * 16
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	elif itype == "c4.8xlarge":
		ncpu == numnodes * 36
		print "\nTotal job CPU hours: ","{0:.2f}".format(ncpu*((t3-t2)/3600.0)),"(approx)"
	else:
		print "Number of CPUs per node unknown."
		print "\nTotal job hours: ","{0:.2f}".format((t3-t2)/3600.0),"* X CPUs per node"

	
def f_main():
	global cdash_ami
	global cdash_subnet
	global configlocation
	global starcluster_config
	global sevenzip
	global mergeresults
	global downbest
	global numdown
	global terminator
	global shutdownnodes
	global convert
	global currency
	global dash_ami_location
	global verbose
	global tracker
	global allowinstances
	global maxnodes
	global ID
	global masternode_different
	global masternode_type
	global switchregion
	global region
	global region_host
	global switchkey
	global switchami
	global switchsubnet
	cdash_ami, cdash_subnet, configlocation, starcluster_config, sevenzip, mergeresults, downbest, numdown, \
	terminator, shutdownnodes, convert, currency, dash_ami_location, verbose, tracker, allowinstances, maxnodes, ID, \
	masternode_different, masternode_type, switchregion, region, region_host, switchkey, switchami, switchsubnet = getconfiguration()
	checkfiles()
	itype, numnodes, update_verbose_configuration = clusterprms(masternode_type)
	if switchregion == True:
		print "\nConfiguration option \"switchregion\" set to True."
		print "\nStarCluster will attempt to start a cluster in AWS region: "+region+".\n Check CDASH configuration if any problems occur."
		print "If CDASH crashes, check that the StarCluster configuration file has been correctly restored"
	print "\n\nIF CDASH IS INTERRUPTED, ENSURE THAT STARCLUSTER CONFIG IS RESTORED"
	print "USING THE BACKUP MADE IN ",configlocation," - config.backup"
	if switchregion == True:
		print "\n    Running in region",region
	
	t1 = time.time() # Start time
	if update_verbose_configuration == True:
		verbose = True
	sdiroot = dashprms()
	configSC(itype,numnodes,starcluster_config)
	numdown = zipper(sdiroot)
	writescripts(numnodes, numdown, mergeresults)
	startcluster(numnodes)
	t2 = time.time() # Time after cluster has started and files are distributed round
	runjobs()
	t3 = time.time() # Time after jobs have completed
	tdownload = shutdown(numnodes, numdown, mergeresults)
	cleanup()
	t4 = time.time() # Total time
	print "\n\n-------\nSetup time =","{0:.2f}".format((t2-t1)/60),"minutes."
	print "\nJob run time =","{0:.2f}".format((t3-t2)/60),"minutes."
	print "\nResult retrieval time =","{0:.2f}".format((t4-t3)/60),"minutes."
	print "\nTotal time =","{0:.2f}".format((t4-t1)/60),"minutes."
	hours = math.ceil((t4-t1)/3600) # Use math.ceil to round up the number of hours as Amazon charges in this manner.
	if shutdownnodes == True:
		total_hours = math.ceil((t4-t1)/3600) # Use math.ceil to round up the number of hours as Amazon charges in this manner.
		node_hours = math.ceil((tdownload-t1)/3600) # Use math.ceil to round up the number of hours as Amazon charges in this manner.
		# Calculate cost, and convert to local currency if needed
		if total_hours == node_hours:
			if masternode_different == True:
				usd = (numnodes-1)*hours*float(allowinstances[allowinstances.index(itype)+1]) + hours*float(allowinstances[allowinstances.index(masternode_type)+1])
			else:
				usd = numnodes*hours*float(allowinstances[allowinstances.index(itype)+1]) # Price in US dollars
			if convert == True:
				cost = convertcurrency(usd)
				print "\nEstimated cost in",currency,"=","{0:.2f}".format(cost)
			else:
				print "\nEstimated cost = $","{0:.2f}".format(usd) 
			if masternode_different == True:
				print "Based on the use of",numnodes-1,"instances of type",itype,"and one instance of type",masternode_type,"for",total_hours,"hours."
			else:
				print "Based on the use of",numnodes,"instances of type",itype,"for",total_hours,"hours."
			print "\n-------"
			cpuhours(itype,t2,t3,numnodes)
		else:
			if masternode_different == True:
				usd = (numnodes-1)*node_hours*float(allowinstances[allowinstances.index(itype)+1]) + total_hours*float(allowinstances[allowinstances.index(masternode_type)+1])
			else:
				usd = (numnodes-1)*node_hours*float(allowinstances[allowinstances.index(itype)+1]) + total_hours*float(allowinstances[allowinstances.index(itype)+1])
			if convert == True:
				cost = convertcurrency(usd)
				print "\nEstimated cost in",currency,"=","{0:.2f}".format(cost)
			else:
				print "\nEstimated cost = $","{0:.2f}".format(usd) 
			if masternode_different == True:
				print "Based on the use of",numnodes-1,"instances of type",itype,"for",node_hours,"and one instance of type",masternode_type,"for",total_hours,"hours."
			else:
				print "Based on the use of",numnodes-1,"instances of type",itype,"for",node_hours,"and one instance of type",itype,"for",total_hours,"hours."
			print "\n-------"
			cpuhours(itype,t2,t3,numnodes)
	else:
		if masternode_different == True:
			usd = (numnodes-1)*hours*float(allowinstances[allowinstances.index(itype)+1]) + hours*float(allowinstances[allowinstances.index(masternode_type)+1])
		else:
			usd = numnodes*hours*float(allowinstances[allowinstances.index(itype)+1]) # Price in US dollars
		if convert == True:
			cost = convertcurrency(usd)
			print "\nEstimated cost in",currency,"=","{0:.2f}".format(cost)
		else:
			print "\nEstimated cost = $","{0:.2f}".format(usd) 
		if masternode_different == True:
			print "Based on the use of",numnodes-1,"instances of type",itype,"for",hours,"and one instance of type",masternode_type,"for",hours,"hours."
		else:
			print "Based on the use of",numnodes,"instances of type",itype,"for",hours,"hours."
		print "\n-------"
		cpuhours(itype,t2,t3,numnodes)
	
	
	
# Used so this file can be used in a modular way or as a stand-alone script.	
if __name__ == '__main__':
	f_main()
	
	
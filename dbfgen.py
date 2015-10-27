import csv
import sys
import os

'''
Generate an arbitrary number of DASH dbf files based on one supplied as an input. This process will merely changes the seed values for each file.

Usage:

python dbfgen.py

or

python dbfgen.py input_dbf_file.dbf

or

python dbfgen.py input_dbf_file.dbf N
where N is an integer number of dbfs to generate.

'''


def getname():
	if len(sys.argv) > 1:
		file = sys.argv[1] # Specify the mol2 file from the command line
		file2 = file.partition('.') # This section checks to see if the full filename has been entered or just the root (without extension)
		if len(file2[2]) < 1:
			file = file+'.dbf'
		while not os.path.exists(file): # If the specified file can't be found, exit the program
			print 'Cannot find dbf called',file
			file = raw_input('Enter name of dbf: ')
			file2 = file.partition('.') # This section checks to see if the full filename has been entered or just the root (without extension)
			if len(file2[2]) < 1:
				file = file+'.dbf'
		#indbf = csv.reader(open(file, 'rb'), delimiter=' ') # input dbf
	else:
		file = raw_input('Enter name of dbf: ')
		file2 = file.partition('.') # This section checks to see if the full filename has been entered or just the root (without extension)
		if len(file2[2]) < 1:
			file = file+'.dbf'
		while not os.path.exists(file): # If the specified file can't be found, exit the program
			print 'Cannot find dbf called',file
			file = raw_input('Enter name of dbf: ')
			file2 = file.partition('.') # This section checks to see if the full filename has been entered or just the root (without extension)
			if len(file2[2]) < 1:
				file = file+'.dbf'
		#indbf = csv.reader(open(file, 'rb'), delimiter=' ') # input dbf
	return file, file2[0]

	
if __name__ == '__main__':
	file, root = getname()
	if len(sys.argv) > 2:
		num = int(sys.argv[2])
	else:
		num = int(raw_input("Enter number of dbf's to generate: "))
	store = []
	indbf = csv.reader(open(file, 'rb'), delimiter=' ') # input dbf
	i = 0
	for line in indbf:
		line = filter(None,line)
		if line[0] == "SEED1":
			seed1 = [int(line[1]),i]
		if line[0] == "SEED2":
			seed2 = [int(line[1]),i]
		if line[0] == "OUT":
			out = i
		store.append(line)
		i+= 1
	i = 0
	j = 0
	while i < num:
		if (i != 0) and (i % 1000 == 0): # DASH can only deal with numbers of runs up to 999 so this splits files into groups of powers of 1000, with a chunk size of 999 for easier processing later.
			j += 1
			if j > 1:
				num += 1 # Compensate for the files being split into chunks of 999 rather than 1000.
		k = (i-(j*1000)) +1
		if k < 10:
			dbf_out = root+'_'+str(j)+'_00'+str(k)+'.dbf'
		elif k < 100:
			dbf_out = root+'_'+str(j)+'_0'+str(k)+'.dbf'
		elif k < 1000:
			dbf_out = root+'_'+str(j)+'_'+str(k)+'.dbf'
		with open(dbf_out, 'wb') as out_file: 
			writer = csv.writer(out_file, delimiter=' ', quotechar='*', quoting=csv.QUOTE_NONE, escapechar=' ') # Open the csv writer for the dbf file.
			l = 0
			for line in store:
				if l == out:
					writer.writerow([dbf_out+'.dash'])
					l+=1
					continue
				if l == seed1[1]:
					writer.writerow(["SEED1  "+str(seed1[0]+i)])
					l+=1
					continue
				if l == seed2[1]:
					writer.writerow(["SEED1  "+str(seed2[0]+i)])
					l+=1
					continue
				writer.writerow(line)
				l+=1
			out_file.close()
			print k,'of 999 set',j+1
			i += 1
			

#!/usr/bin/env python

import sys,os
from subprocess import call, check_output
import argparse
from datetime import datetime
import re
#from scipy.interpolate import interp1d
#from scipy.interpolate import CubicSpline
#from scipy.signal import resample
import numpy as np 
import pandas as pd

starttime = datetime.now()

#logging colors
sectionColor = "\033[94m"
sectionColor2 = "\033[96m"
groupColor = "\033[90m"
mainColor = "\033[92m"

pink = '\033[95m'
yellow = '\033[93m'
red = '\033[91m'


#runs = [0,1,2,3]
# runs = [2]
# songs = ["rest","happy","sadln","sadsh"]
# songrates = ['hnl','snl_s','snl_l']
# song_timepoints =[360,183,515,271] #515 not 530 because already cut 10 from beginning and 5 from end
# rate_time =[168,256,515]
# conditions = ['emo','joy']

song = "sadln"
song_timepoint = '530'


#command line options
parser = argparse.ArgumentParser()

parser.add_argument("--subjects",help="process listed subjects",nargs='+',action="store")
parser.add_argument("--song",help="process listed subjects",nargs='+',action="store")
parser.add_argument("--all",help="process all subjects", action="store_true")
parser.add_argument("--half",help="process half subjects", action="store_true")

args = parser.parse_args()

def checkImageLength(imagename):
	command = 'fslinfo %s' % imagename
	results = check_output(command,shell=True)
	TR = results.split()[9]
	return int(TR)

#set paths
pathbase = "/Volumes/MusicProject/NaturalisticNetwork"
if not os.path.exists(pathbase):
	pathbase = "/Volumes/MusicProject-1/NaturalisticNetwork"
if not os.path.exists(pathbase):
	pathbase = "/Volumes/MusicProject-2/NaturalisticNetwork"

datapath = pathbase + "/fmri_analysis"	
dicompath = pathbase + "/fmri_data"

#Define number to cut from beginning
startvol = 20
cutvols = 20

#develop list of subjects
subjects = args.subjects

if args.all:
	#Get list of subjects
	subjects = os.listdir(datapath)
	subjects = [elem for elem in subjects if "sub" in elem]
	subjects = [elem for elem in subjects if "07" not in elem]
	subjects = [elem for elem in subjects if "pil" not in elem]
	subjects.sort()

if args.half:
	#Get list of subjects
	subjects = os.listdir(datapath)
	subjects = [elem for elem in subjects if "sub" in elem]
	subjects = [elem for elem in subjects if "07" not in elem]
	subjects = [elem for elem in subjects if "pil" not in elem]
	subjects.sort()
	subjects = subjects[0:19]

if subjects:
	print subjects
else:
	print "Subjects must be specified. Use --all for all subjects or --subjects to list specific subjects."
	sys.exit()

##CHECK ISC BETWEEN FD
df = pd.DataFrame()
count = 0
for subject in subjects:
	count = 1
	subjectfolder = "%s/%s/music/" % (datapath,subject)
	motionfdfile = "%s/metric_values_fd_%s" %(subjectfolder,song)
	if os.path.exists(motionfdfile):
		fd = pd.read_csv(motionfdfile, header = None)
		df = pd.concat([df,fd],axis = 1)

corrmat = df.corr()
motion_isc = corrmat.mean(axis = 1)
print motion_isc.mean()
isclist = motion_isc.tolist()

##CHECK ISC BETWEEN absolute motion
dfm = pd.DataFrame()
dfr = pd.DataFrame()
count = 0
for subject in subjects:
	count = 1
	subjectfolder = "%s/%s/music/" % (datapath,subject)
	restfolder = "%s/%s/rest/" % (datapath,subject)
	absmotion = "%s/%s_model1_pre_200hpf.feat/mc/prefiltered_func_data_mcf_abs.rms" %(subjectfolder,song)
	if os.path.exists(absmotion):
		rms = pd.read_csv(absmotion, header = None)
		print subject, rms.mean()
		dfm = pd.concat([dfm,rms],axis = 1)


	#Now do the same for rest
	restfolder = "%s/%s/rest/" % (datapath,subject)
	absmotionrest = "%s/resting_pre.feat/mc/prefiltered_func_data_mcf_abs.rms" %(restfolder)
	if os.path.exists(absmotionrest):
		rms = pd.read_csv(absmotionrest, header = None)
		print subject, rms.mean()
		dfr = pd.concat([dfr,rms],axis = 1)

corrmat = dfm.corr()
motion_isc = corrmat.mean(axis = 1)
print motion_isc.mean()

corrmat = dfr.corr()
motion_isc = corrmat.mean(axis = 1)
print motion_isc.mean()

isclist = motion_isc.tolist()


	

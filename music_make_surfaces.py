#!/usr/bin/python

#Preprocessing script for music naturalistic network study (June 2018)

import sys,os
from subprocess import call, check_output
import argparse
from datetime import datetime
import re
import shutil
from commando import commando
import numpy as np 
#import disutils

#logging colors
sectionColor = "\033[94m"
sectionColor2 = "\033[96m"
groupColor = "\033[90m"
mainColor = "\033[92m"

pink = '\033[95m'
yellow = '\033[93m'
red = '\033[91m'

#Handle command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--subjects",help="process listed subjects",nargs='+',action="store")
parser.add_argument("--all",help="process all subjects", action="store_true")
parser.add_argument("--half",help="process half subjects", action="store_true")
args = parser.parse_args()

subjects = args.subjects

#analysislist = ["generic_resting_pre","generic_pre_music"]
runs = [3]
songs = ["happy","sadln","sadsh"]
#songs = ["SL"]
song_timepoints =[183,495,271] #changed to reflect 20 TRs cut from beginning

#set paths
pathbase = "/Volumes/MusicProject/NaturalisticNetwork"
if not os.path.exists(pathbase):
	pathbase = "/Volumes/MusicProject-1/NaturalisticNetwork"
if not os.path.exists(pathbase):
	pathbase = "/Volumes/MusicProject-2/NaturalisticNetwork"

analysispath = pathbase + "/fmri_analysis"
designpath = analysispath + "/scripts/designs" 
scriptspath = analysispath + "/scripts"
surfacepath = os.path.join(analysispath,"surfaces")


#Change FREESURFER ENVIRONMENT 
newsubjectsdir = os.path.join(analysispath,'freesurfer')
# os.environ['SUBJECTS_DIR'] = newsubjectsdir

os.putenv("SUBJECTS_DIR", "/Volumes/MusicProject/NaturalisticNetwork/fmri_analysis/freesurfer")
os.system("echo $VARIABLE")

#cmd = "export SUBJECTS_DIR='%s'; echo $MY_DATA" %(newsubjectsdir)
#os.system(cmd)

#develop list of subjects
subjects = args.subjects
if args.all:
	#Get list of subjects
	subjects = os.listdir(analysispath)
	subjects = [elem for elem in subjects if "sub" in elem]
	subjects = [elem for elem in subjects if "07" not in elem]
	subjects = [elem for elem in subjects if "pil" not in elem]
	subjects.sort()

if args.half:
	#Get list of subjects
	subjects = os.listdir(analysispath)
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

def checkImageLength(imagename):
	command = 'fslinfo %s' % imagename
	results = check_output(command,shell=True)
	TR = results.split()[9]
	return int(TR)


for subject in subjects:

	#rename export folder to DICOM
	subjectfolder = "%s/%s/"  %(analysispath,subject)
	restfolder = subjectfolder + 'rest/'
	restingreg = '%sresting_pre.feat/reg' %(restfolder)
	funcfolder = subjectfolder + 'music/'
	checkfile1 = newsubjectsdir + '/' + subject + "/label/BA.ctab"

	if not os.path.exists(checkfile1):
		print sectionColor2 + '%s: Making surfaces part 1...%s' %(subject,mainColor)
		command = "recon-all -i %s/%s/mprage.nii.gz -subjid %s" % (analysispath,subject,subject)
		#command = "recon-all -autorecon2-noaseg -subjid %s" % (subject)
		call(command,shell=True)

		print sectionColor2 + '%s: Making surfaces part 2...%s' %(subject,mainColor)	
		command = "recon-all -all -subjid %s" % subject
		call(command,shell=True)
	else: 
		print red + 'Already made surfaces for %s. Moving on to registering...%s' %(subject,mainColor) 

	for run in runs:
		
		song = songs[run-1]

		#featdir = "%s%s_model1_stats_nopnm_cut20_tempderiv_200hpf.feat" % (funcfolder,song)
		featdir = "%s%s_model1_pre_200hpf.feat" %(funcfolder,song)
		checkregfile = '%s/reg/standard.nii.gz' %(featdir)
		checkfile = featdir + '/reg/freesurfer/aparc.a2009s+aseg.nii.gz'


		if not os.path.exists(featdir):
			print red + '%s does not exist. Moving on' %(featdir)
			continue

		#Check to make sure that standard reg has been copied from resting state
		#Then copy just the standards from reg
		if os.path.exists(restingreg):
			if not os.path.exists(checkregfile): 
				print sectionColor + 'Copying reg folder from resting state %s to %s%s' %(subject,featdir,mainColor)
				command = "%s/copyreg.sh %sresting_pre.feat %s" % (scriptspath,restfolder,featdir)
				call(command,shell=True)
		else: 
			print red + 'Cannot find reg folder for %s. Go check and moving on%s' %(subject,mainColor)


		if not os.path.exists(checkfile):
			print sectionColor2 + '%s: Registering feat to surfaces 1 for %s...%s' %(subject,song,mainColor)
			command = "reg-feat2anat --feat %s --subject %s" % (featdir,subject)
			call(command,shell=True)

			print sectionColor2 + '%s: Registering feat to surfaces 2 for %s...%s' %(subject,song,mainColor)
			command = "aseg2feat --feat %s --aseg aparc.a2009s+aseg" % (featdir)
			call(command,shell=True)
		
		else: 
			print red + 'Already registered surfaces for %s. They are in %s. Moving on...%s' %(subject,checkfile,mainColor)
			continue 


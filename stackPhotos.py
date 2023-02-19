""" Align and stack all images in a directory into a single image
    stackPhotos.py
    bcase 02Feb2023

    This program uses the 'align_image_stack' and 'enfuse' utilities from the
    Hugin project to create a single image from multiple images that were taken
    with different focus points.
    Macro photograpy projects can take hundreds of images, this program will
    process them in chunks of 10 images at a time to keep memory usage reasonable.
    Original images are not modified and final image has an unique name.
    """

import os
import subprocess
from datetime import datetime


def createFileDict(inList, modulus=20):
    """ Create dictionary from a list of files

    Save contents of entire input file list into a dictionary where each
    entry has a list of 20 file names. Each dictonary key is a one-up
    integer value starting from zero.

    Args:
       inList - list of all file names from current directory to process
       modulus - number of file names to store in each entry
    Returns:
       Dictionary collection of all files to process
    """
    listCount = 0  # dictionary key value
    fileDict = {}
    list1 = []
    for index, name in enumerate(inList, start=1):
        list1.append(name)
        if index % modulus == 0:
            fileDict[listCount]=list1  # store entry list into dictionary
            listCount+=1
            list1 = list()
        # handle end of file names that don't land on the modulus
        if index == len(inList):
            fileDict[listCount]=list1

    return fileDict

def runSubProcess(cmdList):
    result = subprocess.run(cmdList, capture_output=True, encoding='UTF-8')
    print("\t\t",result.stdout)
    result.check_returncode()  # throws CalledProcessError if returncode is non-zero
    return result  # returns class subprocess.CompletedProcess

def executeAlignCmd(fileList):
    cmd = ["align_image_stack", "-m", "-a", "OUT"]+fileList
    result = runSubProcess(cmd) # cmd results printed in this function
    return result.returncode

def executeStackCmd(stackedFileName):
    outFile = " --output="+stackedFileName
    cmd="enfuse --exposure-weight=0 --saturation-weight=0 --contrast-weight=1 --hard-mask"
    cmd +=outFile
    cmd += ' OUT*.tif'
    # run in shell mode so wildcards can be accepted
    result = subprocess.run(cmd, capture_output=True, encoding='UTF-8', shell=True)
    print("\t\t", result)
    return result.returncode

def deleteFiles(fileName):
    cmd = "rm "+fileName
    # run in shell mode so wildcards can be accepted
    result = subprocess.run(cmd, capture_output=True, encoding='UTF-8', shell=True)
    print("\t\t", result)
    return result.returncode

# Main

print("\n\t Starting to stack all JPG images")
startTime = datetime.now()

fList=[]
with os.scandir() as it:
    for entry in it:
        if entry.name.endswith(".JPG"):
            fList.append(entry.name) # no guarrenteed order

fList.sort() # place filenames in sorted order
allFileDict = createFileDict(fList, modulus=10)  # 20 files per dictionary entry

subject=input("\n\t Enter the subject name (one word) : ")
summaryTxt = "\t Processing {numF} total images of{subj} in {chk} chunks"
print(summaryTxt.format(numF=len(fList), subj=subject, chk=len(allFileDict)))

tempStackedFileList = [] # keep track of output stack name of each chunk
try :
        # for each dictionary entry
    for key in allFileDict.keys():
        print("\n\t working on file chunk #", key+1)
        print("\t\taligning pictures...")

        #   create align command and execute it
        executeAlignCmd(allFileDict.get(key))

        #   create enfuse command and execute it
        tempStackFilename = "stack_"+str(key)+".tif"
        print("\t\tstacking pictures...")
        executeStackCmd(tempStackFilename)
        tempStackedFileList.append(tempStackFilename) # keep track of filename

        #   remove OUTxxx.tif files created by align command
        print("\n\t\tdeleting temp pictures...")
        deleteFiles("OUT*.tif")

    print(" tempStackedFileList = ", tempStackedFileList)
    # align and stack the temp stacked files to create final image
    executeAlignCmd(tempStackedFileList)

    # create unique file name
    fts=datetime.now().strftime("%Y%m%d_%H%M%S.tif") #add file timestamp to make it unique
    ofnTxt="{subj}Stacked{fnum}_{ts}"
    ofn=ofnTxt.format(subj=subject, fnum=len(fList), ts=fts) # output file name
    executeStackCmd(ofn)

    # Housecleaning
    deleteFiles("OUT*.tif")
    #deleteFiles("stack_*.tif") # might be useful to keep for image troubleshooting
    stopTime = datetime.now()

    print("\n\t ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("\t       Stacking of ",len(fList)," images completed - "+ofn+"\n")
    print("\t\t Total processing time = ",stopTime-startTime)
    print("\t ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

except Exception as e:
    print(e)

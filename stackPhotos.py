""" Align and stack all images in a directory into a single image
    stackPhotos.py
    bcase 02Feb2023

    This program uses the 'align_image_stack' and 'enfuse' utilities from the
    Hugin project to create a single image from multiple images that were taken
    with different focus points.
    Macro photograpy projects can take hundreds of images, this program will
    process them in chunks of 10 images at a time to keep memory usage reasonable.
    Original images are not modified and final image has an unique name.

    Invoke from directory containing images to be stacked
    $ python3 stackPhotos.py
    """

import os
import subprocess
import time
from datetime import datetime
import cv2
import rawpy
from PIL import Image

RAW_FORMATS = ['CR2', 'CR3', 'NEF']

def isRAW(extension):
    """ Determine if input extension type is a supported RAW file type

    Args:
       extension - filename extension, case insensitive (i.e. jpg, CR3)
    Returns:
    boolean True if RAW extension, False otherwise
    """
    result = False
    if extension.upper() in RAW_FORMATS:
        result = True
    return result

def determineFileTypes():
    """ Return a dictionary of all file types in current directory

    Create a dictionary of all file extensions and the count of each type
    from the current directory

    Returns:
    ftDict - file type dictionary
    """
    ftDict = {} # file type dictionary
    with os.scandir() as it:
        for entry in it:
            name = entry.name.split('.')
            # print('looking at extension: '+name[-1])
            if name[-1] in ftDict:
                ftDict[name[-1]] += 1
            else:
                ftDict[name[-1]] = 1
    return ftDict

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
            list1 = []
        # handle end of file names that don't land on the modulus
        if index == len(inList):
            if len(list1) > 0:  # ensure we have something valid to save
                fileDict[listCount]=list1

    return fileDict

def runSubProcess(cmdList):
    result = subprocess.run(cmdList, capture_output=True, encoding='UTF-8')
    print("\t\t {}\n".format(result.stdout))
    #print("\t\t",result.stdout)
    result.check_returncode()  # throws CalledProcessError if returncode is non-zero
    return result  # returns class subprocess.CompletedProcess

def convertRaw(files, useJpg=True):
    """ Convert RAW images into JPG or TIFF format for later processing.
    Take a list of filenames and convert them from RAW to a format that can be
    alighned and stacked. Images are either saved as JPEG or TIFF format. Testing
    determined that JPEG format was stacked with better details, so this is the
    default. Return a list of new unique filenames of the converted images so the
    original images are preserved in the directory.
    Args:
       files - List of all file names from current directory to process

    Returns:
       List of new filenames saved in current directory
     """
    convertedFiles = []
    for srcFile in files:
        name = srcFile.split('.')
        raw = rawpy.imread(srcFile)
        rgb = raw.postprocess(use_camera_wb=True)

        if useJpg:
            fname = name[0]+'_temp.JPG'
            Image.fromarray(rgb).save(fname, quality=99, optimize=True)
        else:
            fname = name[0]+'_temp.TIFF'
            Image.fromarray(rgb).save(fname)

        convertedFiles.append(fname)
        raw.close()
    return convertedFiles

def executeAlignCmd(fileList, imageExtension):
    images = []
    if isRAW(imageExtension):
        images = convertRaw(fileList)
    else:
        images = fileList
    cmd = ["align_image_stack", "-m", "-a", "OUT"]+images
    result = runSubProcess(cmd) # cmd results printed in this function
    if isRAW(imageExtension):
        # delete temp files to save disk space. Original RAW images not not touched
        for name in images:
            deleteFiles(name)
    return result.returncode

def executeStackCmd(stackedFileName, inputFile='OUT*.tif'):
    outFile = " --output="+stackedFileName
    cmd="enfuse --exposure-weight=0 --saturation-weight=0 --contrast-weight=1 --hard-mask"
    cmd +=outFile
    cmd += (" "+ inputFile)
    # run in shell mode so wildcards can be accepted
    result = subprocess.run(cmd, capture_output=True, encoding='UTF-8', shell=True)
    print("\t\t {}\n".format(result))
    return result.returncode

def deleteFiles(fileName):
    cmd = "rm "+fileName
    # run in shell mode so wildcards can be accepted
    result = subprocess.run(cmd, capture_output=True, encoding='UTF-8', shell=True)
    print("\t\t", result)
    return result.returncode

def updateEXIF(inFile, outFile):
    print("\n\t\t Restore/update EXIF tags from {} into {}".format(inFile, outFile))
    cmd = "exiftool -tagsFromFile "+inFile
    cmd+=" -overwrite_original "+outFile
    result = subprocess.run(cmd, capture_output=True, encoding='UTF-8', shell=True)
    print("\t\t {}\n".format(result))
    return result.returncode


# Main
# examine current directory, print file extensions, and prompt user for which
# file types to process
fTypes = determineFileTypes()
print('e\t Directory contains the following file types:')
for entry in fTypes:
    print('\t Extension: {} \t Entries: {}'.format(entry, fTypes[entry]))
while True:
    imageType = input('\n\t Select a image file type to stack: ')
    if imageType in fTypes.keys():
        break

    print('\t Invalid selection: '+imageType) # loop back up and prompt again

print("\n\t Starting to stack all {} images".format(imageType))
startTime = datetime.now()

# fetch list of file names associated with the selected image type
fList=[]
with os.scandir() as it:
    for entry in it:
        if entry.name.endswith("."+imageType):
            fList.append(entry.name) # no guarrenteed order

fList.sort() # place filenames in sorted order
allFileDict = createFileDict(fList, modulus=10)  # 10 files per dictionary entry

subject=input("\n\t Enter the subject name (one word) : ")
summaryTxt = "\t Processing {numF} total images of < {subj} > in {chk} chunks"
print(summaryTxt.format(numF=len(fList), subj=subject, chk=len(allFileDict)))

tempStackedFileList = [] # keep track of output stack name of each chunk
try :
        # for each dictionary entry
    for key in allFileDict.keys():
        print("\n\t working on file chunk #", key+1)
        print("\t\taligning pictures...")

        #   create align command and execute it
        executeAlignCmd(allFileDict.get(key), imageType)

        #   create enfuse command and execute it
        tempStackFilename = "stack_"+str(key)+".tif"
        print("\t\tstacking pictures...")
        executeStackCmd(tempStackFilename)
        tempStackedFileList.append(tempStackFilename) # keep track of filename

        #   remove OUTxxx.tif files created by align command
        print("\t\tdeleting temp pictures...")
        deleteFiles("OUT*.tif")

    print(" tempStackedFileList = ", tempStackedFileList)

    # create unique file name
    fts=datetime.now().strftime("%Y%m%d_%H%M%S.tif") #add file timestamp to make it unique
    ofnTxt="{subj}Stacked{fnum}_{ts}"
    ofn=ofnTxt.format(subj=subject, fnum=len(fList), ts=fts) # output file name

    # align and stack the temp stacked files to create final image
    if len(tempStackedFileList) > 1:
        executeAlignCmd(tempStackedFileList, "tif")
        executeStackCmd(ofn)
    else:
        executeStackCmd(ofn, "stack_0.tif")

    time.sleep(5) # let final image flush to disk
    updateEXIF(fList[0], ofn)

    # Housecleaning
    deleteFiles("OUT*.tif")
    #deleteFiles("stack_*.tif") # might be useful to keep for image troubleshooting
    stopTime = datetime.now()

    print("\n\t ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("\t       Stacking of ",len(fList)," images completed - "+ofn+"\n")
    print("\t\t Total processing time = ",stopTime-startTime)
    print("\t ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    time.sleep(2)

    # display final stacked image. Used OpenCV beccause Pillow could not handle
    # 16bit color image
    img = cv2.imread(ofn)
    width = int(img.shape[1]*.25)
    height = int(img.shape[0]*.25)
    image = cv2.resize(img, (width,height))
    cv2.imshow(ofn+" resized to 25% for quick display - Press any key to close", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

except Exception as e:
    print(e)

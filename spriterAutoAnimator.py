import re
import os

def createFolder(frameFolderName, projectFileText):
    print(f"\ncreateFolder()")
    if re.search(rf"<folder id=\"\d+\" name=\"{frameFolderName}\">.*?</folder>", projectFileText, re.S) == None:
        isNewFolder = True
        # create new folder
        folderID = len(re.findall(rf"<folder id=\"(\d+)\" name=\"{frameFolderName}\">.*?</folder>", projectFileText, re.S)).group(1)
        folder = f"\t<folder id=\"{folderID}\" name=\"{frameFolderName}\">\n\t</folder>"
    else:
        isNewFolder = False
        folder = re.search(rf"<folder id=\"\d+\" name=\"{frameFolderName}\">.*?</folder>", projectFileText, re.S).group()
        folder = f"\t{folder}"
        folder = re.sub(r".*</folder>", "\t</folder>", folder)
    fileID = 0
    for frame in os.listdir(frameFolderName):
        if re.search(f"{frameFolderName}/{frame}", projectFileText) == None:
            # add file to folder
            file = f"<file id=\"{fileID}\" name=\"{frameFolderName}/{frame}\" pivot_x=\"0\" pivot_y=\"1\"/>"
            folder = re.sub("(</folder>)", rf"\t{file}\n\t\g<1>", folder)
        else:
            # Bumps existing files into proper indentation
            folder = re.sub(f"(<file id=\"{fileID}\" name=\"{frameFolderName}/{frame}\"[^/]*/>)", r"\g<1>", folder)
        fileID += 1
    print(folder)
    return(folder, isNewFolder)

def createAnimation(frameFolderName, projectFileText, repeatCount, setsOfProperties, folder):
    print("\ncreateAnimation()")
    
    # animation folder
    animationID = len(re.findall(r"<animation id=\"\d+\".*?</animation>", projectFileText, re.S))
    animationName = f"Auto Generated Animation {len(re.findall(r"Auto Generated Animation \d+", projectFileText))}"
    keyframeCount = len(os.listdir(frameFolderName)) * (repeatCount+1)
    # Variables are defined later
    animationText = f"\t</animation>"
        
    # timeline folders
    counter = 0
    for frame in os.listdir(frameFolderName):
        extensionlessFrame = re.sub(r"\..+$", "", frame)
        animationText = re.sub("</animation>", f"\t<timeline id=\"{counter}\" name=\"{extensionlessFrame}\">\n\t\t\t</timeline>\n\t\t</animation>", animationText)
        counter += 1
    
    # mainline + filling timeline folders
    animationText = "\t\t\t<mainline>\n\t\t\t</mainline>\n\t" + animationText
    currentSet = 0
    frameCounter = 0
    keyCounter = 0
    length = 0
    objects = ""
    for counter in range(keyframeCount):
        # mainline
        objects = f"<object_ref id=\"0\" timeline=\"{frameCounter}\" key=\"{keyCounter}\" z_index=\"0\"/>"
        # create key folder
        animationText = re.sub("</mainline>", f"\t<key id=\"{counter}\" time=\"{length}\">\n\t\t\t\t\t{objects}\n\t\t\t\t</key>\n\t\t\t</mainline>", animationText)
        
        # timeline
        keyID = len(re.findall("<key id=", re.search(f"<timeline id=\"{frameCounter}\".*?</timeline>", animationText, re.S).group()))
        key = f"<key id=\"{keyID}\" time=\"{length}\">\n\t\t\t\t</key>"
        fileID = re.search(rf"<file id=\"(\d+)\" name=\"{frameFolderName}/{os.listdir(frameFolderName)[frameCounter]}\"", folder).group(1)
        objectProperties = f"x=\"{setsOfProperties[currentSet]["x"]}\" y=\"{setsOfProperties[currentSet]["y"]}\" angle=\"{setsOfProperties[currentSet]["angle"]}\" pivot_x=\"{setsOfProperties[currentSet]["pivot_x"]}\" pivot_y=\"{setsOfProperties[currentSet]["pivot_y"]}\" scale_x=\"{setsOfProperties[currentSet]["scale_x"]}\" scale_y=\"{setsOfProperties[currentSet]["scale_y"]}\" a=\"{setsOfProperties[currentSet]["a"]}\""
        objectFolder = f"<object folder=\"0\" file=\"{fileID}\" {objectProperties}/>"
        animationText = re.sub(f"(<timeline id=\"{frameCounter}\".*?)(</timeline>)", rf"\g<1>\t{key}\n\t\t\t\g<2>", animationText, flags=re.S)
        animationText = re.sub(f"(<timeline id=\"{frameCounter}\".*?<key id=\"{keyID}\".*?)(</key>)", rf"\g<1>\t{objectFolder}\n\t\t\t\t\g<2>", animationText, flags=re.S)

        
        length += int(setsOfProperties[currentSet]["length"])
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
        frameCounter += 1
        if frameCounter == len(os.listdir(frameFolderName)):
            frameCounter = 0
            keyCounter += 1
    print(animationText)
    animationText = f"\t\t<animation id=\"{animationID}\" name=\"{animationName}\" length=\"{length}\">\n{animationText}"
    return(animationText)

def updateFile(frameFolderName, projectFileText, repeatCount, setsOfProperties):
    print(f"\nupdateFile()")
    folder, isNewFolder = createFolder(frameFolderName=frameFolderName, projectFileText=projectFileText)
    animation = createAnimation(frameFolderName=frameFolderName, projectFileText=projectFileText, repeatCount=repeatCount, setsOfProperties=setsOfProperties, folder=folder)

    if isNewFolder:
        outputText = re.sub("</folder>.+$", rf"\g<0>\n{folder}", projectFileText, flags=re.S)
    else:
        outputText = re.sub(rf"[^\n]*<folder id=\"\d+\" name=\"{frameFolderName}\">.*?</folder>", folder, projectFileText, flags=re.S)
    
    outputText = re.sub("(</animation>)(.+$)", rf"\g<1>\n{animation}\g<2>", projectFileText, flags=re.S)
    print(f"\n{outputText}")
    
    # creates the new animation file
    counter = 0
    while True:
        try:
            outputFile = open(f"spriter{counter}.scml", "x")
            break
        except:
            counter += 1
    outputFile = open(f"spriter{counter}.scml", "w")
    outputFile.write(outputText)
    print(f"spriter{counter}.scml created.")

frameFolderName = "redFrames"
projectFileText = open("redIdle.scml", "r").read()
repeatCount = 0
setsOfProperties = [{
    "x": "0",
    "y": "0",
    "angle": "0",
    "scale_x": "1",
    "scale_y": "1",
    "pivot_x": "0.5",
    "pivot_y": "0",
    "a": "1",
    "length": "200"
}]

updateFile(frameFolderName=frameFolderName, projectFileText=projectFileText, repeatCount=repeatCount, setsOfProperties=setsOfProperties)
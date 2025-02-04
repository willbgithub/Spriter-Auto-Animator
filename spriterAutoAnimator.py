import re
import os

def createFolder(projectFile, frameFolder):
    isolatedFrameFolder = re.search(r"[^\\]+$", frameFolder).group()
    # determine folder id
    if re.search(isolatedFrameFolder, projectFile):
        folderID = re.search(rf"<folder id=\"(\d+)\" name=\"{isolatedFrameFolder}\">.+?</folder>", projectFile, re.S).group(1)
        print("Frame folder already found in project file.")
        folder = re.search(f"<folder id=\"{folderID}\" name=\"{isolatedFrameFolder}\">", projectFile).group()
        fileID = 0
        for frame in os.listdir(frameFolder):
            isolatedFrame = re.search(r"[^\\]+$", frame).group()
            if re.search(rf"<file id=\"(\d+)\" name=\"{isolatedFrameFolder}/{isolatedFrame}\"", folder) == None:
                folder += f"\n\t\t<file id=\"{fileID}\" name=\"{isolatedFrameFolder}/{isolatedFrame}\"/>"
            fileID += 1
        folder += "\n\t</folder>"
        return(folder, False)
    # else
    folderID = len(re.findall(r"<folder id=\"\d+\" name=\"[^\"]+\">", projectFile))
    newFolder = f"\t<folder id=\"{folderID}\" name=\"{isolatedFrameFolder}\">"
    counter = 0
    for frame in os.listdir(frameFolder):
        newFolder += f"\n\t\t<file id=\"{counter}\" name=\"{isolatedFrameFolder}/{frame}\"/>"
        counter += 1
    newFolder += "\n\t</folder>"
    print("New folder created.")
    return(newFolder, True)
        
def createAnimation(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames, folder, folderID):
    animationID = len(re.findall(r"<animation id=\"\d+\" name=\"[^\"]+\">", projectFile))
    counter = 0
    while re.search(rf"<animation id=\"\d+\" name=\"animation{counter}\">", projectFile):
        counter+=1
    animationName = f"animation{counter}"
    length = 0
    currentSet = 0
    for frame in os.listdir(frameFolder):
        length += int(setsOfProperties[currentSet]["length"])
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
    length *= (repeatCount+1)
    animationText = f"\t\t<animation id=\"{animationID}\" name=\"{animationName}\" length=\"{length}\">"

    # mainline
    animationText += "\n\t\t\t<mainline>"
    keyframeAmount = len(setsOfProperties) * (repeatCount+1) * len(os.listdir(frameFolder))
    counter = 0
    currentSet = 0
    time = 0
    objects = "\n\t\t\t\t\t<object_ref id=\"0\" timeline=\"0\" key=\"0\" z_index=\"0\"/>"
    while counter < keyframeAmount:
        animationText += f"\n\t\t\t\t<key id=\"{counter}\" time=\"{time}\">"
        animationText += f"{objects}"
        animationText += "\n\t\t\t\t</key>"
        time += int(setsOfProperties[currentSet]["length"])
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
        counter += 1
        if preserveFrames:
            objects += f"\n\t\t\t\t\t<object_ref id=\"{counter}\" timeline=\"{counter}\" key=\"0\" z_index=\"{counter}\"/>"
        else:
            objects = f"\n\t\t\t\t\t<object_ref id=\"0\" timeline=\"{counter}\" key=\"0\" z_index=\"{counter}\"/>"
    animationText += "\n\t\t\t</mainline>"

    # timeline
    counter = 0
    currentSet = 0
    isolatedFrameFolder = re.search(r"[^\\]+$", frameFolder).group()
    startingTime = 0
    for frame in os.listdir(frameFolder):
        objectProperties = f"x=\"{setsOfProperties[currentSet]["x"]}\" y=\"{setsOfProperties[currentSet]["y"]}\" angle=\"{setsOfProperties[currentSet]["angle"]}\" scale_x=\"{setsOfProperties[currentSet]["scale_x"]}\" scale_y=\"{setsOfProperties[currentSet]["scale_y"]}\" pivot_x=\"{setsOfProperties[currentSet]["pivot_x"]}\" pivot_y=\"{setsOfProperties[currentSet]["pivot_y"]}\" a=\"{setsOfProperties[currentSet]["a"]}\""
        isolatedFrame = re.search(r"[^\\]+$", frame).group()
        fileID = re.search(rf"<file id=\"(\d+)\" name=\"{isolatedFrameFolder}/{isolatedFrame}\"", folder).group(1)
        animationText += f"\n\t\t\t<timeline id=\"{counter}\" name=\"{isolatedFrame}\">"
        keyCounter = 0
        while keyCounter < repeatCount+1:
            animationText += f"\n\t\t\t\t<key id=\"{keyCounter}\" time=\"{startingTime}\">"
            animationText += f"\n\t\t\t\t\t<object folder=\"{folderID}\" file=\"{fileID}\" {objectProperties}/>"
            animationText += f"\n\t\t\t\t</key>"
            keyCounter += 1
        animationText += "\n\t\t\t</timeline>"
        startingTime += int(setsOfProperties[currentSet]["length"])
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
        counter += 1
    animationText += "\n\t\t</animation>"
    return(animationText)

def animateProjectFile(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames):
    folder, isNewFolder = createFolder(projectFile, frameFolder)
    folderID = re.search(rf"\d+", folder).group()
    newAnimation = createAnimation(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames, folder, folderID)
    counter = 0
    while True:
        try:
            open(f"Spriter Auto Animation {counter}.scml", "x")
            break
        except:
            counter += 1
    outputFile = open(f"Spriter Auto Animation {counter}.scml", "w")
    outputText = projectFile
    if isNewFolder:
        outputText = re.sub(r"(.+</folder>)", rf"\g<1>\n{folder}", outputText, flags=re.S)
    else:
        outputText = re.sub(rf"<folder id=\"{folderID}\".*?</folder>", folder, outputText, flags=re.S)
    outputText = re.sub(rf"(.+</animation>)", rf"\g<1>\n{newAnimation}", outputText, flags=re.S)
    outputFile.write(outputText)

    

projectFile = open(r"C:\\Users\wilje\Documents\\GitHub\Spriter-Auto-Animator\\glorpyFile.scml").read()
frameFolder = r"C:\\Users\wilje\Documents\\GitHub\Spriter-Auto-Animator\\imagesFolder"
setsOfProperties = [{
    "x": "15",
    "y": "20",
    "angle": "30",
    "scale_x": "1.5",
    "scale_y": "0.5",
    "pivot_x": "0.2",
    "pivot_y": "0.9",
    "a": "0.7",
    "length": "500"
},
{
    "x": "-15",
    "y": "-20",
    "angle": "-30",
    "scale_x": "0.5",
    "scale_y": "1.5",
    "pivot_x": "0.4",
    "pivot_y": "0.7",
    "a": "1",
    "length": "200"
}]
repeatCount = 0
preserveFrames = False
animateProjectFile(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames)
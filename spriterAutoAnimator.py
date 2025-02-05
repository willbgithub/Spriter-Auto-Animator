import re
import os

def createFolder(projectFile, frameFolder):
    isolatedFrameFolder = re.search(r"[^\\]+$", frameFolder).group()
    # determine folder id
    if re.search(isolatedFrameFolder, projectFile):
        folderID = re.search(rf"<folder id=\"(\d+)\" name=\"{isolatedFrameFolder}\">.+?</folder>", projectFile, re.S).group(1)
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
    return(newFolder, True)
        
def createAnimation(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames, folder, folderID):
    animationID = len(re.findall(r"<animation id", projectFile))
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
    print("Created mainline start.")
    keyframeCount = (repeatCount+1) * len(os.listdir(frameFolder))
    currentSet = 0
    time = 0
    keyNumber = 0
    resettingCounter = 0
    objects = "\n\t\t\t\t\t<object_ref id=\"0\" timeline=\"0\" key=\"0\" z_index=\"0\"/>"
    for counter in range(keyframeCount):
        animationText += f"\n\t\t\t\t<key id=\"{counter}\" time=\"{time}\">"
        print(f"Printed key id \"{counter}\" at time \"{time}\"")
        animationText += f"{objects}"
        print(f"Printed \"{objects}\"")
        animationText += "\n\t\t\t\t</key>"
        print(f"Capped key.")
        time += int(setsOfProperties[currentSet]["length"])
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
        if (counter+1) % len(os.listdir(frameFolder)) == 0:
            keyNumber += 1
            resettingCounter = -1
        if preserveFrames:
            objects += f"\n\t\t\t\t\t<object_ref id=\"{counter}\" timeline=\"{resettingCounter+1}\" key=\"{keyNumber}\" z_index=\"{counter}\"/>"
        else:
            objects = f"\n\t\t\t\t\t<object_ref id=\"0\" timeline=\"{resettingCounter+1}\" key=\"{keyNumber}\" z_index=\"0\"/>"
        resettingCounter += 1
    animationText += "\n\t\t\t</mainline>"
    print("Capped mainline")
    
    # timeline
    counter = 0
    time = 0
    currentSet = 0
    for frame in os.listdir(frameFolder):
        isolatedFrame = re.search(r"^[^\.]+", frame).group()
        animationText += f"\n\t\t\t<timeline id=\"{counter}\" name=\"{isolatedFrame}\">\n\t\t\t</timeline>"
        counter += 1
    counter = 0
    for index in range(keyframeCount):
        keyID = len(re.findall("<key id=\"", re.search(rf"<timeline id=\"{counter}\".*?</timeline>", animationText, re.S).group()))
        keyframe = f"\t<key id=\"{keyID}\" time=\"{time}\">\n\t\t\t\t</key>"
        animationText = re.sub(rf"(<timeline id=\"{counter}\" name=\"[^\"]+\">.*?)(</timeline>)", rf"\g<1>{keyframe}\n\t\t\t\g<2>", animationText, flags=re.S)
        time += int(setsOfProperties[currentSet]["length"])
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
        counter += 1
        if counter == len(os.listdir(frameFolder)):
            counter = 0
    counter = 0
    currentSet = 0
    loopCounter = 0
    print(animationText)
    for index in range(keyframeCount):
        fileID = re.search(f"<file id=\"({counter})\" name=\".*?{os.listdir(frameFolder)[counter]}", folder).group(1)
        objectProperties = f"x=\"{setsOfProperties[currentSet]["x"]}\" y=\"{setsOfProperties[currentSet]["y"]}\" angle=\"{setsOfProperties[currentSet]["angle"]}\" scale_x=\"{setsOfProperties[currentSet]["scale_x"]}\" scale_y=\"{setsOfProperties[currentSet]["scale_y"]}\" pivot_x=\"{setsOfProperties[currentSet]["pivot_x"]}\" pivot_y=\"{setsOfProperties[currentSet]["pivot_y"]}\" a=\"{setsOfProperties[currentSet]["a"]}\""
        currentSet += 1
        if currentSet == len(setsOfProperties):
            currentSet = 0
        objectFolder = f"<object folder=\"{folderID}\" file=\"{fileID}\" {objectProperties}/>"
        animationText = re.sub(rf"(<timeline id=\"{counter}\".*?<key id=\"{loopCounter}\".*?)(</key>)", rf"\g<1>\t{objectFolder}\n\t\t\t\t\g<2>", animationText, flags=re.S)
        print(animationText)
        counter += 1
        if counter == len(os.listdir(frameFolder)):
            counter = 0
            loopCounter += 1
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
repeatCount = 0
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
    "angle": "330",
    "scale_x": "0.5",
    "scale_y": "1.5",
    "pivot_x": "0.4",
    "pivot_y": "0.7",
    "a": "1",
    "length": "200"
}]
repeatCount = 1
preserveFrames = False
animateProjectFile(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames)
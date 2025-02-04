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
        return(folder)
    # else
    folderID = len(re.findall(r"<folder id=\"\d+\" name=\"[^\"]+\">", projectFile))
    newFolder = f"\t<folder id=\"{folderID}\" name=\"{isolatedFrameFolder}\">"
    counter = 0
    for frame in os.listdir(frameFolder):
        newFolder += f"\n\t\t<file id=\"{counter}\" name=\"{isolatedFrameFolder}/{frame}\"/>"
        counter += 1
    newFolder += "\n\t</folder>"
    print("New folder created.")
    return(newFolder)
        
def createAnimation(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames, folder):
    animationID = len(re.findall(r"<animation id=\"\d+\" name=\"[^\"]+\">", projectFile))
    counter = 0
    while re.search(rf"<animation id=\"\d+\" name=\"animation{counter}\">", projectFile):
        counter+=1
    animationName = f"animation{counter}"
    length = 0
    for set in setsOfProperties:
        length += int(set["length"])
    length *= (repeatCount+1) * len(os.listdir(frameFolder))
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
    isolatedFrameFolder = re.search(r"[^\\]+$", frameFolder).group()
    folderID = re.search(rf"\d+", folder).group()
    for frame in os.listdir(frameFolder):
        isolatedFrame = re.search(r"[^\\]+$", frame).group()
        fileID = re.search(rf"<file id=\"(\d+)\" name=\"{isolatedFrameFolder}/{isolatedFrame}\"", folder).group(1)
        animationText += f"\n\t\t\t<timeline id=\"{counter}\" name=\"{isolatedFrame}\">"
        keyCounter = 0
        for match in re.findall(f"<object_ref id=\"{counter}\"", animationText):
            animationText += f"\n\t\t\t\t<key id=\"{keyCounter}\">"
            animationText += f"\n\t\t\t\t\t<object folder=\"{folderID}\" file=\"{fileID}\"/>"
            animationText += f"\n\t\t\t\t</key>"
        animationText += "\n\t\t\t</timeline>"
        counter += 1
    print(animationText)

def animateProjectFile(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames):
    folder = createFolder(projectFile, frameFolder)
    newAnimation = createAnimation(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames, folder)

projectFile = open(r"C:\\Users\wilje\Documents\\GitHub\Spriter-Auto-Animator\\glorpyFile.scml").read()
frameFolder = r"C:\\Users\wilje\Documents\\GitHub\Spriter-Auto-Animator\\imagesFolder"
setsOfProperties = [{
    "x": "0",
    "y": "0",
    "angle": "0",
    "scale_x": "1",
    "scale_y": "1",
    "pivot_x": "0",
    "pivot_y": "1",
    "a": "1",
    "length": "333"
}]
repeatCount = 0
preserveFrames = False
animateProjectFile(projectFile, frameFolder, setsOfProperties, repeatCount, preserveFrames)
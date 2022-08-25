from asyncore import write
import json
import obj
import api
from os.path import join
from datetime import datetime

def writeToJSON():
    with open(join(obj.directory, "keys\\tree.json"), 'w') as w:
        w.write(json.dumps(obj.tree, indent=4))

def loadTreeJSON():
    with open(join(obj.directory, "keys\\tree.json")) as r:
        try:
            tree = dict(json.load(r))

        except:
            tree = {}

    obj.tree = tree

def resetTree():
    with open(join(obj.directory, "keys\\tree.json"), 'w') as w:
        w.write("")

def initializeTree():
    
    resetTree()
    loadTreeJSON()

    if obj.tokens == []:
        obj.tree = {}
        open(join(obj.directory, "keys\\tree.json")).close()

    if obj.tree == {}: #Tree is empty
        obj.tree["HEAD"] = {
            "lastUpdated":str(datetime.now())
        }
        obj.tree["CONTENT"] = {}

    for creds in obj.tokens:
        folderID = api.initializeRootFolder(creds[1])
        obj.tree["CONTENT"][creds[0]] = {
            "id": folderID,
            "content":{}
        }

    writeToJSON()
    loadTreeJSON()


def syncTree():
    for drive in obj.tree["CONTENT"]:
        print(drive)

        driveContent = obj.tree["CONTENT"][drive]["content"]
        driveId = obj.tree["CONTENT"][drive]["id"]

        fillDirectory(driveContent, driveId, drive)

    writeToJSON()
    loadTreeJSON()

def filterFolders(response):
    folders = {}
    files = {}

    for file in response:
        if (response[file]["type"] == "application/vnd.google-apps.folder"):
            folders.update({file:response[file]})

        else:
            files.update({file:response[file]})

    return folders, files

def fillDirectory(directory, id, drive):
    files = api.listFolderDirectoryAPI(
        api.getTokenCredentialsFromList(drive),
        id
    )

    folders, temp = filterFolders(files)
    for file in files:
        directory.update({file:files[file]})

    for folder in folders:
        fillDirectory(directory[folder]["content"], folder, drive)

def directoryToString():
    dirString = "/"

    if obj.octoDirectory == []:
        return "/"

    else:
        for part in obj.octoDirectory:
            dirString += part + "/"

    return dirString

def getFolderMeta():
    if obj.octoDirectory == []:
        return "/", "None"

    else:
        return obj.octoDirectory[len(obj.octoDirectory)-1], obj.octoDirectoryId
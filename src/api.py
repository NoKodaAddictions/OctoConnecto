import obj
import ui
from os.path import join, exists
from os import scandir, remove
from configparser import ConfigParser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from termcolor import colored

pointers = ConfigParser()
pointers.read(join(obj.directory, 'pointers.cfg'))

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

def checkPointers():
    try:
        print(f"src/keys/{pointers['API']['octo']}.json")
        open(join(obj.directory, f"src/keys/{pointers['API']['octo']}.json"))
        
    except Exception as e:
        pass

    else:
        obj.octo = True

    try:
        print(f"src/keys/{pointers['API']['octosecrets']}.json")
        open(join(obj.directory, f"src/keys/{pointers['API']['octosecrets']}.json"))
    
    except Exception as e:
        pass

    else:
        obj.octosecrets = True

def checkTokens():
    print("Checking tokens...")

    obj.tokenPass = 0
    obj.tokenFail = 0

    obj.tokens = []

    for token in scandir(join(obj.directory, "keys\\tokens")):
        if token.is_file() and token.name.endswith(".json"):
            obj.tokens.append([token.name, getTokenCredentials(token.name)])
            if initializeToken(token.name):
                print(f"{token.name}: {colored('Passed', 'green')}")
                obj.tokenPass += 1
            else:
                print(f"{token.name}: {colored('Failed', 'red')}")
                obj.tokenFail += 1
    
    obj.tokenCount = obj.tokenPass + obj.tokenFail
    ui.space()
    print(f"Tokens Passed: {obj.tokenPass} | Token Fail: {obj.tokenFail} | Total Tokens Tested: {obj.tokenCount}")
    
    if obj.tokenPass + obj.tokenFail == 0:
        print("No tokens found/registered")


def getTokenCredentials(tokenFile):
    if exists(join(obj.directory, f"keys\\tokens\\{tokenFile}")):
        try:
            creds = Credentials.from_authorized_user_file(
                join(obj.directory, f"keys\\tokens\\{tokenFile}"), 
                SCOPES
            )
    
            return creds

        except:
            return None

    else:
        print("NONE")
        return None

def getTokenCredentialsFromList(tokenFile):
    if obj.tokens == None or obj.tokens == []:
        return None

    else:
        for token in obj.tokens:
            if token[0] == tokenFile:
                return token[1]

        return None

def initializeToken(tokenFile):
    creds = getTokenCredentials(tokenFile)

    if not creds or not creds.valid:
        print(f"{tokenFile}: Credentials invalid. Checking expiration...")
        if creds and creds.expired and creds.refresh_token:
            print(f"{tokenFile}: Credentials expired. Requesting refresh...")
            try:
                creds.refresh(Request())

            except:
                print("Credentials revoked. Reinitializing...")
                remove(join(obj.directory, f"keys/tokens/{tokenFile}"))
                addToken(tokenFile.split(".json")[0])
                initializeToken(tokenFile)

            return True

        else:
            return False

    else:
        return True

def initializeRootFolder(creds):
    service = build("drive", "v3", credentials=creds)

    response = service.files().list(
        q="name='OctoConnecto' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()

    if not response['files']:
        file_metadata = {
            "name":"OctoConnecto",
            "mimeType":"application/vnd.google-apps.folder"
        }

        file = service.files().create(body=file_metadata, fields="id").execute()

        folder_id = file.get('id')

        print("NO RESPONSE: " + folder_id)

    else:
        folder_id = response['files'][0]['id']
        print("RESPONSE: " + folder_id)

    return folder_id

def listFolderDirectoryFromJSON():
    response = []

    if obj.octoDirectory == []:
        for token in obj.tokens:
            response.append(token[0])

    elif len(obj.octoDirectory) == 1:
        for file in obj.tree["CONTENT"][obj.octoDirectory[0]]["content"]:
            response.append([
                obj.tree["CONTENT"][obj.octoDirectory[0]]["content"][file]["name"],
                obj.tree["CONTENT"][obj.octoDirectory[0]]["content"][file]["type"],
                file
            ])

    return response
            

def listFolderDirectoryAPI(creds, folderID):
    try:    
        service = build("drive", "v3", credentials=creds)

        query = f"parents = '{folderID}'"
        output = {}

        response = service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=None
        ).execute()

        for file in response.get("files", []):
            output.update({
                file.get("id"):{
                    "name":str(file.get("name")),
                    "type":str(file.get("mimeType"))
                }
            })

        for entry in output:
            if output[entry]["type"] == "application/vnd.google-apps.folder":
                output[entry].update({"content":{}})

        return output

    except HttpError as e:
        print(f"-----------ERROR-----------\n{e}")
        print("---------------------------")
        
    return None

def addToken(email):
    flow = InstalledAppFlow.from_client_secrets_file(
        join(obj.directory, f"keys\\{pointers['API']['octosecrets']}.json"),
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open(join(obj.directory, f"keys\\tokens\\{email}.json"), 'w') as token:
        token.write(creds.to_json())

def removeToken(email):
    driveFound = False
    driveRemoved = False

    tempDir = obj.octoDirectory
    obj.octoDirectory = []

    drives = listFolderDirectoryFromJSON()

    for drive in drives:
        if drive == email:
            driveFound = True

            print(f"Are you sure you want to remove {drive}? (Y/n)")
            check = input("- ")

            if check == "y" or check == "Y":
                print(f"Removing {drive}...")
                remove(join(obj.directory, f"keys/tokens/{drive}"))
                driveRemoved = True

            elif check == "n" or check == "N":
                print(f"Not removing {drive}")
                obj.octoDirectory = tempDir

            else:
                print(f"Incorrect command input, not removing {drive}")
                obj.octoDirectory = tempDir
    
    if not driveFound:
        print("Drive not found")

    return driveRemoved
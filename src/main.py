import webbrowser
import api
import ui
import obj
import tree
import sys

__version__ = "0.1.0"

ui.clear()

api.checkPointers()

if obj.octo:
    print("ERROR: Octo service file not found!")
    input()
    sys.exit()

elif obj.octosecrets:
    print("ERROR: Octo secrets file not found!")
    input()
    sys.exit()

api.checkTokens()

tree.initializeTree()
tree.syncTree()

ui.clear()

print(f"Welcome to OctoConnecto | By NoKodaAddictions | {__version__}")

while True:
    if obj.tokenCount == 0:
        print("Enter Email Address: ")
        email = input("- ")
        api.addToken(email)
        ui.clear()
        api.checkTokens()

    else:
        cmd = input(f"{tree.directoryToString()}>> ")
        
        if cmd == "restart":
            ui.clear()
            ui.restart()

        elif cmd == "version":
            print(__version__)

        elif cmd == "refresh":
            ui.clear()
            api.checkTokens()
            tree.initializeTree()
            tree.syncTree()

        elif cmd == "exit":
            ui.clear()
            sys.exit()

        elif cmd == "clear" or cmd == "cls":
            ui.clear()

        elif cmd == "add":
            print("Enter Email Address: ")
            email = input("- ")
            api.addToken(email)
            print("Restarting OctoConnecto")
            ui.restart()

        elif cmd == "remove":
            print("Enter Email Address: ")
            email = input("- ")

            if api.removeToken(email):
                print("Restarting OctoConnecto")
                ui.restart()      

        elif cmd == "json" or cmd == "tree":
            print(tree.json.dumps(obj.tree, indent=4))

        elif cmd == "list" or cmd == "ls":
            print(f"""
Listing Contents Of: {tree.directoryToString()}

Folder Name: {tree.getFolderMeta()[0]}
Folder ID: {tree.getFolderMeta()[1]}
""")
            if obj.octoDirectory == []:
                for file in api.listFolderDirectoryFromJSON():
                    print(file)

            elif len(obj.octoDirectory) == 1:
                for file in api.listFolderDirectoryFromJSON():
                    print(file[0] + ", " + file[1] + ", " + file[2])

            else:
                response = api.listFolderDirectoryAPI(
                    api.getTokenCredentialsFromList(obj.octoDirectory[0]),
                    obj.octoDirectoryId    
                )

                for file in response:
                    print(response[file]["name"] + ", " + response[file]["type"] + ", " + file)
            
            ui.space()

        elif cmd == "cd..":
            obj.octoDirectory = obj.octoPrevDirectory
            obj.octoDirectoryId = obj.octoPrevDirectoryId

            if obj.octoPrevDirectory != []:
                obj.octoPrevDirectory.pop(len(obj.octoPrevDirectory)-1)

        elif "cd" in cmd:
            folderFound = False

            command = cmd.split(" ")

            if len(command) == 1:
                print("Please specify a folder")

            else:
                if obj.octoDirectory == []:
                    drives = api.listFolderDirectoryFromJSON()

                    for drive in drives:
                        if drive == command[1]:
                            obj.octoDirectory.append(drive)
                            obj.octoDirectoryId = obj.tree["CONTENT"][drive]["id"]

                            folderFound = True


                elif len(obj.octoDirectory) == 1:
                    files = api.listFolderDirectoryFromJSON()

                    for file in files:
                        if file[0] == command[1] and file[1] == "application/vnd.google-apps.folder":
                            obj.octoPrevDirectory = obj.octoDirectory
                            obj.octoPrevDirectoryId = obj.octoDirectoryId

                            obj.octoDirectory.append(file[0])
                            obj.octoDirectoryId = file[2]

                            folderFound = True
                            break

                
                else:
                    folders, temp = tree.filterFolders(
                        api.listFolderDirectoryAPI(
                            api.getTokenCredentialsFromList(obj.octoDirectory[0]),
                            obj.octoDirectoryId    
                        )
                    )

                    for folder in folders:
                        if folders[folder]["name"] == command[1]:
                            obj.octoDirectory.append(folders[folder]["name"])
                            obj.octoDirectoryId = folder

                            folderFound = True
                            break

                if not folderFound:
                    print("Folder or drive not found")

        elif "add" in cmd:
            command = cmd.split(" ")

            if len(command) == 1:
                print("Please specify an email address")

            else:
                api.addToken(command[1])
                ui.clear()
                print("Restarting OctoConnecto")
                ui.restart()

            

        elif "remove" in cmd:
            command = cmd.split(" ")

            if len(command) == 1:
                print("Please specify an email address")

            else:
                if api.removeToken(command[1]):
                    print("Restarting OctoConnecto")
                    ui.restart()  


        elif "open" in cmd:
            folderFound = False

            command = cmd.split(" ")
            
            if len(command) == 1:
                print("Please specify a folder or file")
            
            else:
                if len(obj.octoDirectory) == 1:
                    files = api.listFolderDirectoryFromJSON()

                    for file in files:
                        
                        if file[0] == command[1] and file[1] == "application/vnd.google-apps.folder":
                            print(f'https://drive.google.com/drive/folders/{file[2]}')
                            webbrowser.open_new(f'https://drive.google.com/drive/folders/{file[2]}')
                            folderFound = True
                            break

                
                else:
                    folders, temp = tree.filterFolders(
                        api.listFolderDirectoryAPI(
                            api.getTokenCredentialsFromList(obj.octoDirectory[0]),
                            obj.octoDirectoryId    
                        )
                    )

                    for folder in folders:
                        print(folder)
                        if folders[folder]["name"] == command[1]:
                            print(f'https://drive.google.com/folders/{folder}')
                            webbrowser.open_new(f'https://drive.google.com/folders/{folder}')
                            folderFound = True
                            break

                if not folderFound:
                    print("Folder not found")

        else:
            print("Unknown Command")
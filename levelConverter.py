#######################################
# 2.1 level format to 1.9 level auto converter
# for the truest dashers
# uploads to servers automatically and unlisted
# by zmx
######################################

import objCharts
import re
import levelUtil, levelDownloader, saveUtil, sys, base64, objCharts, httpRequest
import os # for error codes
from typing import Dict
from commonTypes import LevelString, RobDict

def uploadLevel(levelString: bytes, levelInfo: RobDict) -> int:
	'''
	Uploads a level to 1.9 servers
	'''

	url = "https://absolllute.com/gdps/gdapi/uploadGJLevel19.php"

	# 1.9 descriptions aren't base64 encoded, we need to remove illegal characters before upload breaks them anyways
	desc: str = base64.urlsafe_b64decode(levelInfo["3"]).decode()
	desc = re.sub(r"[^A-Za-z0-9\., \$\-\_\.\+\!\*\'()]", "", desc) # remove anything not url safe

	# some params don't exist
	postdata = {"gjp": '', "gameVersion": 19, "userName": "21Reupload",
						"unlisted": "1", "levelDesc": desc,
						"levelName": levelInfo["2"], "levelVersion": levelInfo["5"],
						"levelLength": levelInfo["15"], "audioTrack": levelInfo["12"],
            "password": 1, "original": levelInfo["1"], "songID": levelInfo.get("35", 0),
						"objects": levelInfo.get("45", 0), "udid": "hi absolute :)"}
	postdata["levelString"] = levelString

	uploadRequest = httpRequest.postRequest(url, postdata)

	try:
		levelID: int = int(uploadRequest)
		if levelID == -1:  # -1 is an error dumb
				throw
		return levelID
	except:
		print(f"Error occured while reuploading:\n{uploadRequest}")
		raise Exception()

if __name__ == "__main__":
	print("~ 1.9 Level Reuploader by zmx ~\n")

	mainID: int = 128
	try:
		mainID = int(sys.argv[1])
	except:
		print(f"""Usage: {sys.argv[0]} <id>\n
set env variable DRY to true to skip upload
set env variable CLUB to true to convert clubstep blocks 1-8
set env variable GLOW to true to convert the full glow blocks""")
		sys.exit(os.EX_USAGE)

	levelString: LevelString = LevelString(b"")
	levelInfo: RobDict = RobDict({})

	try:
		levelString, levelInfo = levelDownloader.downloadLevel(mainID)
	except:
		print("invalid level!")
		sys.exit(os.EX_DATAERR)

	print(f"Downloaded level `{levelInfo['2']}`")
	if os.getenv("CLUB", False):
		print("Clubstep block conversion enabled!\nThis can make some levels impossible!")
		levelUtil.convClubstep = True
	if os.getenv("GLOW", False):
		print("Glow conversion enabled!")
		levelUtil.convGlow = True

	print("Converting...\n")

	# rob likes his levels encoded
	convLevel: LevelString = levelUtil.convLevelString(levelString)
	encodedLevel: bytes = saveUtil.encodeLevel(convLevel)

	illegalObjs: Dict[int, str] = levelUtil.illegalObjInfo(levelUtil.illegalObj)

	for objID, name in illegalObjs.items():
		print(f"Illegal object: {objID} ({name})")

	if set(levelUtil.illegalObj).intersection(objCharts.clubstepObjConv):
		print("Note: Enabling the CLUB environment variable will convert most of the clubstep blocks, but can make the level impossible!")
	if set(levelUtil.illegalObj).intersection(objCharts.glowObj):
		print("Note: Enabling the GLOW environment variable will convert most of the full glow blocks!")

	if not illegalObjs:
		print("All objects converted!")

	print("")

	if os.getenv("DRY", False):
		print("Dry mode enabled, no upload!")
		sys.exit()

	print("Uploading level...")
	try:
		levelID: int = uploadLevel(encodedLevel, levelInfo)
		print(f"Level reuploaded to id: {levelID}")
	except:
		print("couldn't reupload level!")

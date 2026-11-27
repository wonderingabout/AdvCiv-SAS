# Sid Meier's Civilization 4
# Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from BtS's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\Python\EntryPoints\CvAppInterface.py (the newest of the vanilla Civ4, Warlords and BtS copies), the copy SAS ran before (2026-11-22). See KI#1104. (Claude code Opus 5.5) -->
#
# CvAppInterface.py
#
# These functions are App Entry Points from C++
# WARNING: These function names should not be changed
# WARNING: These functions can not be placed into a class
#
# No other modules should import this
#
# DONT ADD ANY MORE IMPORTS HERE - Moose
import sys
import os
import CvUtil
#

from CvPythonExtensions import *
# <!-- custom: SASTextScale's addMessage and addImmediateMessage give Python's messages the label font the DLL gives its own, as CyInterface()'s went to the EXE at the stock size. See KI#117.2. (Claude code Opus 5.5) -->
import SASTextScale

# globals
gc = CyGlobalContext()

# don't make this an event - Moose
def init():
	# for PythonExtensions Help File
	PythonHelp = 0		# doesn't work on systems which haven't installed Python
			
	# dump Civ python module directory
	if PythonHelp:		
		import CvPythonExtensions
		helpFile=file("CvPythonExtensions.hlp.txt", "w")
		sys.stdout=helpFile
		import pydoc                  
		pydoc.help(CvPythonExtensions)
		helpFile.close()
	
	sys.stderr=CvUtil.RedirectError()
	sys.excepthook = CvUtil.myExceptHook
	sys.stdout=CvUtil.RedirectDebug()

def onSave():
	'Here is your chance to save data.  This function should return a string'
	import CvWBDesc
	import pickle	
	import CvEventInterface
	# if the tutorial is active, it will save out the Shown Messages list
	saveDataStr = pickle.dumps( CvEventInterface.onEvent( ('OnSave',0,0,0,0,0 ) ) )
	return saveDataStr
	
def onLoad(argsList):
	'Called when a file is loaded'
	import pickle	
	import CvEventInterface
	loadDataStr=argsList[0]	
	if len(loadDataStr):
		CvEventInterface.onEvent( ('OnLoad',pickle.loads(loadDataStr),0,0,0,0,0 ) )	

def preGameStart():
	import CvScreensInterface
	# <!-- custom: Applies SASLiveDefineOverrides when a game starts, before its screens are built; until then, such as at the main menu, the defines hold their XML values.
	# The first load sat in BugEventManager's setup at first, but Codex's review (GPT-6.2-Sol) found that BugInit runs it only once the game is fully initialized.
	# Imported here, as the file's note above asks for no more top-level imports.
	# This file is the mod's own copy since KI#1104, which is what made this hook an ordinary SAS edit. See KI#128.5. (Claude code Opus 5.5 + GPT-6.2-Sol) -->
	import SASLiveDefineOverridesBridge
	SASLiveDefineOverridesBridge.refresh()

	if not CyGame().isPitbossHost():
		NiTextOut("Initializing font icons")
		# Load dynamic font icons into the icon map
		CvUtil.initDynamicFontIcons()

	if not CyGame().isPitbossHost():
		# Preload the tech chooser..., only do this release builds, in debug build we may not be raising the tech chooser
		if (not gc.isDebugBuild()):
			NiTextOut("Preloading tech chooser")
			CvScreensInterface.showTechChooser()
			CvScreensInterface.techChooser.hideScreen()
		
	NiTextOut("Loading main interface...")
	CvScreensInterface.showMainInterface()	

def onPbemSend(argsList):
	# <!-- custom: The same five modules the PBEM mail sender always imported, one per line now, as Ruff's E401 asks. See KI#21.7. (Claude code Opus 5.5) -->
	import sys
	import smtplib
	import MimeWriter
	import base64
	import StringIO
			
	szToAddr = argsList[0]	
	szFromAddr = argsList[1]	
	szSubject = argsList[2]	
	szPath = argsList[3]
	szFilename = argsList[4]
	szHost = argsList[5]
	szUser = argsList[6]
	szPassword = argsList[7]
	
	# <!-- custom: BtS's Python 2 print statements became single-string print(...) calls, which Python 2.4 and Ruff both parse; "%s" keeps the one space a comma put between items. See KI#1104. (Claude code Opus 5.5) -->
	print('sending e-mail')
	print('To: %s' % szToAddr)
	print('From: %s' % szFromAddr)
	print('Subject: %s' % szSubject)
	print('Path: %s' % szPath)
	print('File: %s' % szFilename)
	print('Server: %s' % szHost)
	print('User: %s' % szUser)
	
	if len(szFromAddr) == 0 or len(szHost) == 0:
		# <!-- custom: was a Python 2 print statement, which Ruff cannot parse. See KI#1104. (Claude code Opus 5.5) -->
		print('host or address empty')
		return 1

	message = StringIO.StringIO()
	writer = MimeWriter.MimeWriter(message)

	writer.addheader('To', szToAddr)
	writer.addheader('From', szFromAddr)
	writer.addheader('Subject', szSubject)
	writer.addheader('MIME-Version', '1.0')
	writer.startmultipartbody('mixed')

	part = writer.nextpart()
	body = part.startbody('text/plain')
	body.write('CIV4 PBEM save attached')

	part = writer.nextpart()
	part.addheader('Content-Transfer-Encoding', 'base64')
	szStartBody = "application/CivBeyondSwordSave; name=%s" % szFilename
	body = part.startbody(szStartBody)
	base64.encode(open(szPath+szFilename, 'rb'), body)

	# finish off
	writer.lastpart()

	# send the mail
	try:
		smtp = smtplib.SMTP(szHost)
		# trying to get TLS to work...
		#smtp.set_debuglevel(1)
		#smtp.ehlo()
		#smtp.starttls()
		#smtp.ehlo()
		if len(szUser) > 0:
			smtp.login(szUser, szPassword)
		smtp.sendmail(szFromAddr, szToAddr, message.getvalue())
		smtp.quit()
	except smtplib.SMTPAuthenticationError, e:
		SASTextScale.addImmediateMessage("Authentication Error: The server didn't accept the username/password combination provided.", "")	
		SASTextScale.addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")	
		return 1
	except smtplib.SMTPHeloError, e:
		SASTextScale.addImmediateMessage("The server refused our HELO reply.", "")	
		SASTextScale.addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")	
		return 1
	except smtplib.SMTPConnectError, e:
		SASTextScale.addImmediateMessage("Error establishing connection.", "")	
		SASTextScale.addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")	
		return 1
	except smtplib.SMTPDataError, e:
		SASTextScale.addImmediateMessage("The SMTP server didn't accept the data.", "")	
		SASTextScale.addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")	
		return 1
	except smtplib.SMTPRecipientsRefused, e:
		SASTextScale.addImmediateMessage("All recipient addresses refused.", "")	
		return 1
	except smtplib.SMTPSenderRefused, e:
		SASTextScale.addImmediateMessage("Sender address refused.", "")	
		SASTextScale.addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")	
		return 1
	except smtplib.SMTPResponseException, e:
		SASTextScale.addImmediateMessage("Error %d: %s" % (e.smtp_code, e.smtp_error), "")	
		return 1
	except smtplib.SMTPServerDisconnected:
		SASTextScale.addImmediateMessage("Not connected to any SMTP server", "")	
		return 1
	except:
		return 1
	return 0

#####################################33
## INTERNAL USE ONLY
#####################################33
def normalizePath(argsList):
	CvUtil.pyPrint("PathName in = %s" %(argsList[0],))
	pathOut=os.path.normpath(argsList[0])
	CvUtil.pyPrint("PathName out = %s" %(pathOut,))
	return pathOut

def getConsoleMacro(argsList):
	'return a string macro that is used by the in-game python console, fxnKey goes from 1 to 10'
	fxnKey = argsList[0]
	# <!-- custom: Each if and its return on their own lines, as Ruff's E701 asks; the macros are unchanged. See KI#21.7. (Claude code Opus 5.5) -->
	if (fxnKey==1):
		return "player = gc.getPlayer(0)"
	if (fxnKey==2):
		return "import CvCameraControls"
	if (fxnKey==3):
		return "CvCameraControls.g_CameraControls.resetCameraControls()"
	if (fxnKey==4):
		return "CvCameraControls.g_CameraControls.doRotateCamera(360, 45.0)"
	if (fxnKey==5):
		return "CvCameraControls.g_CameraControls.doZoomCamera(0.2, 0.5)"
	if (fxnKey==6):
		return "CvCameraControls.g_CameraControls.doZoomCamera(0.5, 0.15)"
	if (fxnKey==7):
		return "CvCameraControls.g_CameraControls.doPitchCamera(0.5, 0.5)"
	return ""

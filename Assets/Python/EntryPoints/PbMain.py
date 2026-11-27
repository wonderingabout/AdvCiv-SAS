## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
#
# AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
# (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
#
# <!-- custom: Copied from BtS's C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization IV Beyond the Sword\Beyond the Sword\Assets\Python\EntryPoints\PbMain.py (the newest of the vanilla Civ4 and BtS copies), the copy SAS ran before (2026-11-26). See KI#1104. (Claude code Opus 5.5) -->
#
# Sample PitBoss window/app framework
# Mustafa Thamer 2-15-05
#
from CvPythonExtensions import *
import PbWizard
import PbAdmin

localText = CyTranslator()
app = None
bAdmin = False

#
# entry point function
# 
def create():
	global app
	app = PbWizard.StartupIFace(0)
	
#
# entry point function
#
def run():
	global app
	app.startWizard()
	
#
# entry point function
#
def update():
	global bAdmin
	global app
	
	if (not bAdmin):
		app = PbAdmin.AdminIFace(0)
		bAdmin = True
		
	app.update()
	
#
# entry point functions
#
def patchAvailable(argsList):
	global app
	patchName = argsList[0]
	patchUrl = argsList[1]
	app.patchAvailable(patchName, patchUrl)
	
def patchProgress(argsList):
	global app
	bytesRecvd = argsList[0]
	bytesTotal = argsList[1]
	app.patchProgress(bytesRecvd, bytesTotal)
	
def patchDownloadComplete(argsList):
	global app
	bSuccess = argsList[0]
	app.patchDownloadComplete(bSuccess)
	
def appUpToDate():
	app.upToDate()
	
def refreshRow(argsList):
	global app
	rowNum = argsList[0]
	app.refreshRow(rowNum)
	
def refreshCustomMapOptions(argsList):
	global app
	mapName = argsList[0]
	app.refreshCustomMapOptions(mapName)
	
def refreshAdvancedStartPoints(argsList):
	global app
	iPoints = argsList[0]
	app.refreshAdvancedStartPoints(iPoints)
	
def getMessageOfTheDay():
	global app
	return app.getMotD()
	
def addChatMessage(argsList):
	global app
	szMessage = argsList[0]
	app.addChatMessage(szMessage)
	
def displayMessageBox(argsList):
	global app
	szTitle = argsList[0]
	szDesc = argsList[1]
	app.displayMessageBox(szTitle, szDesc)
	
def sendEmail(argsList):
	# <!-- custom: One import per line, as CI's Ruff E401 asks; same modules, imported when an e-mail is sent. (Claude code Opus 5.5) -->
	import sys
	import smtplib
	import MimeWriter
	import base64
	import StringIO
			
	szAddr = argsList[0]	
	szHost = argsList[1]	
	szLogin = argsList[2]
	szPassword = argsList[3]
	szGameName = argsList[4]	
	bUseTimer = argsList[5]
	iTimeLeft = argsList[6]
	szFrom = argsList[7]
	szYear = argsList[8]
	
	if len(szAddr) == 0 or len(szHost) == 0:
		# <!-- custom: print x became print(x), the same output in Python 2.4, so CI's Ruff, which parses Python 3, can read this function (KI#21.7). (Claude code Opus 5.5) -->
		print('host or address empty')
		return 1

	print("sending e-mail")
	print("To: %s" % (szAddr, ))
	print("From: %s" % (szFrom, ))
	print("Server: %s" % (szHost, ))
	if len(szLogin) > 0:
		print("Login: %s" % (szLogin, ))
	else:
		print("Not using authentication")
	
	message = StringIO.StringIO()
	writer = MimeWriter.MimeWriter(message)

	writer.addheader('To', szAddr)
	writer.addheader('From', szFrom)
	writer.addheader('Subject', localText.getText("TXT_KEY_PITBOSS_EMAIL_SUBJECT", (szGameName, szYear)))
	writer.addheader('MIME-Version', '1.0')
	
	szBody = localText.getText("TXT_KEY_PITBOSS_EMAIL_BODY", (szGameName,))
	if (bUseTimer):
		szBody += u"\n"
		szBody += localText.getText("TXT_KEY_PITBOSS_EMAIL_TIMER", (iTimeLeft,))

	body = writer.startbody('text/plain')
	body.write(szBody)	

	# send the mail
	try:
		smtp = smtplib.SMTP(szHost)
		if len(szLogin) > 0:
			smtp.login(szLogin, szPassword)
		smtp.sendmail(szFrom, szAddr, message.getvalue())
		smtp.quit()
	except smtplib.SMTPAuthenticationError, e:
		print("Authentication Error: The server didn't accept the username/password combination provided.")
		print("Error %d: %s" % (e.smtp_code, e.smtp_error))
		return 1
	except smtplib.SMTPHeloError, e:
		print("The server refused our HELO reply.")
		print("Error %d: %s" % (e.smtp_code, e.smtp_error))
		return 1
	except smtplib.SMTPConnectError, e:
		print("Error establishing connection.")
		print("Error %d: %s" % (e.smtp_code, e.smtp_error))
		return 1
	except smtplib.SMTPDataError, e:
		print("The SMTP server didn't accept the data.")
		print("Error %d: %s" % (e.smtp_code, e.smtp_error))
		return 1
	except smtplib.SMTPRecipientsRefused, e:
		print("All recipient addresses refused.")
		return 1
	except smtplib.SMTPSenderRefused, e:
		print("Sender address refused.")
		print("Error %d: %s" % (e.smtp_code, e.smtp_error))
		return 1
	except smtplib.SMTPResponseException, e:
		print("Error %d: %s" % (e.smtp_code, e.smtp_error))
		return 1
	except smtplib.SMTPServerDisconnected:
		print("Not connected to any SMTP server")
		return 1
	except:
		return 1
	return 0
		

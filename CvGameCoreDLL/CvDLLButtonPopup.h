#pragma once

#ifndef CIV4_DLL_BUTTON_POPUP_H
#define CIV4_DLL_BUTTON_POPUP_H

class CvPopup;
class PopupReturn;
class CvPopupInfo;

// <!-- custom: SASPilot drives the game without the window, where a launched popup stays until someone clicks it, so launchButtonPopup can hold popups back instead; see the definitions.
// Free functions, so the class the EXE calls through its virtual table is untouched. (Claude code Fable 5.2) -->
void setSASPilotPopupsHeld(bool bHeld);
bool isSASPilotPopupsHeld();
int getNumSASPilotHeldPopups();
CvPopupInfo const& getSASPilotHeldPopup(int iIndex);
void removeSASPilotHeldPopup(int iIndex);
int getSASPilotHeldPopupId(int iIndex);
int findSASPilotHeldPopup(int iId);
void clearSASPilotHeldPopups();
bool isSASPilotPopupHoldable(ButtonPopupTypes eType);
void holdSASPilotPopup(CvPopupInfo const& kInfo);
void pruneSASPilotHeldPopups();
// <!-- custom: The buttons a held popup can be answered with, for the pilot to list and for answerSASPilotPopup to check. (Claude code Fable 5.2 + GPT-6.1-Sol) -->
std::string getSASPilotPopupButtons(CvPopupInfo const& kInfo);
bool isSASPilotPopupButtonOffered(CvPopupInfo const& kInfo, int iButton);

class CvDLLButtonPopup
{
public:
	CvDLLButtonPopup(); // advc
	virtual ~CvDLLButtonPopup();
	DllExport static CvDLLButtonPopup& getInstance();
	DllExport static void freeInstance();
	// advc (caveat): The EXE calls these virtual functions; hence the virtual destructor also needs to be left alone.
	virtual void OnOkClicked(CvPopup* pPopup, PopupReturn *pPopupReturn, CvPopupInfo &info);
	virtual void OnAltExecute(CvPopup& popup, const PopupReturn& popupReturn, CvPopupInfo &info);
	virtual void OnFocus(CvPopup* pPopup, CvPopupInfo &info);

	DllExport bool launchButtonPopup(CvPopup* pPopup, CvPopupInfo &info);

private:

	static CvDLLButtonPopup* m_pInst;
	CvDLLInterfaceIFaceBase& m_kUI; // advc

	bool launchTextPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchProductionPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchChangeReligionPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchChooseElectionPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDiploVotePopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchRazeCityPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDisbandCityPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchChooseTechPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchChangeCivicsPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchAlarmPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDeclareWarMovePopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchConfirmCommandPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchLoadUnitPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchLeadUnitPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDoEspionagePopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDoEspionageTargetPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchMainMenuPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchConfirmMenu(CvPopup *pPopup, CvPopupInfo &info);
	bool launchPythonPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDetailsPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchAdminPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchAdminPasswordPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchCancelDeal(CvPopup* pPopup, CvPopupInfo &info);
	bool launchExtendedGamePopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchDiplomacyPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchAddBuddyPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchForcedDisconnectPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchPitbossDisconnectPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchKickedPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchVassalDemandTributePopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchVassalGrantTributePopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchEventPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchFreeColonyPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchLaunchPopup(CvPopup* pPopup, CvPopupInfo &info);
	bool launchFoundReligionPopup(CvPopup* pPopup, CvPopupInfo &info);
};

#endif

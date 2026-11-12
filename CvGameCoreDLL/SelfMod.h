// advc.092b: Let's put all self-modifying code in a single place
#pragma once
#ifndef SELF_MOD_H
#define SELF_MOD_H

// Runtime modifications to the native code of Civ4BeyondSword.exe (v3.19)
class Civ4BeyondSwordPatches
{
public:
	void patchPlotIndicatorSize(); // (exposed to Python via CyGameCoreUtils) 
	bool isPlotIndicatorSizePatched() const { return m_bPlotIndicatorSizePatched; }
	// <advc.092c>
	void setHelpTextAreaSize(float fWidth); // (exposed to Python via CyGame)
	float getHelpTextAreaWidth() const { return m_fHelpTextAreaWidth; }
	bool isHelpTextAreaWidthPatched() const { return (getHelpTextAreaWidth() != 0); }
	// </advc.092c>
	// <!-- custom: New: the pre-game setup screen size patch, ported from Realism Invictus; called once at the end of CvXMLLoadUtility::LoadPreMenuGlobals.
	// isSetupScreenSizePatched tells whether its bytes were written. See KI#1082. (Claude code Opus 5.5) -->
	void patchSetupScreenSize();
	bool isSetupScreenSizePatched() const { return m_bSetupScreenSizePatched; }
	// <!-- custom: New: whether patchSetupScreenSize also hooked the world-picker globe, which follows the box. See KI#1082. (Claude code Opus 5.5) -->
	bool isSetupScreenGlobePatched() const { return m_bSetupScreenGlobePatched; }
	Civ4BeyondSwordPatches()
	:	m_bPlotIndicatorSizePatched(false), m_fHelpTextAreaWidth(0), m_bSetupScreenSizePatched(false), m_bSetupScreenGlobePatched(false)
	{}

private:
	bool m_bPlotIndicatorSizePatched;
	float m_fHelpTextAreaWidth; // advc.092c
	bool m_bSetupScreenSizePatched; // <!-- custom: see patchSetupScreenSize (Claude code Opus 5.5) -->
	bool m_bSetupScreenGlobePatched; // <!-- custom: see patchSetupScreenSize (Claude code Opus 5.5) -->
	void showErrorMsgToPlayer(CvWString szMsg);
};

namespace smc
{
	extern Civ4BeyondSwordPatches BtS_EXE;
}

#endif

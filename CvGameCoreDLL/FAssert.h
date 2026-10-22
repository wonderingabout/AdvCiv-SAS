#pragma once

#ifndef FASSERT_H
#define FASSERT_H

#ifdef _DEBUG
	#define FASSERT_ENABLE
	// <advc> Just a little convenience for debugging
	#define debugbreak(expr) if (expr) __debugbreak();
#else
	#define debugbreak(expr)
	// </advc>
#endif

#ifdef FASSERT_ENABLE

#ifdef WIN32

// advc.006f (from C2C): const char* param added. And changed the two call locations below so that __FUNCTION__ is passed.
// <!-- custom: hoisted from multiline signature inside multiline signature by collapse_cpp_signatures.py. (GPT-5.5 (reviewed script output)) -->
// <!-- custom: Persist runtime FAssert/FAssertMsg failures before their dialog or silent resolution and record the effective action afterward, independently of XML-controlled log enablement; preserve the inherited debug/ignore return contract.
// FAssertBounds/FAssertBOOL/FErrorMsg route through these macros too; compile-time/static assertions, CRT assert(), EXE/library assertions and already Ignore-Always-suppressed sites are outside this hook. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
bool FAssertDlg(const char*, const char*, const char*, unsigned int, const char*, bool&);
// <!-- custom: Let BUG's Unicode user/CvAltRoot handoff reach the assertion sink before its first failure.
// A startup assertion that already wrote output keeps its native fallback root so one process log is not split across directories. (ChatGPT-5.6-Sol) -->
void setSASAssertionLogRootDirectory(wchar_t const*);
// <!-- custom: SetGlobalDefines calls this once after all base/SAS/modular overrides finish so failed assertions never query XML/FVariableSystem while resolving their handling policy. (ChatGPT-5.6-Sol) -->
void cacheSASAssertionSilentPolicy();
// <!-- custom: Track startup, actual opening-menu visits, and new/load boundaries with assertion-owned lazy session identities.
// Menu numbering is separate from the shared new/load assertion sequence; independently gated BBAI/SGR suffixes are not required to match. (ChatGPT-5.6-Sol) -->
void startSASAssertionLogForMainMenu();
void startSASAssertionLogForNewGame();
void startSASAssertionLogForLoadedSave();

// <advc.006h>: Evaluate expr once more when debugging
#ifdef _DEBUG
	#define BREAK_FOR_DEBUGGER(expr) \
			{ _asm int 3 } \
			(expr);
#else
	#define BREAK_FOR_DEBUGGER(expr) { _asm int 3 }
#endif // </advc.006h>

#define FAssert(expr) \
{ \
	static bool bIgnoreAlways = false; \
	if (!bIgnoreAlways && !(expr)) \
	{ \
		if (FAssertDlg(#expr, 0, __FILE__, __LINE__, __FUNCTION__, bIgnoreAlways)) \
		BREAK_FOR_DEBUGGER(expr) \
	} \
}

#define FAssertMsg(expr, msg) \
{ \
	static bool bIgnoreAlways = false; \
	if (!bIgnoreAlways && !(expr)) \
	{ \
		if (FAssertDlg(#expr, msg, __FILE__, __LINE__, __FUNCTION__, bIgnoreAlways)) \
		BREAK_FOR_DEBUGGER(expr) \
	} \
}

#else // Non Win32 platforms--just use built-in FAssert
#define FAssert(expr)           FAssert(expr)
#define FAssertMsg(expr, msg)   FAssert(expr)
#endif

/*  <advc.make> Building with snprintf in the K-Mod code below works fine,
	but the VS2010 editor can't handle it. Conversely, the editor can handle
	_snprintf_s (which should be equivalent apart from the return value),
	but then building fails. Therefore define '_CODE_EDITOR' through the project file
	for the editor, but not in the Makefile.
	(BtS had originally used sprintf, which doesn't handle buffer overflows well.) */
#if _MSC_VER <= 1600 // Probably no problem in more recent versions
#ifdef _CODE_EDITOR
#define snprintf _snprintf_s
#endif
#endif // </advc.make>

// K-mod. moved the following macro from CvInitCore.h to here (and modified it)
// advc.006: Renamed from "FASSERT_BOUNDS", casts added
// advc.006f: fnString (function name) param removed
#define FAssertBounds(lower, upper, index) \
	if (static_cast<int>(index) < static_cast<int>(lower)) \
	{ \
		char acOut[256]; \
		snprintf(acOut, 256, "Index expected to be >= %d. (value: %d)", \
				static_cast<int>(lower), static_cast<int>(index)); \
		FAssertMsg(static_cast<int>(index) >= static_cast<int>(lower), acOut); \
	} \
	else if (static_cast<int>(index) >= static_cast<int>(upper)) \
	{ \
		char acOut[256]; \
		snprintf(acOut, 256, "Index expected to be < %d. (value: %d)", \
				static_cast<int>(upper), static_cast<int>(index)); \
		FAssertMsg(static_cast<int>(index) < static_cast<int>(upper), acOut); \
	}
// K-Mod end
// <advc.006>
#define FAssertBOOL(i) \
	FAssertBounds(0, 2, i); // </advc.006>
#else // FASSERT_ENABLE not defined - advc.006c: void(0) added.
#define FAssert(expr) (void)0
#define FAssertMsg(expr, msg) (void)0
// K-Mod:
#define FAssertBounds(lower,upper,index) (void)0
#define FAssertBOOL(i) void(0) // advc.006
#endif

#define FErrorMsg(msg) FAssertMsg(false, msg) // advc.006i (from C2C)

#endif // FASSERT_H

// advc.092b: New implementation file; see comment in header.
// <!-- custom: Patches here may often come from other mods, such as AdvCiv or Realism Invictus.
// Our CI asks new comments to carry a custom marker and a model credit, which is generally useful, but in such cases can tempt wrapping a source's comment in one just to satisfy or fix a CI failure; that may make its finding read as our own analysis, though we may not have checked it as deeply, and it could even be wrong, as ours may be too.
// Quoting it as is, under a line saying it is a quote and naming the source, such as "Quoted from", with each line starting with "// >", shows more clearly where it comes from, without claiming it as ours; custom notes can then keep to what we changed or checked ourselves.
// See AGENTS.md. (Claude code Opus 5.5) -->
#include "CvGameCoreDLL.h"
#include "SelfMod.h"
#include "CvGame.h"
#include "CvBugOptions.h"
#include "CvGameTextMgr.h"

Civ4BeyondSwordPatches smc::BtS_EXE;

namespace
{
/*	This class seems like an elegant way of ensuring that virtual memory protections
	are restored at the end */
class SelfMod : boost::noncopyable
{
public:
	SelfMod() : m_iAddressOffset(0) {}
	virtual ~SelfMod() { restorePageProtections(); }
	// Return false on unexpected failure
	// <!-- custom: AdvCiv's DISABLE_EXE_RUNTIME_MODS moved to GlobalDefines_advciv_sas.xml as SAS_EXE_P_ON, with its polarity inverted, so every EXE patch switch sits in one place. (Claude code Opus 5.5) -->
	bool applyIfEnabled()
	{
		if (GC.getDefineBOOL("SAS_EXE_P_ON"))
			return apply();
		return true;
	}
	/*	Derived classes can override this to be exempt from the
		DISABLE_EXE_RUNTIME_MODS check */
	// <!-- custom: now the SAS_EXE_P_ON check; no class overrides it. (Claude code Opus 5.5) -->
	virtual bool isOptionalThroughXML() const { return true; }
	int getAddressOffset() const { return m_iAddressOffset; }

protected:
	virtual bool apply()=0; // See applyIfEnabled about the return value
	bool unprotectPage(LPVOID pAddress, SIZE_T uiSize, DWORD ulNewProtect = PAGE_EXECUTE_READWRITE)
	{
		/*	Getting a segmentation fault when writing to the text segment under
			Win 8.1. Probably the same on all Windows versions that anyone still uses.
			Need to unprotect the virtual memory page first. Let's hope that this
			long outdated version of VirtualProtect from WinBase.h (nowadays located
			in Memoryapi.h) will still do the trick on recent Win versions. */
		DWORD uiOldProtect; // I get PAGE_EXECUTE_READ here
		if (VirtualProtect(pAddress,
			/*	Will affect an entire page, not just the few bytes we need. Through
				SYSTEM_INFO sysInfo; GetSystemInfo(&sysInfo); sysInfo.dwPageSize;
				I see a page size of 4 KB. */
			uiSize, ulNewProtect, &uiOldProtect) == 0)
		{
			FErrorMsg("Failed to unprotect memory for runtime patch");
			return false;
		}
		/*	A check at VirusTotal.com makes me hopeful that merely calling
			VirtualProtect in some capacity won't make our DLL suspicious to
			static virus scans. To make issues with analyses of runtime memory
			less likely - and to restore protections against accidental memory
			accesses by other parts of the DLL - let's remember what protections
			we've changed and revert them asap. */
		m_aPageProtections.push_back(PageProtection(pAddress, uiSize, uiOldProtect));
		return true;
	}
	/*	This should return 0 when dealing with the exact same build of the EXE
		that has been reverse-engineered to write this class. I don't think a
		compatibility layer should make a difference. Large address awareness
		has been tested both ways. It's unclear whether different builds exist
		apart from the (default) Steam version. Localized editions perhaps.
		So this hasn't really been tested; it's a better-than-nothing effort to
		align a starting address at which a certain sequence of code bytes is
		expected with the address, if any, at which the sequence is actually found.
		Returns the difference between expected and actual address as a byte offset
		or MIN_INT if no such offset has been found. */
	// Sequence that we search for and address at which we expect it to start
	// <!-- custom: hoisted from multiline signature before `pNeedleBytes` by collapse_cpp_signatures.py. (GPT-5.5 (reviewed script output)) -->
	// Shorter sequence to check for upfront, to save time. If found at uiQuckTestStart, then an offset of 0 is returned w/o checking pNeedleBytes.
	// <!-- custom: hoisted from multiline signature between `uiExpectedStart` and `pQuickTestBytes` by collapse_cpp_signatures.py. (GPT-5.5 (reviewed script output)) -->
	// How big an offset we contemplate. Not going to search the entire virtual memory
	// <!-- custom: hoisted from multiline signature between `uiQuickTestStart` and `iMaxAbsOffset` by collapse_cpp_signatures.py. (GPT-5.5 (reviewed script output)) -->
	int findAddressOffset(byte* pNeedleBytes, int iNeedleBytes, uint uiExpectedStart, byte* pQuickTestBytes = NULL, int iQuickTestBytes = 0, uint uiQuickTestStart = 0, int iMaxAbsOffset = 256 * 1024)
	{
		// Preserve the (most recent) offset in m_iAddressOffset
		updateAddressOffset(pNeedleBytes, iNeedleBytes, uiExpectedStart,
				pQuickTestBytes, iQuickTestBytes, uiQuickTestStart, iMaxAbsOffset);
		return m_iAddressOffset;
	}
	bool testCodeLayout(byte* pBytes, int iBytes, uint uiStart) const;

private:
	int m_iAddressOffset;

	struct PageProtection
	{
		PageProtection(LPVOID pAddress, SIZE_T uiSize, DWORD uiProtect)
			:	m_pAddress(pAddress), m_uiSize(uiSize), m_uiProtect(uiProtect) {}
		LPVOID m_pAddress;
		SIZE_T m_uiSize;
		DWORD m_uiProtect;
	};
	std::vector<PageProtection> m_aPageProtections;
	void restorePageProtections()
	{
		for (size_t i = 0; i < m_aPageProtections.size(); i++)
		{
			DWORD uiDummy;
		#ifdef FASSERT_ENABLE
			int iSuccess =
		#endif
			 VirtualProtect(m_aPageProtections[i].m_pAddress, m_aPageProtections[i].m_uiSize,
					m_aPageProtections[i].m_uiProtect, &uiDummy);
			FAssertMsg(iSuccess != 0, "Failed to restore memory protection");
		}
	}
	void updateAddressOffset(byte* pNeedleBytes, int iNeedleBytes, uint uiExpectedStart, byte* pQuickTestBytes = NULL, int iQuickTestBytes = 0, uint uiQuickTestStart = 0, int iMaxAbsOffset = 256 * 1024)
	{
		if (pQuickTestBytes != NULL &&
			testCodeLayout(pQuickTestBytes, iQuickTestBytes, uiQuickTestStart))
		{
			m_iAddressOffset = 0;
			return;
		}
		int iAddressOffset = 0;
		// Base address of the EXE. Reading below that results in a crash.
		int const iLowAddressBound = 0x00400000;
		// I see mostly just zeros above this address in the VS Memory window
		int const iHighAddressBound = 0x0FFFFFFF;
		if (((int)uiExpectedStart) >= iLowAddressBound &&
			((int)uiExpectedStart) <= iHighAddressBound)
		{
			int const iMaxSubtrahend = std::min(iMaxAbsOffset, static_cast<int>(
					uiExpectedStart - iLowAddressBound));
			int const iMaxAddend = std::min(iMaxAbsOffset, static_cast<int>(
					iHighAddressBound - uiExpectedStart));
			int const iHaystackBytes = iMaxSubtrahend + iMaxAddend;
			byte* pHaystackBytes = new byte[iHaystackBytes];
			for (int iOffset = -iMaxSubtrahend; iOffset < iMaxAddend; iOffset++)
			{
				pHaystackBytes[iOffset + iMaxSubtrahend] =
						reinterpret_cast<byte*>(uiExpectedStart)[iOffset];
			}
			// No std::begin, std::end until C++11
			byte* const pHaystackEnd = pHaystackBytes + iHaystackBytes;
			byte* pos = std::search(
					pHaystackBytes, pHaystackEnd,
					pNeedleBytes, pNeedleBytes + iNeedleBytes);
			if (pos == pHaystackEnd)
			{
				FErrorMsg("Failed to locate expected code bytes in EXE");
				m_iAddressOffset = MIN_INT;
				return;
			}
			iAddressOffset = ((int)std::distance(pHaystackBytes, pos))
					- iMaxSubtrahend;
		}
		else
		{
			FErrorMsg("uiExpectedStart doesn't look like a code address");
			m_iAddressOffset = MIN_INT;
			return;
		}
		/*	Run our initial test again to be on the safe side?
			Not likely to work. These offsets can only be used in close proximity,
			if at all. */
		/*if (pQuickTestBytes != NULL &&
			!testCodeLayout(pQuickTestBytes, iQuickTestBytes,
			uiQuickTestStart + iAddressOffset))
		{
			FErrorMsg("Address offset discarded; likely incorrect.");
			m_iAddressOffset = MIN_INT;
			return;
		}*/
		m_iAddressOffset = iAddressOffset;
		return;
	}
};
// Don't want this to be inlined; out-of-class definition accomplishes that.
bool SelfMod::testCodeLayout(byte* pBytes, int iBytes, uint uiStart) const
{
	for (int i = 0; i < iBytes; i++)
	{
		byte iActual = reinterpret_cast<byte*>(uiStart)[i]; // for inspection in debugger
		if (pBytes[i] != iActual)
		{
		#ifdef _DEBUG
			FAssertMsg(iActual != 0xCC, "Interrupt found in native code. "
					/*	Remedy: Should probably keep breakpoints disabled
						until SelfMod is finished */
					"Debugger breakpoint?");
		#endif
			/*FErrorMsg("Unexpected memory layout of EXE"
				" (Steam version? May need to switch to \"unsupported beta\" version of BtS)");*/
			return false;
		}
	}
	return true;
}


class PlotIndicatorSizeMod : public SelfMod
{
public:
	PlotIndicatorSizeMod(int iScreenHeight) : m_iScreenHeight(iScreenHeight) {}
protected:
	bool apply() // override
	{
		/*	Cache (Performance probably no concern, but best not to fiddle
			with memory protections unnecessarily.) */
		static PlotIndicatorSize ffMostRecentBaseSize;

		/*	Size values for plot indicators shown onscreen and offscreen that are
			hardcoded in the EXE. These go through a bunch of calculations,
			only part of which I've located in the debugger. Essentially,
			there appears to be an adjustment proportional to the screen height. */
		PlotIndicatorSize ffBaseSize(42, 68);
		bool bAdjustToFoV = true;
		bool bAdjustToRes = false;
		{
			int iUserChoice = BUGOption::getValue("MainInterface__PlotIndicatorSize");
			switch (iUserChoice)
			{
				/* "Automatic" behavior: Subtract a little b/c the BtS size
					is a bit too big overall, i.e. even on the lowest resolution. */
			case 0: ffBaseSize.onScreen -= 2; break;
			case 1: std::swap(bAdjustToFoV, bAdjustToRes); break; // BtS behavior
			/*	Note that this formula ignores how the choices are labeled.
				That menu text needs to be kept consistent with our code here. */
			default: ffBaseSize.onScreen = 15 + 5 * static_cast<float>(iUserChoice);
			}
		}
		/*	The EXE will adjust to height. Rather than try to change that in the EXE,
			we'll proactively cancel out the adjustment. */
		if (!bAdjustToRes)
		{
			/*	Current screen height relative to the height that the UI was
				most optimized for */
			float fHeightRatio = m_iScreenHeight / 768.f;
			ffBaseSize.onScreen = ffBaseSize.onScreen / fHeightRatio;
					/*	Could use this divisor to not cancel it out entirely -
						but the adjustment really just seems to be a bad idea. */
					// std::pow(fHeightRatio, 0.85f)
		}
		/*	FoV correlates with screen size, (typical) camera distance and
			the player's distance from the screen. And BtS seems to make a small
			adjustment based on FoV and camera distance too (probably
			not explicitly). So it's hard to reason about this adjustment.
			In my tests, it has had the desired result of making the diameters
			about one quarter of a plot's side length. */
		if (bAdjustToFoV)
		{
			float fTypicalFoV = 40;
			ffBaseSize.onScreen *= std::min(2.f, std::max(0.5f,
					std::sqrt(fTypicalFoV / GC.getFIELD_OF_VIEW())));
		}
		/*	(I'm not going to dirty the globe layer in response to a FoV change - that
			would probably cause stuttering while the player adjusts the FoV slider.) */
		{
			int iUserChoice = BUGOption::getValue("MainInterface__OffScreenUnitSizeMult");
			if (iUserChoice == 7)
			{	// Meaning "disable". 0 size seems to accomplish that.
				ffBaseSize.offScreen = 0;
			}
			else ffBaseSize.offScreen = ffBaseSize.onScreen * (0.8f + 0.2f * iUserChoice);
		}

		if (ffBaseSize.equals(ffMostRecentBaseSize))
			return true;
		ffMostRecentBaseSize = ffBaseSize;

		/*	The onscreen size is hardcoded as an immediate operand (in FP32 format)
			in three places and the offscreen size in one place.
			|Code addr.| Disassembly						| Code bytes
			------------------------------------------------------------------------------
			 00464A08	push 42280000h						 68 00 00 28 42
			 004B76F4		(same as above)
			 00496DEB	mov dword ptr [esi+17Ch],42280000h	 C7 86 7C 01 00 00 00 00 28 42
			 0049905F	push 42880000h						 68 00 00 88 42
			------------------------------------------------------------------------------
			One can get the debugger close to the first location by setting a breakpoint
			at the end of CvPlayer::getGlobeLayerColors. The second is triggered by
			interface messages that show a plot indicator; a breakpoint in
			CvTalkingHeadMessage::getOnScreenArrows should help. The third one seems
			to be reached in all cases, look for a call to 00496DB0.
			The fourth one is triggered by selecting any unit. */
		uint aCodeAdresses[] = {
			0x00464A08, 0x004B76F4, 0x00496DEB, 0x0049905F
		};
		// The data we need to change is not right at the start
		uint aOperandOffsets[ARRAYSIZE(aCodeAdresses)] = {
					1,			1,			6,			1
		};

		/*	Before applying our patch, let's confirm that the code is layed out
			in memory as we expect it to be. */
		/*	This is the call to CvPlayer::getGlobeLayerColors,
			for a quick test upfront.
			 004649A9	call dword ptr ds:[0BC1E64h] */
		byte aQuickTestBytes[] = { 0xFF, 0x15, 0x64, 0x1E, 0xBC, 0x00 };
		/*	Longer sequence to search for if we have to find an address offset.
			25 instructions near the start of the function that calls
			CvPlayer::getGlobeLayerColors. This is a fairly long sequence w/o any
			absolute addresses in operands. After this sequence, there are a bunch
			of DLL calls, the last one being CvPlayer::getGlobeLayerColors.
			I've verified that this sequence exists in the Steamless (unpacked)
			version of the Steam BtS EXE on disk, namely at 0x00464F88, i.e. at
			an offset of 1616. */
		byte aNeedleBytes[] = {
			0xA1, 0x00, 0x00, 0x00, 0x00, 0x50, 0x64, 0x89, 0x25, 0x00, 0x00,
			0x00, 0x00, 0x83, 0xEC, 0x68, 0x53, 0x55, 0x56, 0x57, 0x33, 0xFF,
			0x89, 0x7C, 0x24, 0x54, 0x89, 0x7C, 0x24, 0x58, 0x89, 0x7C, 0x24,
			0x5C, 0x89, 0xBC, 0x24, 0x80, 0x00, 0x00, 0x00, 0x89, 0x7C, 0x24,
			0x44, 0x89, 0x7C, 0x24, 0x48, 0x89, 0x7C, 0x24, 0x4C, 0x8D, 0x54,
			0x24, 0x40, 0x52, 0xC6, 0x84, 0x24, 0x84, 0x00, 0x00, 0x00, 0x01,
			0x8B, 0x41, 0x04, 0x8D, 0x54, 0x24, 0x54, 0x52, 0x50, 0x8B, 0x41,
			0x08, 0x50
		};
		int iNeedleOffset = findAddressOffset(
				aNeedleBytes, ARRAYSIZE(aNeedleBytes), 0x00464938,
				aQuickTestBytes, ARRAYSIZE(aQuickTestBytes), 0x004649A9);
		/*	This offset is too far away from most of the code locations. Would
			need two more search patterns. I'll just hardcode the offsets
			instead and use the calculated offset only as confirmation that
			we're dealing with Steam. */
		/*if (iNeedleOffset == MIN_INT)
			return false;*/
		int aAdressOffsets[4] = {};
		if (iNeedleOffset == 1616)
		{
			aAdressOffsets[0] = 1616;
			aAdressOffsets[1] = 704;
			aAdressOffsets[2] = 544;
			aAdressOffsets[3] = 544;
		}
		else if (iNeedleOffset != 0)
			return false;

		// Finally apply the actual patch
		for (int i = 0; i < ARRAYSIZE(aCodeAdresses); i++)
		{
			float fSize = (i >= 3 ? ffBaseSize.offScreen : ffBaseSize.onScreen);
			uint uiCodeAddress = aCodeAdresses[i] + aOperandOffsets[i];
			FAssert(((int)uiCodeAddress) > -aAdressOffsets[i]);
			uiCodeAddress += aAdressOffsets[i];
			if (!unprotectPage(reinterpret_cast<LPVOID>(uiCodeAddress), sizeof(float)))
				return false;
			*reinterpret_cast<float*>(uiCodeAddress) = fSize;
		}
		return true;
	}

private:
	int const m_iScreenHeight;
	struct PlotIndicatorSize
	{
		PlotIndicatorSize(float fOnScreen = 0, float fOffScreen = 0)
		:	onScreen(fOnScreen), offScreen(fOffScreen) {}
		// Overriding operator== for this nested thing would be a PITA
		bool equals(PlotIndicatorSizeMod::PlotIndicatorSize const& kOther)
		{	// Exact floating point comparison
			return (onScreen == kOther.onScreen &&
					offScreen == kOther.offScreen);
		}
		float onScreen, offScreen;
	};
};

// advc.092c:
class HelpTextAreaWidthMod : public SelfMod
{
public:
	HelpTextAreaWidthMod(double dTargetWidth) : m_dTargetWidth(dTargetWidth) {}
protected:
	bool apply() // override
	{
		byte const iTargetMultiplicand = calculateTargetMultiplicand();
		/*	The multiplicand is hardcoded as a single-byte immediate operand:
			|Code addr.| Disassembly						| Code bytes
			------------------------------------------------------------------------------
			 00559A91	push 1Dh							  6A 1D
			------------------------------------------------------------------------------
			This is in a function that seems to get called (only?) via
			CyGInterface.setHelpTextArea - and probably not directly from that
			function and not on every call of it (reliably on the first call,
			it seems). The push comes before calling some setter member function. */
		uint uiCodeAddress = 0x00559A91;
		/*	Before applying our patch, let's confirm that the code is layed out
			in memory as we expect it to be. This is right up to the byte that
			we wish to change. */
		byte aQuickTestBytes[] = { 0x8B, 0x4E, 0x7C, 0x6A };
		/*	Longer sequence to search for if we have to find an address offset.
			A group of 12 instructions that contain no absolute addresses, a few
			instructions before the one we wish to change.*/
		byte aNeedleBytes[] = {
			0x8B, 0x11, 0x55, 0xff, 0x52, 0x10, 0x8B, 0xCF, 0x89, 0x7E, 0x7C,
			0x8B, 0x41, 0x58, 0x8B, 0x51, 0x5C, 0x80, 0xE4, 0xBF, 0x80, 0xCC,
			0x30, 0x55, 0x52, 0x50
		};
		int iAddressOffset = findAddressOffset(
				aNeedleBytes, ARRAYSIZE(aNeedleBytes), 0x00559A6F,
				aQuickTestBytes, ARRAYSIZE(aQuickTestBytes), 0x00559A8E);
		if (iAddressOffset == MIN_INT)
			return false;
		/*	In the default Steam version, I find the needle at 0x0055AD2F and
			the corresponding offset (4800) should also be valid for the code byte
			that we'll change. If the offset is different, then I don't know
			what we're dealing with. Pitboss possibly. */
		FAssertMsg(iAddressOffset == 0 || iAddressOffset == 4800,
				"Unrecognized version of the BtS executable; might still work.");
		// Apply our patch
		uiCodeAddress += 1; // Offset for the operand
		FAssert(((int)uiCodeAddress) > -iAddressOffset);
		uiCodeAddress += iAddressOffset;
		if (!unprotectPage(reinterpret_cast<LPVOID>(uiCodeAddress), sizeof(byte)))
			return false;
		*reinterpret_cast<byte*>(uiCodeAddress) = iTargetMultiplicand;
		return true;
	}

private:
	double const m_dTargetWidth;
	byte calculateTargetMultiplicand()
	{
		/*	The EXE seems to convert the font size set by the theme to a somewhat
			smaller scale, perhaps one expressing the horizontal space taken up. */
		double dFontFactorInternal = floor(GAMETEXT.getHelpFontSize() / 1.5);
		/*	The total width seems to get calculated as a hardcoded constant times
			the font size factor */
		double const dMultiplicandInternal = 29;
		double dWidthInternal = std::max<double>(dFontFactorInternal, 5) * dMultiplicandInternal;
		double dAdjustmentFactor = m_dTargetWidth / dWidthInternal;
		return safeIntCast<byte>(fmath::round(
				dMultiplicandInternal * dAdjustmentFactor));
	}
};

// <!-- custom: Pre-game setup screen size, ported from Realism Invictus's setSetupScreenSize (RI r5619/r5620, "Scaled the main menu as well").
// Quoted from RI's SelfMod.cpp r5655 below, in RI's words and layout, not ours, so its findings stay its own; the custom note after it says what AdvCiv-SAS changed. (Claude code Opus 5.5) -->
//	> The pre-game setup screens (Custom Game, Play Now "Final Setup", MP staging,
//	> scenario) size their centred window from a single shared getSize, FUN_0059acf0,
//	> which writes two hardcoded imm32s into the caller's SIZE struct: width 0x352 (850),
//	> height 0x239 (569). The builder then centres the window on the screen resolution
//	> (X = screenW/2 - w/2), so changing the returned size auto-recentres. We rewrite the
//	> two immediates per UI font so the window grows for Large/XL (whose font-scaled
//	> content needs the room); Normal/Small keep 850x569, byte-identical to stock. Shared,
//	> so all four setup screens grow together (intended).
//	>
//	> Body (identical in both EXE variants; only the entry address differs):
//	>   8B 44 24 04           MOV EAX,[ESP+4]
//	>   C7 00 52 03 00 00     MOV [EAX],0x352      ; width  imm32 at entry+6
//	>   C7 40 04 39 02 00 00  MOV [EAX+4],0x239     ; height imm32 at entry+13
//	>   C2 04 00              RET 4
//	> V1 = GoG/non-Steam 0x0059ACF0, V2 = Steam 0x0059B7B0. The full 17-byte signature
//	> plus the stock 850/569 value check can't bind the wrong site or the wrong variant.
// <!-- custom: What AdvCiv-SAS changed.
// In our capture Custom Game already fills the window, unlike the list above.
// AdvCiv-SAS had squeezed Simple Game into that box by pushing its title off the top (Layout_MainMenu_OuterMargin in Civ4Theme_Common.thm, commit d194577b3); a larger box makes room again.
// Our first port rewrote the two immediates like RI, with one tunable size instead of one per font, and on 2026-11-12 1150 x 800 showed all 23 maps without scrolling.
// But a size larger than the game window spilled off every edge (2400 x 1400 hid the map list and GO BACK), and 1150 x 800 is already taller than a 1366 x 768 screen, while the game's resolution is unknown when the patch runs at startup.
// So the function's entry now jumps to sasSetupScreenGetSize, which measures the game window each time a setup screen opens and returns a tunable percentage of it; a resolution change follows too.
// Before writing, we compare the whole 20-byte body quoted above, RI's 17-byte signature and its RET 4, rather than RI's signature and value check.
// Both addresses are RI's; we confirmed Steam's on 2026-11-12, as README_EXE_Patches.md describes, while GOG's is untested by us.
// See README_EXE_Patches.md. See KI#1082. (Claude code Opus 5.5) -->
// <!-- custom: size = window size * percent / 100 + add. The percent scales with the resolution; the add, in pixels and possibly negative, covers what does not, such as the main menu's bottom bar of about 44 px.
// A percent of 0 makes the add a fixed manual size, so one formula gives scaling, a fixed size or both, with no mode switch; we find this fairly elegant, like CSS's calc(100% - 86px).
// On 2026-11-12 100% - 120 px, the first default, left a visible gap above that bar; 100% - 88 px reached it in 1920 x 1080 and 2560 x 1380 windows, but a thin dark line still showed above it, and -84 covered half the bar's gold stripe. Pixel rows showed -86 and -87 render alike, since the centring rounds the odd pixel away: the box's own black 1 px border sits on the stripe's top row, and -88 shows the stripe in full under a 1 px dark edge. The -86 default was chosen by eye, in 1920 x 1080 and 2560 x 1380 windows alike, since the bar keeps its pixel height at every resolution. See KI#1082. (Claude code Opus 5.5) -->
int g_iSetupScreenWidthPercent = 0;
int g_iSetupScreenHeightPercent = 0;
int g_iSetupScreenWidthAdd = 0;
int g_iSetupScreenHeightAdd = 0;
int g_iSetupScreenWidthFreeMin = 0;
int g_iSetupScreenHeightFreeMin = 0;
// <!-- custom: The world-picker globe's size uses the box's formula, applied to the box instead of the window: globe size = box size * percent / 100 + add, for width and height.
// The first version scaled both sides by one factor (/256 as in RI's cave) derived from the box's growth over the stock 850 x 569; the user asked on 2026-11-12 for a formula tunable both ways without a compile.
// g_iSetupScreenGlobeWidth and _Height hold the result the cave writes; 0 keeps the EXE's own size for that side. See KI#1082. (Claude code Opus 5.5) -->
bool g_bSetupScreenGlobeOn = false;
int g_iSetupScreenGlobeWidthPercent = 0;
int g_iSetupScreenGlobeHeightPercent = 0;
int g_iSetupScreenGlobeWidthAdd = 0;
int g_iSetupScreenGlobeHeightAdd = 0;
int g_iSetupScreenGlobeWidth = 0;
int g_iSetupScreenGlobeHeight = 0;

// <!-- custom: Picks this process's largest visible top-level window: the game window, not the startup splash or a message box. (Claude code Opus 5.5) -->
BOOL CALLBACK sasFindLargestOwnWindow(HWND hWnd, LPARAM lParam)
{
	DWORD uiProcessId = 0;
	GetWindowThreadProcessId(hWnd, &uiProcessId);
	RECT rect;
	if (uiProcessId == GetCurrentProcessId() && IsWindowVisible(hWnd) && GetClientRect(hWnd, &rect))
	{
		std::pair<HWND,int>& best = *reinterpret_cast<std::pair<HWND,int>*>(lParam);
		int const iArea = (rect.right - rect.left) * (rect.bottom - rect.top);
		if (iArea > best.second)
			best = std::make_pair(hWnd, iArea);
	}
	return TRUE;
}

// <!-- custom: Replaces the EXE's size function, so it keeps that function's contract: one stack argument, the caller's SIZE (width then height), popped by the callee as its RET 4 did, and the same pointer returned in EAX, as MSVC returns a struct through a hidden pointer.
// If no window is found, the stock 850 x 569 is returned; FAssert reports that in assert builds, since a setup screen only opens once the game window exists. (Claude code Opus 5.5) -->
int* __stdcall sasSetupScreenGetSize(int* piSize)
{
	int iWidth = 850;
	int iHeight = 569;
	std::pair<HWND,int> best(static_cast<HWND>(NULL), 0);
	EnumWindows(sasFindLargestOwnWindow, reinterpret_cast<LPARAM>(&best));
	RECT rect;
	if (best.first != NULL && GetClientRect(best.first, &rect))
	{
		int const iWindowWidth = rect.right - rect.left;
		int const iWindowHeight = rect.bottom - rect.top;
		// <!-- custom: Computed in 64 bits: a large PCT times a 4K window could overflow int before the cut below. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		__int64 const iWantedWidth = static_cast<__int64>(iWindowWidth) * g_iSetupScreenWidthPercent / 100 + g_iSetupScreenWidthAdd;
		__int64 const iWantedHeight = static_cast<__int64>(iWindowHeight) * g_iSetupScreenHeightPercent / 100 + g_iSetupScreenHeightAdd;
		// <!-- custom: An exception to letting bad define values fail loudly: on 2026-11-12 a 2400 x 1400 box in a 1920 x 1080 window hid GO BACK and the map list, leaving a player stuck in a setup screen they cannot fully see or leave.
		// A first clamp to the full window still covered GO BACK at 150% x 150%: the main menu's bottom bar sits under the centred box.
		// So the result is cut to the window minus SAS_EXE_P_DYNAM_MAIN_MENU_WIDTH_FREE_MIN and _HEIGHT_FREE_MIN; assert builds still report the out-of-range setting.
		// The height default, 80, is a little under twice the bar's 44 px measured in 1920 x 1080 and 2560 x 1380 windows on 2026-11-12: the box may overlap the bar's top edge, as -84 did, but not GO BACK's text; the width default, 0, lets the box reach the window's sides.
		// Both margins were a fixed 80 and nothing in C++ at first; defines let players tune them without a compile. See KI#1082. (Claude code Opus 5.5) -->
		// <!-- custom: Codex's review found the cut still allowed unusable boxes: a zero or negative result became 1 px, and a negative FREE_MIN raised the cap beyond the window.
		// So a negative FREE_MIN counts as 0, and a result under 1 px keeps BtS's stock size for that side, cut to the window like any other. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		// <!-- custom: Its second review found two gaps left: a requested 1 px passed as is, and a FREE_MIN at or above the window size still cut the box to 1 px.
		// The patch only ever enlarges the box, so a result under the stock size now keeps the stock size, and a FREE_MIN leaving less than the stock size is ignored for that side, so the box can always show the setup screen. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
		int const iFreeWidth = iWindowWidth - std::max(0, g_iSetupScreenWidthFreeMin);
		int const iFreeHeight = iWindowHeight - std::max(0, g_iSetupScreenHeightFreeMin);
		int const iMaxWidth = iFreeWidth >= iWidth ? iFreeWidth : iWindowWidth;
		int const iMaxHeight = iFreeHeight >= iHeight ? iFreeHeight : iWindowHeight;
		iWidth = static_cast<int>(std::min<__int64>(std::max<__int64>(iWantedWidth, iWidth), iMaxWidth));
		iHeight = static_cast<int>(std::min<__int64>(std::max<__int64>(iWantedHeight, iHeight), iMaxHeight));
		FAssertMsg(iWidth == iWantedWidth && iHeight == iWantedHeight && g_iSetupScreenWidthFreeMin >= 0 && g_iSetupScreenHeightFreeMin >= 0, "Setup screen size outside the game window; check SAS_EXE_P_DYNAM_MAIN_MENU_* defines");
	}
	else FErrorMsg("Setup screen size: no game window found; using the stock 850 x 569");
	// <!-- custom: The globe follows the box just computed.
	// Measured by eye on 2026-11-12, the map step's black panel is about 57% x 67% of the box (926 x 671 in a 1632 x 994 box), around a stock 450 x 320 globe; a first script measurement of 927 x 559 was wrong, as the dark globe broke its scan.
	// The size set here is the globe's whole area, a rounded rectangle with its own starfield, centred in the panel: Great_Plains' flat picture fills it, 3D globes such as Pangaea about 87% of its height, SAS's .dds previews its middle; so Great_Plains is the check for overflow.
	// An area taller than a step's panel, as on some option steps, is clipped at the panel's frame, not drawn over it (seen at 1080p, 1440p and 4K on 2026-11-12).
	// A result under 1 px keeps the EXE's size for that side, and the globe is cut to the box, beyond which it would spill over the map list. See KI#1082. (Claude code Opus 5.5) -->
	if (g_bSetupScreenGlobeOn)
	{
		__int64 const iGlobeWidth = static_cast<__int64>(iWidth) * g_iSetupScreenGlobeWidthPercent / 100 + g_iSetupScreenGlobeWidthAdd;
		__int64 const iGlobeHeight = static_cast<__int64>(iHeight) * g_iSetupScreenGlobeHeightPercent / 100 + g_iSetupScreenGlobeHeightAdd;
		g_iSetupScreenGlobeWidth = iGlobeWidth < 1 ? 0 : static_cast<int>(std::min<__int64>(iGlobeWidth, iWidth));
		g_iSetupScreenGlobeHeight = iGlobeHeight < 1 ? 0 : static_cast<int>(std::min<__int64>(iGlobeHeight, iHeight));
		FAssertMsg(g_iSetupScreenGlobeWidth == iGlobeWidth && g_iSetupScreenGlobeHeight == iGlobeHeight, "Setup screen globe size outside the box; check SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_* defines");
	}
	piSize[0] = iWidth;
	piSize[1] = iHeight;
	return piSize;
}

// <!-- custom: True if [uiAddress, uiAddress + iBytes) sits in one committed, executable region of the EXE image, so reading it cannot fault; Codex's first review asked for this check before the byte comparison. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
bool sasIsExeCode(uint uiAddress, int iBytes)
{
	MEMORY_BASIC_INFORMATION info;
	if (VirtualQuery(reinterpret_cast<LPCVOID>(uiAddress), &info, sizeof(info)) != sizeof(info))
		return false;
	DWORD const uiExecutable = PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY;
	return (info.State == MEM_COMMIT && (info.Protect & uiExecutable) != 0 && (info.Protect & PAGE_GUARD) == 0 &&
			info.AllocationBase == static_cast<LPVOID>(GetModuleHandle(NULL)) &&
			uiAddress + iBytes <= reinterpret_cast<uint>(info.BaseAddress) + info.RegionSize);
}

class SetupScreenSizeMod : public SelfMod
{
public:
	SetupScreenSizeMod(bool bGog, bool bSteam) : m_bGog(bGog), m_bSteam(bSteam) {}
protected:
	bool apply() // override
	{
		// <!-- custom: Unlike RI, which rewrites the two immediates in the body quoted above, the first 5 bytes become jmp sasSetupScreenGetSize (E9 rel32); the rest is never reached. (Claude code Opus 5.5) -->
		byte aStockBytes[] = { 0x8B, 0x44, 0x24, 0x04, 0xC7, 0x00, 0x52, 0x03, 0x00, 0x00, 0xC7, 0x40, 0x04, 0x39, 0x02, 0x00, 0x00, 0xC2, 0x04, 0x00 };
		uint const aSites[] = { 0x0059ACF0, 0x0059B7B0 };
		bool const abEnabled[] = { m_bGog, m_bSteam };
		for (int i = 0; i < ARRAYSIZE(aSites); i++)
		{
			// <!-- custom: testCodeLayout reads the site directly, which would crash if an unknown EXE left that address unmapped, so first check that it lies in the EXE's own committed code. (Claude code Opus 5.5 + GPT-6.1-Sol) -->
			if (!abEnabled[i] || !sasIsExeCode(aSites[i], ARRAYSIZE(aStockBytes)) || !testCodeLayout(aStockBytes, ARRAYSIZE(aStockBytes), aSites[i]))
				continue;
			byte* const pSite = reinterpret_cast<byte*>(aSites[i]);
			if (!unprotectPage(pSite, 5))
				return false;
			pSite[0] = 0xE9;
			*reinterpret_cast<int*>(pSite + 1) = reinterpret_cast<int>(&sasSetupScreenGetSize) - reinterpret_cast<int>(pSite + 5);
			FlushInstructionCache(GetCurrentProcess(), pSite, 5);
			return true;
		}
		return false;
	}
private:
	bool const m_bGog;
	bool const m_bSteam;
};

// <!-- custom: World-picker globe size, ported from Realism Invictus's WorldPickerSizePatch.
// Quoted from RI's SelfMod.cpp r5655 below, in RI's words and layout, not ours, so its findings stay its own; the custom note after it says what AdvCiv-SAS changed. (Claude code Opus 5.5) -->
//	> The setup screens (Custom Game / Final Setup / map & world-size pickers) show a rotating 3D
//	> world-picker (globe). All four builders create it through one shared function -- FUN_004d2b90
//	> (V1) / FUN_004d2fe0 (V2), `__cdecl(obj, width, height)` -- which renders the CvWorldPickerInfo
//	> model at width x height (stored at picker+0x14/0x18/0x20/0x24). The size is a hardcoded 320x450
//	> passed by each caller, so enlarging the setup window leaves the globe put and its dark backdrop
//	> panel shows past it as a letterbox. The size is a call ARGUMENT (no immediate to poke), so we
//	> inline-detour the shared function and scale the width/height args on entry by a per-font factor
//	> (fixed-point /256). Installed only at Large/XL -> Normal/Small keep the stock EXE. One hook
//	> covers all four globe screens.
//	>
//	> Prologue displaced (identical shape both variants; both PUSHes are absolute -> relocatable):
//	>   6A FF          PUSH -1
//	>   68 <imm32>     PUSH offset <SEH handler>   (V1 0x00A38EB8 / V2 0x009F6B58)
//	>   ... resume at entry+7 (the MOV EAX,FS:[0])
//	> Cave: MOV ECX,[g_num]; scale [ESP+8] & [ESP+0xC] via IMUL/SAR 8; replay the two PUSHes; JMP
//	> entry+7. V1 entry 0x004D2B90, V2 entry 0x004D2FE0. Matches the BridgeRouteTypePatch cave idiom.
// <!-- custom: What AdvCiv-SAS changed: the hook, the displaced prologue and the cave's ending are RI's, ported.
// Our cave instead writes the sizes sasSetupScreenGetSize computes from the box, g_iSetupScreenGlobeWidth and _Height, each left alone while 0, rather than RI's fixed per-font factor; it is installed whenever the box patch is applied, at any font.
// For us, the stock globe also kept our map previews small inside the enlarged box.
// Both entries are RI's; we confirmed Steam's bytes on 2026-11-12, as README_EXE_Patches.md describes, while GOG's are untested by us. See KI#1082. (Claude code Opus 5.5) -->
class SetupScreenGlobeMod : public SelfMod
{
public:
	SetupScreenGlobeMod(bool bGog, bool bSteam) : m_bGog(bGog), m_bSteam(bSteam) {}
protected:
	bool apply() // override
	{
		// <!-- custom: The 7 prologue bytes quoted above, compared with each EXE's own handler operand before they become a jmp to the cave. (Claude code Opus 5.5) -->
		uint const aSites[] = { 0x004D2B90, 0x004D2FE0 };
		uint const aHandlers[] = { 0x00A38EB8, 0x009F6B58 };
		bool const abEnabled[] = { m_bGog, m_bSteam };
		for (int i = 0; i < ARRAYSIZE(aSites); i++)
		{
			byte aStockBytes[] = { 0x6A, 0xFF, 0x68, 0, 0, 0, 0 };
			*reinterpret_cast<uint*>(aStockBytes + 3) = aHandlers[i];
			if (!abEnabled[i] || !sasIsExeCode(aSites[i], ARRAYSIZE(aStockBytes)) || !testCodeLayout(aStockBytes, ARRAYSIZE(aStockBytes), aSites[i]))
				continue;
			// <!-- custom: As in RI's patch, the cave is allocated once and never freed: the EXE jumps into it for the rest of the process. (Claude code Opus 5.5) -->
			byte* const pCave = static_cast<byte*>(VirtualAlloc(NULL, 64, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));
			if (pCave == NULL)
				return false;
			int iByte = 0;
			// <!-- custom: The cave's content is ours, inside RI's cave structure: for the width at [esp+8], then the height at [esp+0Ch]: mov eax,[global]; test eax,eax; jz +4; mov [esp+n],eax.
			// RI's cave scales the same two arguments by a fixed factor (IMUL, SAR 8); ours writes the computed size. (Claude code Opus 5.5) -->
			int* const apSizes[] = { &g_iSetupScreenGlobeWidth, &g_iSetupScreenGlobeHeight };
			byte const aStackOffsets[] = { 0x08, 0x0C };
			for (int j = 0; j < ARRAYSIZE(aStackOffsets); j++)
			{
				pCave[iByte++] = 0xA1;
				*reinterpret_cast<int**>(pCave + iByte) = apSizes[j]; iByte += 4;
				pCave[iByte++] = 0x85; pCave[iByte++] = 0xC0;
				pCave[iByte++] = 0x74; pCave[iByte++] = 0x04;
				pCave[iByte++] = 0x89; pCave[iByte++] = 0x44; pCave[iByte++] = 0x24; pCave[iByte++] = aStackOffsets[j];
			}
			// <!-- custom: RI's cave ending, ported: the two displaced pushes, then jmp entry + 7. (Claude code Opus 5.5) -->
			for (int j = 0; j < ARRAYSIZE(aStockBytes); j++)
				pCave[iByte++] = aStockBytes[j];
			pCave[iByte++] = 0xE9;
			*reinterpret_cast<int*>(pCave + iByte) = static_cast<int>(aSites[i] + 7) - reinterpret_cast<int>(pCave + iByte + 4); iByte += 4;
			FAssert(iByte <= 64);
			FlushInstructionCache(GetCurrentProcess(), pCave, iByte);
			byte* const pSite = reinterpret_cast<byte*>(aSites[i]);
			if (!unprotectPage(pSite, 7))
				return false;
			pSite[0] = 0xE9;
			*reinterpret_cast<int*>(pSite + 1) = reinterpret_cast<int>(pCave) - reinterpret_cast<int>(pSite + 5);
			pSite[5] = 0x90;
			pSite[6] = 0x90;
			FlushInstructionCache(GetCurrentProcess(), pSite, 7);
			return true;
		}
		return false;
	}
private:
	bool const m_bGog;
	bool const m_bSteam;
};

} // (end of unnamed namespace)


void Civ4BeyondSwordPatches::showErrorMsgToPlayer(CvWString szMsg)
{
	// Don't need more error messages if assertions are enabled
#ifndef FASSERT_ENABLE
	if (GC.IsGraphicsInitialized() && GC.getGame().getActivePlayer() != NO_PLAYER)
	{
		gDLL->getInterfaceIFace()->addMessage(GC.getGame().getActivePlayer(), true,
				GC.getEVENT_MESSAGE_TIME(), szMsg, NULL, MESSAGE_TYPE_INFO, NULL,
				(ColorTypes)GC.getInfoTypeForString("COLOR_RED"));
	}
#endif
}


void Civ4BeyondSwordPatches::patchPlotIndicatorSize()
{
	int const iScreenHeight = GC.getGame().getScreenHeight();
	if (iScreenHeight <= 0)
	{
		FErrorMsg("Caller should've ensured that screen dims are set");
		return;
	}
	// (If we fail past here, there won't be a point in trying again.)
	m_bPlotIndicatorSizePatched = true;
	// <!-- custom: Its own switch, now that SAS ports more EXE patches and SAS_EXE_P_ON alone would turn them all off together; off counts as done, so no error message is shown.
	// Read once per process. (Claude code Opus 5.5) -->
	if (!GC.getDefineBOOL("SAS_EXE_P_PLOT_INDICATOR_ON"))
		return;
	if (!PlotIndicatorSizeMod(iScreenHeight).applyIfEnabled())
	{
		showErrorMsgToPlayer(
				"Failed to change balloon icon size. To avoid seeing "
				"this error message, set the size to \"BtS\" on the Map tab "
				"of the BUG menu. If using Steam, consider installing the "
				"\"unsupported beta\" version of BtS.");
	}
}

// advc.092c:
void Civ4BeyondSwordPatches::setHelpTextAreaSize(float fWidth)
{
	if (abs(fWidth - getHelpTextAreaWidth()) < 0.5f)
		return;
	m_fHelpTextAreaWidth = fWidth;
	// <!-- custom: Its own switch, like SAS_EXE_P_PLOT_INDICATOR_ON; this runs only when the width setting changes, so the read is not cached. (Claude code Opus 5.5) -->
	if (!GC.getDefineBOOL("SAS_EXE_P_HELP_TEXT_AREA_ON"))
		return;
	if (!HelpTextAreaWidthMod(fWidth).applyIfEnabled())
		FErrorMsg("Failed to change help text area width");
}

// <!-- custom: Called once at the end of LoadPreMenuGlobals, so the size is in place before the main menu can open a setup screen; RI calls its version at the same point.
// These define reads run once per process, so they need no static const cache; the six values are kept in globals so that sasSetupScreenGetSize, which runs each time a setup screen opens, does no string lookup. See KI#1082. (Claude code Opus 5.5) -->
void Civ4BeyondSwordPatches::patchSetupScreenSize()
{
	// <!-- custom: Test AdvCiv's master switch here rather than through applyIfEnabled, which returns true when the switch is off and nothing was applied; m_bSetupScreenSizePatched must mean the bytes were written. (Claude code Opus 5.5) -->
	if (!GC.getDefineBOOL("SAS_EXE_P_ON") || !GC.getDefineBOOL("SAS_EXE_P_DYNAM_MAIN_MENU_ON"))
		return;
	g_iSetupScreenWidthPercent = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_WIDTH_PCT");
	g_iSetupScreenHeightPercent = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_HEIGHT_PCT");
	g_iSetupScreenWidthAdd = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_WIDTH_ADD");
	g_iSetupScreenHeightAdd = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_HEIGHT_ADD");
	g_iSetupScreenWidthFreeMin = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_WIDTH_FREE_MIN");
	g_iSetupScreenHeightFreeMin = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_HEIGHT_FREE_MIN");
	bool const bGog = GC.getDefineBOOL("SAS_EXE_P_GOG_ON");
	bool const bSteam = GC.getDefineBOOL("SAS_EXE_P_STEAM_ON");
	SetupScreenSizeMod patch(bGog, bSteam);
	m_bSetupScreenSizePatched = patch.applyIfEnabled();
	FAssertMsg(m_bSetupScreenSizePatched, "Setup screen size patch skipped: unknown EXE, or its build switched off");
	// <!-- custom: The globe follows the box, so it is hooked only when the box patch was applied.
	// Until the box is first sized, the cave reads 0 and leaves the EXE's size alone. See KI#1082. (Claude code Opus 5.5) -->
	if (!m_bSetupScreenSizePatched || !GC.getDefineBOOL("SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_ON"))
		return;
	g_iSetupScreenGlobeWidthPercent = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_WIDTH_PCT");
	g_iSetupScreenGlobeHeightPercent = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_HEIGHT_PCT");
	g_iSetupScreenGlobeWidthAdd = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_WIDTH_ADD");
	g_iSetupScreenGlobeHeightAdd = GC.getDefineINT("SAS_EXE_P_DYNAM_MAIN_MENU_GLOBE_HEIGHT_ADD");
	g_bSetupScreenGlobeOn = true;
	SetupScreenGlobeMod globePatch(bGog, bSteam);
	m_bSetupScreenGlobePatched = globePatch.applyIfEnabled();
	FAssertMsg(m_bSetupScreenGlobePatched, "Setup screen globe patch skipped: unknown EXE");
}

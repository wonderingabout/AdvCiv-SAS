#include "CvGameCoreDLL.h"
#include "ModName.h"
#include <fstream> // <!-- custom: Read the small exported source-metadata marker used by archive/runtime version resolution. (ChatGPT-5.6-Sol) -->
#include <string.h> // <!-- custom: Supply memcpy for the mutable CreateProcess command buffer used by the one-time Git resolver. (ChatGPT-5.6-Sol) -->

// advc.106i: New implementation file; see comment in header.

namespace
{
	// <!-- custom: Private source/version helpers stay local to ModName.
	// Dirty-file display limits protect log readability/buffers only; the uncapped total dirty-file count is still recorded, so these are implementation safety limits rather than player-tunable settings. (ChatGPT-5.6-Sol) -->
	char const* const SAS_VERSION_METADATA_RELATIVE_PATH = "Assets\\SASModVersion.txt";
	int const SAS_VERSION_DIRTY_FILE_DISPLAY_LIMIT = 32; // maximum changed paths written into dirtyFiles
	int const SAS_VERSION_DIRTY_FILES_DISPLAY_CHAR_LIMIT = 1200; // maximum aggregate dirtyFiles text; bounds diagnostic-row size/readability

	// <!-- custom: Small normalization/validation helpers below belong only to the source-version resolver; keeping them private avoids adding generic-looking utilities to the wider DLL API. (ChatGPT-5.6-Sol) -->
	CvString trimSourceValue(CvString value)
	{
		while (!value.empty() && (value[0] == ' ' || value[0] == '\t' || value[0] == '\r' || value[0] == '\n'))
			value.erase(0, 1);
		while (!value.empty())
		{
			char const c = value[value.length() - 1];
			if (c != ' ' && c != '\t' && c != '\r' && c != '\n')
				break;
			value.erase(value.length() - 1, 1);
		}
		return value;
	}

	// <!-- custom: Git short-status uses a leading space as its unstaged-status column, so command output cleanup must preserve leading whitespace and remove only trailing CR/LF line endings. (ChatGPT-5.6-Sol) -->
	CvString trimSourceCommandOutput(CvString value)
	{
		while (!value.empty() && (value[value.length() - 1] == '\r' || value[value.length() - 1] == '\n'))
			value.erase(value.length() - 1, 1);
		return value;
	}

	bool isDecimalSourceValue(CvString const& value)
	{
		if (value.empty())
			return false;
		for (int i = 0; i < (int)value.length(); i++)
		{
			if (value[i] < '0' || value[i] > '9')
				return false;
		}
		return true;
	}

	bool parseSourceCount(CvString const& value, int& iResult)
	{
		CvString const normalized = trimSourceValue(value);
		if (!isDecimalSourceValue(normalized))
			return false;
		iResult = 0;
		for (int i = 0; i < (int)normalized.length(); i++)
			iResult = iResult * 10 + (normalized[i] - '0');
		return true;
	}

	// <!-- custom: Git rev-list --left-right --count emits two decimal counts separated by whitespace; parse both without relying on locale-dependent stream formatting.
	// VC2003 rejected size_t indexing of const CvString with C2666 (its const overload takes int); use c_str() for byte indexing without narrowing the position. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
	bool parseSourceAheadBehind(CvString const& value, int& iCurrentOnly, int& iDefaultOnly)
	{
		CvString const normalized = trimSourceValue(value);
		size_t iSplit = 0;
		while (iSplit < normalized.length() && normalized.c_str()[iSplit] >= '0' && normalized.c_str()[iSplit] <= '9')
			iSplit++;
		if (iSplit == 0)
			return false;
		size_t iSecond = iSplit;
		while (iSecond < normalized.length() && (normalized.c_str()[iSecond] == ' ' || normalized.c_str()[iSecond] == '\t'))
			iSecond++;
		if (iSecond == iSplit || iSecond >= normalized.length())
			return false;
		return parseSourceCount(normalized.substr(0, iSplit), iCurrentOnly) &&
				parseSourceCount(normalized.substr(iSecond), iDefaultOnly);
	}

	// <!-- custom: Validate each patch header against its raw NUL-list path before pairing them; equal block counts alone cannot detect a reordered or changed name list.
	// ASCII bytes below 32 and DEL (127) are controls; bytes >= 128 include non-ASCII UTF-8 data.
	// Git quotes controls/backslashes/quotes and normally octal-escapes UTF-8 bytes; core.quotePath=false retains those bytes, so recognize either documented header spelling. (GPT-6.1-Sol) -->
	CvString quoteSourcePatchPath(CvString const& path, bool bQuoteHighBytes)
	{
		CvString result = "\"";
		for (size_t i = 0; i < path.length(); i++)
		{
			unsigned char const c = (unsigned char)path.c_str()[i];
			switch (c)
			{
			case '\\': result += "\\\\"; break;
			case '"': result += "\\\""; break;
			case '\a': result += "\\a"; break;
			case '\b': result += "\\b"; break;
			case '\t': result += "\\t"; break;
			case '\n': result += "\\n"; break;
			case '\v': result += "\\v"; break;
			case '\f': result += "\\f"; break;
			case '\r': result += "\\r"; break;
			default:
				if (c < 32 || c == 127 || (bQuoteHighBytes && c >= 128))
					result += CvString::format("\\%03o", (unsigned int)c);
				else result += (char)c;
			}
		}
		return result + "\"";
	}

	bool isHexSourceValue(CvString const& value, size_t iExpectedLength)
	{
		if (value.length() != iExpectedLength)
			return false;
		for (int i = 0; i < (int)value.length(); i++)
		{
			char const c = value[i];
			if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')))
				return false;
		}
		return true;
	}

	CvString normalizedPathForCompare(CvString value)
	{
		value = trimSourceValue(value);
		for (size_t i = 0; i < value.length(); i++)
		{
			if (value[i] == '/')
				value[i] = '\\';
			else if (value[i] >= 'A' && value[i] <= 'Z')
				value[i] = (char)(value[i] - 'A' + 'a');
		}
		while (value.length() > 3 && value[value.length() - 1] == '\\')
			value.erase(value.length() - 1, 1);
		return value;
	}

	// <!-- custom: Run Git without a console-window flash, capture stdout through a pipe, and discard stderr so warnings cannot contaminate parsed metadata/status rows.
	// This is used only for a real development checkout; exported archives normally resolve the marker first and never spawn Git. (ChatGPT-5.6-Sol) -->
	bool runHiddenSourceCommand(CvString const& commandLine, CvString& output)
	{
		output.clear();
		SECURITY_ATTRIBUTES kSecurity;
		ZeroMemory(&kSecurity, sizeof(kSecurity));
		kSecurity.nLength = sizeof(kSecurity);
		kSecurity.bInheritHandle = TRUE;
		HANDLE hRead = NULL;
		HANDLE hWrite = NULL;
		if (!CreatePipe(&hRead, &hWrite, &kSecurity, 0))
			return false;
		if (!SetHandleInformation(hRead, HANDLE_FLAG_INHERIT, 0))
		{
			CloseHandle(hRead);
			CloseHandle(hWrite);
			return false;
		}

		HANDLE hNull = CreateFileA("NUL", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, &kSecurity, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
		if (hNull == INVALID_HANDLE_VALUE)
		{
			CloseHandle(hRead);
			CloseHandle(hWrite);
			return false;
		}

		STARTUPINFOA kStartup;
		PROCESS_INFORMATION kProcess;
		ZeroMemory(&kStartup, sizeof(kStartup));
		ZeroMemory(&kProcess, sizeof(kProcess));
		kStartup.cb = sizeof(kStartup);
		kStartup.dwFlags = STARTF_USESTDHANDLES;
		kStartup.hStdInput = hNull;
		kStartup.hStdOutput = hWrite;
		kStartup.hStdError = hNull;

		std::vector<char> command(commandLine.length() + 1);
		memcpy(&command[0], commandLine.c_str(), commandLine.length() + 1);
		BOOL const bCreated = CreateProcessA(NULL, &command[0], NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &kStartup, &kProcess);
		CloseHandle(hNull);
		CloseHandle(hWrite);
		if (!bCreated)
		{
			CloseHandle(hRead);
			return false;
		}

		char buffer[2048];
		DWORD iRead = 0;
		while (ReadFile(hRead, buffer, sizeof(buffer), &iRead, NULL) && iRead > 0)
			output.append(buffer, iRead);
		CloseHandle(hRead);
		WaitForSingleObject(kProcess.hProcess, INFINITE);
		DWORD iExitCode = 1;
		GetExitCodeProcess(kProcess.hProcess, &iExitCode);
		CloseHandle(kProcess.hThread);
		CloseHandle(kProcess.hProcess);
		output = trimSourceCommandOutput(output);
		return (iExitCode == 0);
	}

	CvString sourceGitCommand(CvString const& modPath, char const* szArguments)
	{
		return CvString::format("git.exe -C \"%s\" %s", modPath.c_str(), szArguments);
	}

	void splitFirstSourceLine(CvString const& value, CvString& first, CvString& rest)
	{
		size_t const iBreak = value.find('\n');
		if (iBreak == CvString::npos)
		{
			first = trimSourceValue(value);
			rest.clear();
			return;
		}
		first = trimSourceValue(value.substr(0, iBreak));
		rest = trimSourceValue(value.substr(iBreak + 1));
	}

	CvString summarizeTrackedSourceStatus(CvString const& rawStatus, int& iFileCount)
	{
		iFileCount = 0;
		int iDisplayedFileCount = 0;
		CvString result;
		size_t iStart = 0;
		while (iStart < rawStatus.length())
		{
			size_t iEnd = rawStatus.find('\n', iStart);
			if (iEnd == CvString::npos)
				iEnd = rawStatus.length();
			CvString line = trimSourceValue(rawStatus.substr(iStart, iEnd - iStart));
			if (!line.empty())
			{
				iFileCount++;
				if (iDisplayedFileCount < SAS_VERSION_DIRTY_FILE_DISPLAY_LIMIT)
				{
					// <!-- custom: Preserve Git's two status columns, including staged-vs-unstaged distinction. (ChatGPT-5.6-Sol) -->
					CvString displayLine = rawStatus.substr(iStart, iEnd - iStart);
					if (!displayLine.empty() && displayLine[displayLine.length() - 1] == '\r')
						displayLine.erase(displayLine.length() - 1, 1);
					for (size_t i = 0; i < displayLine.length(); i++)
					{
						if (displayLine[i] == '"')
							displayLine[i] = '\'';
					}
					if (displayLine.length() >= 3)
						displayLine = "[" + displayLine.substr(0, 2) + "] " + displayLine.substr(3);
					size_t const iSeparatorLength = (result.empty() ? 0 : 2);
					if (result.length() + iSeparatorLength + displayLine.length() <= SAS_VERSION_DIRTY_FILES_DISPLAY_CHAR_LIMIT)
					{
						if (!result.empty())
							result += "; ";
						result += displayLine;
						iDisplayedFileCount++;
					}
				}
			}
			iStart = iEnd + 1;
		}
		if (iFileCount > iDisplayedFileCount)
		{
			if (!result.empty())
				result += "; ";
			result += CvString::format("... (+%d more)", iFileCount - iDisplayedFileCount);
		}
		return result;
	}


	// <!-- custom: Parse SAS_VERSION_ANCHOR_<base>[-<distance>-g<sha>] from Git describe/export-subst.
	// Git documents the distance as the number of commits in anchor..target, so base practical version + distance exactly reconstructs git rev-list --count for descendants of a correctly named immutable anchor, including merges. (ChatGPT-5.6-Sol) -->
	bool resolveVersionFromAnchorDescribe(CvString const& describeValue, CvString& version)
	{
		char const* const szPrefix = "SAS_VERSION_ANCHOR_";
		CvString const prefix(szPrefix);
		CvString const value = trimSourceValue(describeValue);
		if (value.find(prefix) != 0)
			return false;
		size_t const iVersionStart = prefix.length();
		size_t const iDash = value.find('-', iVersionStart);
		CvString const baseText = value.substr(iVersionStart, (iDash == CvString::npos ? value.length() : iDash) - iVersionStart);
		if (!isDecimalSourceValue(baseText))
			return false;

		int iBase = 0;
		for (int i = 0; i < (int)baseText.length(); i++)
			iBase = iBase * 10 + (baseText[i] - '0');
		int iDistance = 0;
		if (iDash != CvString::npos)
		{
			size_t const iGitHash = value.find("-g", iDash + 1);
			if (iGitHash == CvString::npos)
				return false;
			CvString const distanceText = value.substr(iDash + 1, iGitHash - iDash - 1);
			if (!isDecimalSourceValue(distanceText) || iGitHash + 2 >= value.length())
				return false;
			for (int i = 0; i < (int)distanceText.length(); i++)
				iDistance = iDistance * 10 + (distanceText[i] - '0');
		}
		version = CvString::format("%d", iBase + iDistance);
		return true;
	}

	// <!-- custom: Hash the tracked gameplay code/rules/script diff relative to HEAD.
	// This intentionally scopes out docs/LLM helpers and the compiled DLL (fingerprinted separately), while covering CvGameCoreDLL sources plus Config/Python/XML/PrivateMaps inputs. (ChatGPT-5.6-Sol) -->
	CvString fingerprintTrackedCodeRulesDiff(CvString const& diff)
	{
		unsigned __int64 uiHash = ((unsigned __int64)0xCBF29CE4 << 32) | 0x84222325;
		unsigned __int64 const uiPrime = ((unsigned __int64)0x00000100 << 32) | 0x000001B3;
		// <!-- custom: Visual C++ 2003 reported C2666 for CvString::operator[] with a size_t index because CvString exposes an int subscript plus a const char* conversion.
		// Use int to select the member overload unambiguously. (GPT-5.6-Sol) -->
		for (int i = 0; i < (int)diff.length(); i++)
		{
			uiHash ^= (unsigned char)diff[i];
			uiHash *= uiPrime;
		}
		CvString fingerprint;
		fingerprint.Format("FNV1A64:%016I64X", uiHash);
		return fingerprint;
	}

	// <!-- custom: Read the tiny export-subst marker used when no live Git worktree ships with the mod.
	// Exact SHA validates the marker; the optional anchor describe string reconstructs the practical numeric version. (ChatGPT-5.6-Sol) -->
	bool readExportedSourceMetadata(CvString const& modPath, CvString& version, CvString& commitHash, CvString& commitDate)
	{
		CvString path = modPath;
		if (!path.empty() && path[path.length() - 1] != '\\' && path[path.length() - 1] != '/')
			path += "\\";
		path += SAS_VERSION_METADATA_RELATIVE_PATH;
		std::ifstream input(path.c_str());
		if (!input.is_open())
			return false;
		std::string rawLine;
		while (std::getline(input, rawLine))
		{
			CvString line = trimSourceValue(rawLine.c_str());
			size_t const iEquals = line.find('=');
			if (iEquals == CvString::npos)
				continue;
			CvString const key = trimSourceValue(line.substr(0, iEquals));
			CvString const value = trimSourceValue(line.substr(iEquals + 1));
			if (key == "versionDescribe" && value.find("$Format:") == CvString::npos)
				resolveVersionFromAnchorDescribe(value, version);
			else if (key == "commit" && isHexSourceValue(value, 40))
				commitHash = value;
			else if (key == "commitDate" && value.find("$Format:") == CvString::npos)
				commitDate = value;
		}
		// <!-- custom: Exact SHA is the trust anchor for exported metadata; an unsubstituted/hand-edited marker must not be treated as valid source provenance. (ChatGPT-5.6-Sol) -->
		if (commitHash.empty())
		{
			version.clear();
			commitDate.clear();
			return false;
		}
		return true;
	}
}

// <!-- custom: Initialize the lazy source/version cache explicitly; ModName exists before any source-details getter is necessarily called. (ChatGPT-5.6-Sol) -->
ModName::ModName()
{
	resetSourceDetails();
}

// <!-- custom: Invalidate every cached source field together.
// update() calls this when BtS refreshes the loaded mod path, so no provenance from a previous path can survive. (ChatGPT-5.6-Sol) -->
void ModName::resetSourceDetails()
{
	m_bSourceDetailsResolved = false;
	m_bDiagnosticSourceDetailsResolved = false;
	m_bSourceDiffDetailsAvailable = false;
	m_iSourceDirtyState = -1;
	m_iSourceDirtyFileCount = -1;
	m_iSourceCurrentOnlyCommitCount = -1;
	m_iSourceDefaultOnlyCommitCount = -1;
	m_iSourceCodeRulesDiffBytes = -1;
	m_iSourceStagedCodeRulesDiffBytes = -1;
	m_iSourceUnstagedCodeRulesDiffBytes = -1;
	m_sVersion.clear();
	m_sCommitHash.clear();
	m_sBranch.clear();
	m_sCommitDate.clear();
	m_sSourceMetadataType = "unknown";
	m_sSourceDirtyFiles.clear();
	m_sSourceCodeRulesDiffFingerprint = "-";
	m_sSourceStagedCodeRulesDiffFingerprint = "-";
	m_sSourceUnstagedCodeRulesDiffFingerprint = "-";
	m_sSourceDefaultBranch.clear();
	m_sSourceDefaultCommitHash.clear();
	m_sSourceDefaultVersion.clear();
	m_sSourceDefaultRefSource = "UNAVAILABLE";
	m_sSourceMergeBaseCommitHash.clear();
	m_sSourceMergeBaseVersion.clear();
	m_sSourceBranchRelation = "UNAVAILABLE";
	m_aSourceDiffFiles.clear();
}

void ModName::update(char const* szFullPath, char const* szPathInRoot)
{
	m_sFullPath = szFullPath;
	m_sPathInRoot = szPathInRoot;
	m_sName = m_sPathInRoot;
	size_t posMods = m_sName.find("Mods");
	if (posMods != CvString::npos)
	{
		/*	Skip over "Mods" plus the path separator.
			And chop off the separator at the end. */
		m_sName = m_sName.substr(posMods + 5, m_sName.length() - posMods - 6);
	}
	// <!-- custom: Resolve branded identity here, while BtS's loaded folder is already known but before XML/Python startup can request the display name.
	// This keeps the practical-6326 two-identity model without making an early Python import depend on later GlobalDefines. See KI#110.2. (ChatGPT-5.6-Sol) -->
	cacheDisplayName();
	// <!-- custom: A refreshed loaded-mod path invalidates any source metadata cached for the previous path. (ChatGPT-5.6-Sol) -->
	resetSourceDetails();
}

// <!-- custom: Central branded/project identity cached from the mod INI during update(); never substitute the installed folder because the two identities deliberately may differ.
// Failed configuration is reported once by cacheDisplayName(), including in Release, with an explicit unavailable label rather than guessed branding. See KI#110.2. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
char const* ModName::getDisplayName() const
{
	FAssertMsg(!m_sDisplayName.empty(), "Branded mod name requested before ModName initialization; see KI#110.2");
	return m_sDisplayName.c_str();
}

// <!-- custom: Convert AdvCiv/BtS's cached mod path into an absolute filesystem path for the metadata-file/.git checks without changing the public loaded-folder identity. (ChatGPT-5.6-Sol) -->
CvString ModName::getAbsoluteModPath() const
{
	CvString path = m_sFullPath;
	bool const bAbsoluteDrivePath = (path.length() >= 3 && path[1] == ':' && (path[2] == '\\' || path[2] == '/'));
	bool const bAbsoluteUNCPath = (path.length() >= 2 && ((path[0] == '\\' && path[1] == '\\') || (path[0] == '/' && path[1] == '/')));
	if (!bAbsoluteDrivePath && !bAbsoluteUNCPath)
	{
		char szExePath[MAX_PATH + 1];
		DWORD const iLength = GetModuleFileNameA(NULL, szExePath, MAX_PATH);
		if (iLength == 0 || iLength >= MAX_PATH)
			return "";
		szExePath[iLength] = '\0';
		CvString exePath(szExePath);
		size_t const iSlash = exePath.find_last_of("\\/");
		if (iSlash == CvString::npos)
			return "";
		path = exePath.substr(0, iSlash + 1) + m_sPathInRoot;
	}
	while (path.length() > 3 && (path[path.length() - 1] == '\\' || path[path.length() - 1] == '/'))
		path.erase(path.length() - 1, 1);
	return path;
}

// <!-- custom: Civ4 mod INIs conventionally match the loaded folder name; BUG's own NoCustomAssets reader already uses getModFolder() + ".ini".
// Read only the branded [CONFIG] Name from that folder-matched INI, with an explicit capacity passed to Win32's INI API; folder/path identity remains independently cached in m_sName/m_sPathInRoot.
// This runs from update() before the Python import path that exposed assertion #1, and replaces the later SAS_MOD_DISPLAY_NAME dependency introduced by SAS commit 66b46c22d2. See KI#110.2. (ChatGPT-5.6-Sol) -->
void ModName::cacheDisplayName()
{
	m_sDisplayName.clear();
	CvString const modPath = getAbsoluteModPath();
	// <!-- custom: A missing INI/key or blank name must be visible in ordinary Release builds too; FAssert alone disappears there and can be ignored automatically in diagnostic builds.
	// Report once at initialization, not on each getter, and mark subsequent UI/log output explicitly unavailable instead of substituting installation-folder identity.
	// update() runs before CvGlobals assigns gDLL, so use Win32 directly rather than the EXE message/log interfaces. See KI#110.2. (GPT-6.1-Sol) -->
	CvString const iniPath = (modPath.empty() || m_sName.empty()) ? "" : modPath + "\\" + m_sName + ".ini";
	if (!iniPath.empty())
	{
		// <!-- custom: Unlike the capacity-less FXML path from KI#1001, GetPrivateProfileStringA receives the destination size.
		// Grow and retry on its capacity - 1 truncation signal so the central branded value is never silently shortened or constrained by another arbitrary 256-byte contract. See KI#110.2. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
		std::vector<char> displayNameBuffer(256);
		for (;;)
		{
			DWORD const iLength = GetPrivateProfileStringA("CONFIG", "Name", "",
					&displayNameBuffer[0], static_cast<DWORD>(displayNameBuffer.size()), iniPath.c_str());
			if (iLength == 0)
				break;
			if (iLength < displayNameBuffer.size() - 1)
			{
				m_sDisplayName = trimSourceValue(&displayNameBuffer[0]);
				break;
			}
			displayNameBuffer.resize(displayNameBuffer.size() * 2);
		}
	}
	if (!m_sDisplayName.empty())
		return;
	m_sDisplayName = "[Mod name unavailable]";
	CvString message;
	message.Format("Cannot read a non-empty branded mod name from [CONFIG] Name.\n\nINI path: %s\n\nCheck that this file exists, is readable, and contains [CONFIG] followed by Name = your project name. The INI filename must match the installed mod folder.\n\nIf you continue, runtime branding will show [Mod name unavailable]. Correct the configuration and restart Civilization IV. See KI#110.2.",
			iniPath.empty() ? "<unresolved loaded mod path>" : iniPath.c_str());
	OutputDebugStringA(message.c_str());
	MessageBoxA(NULL, message.c_str(), "Mod identity configuration error", MB_OK | MB_ICONERROR | MB_TASKMODAL);
}

// <!-- custom: Split one Git diff layer into per-file patch fingerprints without spawning Git once per path.
// Return true only for a complete layer, including an empty one, so failed detail capture is distinct from a clean tree.
// Walk the NUL-separated name list and ordered patch blocks in tandem instead of duplicating the full diff into a second vector; if an unusual Git output shape breaks that invariant, roll back the layer rather than attach a fingerprint to the wrong file. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
bool ModName::appendSourceDiffLayer(char const* szScope, CvString const& paths, CvString const& diff) const
{
	if (paths.empty() && diff.empty())
		return true;
	if (paths.empty() || diff.empty() || diff.find("diff --git ") != 0)
		return false;
	size_t const iInitialEntries = m_aSourceDiffFiles.size();
	size_t iPathStart = 0;
	size_t iBlockStart = 0;
	while (iPathStart < paths.length())
	{
		size_t iPathEnd = paths.find('\0', iPathStart);
		if (iPathEnd == CvString::npos)
			iPathEnd = paths.length();
		if (iPathEnd == iPathStart)
		{
			iPathStart = iPathEnd + 1;
			continue;
		}
		if (iBlockStart >= diff.length() || diff.compare(iBlockStart, 11, "diff --git ") != 0)
		{
			m_aSourceDiffFiles.resize(iInitialEntries);
			return false;
		}
		size_t const iMarker = diff.find("\ndiff --git ", iBlockStart + 1);
		size_t const iBlockEnd = (iMarker == CvString::npos ? diff.length() : iMarker + 1);
		CvString const path = paths.substr(iPathStart, iPathEnd - iPathStart);
		size_t const iHeaderEnd = diff.find('\n', iBlockStart);
		CvString const header = diff.substr(iBlockStart, iHeaderEnd - iBlockStart);
		CvString const from = "a/" + path;
		CvString const to = "b/" + path;
		if (header != "diff --git " + from + " " + to &&
				header != "diff --git " + quoteSourcePatchPath(from, true) + " " + quoteSourcePatchPath(to, true) &&
				header != "diff --git " + quoteSourcePatchPath(from, false) + " " + quoteSourcePatchPath(to, false))
		{
			m_aSourceDiffFiles.resize(iInitialEntries);
			return false;
		}
		CvString const szBlock = diff.substr(iBlockStart, iBlockEnd - iBlockStart);
		SourceDiffFile entry;
		entry.szScope = szScope;
		entry.szPath = path;
		entry.iDiffBytes = (__int64)szBlock.length();
		entry.szDiffFingerprint = fingerprintTrackedCodeRulesDiff(szBlock);
		m_aSourceDiffFiles.push_back(entry);
		iPathStart = iPathEnd + 1;
		iBlockStart = (iMarker == CvString::npos ? diff.length() : iMarker + 1);
	}
	if (iBlockStart != diff.length())
	{
		m_aSourceDiffFiles.resize(iInitialEntries);
		return false;
	}
	return true;
}

// <!-- custom: Resolve source provenance lazily once per loaded mod path, then cache it for the rest of the process.
// Archives normally cost one tiny metadata-file read; Git checkouts resolve identity/status once, while expensive ancestry and patches belong to the separate diagnostic resolver. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void ModName::resolveSourceDetails() const
{
	if (m_bSourceDetailsResolved)
		return;
	m_bSourceDetailsResolved = true;
	CvString const modPath = getAbsoluteModPath();
	if (modPath.empty())
		return;

	// <!-- custom: GitHub/git-archive downloads can reconstruct the exact practical version from one immutable SAS_VERSION_ANCHOR_<exact-count> tag plus Git describe distance, while export-subst supplies exact commit/date.
	// Archive metadata deliberately has no branch/default-branch relation or dirty-layer detail because those facts require an inspectable checkout. (ChatGPT-5.6-Sol) -->
	if (readExportedSourceMetadata(modPath, m_sVersion, m_sCommitHash, m_sCommitDate))
	{
		m_sSourceMetadataType = (m_sVersion.empty() ? "gitArchive" : "gitArchiveVersioned");
		return;
	}

	// <!-- custom: If this is a plain copied/exported folder whose metadata marker was not substituted, avoid spawning Git merely to discover an unrelated parent repository.
	// Git worktrees may use either a .git directory or file, so existence is enough here; the exact top-level path is still verified below. (ChatGPT-5.6-Sol) -->
	CvString const gitMarker = modPath + "\\.git";
	if (GetFileAttributesA(gitMarker.c_str()) == INVALID_FILE_ATTRIBUTES)
		return;

	CvString output;
	if (!runHiddenSourceCommand(sourceGitCommand(modPath, "rev-parse --show-toplevel"), output))
		return;
	if (normalizedPathForCompare(output) != normalizedPathForCompare(modPath))
		return;

	// <!-- custom: %cI is Git's strict ISO-8601 committer date with the timezone offset stored in the commit.
	// Keep that canonical commit metadata rather than rewriting it to the runtime log's UTC event-time convention. (ChatGPT-5.6-Sol) -->
	CvString commitAndDate;
	if (!runHiddenSourceCommand(sourceGitCommand(modPath, "show -s --format=%H%n%cI HEAD"), commitAndDate))
		return;
	splitFirstSourceLine(commitAndDate, m_sCommitHash, m_sCommitDate);
	if (!isHexSourceValue(m_sCommitHash, 40))
	{
		m_sCommitHash.clear();
		m_sCommitDate.clear();
		return;
	}

	runHiddenSourceCommand(sourceGitCommand(modPath, "rev-parse --abbrev-ref HEAD"), m_sBranch);
	CvString shallow;
	bool const bShallowKnown = runHiddenSourceCommand(sourceGitCommand(modPath, "rev-parse --is-shallow-repository"), shallow);
	bool const bShallow = (bShallowKnown && trimSourceValue(shallow) == "true");
	bool const bFullHistory = (bShallowKnown && trimSourceValue(shallow) == "false");
	if (bFullHistory)
	{
		CvString version;
		if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("rev-list --count %s", m_sCommitHash.c_str()).c_str()), version) && isDecimalSourceValue(version))
			m_sVersion = version;
	}

	CvString status;
	if (runHiddenSourceCommand(sourceGitCommand(modPath, "status --short --untracked-files=no"), status))
	{
		m_sSourceDirtyFiles = summarizeTrackedSourceStatus(status, m_iSourceDirtyFileCount);
		m_iSourceDirtyState = (m_iSourceDirtyFileCount > 0 ? 1 : 0);
	}
	m_sSourceMetadataType = (bShallow ? "gitShallow" : (bFullHistory ? "git" : "gitHistoryUnknown"));
}

// <!-- custom: Basic version/dirty UI getters must not enumerate ancestry or construct diagnostic patches when logging is disabled.
// Only diagnostic accessors enter this second lazy cache, after their caller's BBAI/SGR/runtime enable gate; each patch layer is released before reading the next.
// Like the basic identity, this is a first-use snapshot for the loaded mod path, not live monitoring of later source edits.
// Anchor counts/diffs to the captured commit SHAs: movable HEAD/default refs may change between the basic lookup and the first diagnostic request. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
void ModName::resolveDiagnosticSourceDetails() const
{
	if (m_bDiagnosticSourceDetailsResolved)
		return;
	m_bDiagnosticSourceDetailsResolved = true;
	resolveSourceDetails();
	if (m_sSourceMetadataType != "git" && m_sSourceMetadataType != "gitShallow" && m_sSourceMetadataType != "gitHistoryUnknown")
		return;
	CvString const modPath = getAbsoluteModPath();
	if (m_sSourceMetadataType == "git")
	{
		// <!-- custom: The practical count belongs to this exact HEAD, not to a global timeline.
		// Resolve the locally known default branch and merge-base relationship so feature/reproducer branches can be interpreted later without mistaking main+N for a future main practical number.
		// No fetch is attempted; the chosen local ref source is recorded explicitly. (ChatGPT-5.6-Sol) -->
		CvString originHead;
		if (runHiddenSourceCommand(sourceGitCommand(modPath, "symbolic-ref --quiet refs/remotes/origin/HEAD"), originHead))
		{
			originHead = trimSourceValue(originHead);
			char const* const szRemotePrefix = "refs/remotes/origin/";
			CvString const remotePrefix(szRemotePrefix);
			if (originHead.find(remotePrefix) == 0 && originHead.length() > remotePrefix.length())
			{
				m_sSourceDefaultBranch = originHead.substr(remotePrefix.length());
				CvString defaultRef = CvString("refs/heads/") + m_sSourceDefaultBranch;
				CvString defaultCommit;
				if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("rev-parse --verify %s", defaultRef.c_str()).c_str()), defaultCommit) && isHexSourceValue(trimSourceValue(defaultCommit), 40))
					m_sSourceDefaultRefSource = "LOCAL_BRANCH";
				else
				{
					defaultRef = originHead;
					if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("rev-parse --verify %s", defaultRef.c_str()).c_str()), defaultCommit) && isHexSourceValue(trimSourceValue(defaultCommit), 40))
						m_sSourceDefaultRefSource = "REMOTE_TRACKING";
					else defaultRef.clear();
				}
				if (!defaultRef.empty())
				{
					m_sSourceDefaultCommitHash = trimSourceValue(defaultCommit);
					CvString defaultVersion;
					if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("rev-list --count %s", m_sSourceDefaultCommitHash.c_str()).c_str()), defaultVersion) && isDecimalSourceValue(defaultVersion))
						m_sSourceDefaultVersion = defaultVersion;
					CvString mergeBase;
					if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("merge-base %s %s", m_sCommitHash.c_str(), m_sSourceDefaultCommitHash.c_str()).c_str()), mergeBase) && isHexSourceValue(trimSourceValue(mergeBase), 40))
					{
						m_sSourceMergeBaseCommitHash = trimSourceValue(mergeBase);
						CvString mergeBaseVersion;
						if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("rev-list --count %s", m_sSourceMergeBaseCommitHash.c_str()).c_str()), mergeBaseVersion) && isDecimalSourceValue(mergeBaseVersion))
							m_sSourceMergeBaseVersion = mergeBaseVersion;
					}
					CvString aheadBehind;
					if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("rev-list --left-right --count %s...%s", m_sCommitHash.c_str(), m_sSourceDefaultCommitHash.c_str()).c_str()), aheadBehind) &&
							parseSourceAheadBehind(aheadBehind, m_iSourceCurrentOnlyCommitCount, m_iSourceDefaultOnlyCommitCount))
					{
						if (m_iSourceCurrentOnlyCommitCount == 0 && m_iSourceDefaultOnlyCommitCount == 0)
							m_sSourceBranchRelation = "AT_DEFAULT";
						else if (m_iSourceCurrentOnlyCommitCount > 0 && m_iSourceDefaultOnlyCommitCount == 0)
							m_sSourceBranchRelation = "AHEAD_OF_DEFAULT";
						else if (m_iSourceCurrentOnlyCommitCount == 0 && m_iSourceDefaultOnlyCommitCount > 0)
							m_sSourceBranchRelation = "BEHIND_DEFAULT";
						else m_sSourceBranchRelation = "DIVERGED";
					}
				}
			}
		}
	}
	bool bStagedDetailsAvailable = false;
	bool bUnstagedDetailsAvailable = false;
	{
		// <!-- custom: Keep the original combined HEAD-to-working-tree patch for backward-compatible whole-state provenance, then preserve staged and unstaged patches independently so an MM file cannot hide how the tested state was assembled.
		// Scope remains tracked runtime-relevant C++/Config/Python/XML/PrivateMaps inputs; untracked files are not claimed and the loaded DLL has its own exact-byte fingerprint. (ChatGPT-5.6-Sol) -->
		{
			CvString diff;
			if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("diff --src-prefix=a/ --dst-prefix=b/ --no-relative --binary --full-index --no-ext-diff --no-textconv --no-renames --no-color %s -- CvGameCoreDLL Assets/Config Assets/Python Assets/XML PrivateMaps", m_sCommitHash.c_str()).c_str()), diff))
			{
				m_iSourceCodeRulesDiffBytes = (__int64)diff.length();
				m_sSourceCodeRulesDiffFingerprint = fingerprintTrackedCodeRulesDiff(diff);
			}
		}
		{
			CvString stagedDiff;
			if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("diff --cached --src-prefix=a/ --dst-prefix=b/ --no-relative --binary --full-index --no-ext-diff --no-textconv --no-renames --no-color %s -- CvGameCoreDLL Assets/Config Assets/Python Assets/XML PrivateMaps", m_sCommitHash.c_str()).c_str()), stagedDiff))
			{
				m_iSourceStagedCodeRulesDiffBytes = (__int64)stagedDiff.length();
				m_sSourceStagedCodeRulesDiffFingerprint = fingerprintTrackedCodeRulesDiff(stagedDiff);
				CvString stagedPaths;
				if (runHiddenSourceCommand(sourceGitCommand(modPath, CvString::format("diff --cached --name-only -z --no-renames %s -- CvGameCoreDLL Assets/Config Assets/Python Assets/XML PrivateMaps", m_sCommitHash.c_str()).c_str()), stagedPaths))
					bStagedDetailsAvailable = appendSourceDiffLayer("STAGED", stagedPaths, stagedDiff);
			}
		}
		{
			CvString unstagedDiff;
			if (runHiddenSourceCommand(sourceGitCommand(modPath, "diff --src-prefix=a/ --dst-prefix=b/ --no-relative --binary --full-index --no-ext-diff --no-textconv --no-renames --no-color -- CvGameCoreDLL Assets/Config Assets/Python Assets/XML PrivateMaps"), unstagedDiff))
			{
				m_iSourceUnstagedCodeRulesDiffBytes = (__int64)unstagedDiff.length();
				m_sSourceUnstagedCodeRulesDiffFingerprint = fingerprintTrackedCodeRulesDiff(unstagedDiff);
				CvString unstagedPaths;
				if (runHiddenSourceCommand(sourceGitCommand(modPath, "diff --name-only -z --no-renames -- CvGameCoreDLL Assets/Config Assets/Python Assets/XML PrivateMaps"), unstagedPaths))
					bUnstagedDetailsAvailable = appendSourceDiffLayer("UNSTAGED", unstagedPaths, unstagedDiff);
			}
		}
	}
	m_bSourceDiffDetailsAvailable = bStagedDetailsAvailable && bUnstagedDetailsAvailable;
}

// <!-- custom: Thin public accessors keep source lookup policy in ModName.
// Basic UI accessors use only identity/status; diagnostic accessors below use the separately gated ancestry/patch cache. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
char const* ModName::getVersion() const
{
	resolveSourceDetails();
	return m_sVersion.c_str();
}

char const* ModName::getCommitHash() const
{
	resolveSourceDetails();
	return m_sCommitHash.c_str();
}

char const* ModName::getBranch() const
{
	resolveSourceDetails();
	return m_sBranch.c_str();
}

char const* ModName::getCommitDate() const
{
	resolveSourceDetails();
	return m_sCommitDate.c_str();
}

char const* ModName::getSourceMetadataType() const
{
	resolveSourceDetails();
	return m_sSourceMetadataType.c_str();
}

int ModName::getSourceDirtyState() const
{
	resolveSourceDetails();
	return m_iSourceDirtyState;
}

int ModName::getSourceDirtyFileCount() const
{
	resolveSourceDetails();
	return m_iSourceDirtyFileCount;
}

char const* ModName::getSourceDirtyFiles() const
{
	resolveSourceDetails();
	return m_sSourceDirtyFiles.c_str();
}

char const* ModName::getSourceDefaultBranch() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceDefaultBranch.c_str();
}

char const* ModName::getSourceDefaultCommitHash() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceDefaultCommitHash.c_str();
}

char const* ModName::getSourceDefaultVersion() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceDefaultVersion.c_str();
}

char const* ModName::getSourceDefaultRefSource() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceDefaultRefSource.c_str();
}

char const* ModName::getSourceMergeBaseCommitHash() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceMergeBaseCommitHash.c_str();
}

char const* ModName::getSourceMergeBaseVersion() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceMergeBaseVersion.c_str();
}

char const* ModName::getSourceBranchRelation() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceBranchRelation.c_str();
}

int ModName::getSourceCurrentOnlyCommitCount() const
{
	resolveDiagnosticSourceDetails();
	return m_iSourceCurrentOnlyCommitCount;
}

int ModName::getSourceDefaultOnlyCommitCount() const
{
	resolveDiagnosticSourceDetails();
	return m_iSourceDefaultOnlyCommitCount;
}

// <!-- custom: Fingerprint tracked gameplay code/rules/scripts relative to HEAD so logs can distinguish different runtime-relevant edits without hashing docs, LLM helpers, or the separately fingerprinted loaded DLL. (ChatGPT-5.6-Sol) -->
__int64 ModName::getSourceCodeRulesDiffBytes() const
{
	resolveDiagnosticSourceDetails();
	return m_iSourceCodeRulesDiffBytes;
}

char const* ModName::getSourceCodeRulesDiffFingerprint() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceCodeRulesDiffFingerprint.c_str();
}

__int64 ModName::getSourceStagedCodeRulesDiffBytes() const
{
	resolveDiagnosticSourceDetails();
	return m_iSourceStagedCodeRulesDiffBytes;
}

char const* ModName::getSourceStagedCodeRulesDiffFingerprint() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceStagedCodeRulesDiffFingerprint.c_str();
}

__int64 ModName::getSourceUnstagedCodeRulesDiffBytes() const
{
	resolveDiagnosticSourceDetails();
	return m_iSourceUnstagedCodeRulesDiffBytes;
}

char const* ModName::getSourceUnstagedCodeRulesDiffFingerprint() const
{
	resolveDiagnosticSourceDetails();
	return m_sSourceUnstagedCodeRulesDiffFingerprint.c_str();
}

int ModName::getSourceDiffFileCount() const
{
	resolveDiagnosticSourceDetails();
	return (int)m_aSourceDiffFiles.size();
}

char const* ModName::getSourceDiffFileScope(int iIndex) const
{
	resolveDiagnosticSourceDetails();
	return (iIndex >= 0 && iIndex < (int)m_aSourceDiffFiles.size() ? m_aSourceDiffFiles[iIndex].szScope.c_str() : "");
}

char const* ModName::getSourceDiffFilePath(int iIndex) const
{
	resolveDiagnosticSourceDetails();
	return (iIndex >= 0 && iIndex < (int)m_aSourceDiffFiles.size() ? m_aSourceDiffFiles[iIndex].szPath.c_str() : "");
}

__int64 ModName::getSourceDiffFileBytes(int iIndex) const
{
	resolveDiagnosticSourceDetails();
	return (iIndex >= 0 && iIndex < (int)m_aSourceDiffFiles.size() ? m_aSourceDiffFiles[iIndex].iDiffBytes : -1);
}

char const* ModName::getSourceDiffFileFingerprint(int iIndex) const
{
	resolveDiagnosticSourceDetails();
	return (iIndex >= 0 && iIndex < (int)m_aSourceDiffFiles.size() ? m_aSourceDiffFiles[iIndex].szDiffFingerprint.c_str() : "-");
}

// <!-- custom: Aggregate diff success alone does not establish per-file coverage: a missing names command or rejected patch shape must remain explicitly unavailable in diagnostic summaries. (GPT-6.1-Sol) -->
bool ModName::isSourceDiffDetailsAvailable() const
{
	resolveDiagnosticSourceDetails();
	return m_bSourceDiffDetailsAvailable;
}

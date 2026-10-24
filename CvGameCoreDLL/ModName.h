#pragma once
#ifndef MOD_NAME_H
#define MOD_NAME_H

#include <vector> // <!-- custom: ModName owns the per-file diagnostic snapshot vector; its complete container definition is required for the member, rather than relying on the game PCH. (GPT-6.1-Sol) -->

/*	advc.106i: Small class for caching the mod's name and install location.
	(Could be expanded to also modify the name stored by the EXE; see the
	ModName class in the Taurus mod.) */
// <!-- custom: AdvCiv-SAS also uses this existing central object for branded display identity and lazily resolved source/version provenance, centralizing identity while keeping diagnostic-only work separately lazy. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->

class ModName
{
public:
	// <!-- custom: Initialize the AdvCiv-SAS source/version cache alongside the legacy ModName path cache. (ChatGPT-5.6-Sol) -->
	ModName();
	/*	The first param (and our m_sFullPath) is for the result of
		CvDLLUtilityIFaceBase::getExternalModName with bFullPath=true,
		the second (our m_sPathInRoot) is the result for bFullPath=false.
		I'm always seeing the same result, namely a path relative to the
		folder containing the Mods folder (I'll refer to that folder as "root"):
		"Mods\AdvCiv\"
		I don't know that the bFullPath parameter will never matter, so
		it seems safer to store both strings. Maybe the full path could
		be longer than what I've seen, maybe the non-full path could be
		just the actual mod name. We will, in any case, extract the actual
		mod name into m_sName. */
	void update(char const* szFullPath, char const* szPathInRoot);
	char const* getFullPath() const { return m_sFullPath.c_str(); }
	char const* getPathInRoot() const { return m_sPathInRoot.c_str(); }
	// <!-- custom: Keep getName() as the actual loaded mod-folder name detected by AdvCiv/BtS; it may differ from the branded display name after a user renames the installed folder. (ChatGPT-5.6-Sol) -->
	char const* getName() const { return m_sName.c_str(); }
	// <!-- custom: Return the branded/project name cached from the loaded mod INI's [CONFIG] Name during update(), before XML/Python startup consumers can ask for it.
	// Keep this separate from getName(), which is the actual installed folder identity. See KI#110.2. (ChatGPT-5.6-Sol) -->
	char const* getDisplayName() const;

	// <!-- custom: Resolve source/version metadata lazily from either an exported archive marker or the exact Git checkout rooted at this loaded mod folder.
	// A shallow Git checkout keeps the exact SHA but intentionally omits the misleading incomplete commit-count version. (ChatGPT-5.6-Sol) -->
	char const* getVersion() const;
	char const* getCommitHash() const;
	char const* getBranch() const;
	char const* getCommitDate() const;
	char const* getSourceMetadataType() const;
	// <!-- custom: Tri-state dirty status: -1 = unavailable/no inspectable Git worktree, 0 = verified clean tracked tree, 1 = verified tracked changes. (ChatGPT-5.6-Sol) -->
	int getSourceDirtyState() const;
	int getSourceDirtyFileCount() const;
	char const* getSourceDirtyFiles() const;
	// <!-- custom: Keep feature-branch ancestry separate from the per-commit practical count: a branch can be behind, ahead of, or diverged from the locally known default branch while still having its own exact rev-list count.
	// These values come from the local checkout without fetching, so unavailable/stale local refs stay explicit rather than being treated as current remote truth. (ChatGPT-5.6-Sol) -->
	char const* getSourceDefaultBranch() const;
	char const* getSourceDefaultCommitHash() const;
	char const* getSourceDefaultVersion() const;
	char const* getSourceDefaultRefSource() const;
	char const* getSourceMergeBaseCommitHash() const;
	char const* getSourceMergeBaseVersion() const;
	char const* getSourceBranchRelation() const;
	int getSourceCurrentOnlyCommitCount() const;
	int getSourceDefaultOnlyCommitCount() const;
	// <!-- custom: Preserve the older net HEAD-to-working-tree diff fingerprint while also separating staged and unstaged layers, which can otherwise mask or cancel one another. (ChatGPT-5.6-Sol) -->
	__int64 getSourceCodeRulesDiffBytes() const;
	char const* getSourceCodeRulesDiffFingerprint() const;
	__int64 getSourceStagedCodeRulesDiffBytes() const;
	char const* getSourceStagedCodeRulesDiffFingerprint() const;
	__int64 getSourceUnstagedCodeRulesDiffBytes() const;
	char const* getSourceUnstagedCodeRulesDiffFingerprint() const;
	// <!-- custom: Distinguish a complete empty per-file snapshot from a failed detail capture; aggregate patch hashes alone cannot make this claim. (GPT-6.1-Sol) -->
	bool isSourceDiffDetailsAvailable() const;
	int getSourceDiffFileCount() const;
	char const* getSourceDiffFileScope(int iIndex) const;
	char const* getSourceDiffFilePath(int iIndex) const;
	__int64 getSourceDiffFileBytes(int iIndex) const;
	char const* getSourceDiffFileFingerprint(int iIndex) const;

private:
	// <!-- custom: Internal source/version resolver helpers; resolution is lazy and reset only if update() changes the loaded mod path. (ChatGPT-5.6-Sol) -->
	void resetSourceDetails();
	void resolveSourceDetails() const;
	// <!-- custom: Diagnostic-only ancestry and patch capture must not be pulled in by ordinary version UI; callers gate diagnostic getters before requesting this separate first-use cache. (GPT-6.1-Sol) -->
	void resolveDiagnosticSourceDetails() const;
	// <!-- custom: Return false when per-file evidence is incomplete, independently of aggregate patch availability. (GPT-6.1-Sol) -->
	bool appendSourceDiffLayer(char const* szScope, CvString const& paths, CvString const& diff) const;
	CvString getAbsoluteModPath() const;
	// <!-- custom: Cache the Civ4 mod INI's [CONFIG] Name from the EXE-derived loaded folder path, avoiding any GlobalDefines dependency during Python/XML startup. See KI#110.2. (ChatGPT-5.6-Sol) -->
	void cacheDisplayName();

	CvString m_sFullPath;
	CvString m_sPathInRoot;
	CvString m_sName;
	// <!-- custom: Own the early INI-derived branding independently of installation identity; a reported configuration failure stores an explicit unavailable label. See KI#110.2. (GPT-6.1-Sol) -->
	CvString m_sDisplayName;
	// <!-- custom: Cache only authoritative source/version facts.
	// Derived presentation values such as a short SHA are intentionally computed by callers from these primary fields.
	// mutable allows const UI/log getters to populate the cache once without making source resolution part of ModName's logical identity mutation. (ChatGPT-5.6-Sol) -->
	struct SourceDiffFile
	{
		CvString szScope;
		CvString szPath;
		__int64 iDiffBytes;
		CvString szDiffFingerprint;
	};
	mutable bool m_bSourceDetailsResolved;
	// <!-- custom: Keep diagnostic work independently lazy, with explicit per-file completeness rather than treating a failed enumeration as a clean tree. (GPT-6.1-Sol) -->
	mutable bool m_bDiagnosticSourceDetailsResolved;
	mutable bool m_bSourceDiffDetailsAvailable;
	mutable int m_iSourceDirtyState;
	mutable int m_iSourceDirtyFileCount;
	mutable int m_iSourceCurrentOnlyCommitCount;
	mutable int m_iSourceDefaultOnlyCommitCount;
	mutable __int64 m_iSourceCodeRulesDiffBytes;
	mutable __int64 m_iSourceStagedCodeRulesDiffBytes;
	mutable __int64 m_iSourceUnstagedCodeRulesDiffBytes;
	mutable CvString m_sVersion;
	mutable CvString m_sCommitHash;
	mutable CvString m_sBranch;
	mutable CvString m_sCommitDate;
	mutable CvString m_sSourceMetadataType;
	mutable CvString m_sSourceDirtyFiles;
	mutable CvString m_sSourceCodeRulesDiffFingerprint;
	mutable CvString m_sSourceStagedCodeRulesDiffFingerprint;
	mutable CvString m_sSourceUnstagedCodeRulesDiffFingerprint;
	mutable CvString m_sSourceDefaultBranch;
	mutable CvString m_sSourceDefaultCommitHash;
	mutable CvString m_sSourceDefaultVersion;
	mutable CvString m_sSourceDefaultRefSource;
	mutable CvString m_sSourceMergeBaseCommitHash;
	mutable CvString m_sSourceMergeBaseVersion;
	mutable CvString m_sSourceBranchRelation;
	mutable std::vector<SourceDiffFile> m_aSourceDiffFiles;
};

#endif

#include "CvGameCoreDLL.h"
#include "ModName.h"

// advc.106i: New implementation file; see comment in header.

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
}

// <!-- custom: Central branded/project identity. The actual folder/path remains the EXE-derived data cached by update(). (ChatGPT-5.6-Sol) -->
char const* ModName::getDisplayName() const
{
	char const* szDisplayName = GC.getDefineSTRING("SAS_MOD_DISPLAY_NAME");
	if (szDisplayName != NULL && szDisplayName[0] != '\0')
		return szDisplayName;
	return getName();
}

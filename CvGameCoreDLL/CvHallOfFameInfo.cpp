#include "CvGameCoreDLL.h"
#include "CvHallOfFameInfo.h"
#include "CvReplayInfo.h"
#include "CvGame.h"
#include "SASGameRecordLog.h" // <!-- custom: Use the cached SGR enable gate before activating collective replay-rejection diagnostics. See KI#166.2. (GPT-6.1-Sol) -->

CvHallOfFameInfo::CvHallOfFameInfo()
{
	GC.getGame().setHallOfFame(this); // advc.106i
}

CvHallOfFameInfo::~CvHallOfFameInfo()
{	// <advc.106i>
	uninit();
}

void CvHallOfFameInfo::uninit()
{
	GC.getGame().setHallOfFame(NULL);
	CvGlobals::getInstance().setHoFScreenUp(false);
	for(size_t i = 0; i < m_aReplays.size(); i++)
		SAFE_DELETE(m_aReplays[i]);
	m_aReplays.clear();
} // </advc.106i>

// <!-- custom: Batch only one synchronous Hall-of-Fame scan; an automatic scope emits the summary and deactivates collection on normal return or C++ exception unwinding.
// With SGR disabled, no collection scope is opened and no records are allocated/formatted.
// Individual replay parsing still stops at its first unsafe field; the EXE can then try the next file, so one shared incompatibility can repeat at the same assertion site across many inputs.
// The scope is for whole-scan cleanup/output, not for continuing a rejected file. See KI#166.2. (GPT-6.1-Sol) -->
namespace
{
	class SASReplayRejectionScope
	{
	public:
		SASReplayRejectionScope() { beginSASGameRecordReplayRejectionBatch(); }
		~SASReplayRejectionScope() { endSASGameRecordReplayRejectionBatch(); }
	};
}

void CvHallOfFameInfo::loadReplays()
{
	CvGlobals::getInstance().setHoFScreenUp(true); // advc.106i
	// <!-- custom: Pre-gate batch setup rather than collecting diagnostics and discarding them later.
	// The EXE owns replay enumeration; bracket its call to summarize all reader rejections it produces.
	// Keep the scope object and loadReplays inside the same braces: a declaration used alone as the if-body would destroy the scope before scanning, ending collection too early.
	// The else branch scans normally without collection; only one loadReplays call executes. See KI#166.2. (GPT-6.1-Sol) -->
	if(isSASGameRecordLogEnabled())
	{
		SASReplayRejectionScope kRejectionScope;
		gDLL->loadReplays(m_aReplays);
	}
	else gDLL->loadReplays(m_aReplays);
}

int CvHallOfFameInfo::getNumGames() const
{
	return (int)m_aReplays.size();
}

CvReplayInfo* CvHallOfFameInfo::getReplayInfo(int i)
{
	return m_aReplays[i];
}

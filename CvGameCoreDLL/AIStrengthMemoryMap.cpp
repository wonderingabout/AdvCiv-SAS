#include "CvGameCoreDLL.h"
#include "AIStrengthMemoryMap.h"
#include "CvTeam.h"
#include "CvMap.h"

// advc.158: New implementation file; see comment in header.

void AIStrengthMemoryMap::init(PlotNumTypes eMapSize, TeamTypes eTeam)
{
	FAssert(eMapSize > 0);
	FAssert(eTeam != NO_TEAM);
	/*m_aiMap.clear();
	m_aiMap.resize(eMapSize, 0);*/
	m_map.clear();
	m_eTeam = eTeam;
}


void AIStrengthMemoryMap::reset()
{
	//m_aiMap.clear();
	m_map.clear();
}


// <!-- custom: removed old uiflag code (e.g. `if(uiFlag < 12)`), and now running any modern compliant uiflag such as of now according to chatgpt 5 anyways where uiflag == 17 is true such as uiflag >= 6, uiflag >= 15 or such, see code comment around as of now the top of CvCity::read. -->
// <!-- custom: note: here uiflag is not defined but passed as a parameter it seems, so handling it slightly differently, as advised by chatgpt 5, check if accurate -->
void AIStrengthMemoryMap::read(FDataStreamBase* pStream, uint /* <!-- custom: disable this and remove subsequent checks/usage of this parameter in the function i mean, as advised by chatgpt 5, check if accurate --> uiFlag */, TeamTypes eTeam)
{
	m_eTeam = eTeam;
	
	size_t iSize;
	pStream->Read(&iSize);
	if (iSize > 0)
	{
		/*FAssert(GC.getMap().numPlots() == (int)iSize);
		m_aiMap.resize(iSize, 0);
		pStream->Read(m_aiMap.size(), &m_aiMap[0]);*/
		for (size_t i = 0; i < iSize; i++)
		{
			PlotNumTypes ePlot;
			pStream->Read((int*)&ePlot);
			int iStrength;
			pStream->Read(&iStrength);
			m_map[ePlot] = iStrength;
		}
	}
}


void AIStrengthMemoryMap::write(FDataStreamBase* pStream) const
{
	/*FAssert(m_aiMap.size() == GC.getMap().numPlots());
	// the consequences of the assert failing are really bad.
	m_aiMap.resize(GC.getMap().numPlots());
	FAssert(!m_aiMap.empty());
	pStream->Write(m_aiMap.size(), &m_aiMap[0]);*/ // K-Mod
	// Replacing the above (still using a vector):
	/*pStream->Write(m_aiMap.size());
	if (!m_aiMap.empty())
		pStream->Write(m_aiMap.size(), &m_aiMap[0]);*/
	// Using PlotStrengthMap (and discarding zeros):
#ifndef ENABLE_REPRO_TEST
	size_t uiSize = 0;
	for (PlotStrengthMap::const_iterator it = m_map.begin(); it != m_map.end(); ++it)
	{
		if (it->second != 0)
			uiSize++;
	}
	pStream->Write(uiSize);
	for (PlotStrengthMap::const_iterator it = m_map.begin(); it != m_map.end(); ++it)
	{
		if (it->second == 0)
			continue;
		pStream->Write(it->first);
		pStream->Write(it->second);
	}
	// hash_map seems to have an unstable order, not reproducible after reloading.
#else
	std::vector<std::pair<PlotNumTypes,int> > aeiSorted;
	for (PlotStrengthMap::const_iterator it = m_map.begin(); it != m_map.end(); ++it)
	{
		if (it->second != 0)
			aeiSorted.push_back(std::make_pair(it->first, it->second));
	}
	std::sort(aeiSorted.begin(), aeiSorted.end());
	REPRO_TEST_BEGIN_WRITE(CvString::format("AIStrengthMemoryMap(%d)", m_eTeam).GetCString());
	pStream->Write(aeiSorted.size());
	for (size_t i = 0; i < aeiSorted.size(); i++)
	{
		pStream->Write(aeiSorted[i].first);
		pStream->Write(aeiSorted[i].second);
	}
	REPRO_TEST_END_WRITE();
#endif
}


int AIStrengthMemoryMap::get(CvPlot const& kPlot) const
{
	return get(kPlot.plotNum());
}


void AIStrengthMemoryMap::set(CvPlot const& kPlot, int iNewValue)
{
	PlotNumTypes ePlot = kPlot.plotNum();
	/*FAssertBounds(0, m_aiMap.size(), ePlot);
	m_aiMap[ePlot] = iNewValue;*/
	m_map[ePlot] = iNewValue;
}


void AIStrengthMemoryMap::decay()
{
	PROFILE_FUNC();
	/*if (m_aiMap.size() != GC.getMap().numPlots())
		return;*/
	CvTeam const& kTeam = CvTeam::getTeam(m_eTeam);
	// K-Mod: reduce by 4% (arbitrary number), rounding down.
	int const iDecayPercent = 4;
	/*for (int i = 0; i < GC.getMap().numPlots(); i++)
	{
		if (m_aiMap[i] == 0)
			continue;
		FAssert(m_aiMap[i] > 0);
		CvPlot const& kPlot = GC.getMap().getPlotByIndex(i);*/
	PlotStrengthMap::iterator it = m_map.begin();
	while (it != m_map.end())
	{
		CvPlot const& kPlot = GC.getMap().getPlotByIndex(it->first);
		if (kPlot.isVisible(m_eTeam) &&
			!kPlot.isVisibleEnemyUnit(kTeam.getLeaderID()))
		{
			it = m_map.erase(it);
			//m_aiMap[i] = 0;
		}
		//else m_aiMap[i] = ((100 - iDecayPercent) * m_aiMap[i]) / 100;
		else
		{
			it->second = ((100 - iDecayPercent) * it->second) / 100;
			++it;
		}
	}
}

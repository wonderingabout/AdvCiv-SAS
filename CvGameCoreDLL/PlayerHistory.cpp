#include "CvGameCoreDLL.h"
#include "PlayerHistory.h"
#include "CvPlayer.h"

// advc.004s: New implementation file; see comment in header.

void PlayerHistory::grow(int iSize)
{
	FAssert(iSize >= 0);
	while (iSize >= size())
		m_aiValues.push_back(-1);
}


void PlayerHistory::set(int iTurn, int iValue)
{
	grow(iTurn);
	if (m_iMovingAvgSamples <= 0)
	{
		m_aiValues[iTurn] = iValue;
		return;
	}
	int iOldSamples = std::min(m_iMovingAvgSamples - 1, iTurn - 1);
	int iSamples = iOldSamples;
	int iSum = 0;
	// Discard new sample (iValue) if in anarchy
	if (!GET_PLAYER(m_eOwner).isAnarchy() || iTurn == 0)
	{
		iSum += iValue;
		iSamples++;
	}
	for (int i = iTurn - 1; i >= iTurn - iOldSamples; i--)
		iSum += std::max(m_aiValues[i], 0);
	m_aiValues[iTurn] = intdiv::round(iSum, std::max(1, iSamples));
}


// <!-- custom: AdvCiv's bLegacy branch converted sparse turn/value pairs from before advc.004s.
// CvPlayer has requested the vector layout since KI#46, so read the stored samples directly. See KI#46.2. (GPT-6.2-Sol) -->
void PlayerHistory::read(FDataStreamBase* pStream, PlayerTypes eOwner)
{
	m_eOwner = eOwner;
	FAssert(size() == 0);
	int iSize;
	pStream->Read(&iSize);
	if (iSize > 0)
	{
		m_aiValues.resize(iSize);
		pStream->Read(iSize, &m_aiValues[0]);
	}
}


void PlayerHistory::write(FDataStreamBase* pStream)
{
	int iSize = size();
	pStream->Write(iSize);
	if (iSize > 0)
		pStream->Write(iSize, &m_aiValues[0]);
}

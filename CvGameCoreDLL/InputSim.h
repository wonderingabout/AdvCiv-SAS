#pragma once

#ifndef INPUT_SIM_H
#define INPUT_SIM_H

/*	ccgs: Wrappers for win functions that emulate keyboard and mouse inputs
	(I guess "emulate" really is the more appropriate term here - although
	"simulate" seems to be more commonly used and is easier to abbreviate.) */

namespace input_sim
{
	void keySequence(std::vector<byte> aucVK, bool bContinueSeq = false);
	void keyPressed(byte ucVK);
	void mouseClicked();
}

#endif

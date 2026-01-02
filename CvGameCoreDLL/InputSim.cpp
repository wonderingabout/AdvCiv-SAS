#include "CvGameCoreDLL.h"
#include "InputSim.h"

// AdvCiv-SAS - CuCuGS

void input_sim::keySequence(std::vector<byte> aucVK, bool bContinueSeq)
{
	for (size_t i = 0; i < aucVK.size(); i++)
	{
		if (i != 0 || bContinueSeq)
			Sleep(10);
		keyPressed(aucVK[i]);
	}
}


void input_sim::keyPressed(byte ucVK)
{
	for (int i = 0; i < 2; i++)
	{
		INPUT inputs[1];
		ZeroMemory(inputs, sizeof(inputs));
		inputs[0].type = INPUT_KEYBOARD;
		inputs[0].ki.wVk = ucVK;
		if (i == 1)
		{
			/*	Sending the key-down and key-up event in a single call
				(as an example at docs.microsoft.com suggests) will send
				them in the proper order, but with equal timestamps.
				Which may or may not be a problem(?). */
			Sleep(10);
			/*	Might also work, but timestamps aren't really supposed to be
				postdated, from what I've read. */
			//inputs[0].ki.time = 10;
			inputs[0].ki.dwFlags = KEYEVENTF_KEYUP;
		}
		uint uSent = SendInput(ARRAYSIZE(inputs), inputs, sizeof(inputs[0]));
		FAssert(uSent == ARRAYSIZE(inputs));
		(void)uSent; // Suppress unused variable warning in Release builds
	}
	// Could also use
	//keybd_event(ucVK, 0, 0 /* key down */, 0);
	//Sleep(10);
	//keybd_event(ucVK, 0, KEYEVENTF_KEYUP, 0);
	// --which doesn't require _WIN32_WINNT to be defined.
}


void input_sim::mouseClicked()
{
	for (int i = 0; i < 2; i++)
	{
		INPUT inputs[1];
		ZeroMemory(inputs, sizeof(inputs));
		inputs[0].type = INPUT_MOUSE;
		if (i == 0)
			inputs[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
		else
		{
			Sleep(5);
			inputs[0].mi.dwFlags = MOUSEEVENTF_LEFTUP;
		}
		uint uSent = SendInput(ARRAYSIZE(inputs), inputs, sizeof(inputs[0]));
		FAssert(uSent == ARRAYSIZE(inputs));
		(void)uSent; // Suppress unused variable warning in Release builds
	}
}

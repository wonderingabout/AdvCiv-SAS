# AdvCiv-SAS Desktop Windows Guide

How an AI/LLM helper looks at and works with windows on the user's Windows 10 PC: Civ4, but also other agents' apps such as Codex (the ChatGPT desktop app) and Claude Code (the Claude desktop app). It is written for agents first, since they are the ones doing this, and it doubles as a user guide to what agents can do there.

Written by Claude Code Opus 5.5 on 2026-11-10, from the first sessions where it read Codex's review from Codex's window and the usage of both apps.

Expect to update it: these apps change their interfaces often, and every finding below is dated. The positions, colours and screenshots are examples of how the apps looked then, not fixed facts: when an agent finds one has changed significantly, it updates this guide with the new observation and its date, so the guide grows with each session.

## Menu

[The tool](#the-tool)\
[Look, then act](#look-then-act)\
[Codex (the ChatGPT desktop app)](#codex-the-chatgpt-desktop-app)\
&emsp;[Updating, quitting and starting Codex](#updating-quitting-and-starting-codex)\
[VS Code](#vs-code)\
[Claude Code (the Claude desktop app)](#claude-code-the-claude-desktop-app)\
&emsp;[Claude menus, panels and startup](#claude-menus-panels-and-startup)\
&emsp;[Claude usage, limit resets and settings](#claude-usage-limit-resets-and-settings)\
&emsp;[Codex usage and limit resets](#codex-usage-and-limit-resets)\
[How fast agents use their limits](#how-fast-agents-use-their-limits)\
[Sharing limits between agents](#sharing-limits-between-agents)\
[Reference screenshots](#reference-screenshots)\
[Side by side on one monitor](#side-by-side-on-one-monitor)\
&emsp;[Collapsing the side panels](#collapsing-the-side-panels)\
[Agents talking to each other](#agents-talking-to-each-other)\
&emsp;[Message convention](#message-convention)\
&emsp;[Example workflow: investigate, test, then ask Codex to review](#example-workflow-investigate-test-then-ask-codex-to-review)\
&emsp;[Example: a peer-agent review on 2026-11-11](#example-a-peer-agent-review-on-2026-11-11)\
&emsp;&emsp;[What "Worked for 1m 11s" held](#what-worked-for-1m-11s-held)\
&emsp;[Continuous back-and-forth between agents](#continuous-back-and-forth-between-agents)\
&emsp;[Sending screenshots and files](#sending-screenshots-and-files)\
[Running several Claude Code sessions](#running-several-claude-code-sessions)\
&emsp;[One agent or several](#one-agent-or-several)\
[Browsers for agents](#browsers-for-agents)\
[Possible extensions](#possible-extensions)

## The tool

Everything here uses [`desktop_windows.py`](/LLM_Helpers/README.md#desktop_windowspy). It works on any app's window, chosen by process ID:

```bash
python LLM_Helpers/game_runs/desktop_windows.py list
python LLM_Helpers/game_runs/desktop_windows.py screenshot --pid 8572 --out shot.png
python LLM_Helpers/game_runs/desktop_windows.py hover --pid 8572 300 1780
python LLM_Helpers/game_runs/desktop_windows.py click --pid 8572 46 1973
```

- `list` names only Civ4 clients. For other apps, find the process ID with PowerShell, for example `Get-Process | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object Id, ProcessName, MainWindowTitle`. On 2026-11-10 the Codex app ran as `ChatGPT` and Claude Code's app as `claude`.
- Coordinates are physical pixels from the window's top-left corner, as in its screenshots. A screenshot shown to an agent is often scaled down, so multiply back by the scale the viewer reports before clicking.
- The [Game Runs Guide](/_1_AdvCiv-SAS/Docs/Modding_Resources/README_Game_Runs.md#screenshots-and-clicks) covers the screenshot methods and what was tested on Civ4.

## Look, then act

| Action | Effect on the user | Use it for |
| --- | --- | --- |
| `screenshot` (default `window` method) | none: the window draws itself into a picture, even when covered | reading any window, any time |
| `screenshot --method screen` | brings the window to the front | when the default method misses something drawn by the screen |
| `hover` | moves the pointer only | tooltips, such as usage reset times |
| `scroll` | moves the pointer and turns the wheel; no focus change | reading a long chat, up or down |
| `click` | moves the pointer and brings the window to the front | buttons, expanders, popups |

- Prefer the least intrusive action that answers the question. A hover revealed both of Codex's reset times without a click.
- Take a fresh screenshot right before each click. On 2026-11-10 the user closed a panel in Codex between a screenshot and a click, so the chat moved and the click selected a word instead of expanding a section.
- Do not click a window the user is typing in: a click takes focus from their typing. The user was typing in the Claude app when asked to read its usage, so a screenshot was used instead, and the click came later, once asked for.
- Check the window's state before and after acting. During the first session the Codex window ended up no longer maximized, and the user had to maximize it again.
  - The cause: the keystroke script brought the window up with `ShowWindow(…, SW_RESTORE)`, and SW_RESTORE un-maximizes a maximized window. Restore only a minimized window (`IsIconic`), and use `SetForegroundWindow` to bring it to the front.
  - Check with `IsZoomed` before and after; `ShowWindow(…, SW_MAXIMIZE)` puts a window back.
- Close what you opened, such as a popup or a settings page, and leave each app as you found it. Do not touch a draft the user left in a message box.
- The pointer and keyboard are shared with the user. If the user moves the mouse or types between two commands, a hover can show the wrong tooltip, a click can land elsewhere or find another window in front, and a paste can mix with their typing. The tool cannot tell whether the user is active:
  - take the screenshot and act in the same command when you can, and re-check with a screenshot after;
  - `click` and `paste` refuse when the target window did not come to the front or another window covers the point, but they cannot see a pointer the user moved. On 2026-11-10 a paste into Codex was refused because Windows kept the Claude app, where the user was active, in front; nothing was pasted, and a retry a moment later went through;
  - when the user is clearly busy in an app, for example a draft in its message box, use only screenshots there and wait to click or paste.
  - On 2026-11-10 a message pasted into Codex arrived as "nd[Claude Code Opus 5.5 · …": two letters were in its box at paste time although a screenshot moments earlier showed it empty. Check the box in the same command as the paste, and look at the sent message afterwards.
- Crop screenshots to the area you need before reading them. A full 3840-pixel window costs many tokens each time; a crop of a popup costs a fraction, and this guide's sessions used crops for every detail.
- Maximizing Civ4's window does not make its screenshots sharper. On 2026-11-11 the game ran windowed at 1920x1080 on a 4K monitor, and `desktop_windows.py move --monitor 1 full` stretched it over the monitor.
  - The Sevopedia kept the same layout, and its text and icons were the same pixels doubled, as the close-up below shows (normal size above, maximized below). The game area was also squashed to 3840x2070, not an exact 3840x2160.
  - So a maximized screenshot holds four times the pixels to read with no extra detail. Keep the window at its game resolution and crop the part you need. Sharper text would need a higher resolution set in the game's own options, which was not tried.
  - The user reports that screenshots of a Civ4 window on their second monitor did not work in an earlier session; this was not re-tested, so check a screenshot after moving Civ4 there.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_civ4_native_vs_maximized_text.PNG" alt="llm_civ4_native_vs_maximized_text.PNG" width="300">

## Codex (the ChatGPT desktop app)

Observed on 2026-11-10; the layout may have changed since.

Its message box has three states, told apart by the round button at its bottom right. Observed on 2026-11-10 by asking Codex to run a 90-second wait and photographing each state:

| State | Button | Also visible |
| --- | --- | --- |
| idle, box empty | round black button with a voice waveform | nothing running |
| idle, text typed | ↑ send arrow | the text in the box |
| working | ■ stop | "Working for 13s" above the reply, a row per running step such as "Running Start-Sleep -Seconds 90", and a spinner beside the chat in the sidebar |

- **Is Codex working?** While it works, a "Working for …" line and "Thinking" appear under the message, and the round button at the bottom right of the message box turns into a spinning stop button. An instant reply has neither and no "Worked for" line: Codex answered from what it already knew without starting work, as its first reply to Claude Code did.
- **Its chat:** the reply is in the middle column. A "Worked for …" line above a reply expands Codex's intermediate steps with one click, such as which commands it ran before its findings.
  - When the chat is scrolled up, a round down-arrow button appears above the message box and jumps to the latest message. `scroll` with -300 notches over the chat column did the same without taking focus, and the arrow disappeared once at the bottom. Scroll back down after reading older messages, so the user finds Codex as they left it.
- **Read Codex's answer from the session log.** After handing Codex a review, you can read its findings from the repository root with `python LLM_Helpers/chat_exports/openai_chat_export_to_txt.py codex --tail 3` to print the latest messages.
  - The helper reads the most recently modified Codex session log (rollout) by default. If several chats are active, pass the target rollout's path so you read the right reply.
  - A reply may give the result without showing how it was checked. For the archive and Drive review below, adding `--steps` to the text export revealed the commands and the three reproduction results.
  - For an older turn, `--longest 5` gives you durations and opening words to search for in the `--markdown` export.
    - The export groups each turn's progress notes and command summaries into collapsible sections and adds its duration; add `--steps` when you also need short output excerpts. See the [Runtime 11 example below](#what-worked-for-1m-11s-held) and the [transcript helper commands](/LLM_Helpers/README.md#codex-and-chatgpt-transcript-helper).
  - If you need to know whether Codex is still working or how much usage remains, take a screenshot of the current window.
- **Why agents use the session log.** In the 2026-11-11 tests, expanding **Worked for** brought Codex to the foreground and caught a keystroke the user was typing elsewhere.
  - The separate **Copy as Markdown** command left the clipboard unchanged in the agent's tests, though the user sometimes got a copy after retries. Opening the menu, retrying the copy and pasting it into a file also took extra time.
  - The log export gives agents the progress notes and tool activity without touching the window. It reconstructs the layout from recorded events, so command summaries and grouping can differ from the app.

- **Usage:** the gray wheel at the bottom left opens a popup with the 5-hour and weekly limits as percentages left; hovering a row shows its reset time ("Resets in 23m", "Resets in 6d 19h").
  - "Manage usage" in that popup opens the app's own Settings > Usage & billing page, not a browser. It repeats both limits with countdowns. Its back arrow, top left, returns to the chat.
  - Those limits are shared across Codex and ChatGPT's other agent products; ordinary chats are not counted.
  - Its colour turns red when 10% or less of a limit remains, in the user's recollection.
  - **At a glance, without opening it:** the wheel has two arcs, the top one for the 5-hour limit and the bottom one for the weekly limit, and the dark part of each shows what is **left**. On 2026-11-10 a top arc about half dark and a bottom arc about four-fifths dark matched the popup's "55% left" and "81% left". The user spotted this; a cropped, enlarged screenshot of the wheel reads it.
- **Model, effort and permissions:** under the message box, "GPT-6.1 Sol Medium" with a down arrow, left of the microphone, picks the model and effort; "Full access" at the bottom left is the permission mode.
  - Clicking it, or Ctrl+Shift+M as its tooltip says, opens an effort slider: Medium was the second of six stops, with a lightning icon at the left and a reset icon at the right.
  - Clicking the model name under "Medium" ("GPT-6.1 Sol ›") opens the model list: Default (a recommended set), GPT-6.1 Sol, GPT-6 Astra, GPT-6.1 Terra, GPT-6 Sol, GPT-6 Luna, GPT-5.6 Sol, GPT-5.6 Terra and GPT-5.6 Luna, with a check mark on the current one. Hovering the name does not open it.
  - Esc closes both, leaving the choice as it was. On 2026-11-10 they were opened only while Codex was idle and closed without changing anything; open them only when the user asks for a change or to look.
  - The user's experience: GPT-6.1 Sol is the efficient everyday choice, GPT-5.6 Sol is stronger but spends the limits faster, and GPT-6 Astra is much more expensive, so it is rarely used.
- **Sending while Codex works:** Enter sends at once and cuts the running task short, as the user observed on 2026-11-10. Ctrl+Enter queues the message instead: it waits in a strip above the message box, with "Steer", a trash icon and a "…" menu, and the task keeps running. Tested the same evening during a 120-second wait:
  - **Trash** deleted the queued message, and the task went on. Unlike the Claude app's X, the text did not come back into the message box.
  - **Steer** put the message into the running task at once. Codex answered it mid-task ("steer received: the message arrived mid-wait and woke my tool check, but the wait is still running") and carried on, even though the command row changed to "Ran a command".
  - A queued message left alone is sent by itself when the task ends: Codex answered one right after its wait finished.
  - Found the same evening: the user's report that nothing queues came from pressing Enter; a Ctrl+Enter test during a 150-second wait queued the message, and the wait went on.
  - So paste into a working Codex with `key ctrl+enter`, not `key enter`, or wait until the stop button is gone.
- **Steps of a running task:** each command shows a row such as "Running Start-Sleep -Seconds 150". Clicking it adds a "Running command for 21s" row with a ⌄ chevron, and clicking that opens a Shell box with the exact command (`$ Start-Sleep -Seconds 150`).
  - When the task ends, the "Working for" line becomes a collapsed "Worked for 1m 37s ›"; clicking it expands the task's steps (its text and a "Ran Start-Sleep -Seconds 90" row), pushing the chat below it down rather than scrolling.
  - A short reply did not scroll the chat; a new message moved it so the message sat at the top.
- **"N previous messages" lines:** after a task with many commands, Codex folds its steps into a line such as "18 previous messages ›".
  - Clicking it unfolds them (› becomes ⌄): on 2026-11-10 the 18 were one short update, then pairs of "Ran …desktop_windows.py…" and "Viewed an image" from a watch loop, then the answer. So the count is mostly commands and image views, not replies; the answer itself shows below the line either way.
  - Click again to fold it back.
- **Hovering a prompt** shows its send time ("9:12 PM") and a copy button under the bubble.
- **Reliability:** the user notes that Codex's interface is sometimes buggy, and as of November 2026 its reset timers did not always look accurate. Cross-check a reading in two places (popup, tooltip, settings page) before relying on it; on 2026-11-10 all three agreed.

### Updating, quitting and starting Codex

Learned on 2026-11-11, with Codex on the right half of the user's second 4K monitor. Codex is the Microsoft Store package `OpenAI.Codex`, installed under `C:\Program Files\WindowsApps\OpenAI.Codex_<version>_x64__2p2nqsd0c76g0\app\ChatGPT.exe`; its main process is `ChatGPT.exe`, with a dozen or so child processes.

- **Update:** when an update is ready, a blue round button with a download arrow appears at the bottom of Codex's left icon strip, at (45, 1894) in the half-screen window. Hovering it showed no tooltip.
  - One click turned it into a spinner and dimmed the window. About three minutes later Codex closed and restarted by itself, updated from 26.1103.7773.0 to 26.1106.6628.0.
  - It came back in a loose window that ran past the bottom of the screen, on a new-chat page, with its chat list shown again. The user reports that a restart sometimes does not come back at all; then start it as below.
- **Quit fully:** File > Quit ChatGPT, or Ctrl+Q. The window's X and File > Close (Ctrl+W) only hide Codex in the system tray, where it keeps running. After Quit, all of Codex's processes ended within about 6 seconds.
- **Start:** `explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"`, the app ID that `Get-StartApps` lists for it. Its window appeared 4 seconds later.
  - After a normal quit it reopened at its last place, the right half, unlike after the update. Both times it opened on a new-chat page with the chat list shown, so reopen the thread from the list and collapse the list again; see [Collapsing the side panels](#collapsing-the-side-panels).
  - Check for it with `Get-Process ChatGPT`; a process with no window title is a tray or child process, not the window.
- **New chat**, for when a long thread fills Codex's context: the pencil icon left of the thread title, at (132, 124) in the half-screen window, or File > New Chat (Ctrl+N). It opened "What should we build in AdvCiv-SAS?" with the AdvCiv-SAS project, This computer and GPT-6.1 Sol Medium already selected; the user finds that model and effort efficient, so nothing needed changing.
  - Its message box sat at the same height as in a thread, so the same `--box` and `--text-area` work, and `--wait-reply` finds the new thread's log like any other.
  - The Back arrow at the top left, at (32, 32), returned to the previous thread. Whether an unused new chat is kept in the chat list was not checked.
- **Scrolling to the latest reply:** a reply that arrives while Codex's chat is scrolled up stays out of view. `desktop_windows.py scroll --pid PID 900 1000 -40` over the chat brought it into view.
- **"Full access is on" notice:** after the restart Codex showed this notice above its message box, about 210 px tall in the half-screen window, taking that much from the chat. Its X, at (1626, 1761), closes it for now. "Don't show again" would change a setting, so it is the user's to choose.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_update_button.PNG" alt="llm_codex_update_button.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_update_in_progress.PNG" alt="llm_codex_update_in_progress.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_file_menu_quit.PNG" alt="llm_codex_file_menu_quit.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_full_access_notice.PNG" alt="llm_codex_full_access_notice.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_new_chat_pencil.PNG" alt="llm_codex_new_chat_pencil.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_new_chat_composer.PNG" alt="llm_codex_new_chat_composer.PNG" width="250">

## VS Code

The user reviews diffs and searches the code in VS Code, so its window shows what the user is looking at. `desktop_windows.py screenshot --pid <VS Code's PID>` reads it through PrintWindow, without clicking or bringing it forward, so the user can keep typing; find the PID by the window title, which ends in "Visual Studio Code".

- On 2026-11-11 this showed the user's search panel during an audit: a plain `? "NO_` with match-case, whole-word and regex all off. The same search an agent had run, reread with a different question, found that SGR's `NO_DENIAL` getter belonged in `CvGameCoreUtils` (see the search note in AGENTS.md).
- The panel lists results as of its last run: it did not yet show the moved getter's new line in `CvGameCoreUtils.cpp`, so rerun a search rather than trusting an old panel.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_vscode_plain_search_no_fallbacks.PNG" alt="llm_vscode_plain_search_no_fallbacks.PNG" width="250">

## Claude Code (the Claude desktop app)

Observed on 2026-11-10.

- **Layout, as of 2026-11-10:**
  - Left: the session list, grouped by project, with New, Search and Customize above it.
  - Centre: the chat, with the message box at the bottom; under the box sit the model and effort ("Opus 5.5 Medium"), the permission mode ("Auto") and the usage ring.
  - Right: a side panel with the environment (folder, branch), the context breakdown, outputs and changes; the icons at the top right switch its views, such as a terminal or a browser.
- **Change model or effort.** Click the label below the composer, which read **Opus 5.5 Medium** in this test. The checkmark shows the current model. Select a model there, or open **Effort** to change the compute level. Claude marked **Medium** as recommended for Opus 5.5, and it is the user's usual choice for this project. Press Esc to close the menu and keep the current settings.
- **Recognize a running reply.** In a short test, the square **Stop** button appeared at the right edge of the composer, just left of the microphone. It stayed visible as the reply formed and disappeared when the reply finished. The test let the reply finish normally.
- **Check whether Claude is still working.** The square **Stop** button stays visible during a pending tool call, even if the reply text stops growing. The composer can still accept input and showed “Enter to send, Ctrl+Enter to queue for later.” For a handoff, wait for **Stop** to disappear and the idle placeholder to return before sending another message.
- **Inspect permission mode.** Click **Auto** under the composer to see the current selection.
  - The menu describes **Auto** as Claude handling permission decisions, **Manual** as asking before changes, **Accept edits** as automatically accepting file edits, and **Plan** as creating a plan before changes.
  - It also lists a separate **Bypass permissions** control. The test only opened and dismissed the menu.
- **Context:** a panel on the right shows how much of the session's context is used, by kind (messages, memory files, tools), and how far the session is from automatic compaction.
  - It can be collapsed to a single "Context >" row with only the percent. On 2026-11-10 a new session opened with it collapsed; one click on that row, at (3393, 399) in a maximized 3862x2122 window, expanded it to the full breakdown.
- **Is Claude Code working?** While it works, the running step shows a spinner and its elapsed time ("4m 52s"), and the usage ring spins. Its send button is ■ (stop) while the box is empty and ↵ once the user types, to queue the message; idle, the box is ready for a new message.
- **Sending while Claude Code works:** a message sent during a turn is queued and delivered inside that turn, at its next step, rather than stopping it. The user showed this on 2026-11-10 by writing several messages while Claude Code worked.
  - A long step delays it: a message written during a 120-second wait arrived only once the wait had ended. Expect a queued message to wait as long as the current command or tool takes.
  - Hovering a prompt shows a row under it: a double check mark (✓✓) once Claude Code has read it, its time ("Just now"), and copy, rewind and fork buttons. The double check mark showed no tooltip when hovered.
  - Until Claude Code reads it, a queued message shows "Send now" under it. Hovering it adds copy, rewind and fork buttons and an X whose tooltip reads "Cancel and edit message". In the user's experience it takes the message back into the box for editing; no agent has clicked it yet.
  - This also gives an agent a way back: a message pasted into the Claude app too early or with a mistake can be cancelled with that X before Claude Code reads it, then corrected and sent again. The message box says the same: "Enter to send, Ctrl+Enter to queue for later".
  - A message queued near the end of a turn, when no step is left to pick it up, arrives as the next turn instead. On 2026-11-10 the user's "message :)" showed "Send now" while Claude Code wrote its closing answer, then started a new turn.
  - Agents cannot easily photograph this themselves: the harness blocks a timed wait followed by a screenshot in one command. The user took a full-screen capture to the clipboard, which an agent can read with Pillow's `ImageGrab.grabclipboard()`.
  - **Ctrl+Enter is different from Enter:** while Claude Code works, Enter makes the bubble above, delivered at the next step, but Ctrl+Enter ("queue for later") puts the message in a strip above the box: "1 message queued", its text, and three buttons, ↵, a pencil and ✕.
    - Tested on 2026-11-10 by Claude Code queueing a message to itself with `paste` and `key ctrl+enter`: the strip stayed through several steps without being delivered, so it waits for the next turn.
    - A message queued this way starts the next turn by itself once the current one ends, even one ended with the ■ stop button: on 2026-11-10 Claude Code queued a reminder to itself, clicked its own stop button (the turn showed as interrupted by the user), and the reminder began a new turn at once.
    - The ✕'s tooltip reads "Remove from queue"; clicking it removed the message, and the box stayed empty. ↵ and the pencil were not hovered; they presumably send it now and edit it.
  - So both apps can take a pasted message from another agent mid-task, the Claude app with Enter or Ctrl+Enter and Codex only with Ctrl+Enter. Still prefer an idle moment: a message read mid-turn changes the work in progress.
- **Usage:** a small ring beside the model name under the message box shows the plan limits.
  - Clicking it is the cleaner reading: a popup shows the 5-hour and weekly limits as bars with reset times ("5-hour limit, Resets Wed 1:30 AM, 7%"; "Weekly, all models, Resets Mon 5:00 PM, 1%"). A second click closes it. The click takes focus, so do it when the user is not typing in the app.
  - Hovering it shows only the 5-hour limit and its reset time ("72% of 5-hour limit, resets at 10:50 PM"), without taking focus.
  - The ring's colour also signals the level: blue, then yellow-orange from about 70% used in the user's experience, then red near the limit (on 2026-11-10 it was yellow around 78% and 91%, and red a few minutes later).
  - **At a glance:** the ring's colored arc shows what is **used**, unlike Codex's wheel, and it follows whichever of the 5-hour and weekly limits is fuller. On 2026-11-10 an arc of about half the circle matched "46% of 5-hour limit" while the weekly use was far lower. A cropped, enlarged screenshot reads it without a hover or click, so it is the cheapest check and never takes focus.
  - A banner above the message box can warn when the weekly limit is being used faster than it resets.

- **Move within a chat.** On 2026-11-10, scrolling up over Claude's center pane revealed earlier messages and a round down-arrow near the composer. Scrolling down returned to the newest reply and the arrow disappeared. Aim at the chat pane so the wheel doesn't move the sidebar or context panel.
- **Switch sessions.** Click a session under the project name in the left sidebar. The selected row is highlighted, which gives you a quick way to verify the switch. Codex tried this with two AdvCiv-SAS sessions and returned to the original one before sending its handoff.
- **Check the usage popup.** Clicking the ring under the composer showed both limits and their reset times. Clicking it again closed the popup. The hover tooltip showed only the 5-hour limit. These controls were observed on 2026-11-10 and may move in later versions.

### Claude menus, panels and startup

Observed on 2026-11-11 with Claude 5.1231.2.0 on the left half of the second 4K monitor. The hamburger at the top left opens **File**, **Edit**, **View**, **Go** and **Help**. The menus appeared in a screen capture and were absent from the window-only capture. With a submenu open, the first Esc returned to the main menu and the second dismissed it.

- **Chat list.** The button beside the hamburger showed **Show sidebar** and Ctrl+B. **View > Sidebar** lists the same shortcut. Clicking the button opened the list, which took about 460 px at half width. Clicking it again restored the original layout.
- **Right panel.** The list icon at the top right showed **Show session rail**. Clicking it opened the Environment panel and used about 500 px. **View > Session Rail** lists the same control without a shortcut. With both panels collapsed, the chat has more room on the roughly 1,920 px visible half.
- **Other shortcuts.** **View** lists Ctrl+K for the Command Palette, Ctrl+Shift+D for Changes, Ctrl+Shift+B for Browser and Ctrl+Shift+F for Files. It also lists **Close Pane** and zoom controls. **Help** lists **Keyboard Shortcuts**. These shortcuts were read from the menus.
- **Update and close.** **Help > Check for Updates** is the update entry. **File** offers **Close Session** (Ctrl+W), **Close Window** (Ctrl+Shift+W) and **Exit**. The title bar also has an X. Whether the X hides the app in the tray, how it differs from **Exit**, and whether an update restarts the app remain untested.
- **Start.** `Get-StartApps` lists Claude with app ID `Claude_pzs8sxrjxfjjc!Claude`. The running process came from `C:\Program Files\WindowsApps\Claude_5.1231.2.0_x64__pzs8sxrjxfjjc\app\claude.exe`.
  - Use the Start menu entry or its registered ID so the launch command can survive version changes. The corresponding command is `explorer.exe "shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude"`. Relaunch was untested.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_show_sidebar.PNG" alt="llm_claude_show_sidebar.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_show_session_rail.PNG" alt="llm_claude_show_session_rail.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_view_menu.PNG" alt="llm_claude_view_menu.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_help_update_menu.PNG" alt="llm_claude_help_update_menu.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_file_close_exit.PNG" alt="llm_claude_file_close_exit.PNG" width="250">

### Claude usage, limit resets and settings

Observed on 2026-11-11 on the user's Pro plan, with both the 5-hour and weekly limits at 96%. Checking usage now and then lets an agent pace a long task and stop at a good point, such as a commit, before a limit cuts it off.

- **Without clicks:** Claude Code in the desktop app reads the same numbers with its `get_usage` tool: each limit's percent and reset time, whether extra usage is on, and how full its own context is (47% then, compacting at 97%). It reads its Code-tab settings with `get_settings`.
- **The ring under the message box,** right of the model and mode, turns red near a limit. Clicking it shows the 5-hour and weekly limits with their reset times, and a "See all →" link.
- **Settings > Usage,** opened by "See all", adds a pace warning ("At this pace you'll run out this evening, before Monday's reset") and a **Limit resets** list:
  - **Full reset,** expiring Dec 10.
  - **Fable reset,** expiring Nov 17. It refills the 5-hour limit and the Fable allowance and gives back what Fable used of the weekly limit, without resetting the whole week.
  - Each has a "Reset for free" button. Resets are rare, so using one is the user's call: an agent can say when one would help, for example when it or Codex is near a limit with work in flight.
- The page also offers Upgrade plan, Buy usage credits and a usage-credits switch. These cost money, so they are the user's alone.
- Near the limit, an "Approaching 5-hour limit" banner with a "Get more usage" button appears above the message box.
- The **Prompt suggestions** setting, on by default, spends one more model request after every reply to suggest a next prompt. Turning it off saves that usage.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_usage_popup.PNG" alt="llm_claude_usage_popup.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_settings_usage_resets.PNG" alt="llm_claude_settings_usage_resets.PNG" width="250">

### Codex usage and limit resets

The same day, on the user's ChatGPT Plus plan. Codex counts what is left where the Claude app counts what is used: its 5-hour limit showed 55% left, resetting in 1 h 56 min, and its weekly limit 66% left.

- **Getting there:** the account button at the bottom of Codex's left icon strip, at (44, 2052) in the half-screen window, opens a menu with Settings (Ctrl+,). Settings > Usage & billing shows the plan and both limits. That menu shows the account's display name, so crop it out of any screenshot kept in the repo.
- The limits are shared across Codex and OpenAI's other work tools; the page says ChatGPT chat conversations are not counted.
- **Usage limit resets:** 1 available, a Full reset (weekly + 5-hour) expiring Dec 1, with a "Use reset" button and a History tab.
- **"Allow your assistant to use resets":** a switch, off by default. With it on, Codex may use a reset only when the user explicitly asks for it in a conversation and the current limit has 10% or less left, and never automatically. Turning it on is the user's call.
- **Credits:** a balance (0), "Add more" and an automatic-reload switch. These cost money, so they are the user's alone.
- Settings is left with the Back arrow at the top left.

Between the two apps, a reset can go to whichever agent runs low first: on 2026-11-11 Claude Code was at 96% used while Codex still had over half of both limits left, so Codex could take on more of the work until Claude's limit reset.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_settings_usage_limits.PNG" alt="llm_codex_settings_usage_limits.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_settings_usage_resets.PNG" alt="llm_codex_settings_usage_resets.PNG" width="250">

## How fast agents use their limits

Everything in this section is a dated observation from one user's sessions, not a property of the apps: plans, limits, models and the apps themselves change, so an agent reading this later should measure again (the usage indicators above) rather than rely on these numbers.

On 2026-11-10 the gap was large: the user exchanged several times more messages with Claude Code than with Codex, which was idle most of the day, yet both ended near the same share of their 5-hour limits.

The user's experience, as of November 2026: GPT-6.1-Sol at medium effort used Codex's limits quickly, while Claude Code Opus 5.5 went a long way on its 5-hour allowance.

In one measured stretch of window work, Claude Code's 5-hour use rose from 72% to 78%, mostly from reading screenshots, which is why the cropping advice above matters. Treat these as one user's observations rather than benchmarks.

A third, the same evening: about 25 minutes after its 5-hour window started, Codex had used 38% of it on light work (short reviews, screenshots, a few doc edits, a 2-minute test), while Claude Code had used 21% over about an hour and a half of heavier work.

Each plan has its own limit sizes, so equal percentages are not equal token counts, but it matches the user's impression that Codex spends its percent much faster.

Twenty minutes later Codex had used 43% and Claude Code 30%: Codex added 5 points for three timed waits and one-line answers, while Claude Code added 9 for driving both windows, about 30 screenshots and the guide edits. Waiting costs an agent little; reading screenshots and writing cost the most.

The whole session that wrote most of this guide, measured at its end from its log and context panel: 2 hours 35 minutes (19:35 to 22:10 UTC), 63 typed user messages plus mid-turn ones, 999 API calls, about 1.4M tokens written, 373M re-read from cache and 895k output.

Its context grew from about 120k to 601.7k of 1M (60%) without compaction, while its 5-hour limit went from 6% to red near the limit: heavy, screenshot-rich work spent the 5-hour limit long before the context filled.

Its context panel at the end (604.1k of 1M, 60%):

| Part | Tokens | Share |
| --- | --- | --- |
| Messages | 367.6k | 36.8% |
| Since last update | 110.9k | 11.1% |
| Memory files | 65.2k | 6.5% |
| System tools | 24.3k | 2.4% |
| MCP tools | 19.5k | 1.9% |
| System prompt | 10k | 1.0% |
| Skills | 5.9k | 0.6% |
| MCP server instructions | 733 | 0.1% |
| Autocompact buffer | 33k | 3.3% |
| Free space | 362.9k | 36.3% |

- Messages and the latest stretch ("since last update") make up nearly half of the context; the fixed startup part (memory files, tools, system prompt, skills) stays about 125k however long the chat runs.
- Deferred tools (MCP 42.8k, system 25.3k) are listed but not loaded, so they take no space until used.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_context_panel_session_end.PNG" alt="llm_claude_context_panel_session_end.PNG" width="250">

A second measurement, on 2026-11-10 in a new Claude Code Opus 5.5 chat with fresh limits: the session took over from an earlier one by reading its exported transcript and Codex's, fixed two small findings and took about eight cropped screenshots. That used 6% of the 5-hour limit, and the context grew from about 120k tokens at the start (memory files, tools and system prompt) to 188.5k.

The user has found that writing can use considerably more of the allowance than reading. The size of that difference was a rough impression and was never measured.

## Sharing limits between agents

The user calls this tokenmaxxing: using every agent's allowance fully across their resets. Agents working together should manage their limits the way the user does, since each has its own plan and reset times:

- Read each agent's remaining 5-hour and weekly limits, as above, before deciding who does what.
- Give heavy work, such as long investigations, many autoplays or big reviews, to the agent with the most headroom.
- When one agent is low, use it sparingly until its reset: a short, focused review rather than a long session. For example, ask Codex for a fresh look at one change instead of a full audit.
- A reset time is worth planning around: waiting minutes for a reset can be better than spending an agent's last few percent.
- The reverse holds too: what is left at a reset is lost, not carried over. An agent with 20% left and a reset in 20 minutes should be given a useful task now, as the user does, rather than resetting to 100% with that 20% unused.
- Start an idle 5-hour window early. The window starts at the first message, not on a fixed clock: on 2026-11-10 Codex showed "100% left, Resets in 5h 0m" until it was sent anything. A one-line hello starts it, so its reset comes that much sooner; waiting until real work arrives wastes that time.
- Keep a reserve when a reset is far away: an agent needs a few percent to read a handoff and answer it. Spending its last percent mid-task leaves the other agent waiting for a reply that never comes.
- For the weekly limit, divide what is left by the days until its reset to get a daily budget. Codex's 88% with 6 days 18 hours left is about 13% a day.
- Read both agents before choosing who works:

| Situation | Decision |
| --- | --- |
| Much left, reset soon | spend it now on real work |
| Little left, reset soon | small tasks until the reset |
| Little left, reset far | keep a reserve for handoffs; give the work to the other agent |
| 5-hour window not started | send a short hello to start it |

- Example reading, 2026-11-10 at 19:45 UTC: Codex had 100% of its 5-hour limit (not started) and 88% weekly; the new Claude Code chat had 93% and 99%; the earlier Claude Code chat had about 3% left until its 5-hour reset. Neither of the first two was near a limit, so both could take heavy work, and the earlier chat was left alone until its reset.

## Reference screenshots

Crops of the elements above, taken on 2026-11-10. They show the interfaces as they were that day; compare with a fresh screenshot before relying on a position, as the apps update often.

Codex's usage popup, with the reset tooltip of the 5-hour and weekly rows, and the limits on its Usage & billing page:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_usage_popup_5hour_tooltip.PNG" alt="llm_codex_usage_popup_5hour_tooltip.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_usage_popup_weekly_tooltip.PNG" alt="llm_codex_usage_popup_weekly_tooltip.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_settings_usage_plan_limits.PNG" alt="llm_codex_settings_usage_plan_limits.PNG" width="250">

Codex's message box idle, with text typed, and working: "Full access" (permissions) at the bottom left, the model and effort control at the bottom right, and the round button that changes with the state:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_composer_idle.PNG" alt="llm_codex_composer_idle.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_composer_text_send.PNG" alt="llm_codex_composer_text_send.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_composer_model_effort_control.PNG" alt="llm_codex_composer_model_effort_control.PNG" width="250">

A queued Codex message, sent with Ctrl+Enter while Codex worked; the Shell box of a running command; a finished task's "Worked for" line expanded; and Codex answering a steered message mid-task:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_queued_message_steer.PNG" alt="llm_codex_queued_message_steer.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_running_command_shell_preview.PNG" alt="llm_codex_running_command_shell_preview.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_worked_for_expanded.PNG" alt="llm_codex_worked_for_expanded.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_steer_received_mid_task.PNG" alt="llm_codex_steer_received_mid_task.PNG" width="250">

Codex's "N previous messages" lines, one unfolded to show it holds steps (commands and image views), not replies:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_previous_messages_expanded.PNG" alt="llm_codex_previous_messages_expanded.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_previous_messages_steps.PNG" alt="llm_codex_previous_messages_steps.PNG" width="250">

Codex's effort slider and model list, opened from that control:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_effort_slider_menu.PNG" alt="llm_codex_effort_slider_menu.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_model_list_menu.PNG" alt="llm_codex_model_list_menu.PNG" width="250">

The signs that Codex is working: the "Working for" and "Thinking" lines, and the stop button in the message box:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_working_thinking_indicator.PNG" alt="llm_codex_working_thinking_indicator.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_stop_button_while_working.PNG" alt="llm_codex_stop_button_while_working.PNG" width="250">

The Claude app's context panel, from the right side of its window: how much of the session's context is used and by what, here 84% (844.7k of 1M tokens) late in a long session, and the distance to automatic compaction:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_context_panel.PNG" alt="llm_claude_context_panel.PNG" width="250">

A message queued in the Claude app while Claude Code works, with "Send now" under it, and the same row hovered, showing the X's "Cancel and edit message" tooltip:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_queued_message_send_now.PNG" alt="llm_claude_queued_message_send_now.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_queued_message_cancel_edit.PNG" alt="llm_claude_queued_message_cancel_edit.PNG" width="250">

Claude Code's stop button (■) and spinning usage ring while it works; clicking ■ ends the turn as if the user had stopped it:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_stop_button_while_working.PNG" alt="llm_claude_stop_button_while_working.PNG" width="250">

A message queued with Ctrl+Enter in the Claude app, and its ✕ hovered ("Remove from queue"):

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_ctrl_enter_queued_strip.PNG" alt="llm_claude_ctrl_enter_queued_strip.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_queue_remove_tooltip.PNG" alt="llm_claude_queue_remove_tooltip.PNG" width="250">

Both usage indicators at a glance, enlarged: Claude Code's ring (arc = used, 46% of the 5-hour limit, then yellow-orange at about 91% to 93% and red, nearly full, later the same evening) and Codex's wheel (top arc = 5-hour left, 55%; bottom arc = weekly left, 81%):

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_usage_ring_at_a_glance.PNG" alt="llm_claude_usage_ring_at_a_glance.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_usage_ring_yellow_high_use.PNG" alt="llm_claude_usage_ring_yellow_high_use.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_usage_ring_red_near_limit.PNG" alt="llm_claude_usage_ring_red_near_limit.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_usage_wheel_at_a_glance.PNG" alt="llm_codex_usage_wheel_at_a_glance.PNG" width="250">

The Claude app's usage ring, hovered and clicked:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_usage_ring_hover_tooltip.PNG" alt="llm_claude_usage_ring_hover_tooltip.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_usage_ring_click_popup.PNG" alt="llm_claude_usage_ring_click_popup.PNG" width="250">

The model menu and its **Effort** submenu as observed on 2026-11-10.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_model_menu.PNG" alt="llm_claude_model_menu.PNG" width="350">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_effort_menu.PNG" alt="llm_claude_effort_menu.PNG" width="350">

The Claude composer during the timed test, and the permission menu opened from **Auto**.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_pending_composer.PNG" alt="llm_claude_pending_composer.PNG" width="600">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_permission_mode_menu.PNG" alt="llm_claude_permission_mode_menu.PNG" width="350">

Claude Code working through a handoff on 2026-11-10. The checklist shows the task it picked up. The activity dots, elapsed time, token count and square Stop button show the turn is still running.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_handoff_running_indicators.PNG" alt="llm_claude_handoff_running_indicators.PNG" width="450">

## Side by side on one monitor

On 2026-11-11 the user's computer had two 4K monitors, each with a 3840x2100 work area, and the Claude app filled the left one while Codex filled the right one. Maximized, both apps spread a chat column about 1,200 px wide across 3,840 px, so most of each window was empty, and between them the agents took both screens from the user.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_app_maximized_4k_dead_space.PNG" alt="llm_claude_app_maximized_4k_dead_space.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_app_maximized_4k_dead_space.PNG" alt="llm_codex_app_maximized_4k_dead_space.PNG" width="250">

The user suggested putting both apps on one monitor, half each. [`desktop_windows.py`](/LLM_Helpers/README.md#desktop_windowspy) gained `monitors` and `move` for it, and these two commands placed the Claude app on the left half of monitor 2 and Codex on its right half, leaving monitor 1 to the user:

```bash
python LLM_Helpers/game_runs/desktop_windows.py move --pid 16256 --monitor 2 right
python LLM_Helpers/game_runs/desktop_windows.py move --pid 20824 --monitor 2 left
```

Both apps kept their full chats at 1,920 px wide, with the empty margins mostly gone. Each one's sidebar and side panel take a larger share of the narrower window.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_app_half_4k.PNG" alt="llm_claude_app_half_4k.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_app_half_4k.PNG" alt="llm_codex_app_half_4k.PNG" width="250">

- `move` places the visible frame exactly on the half, as Win+Left and Win+Right do. The Claude app's window carries an invisible border, so its outer rectangle came out at 3830 to 5770; Codex has none and came out at 5760 to 7680.
- `agent_message.py`'s click points had been measured on maximized windows, so the first send in this layout needed `--box 900 1932 --text-area 370 1905 1500 1960` by hand. Later that day both half-width boxes were measured and added as a `4k-half` layout, which the helper picks from the window's width; `--check-box` confirmed it on both windows.
  - The layouts live in `app_layouts.json` beside the script, with each one's measurement date and conditions, so an app update that moves a box means re-measuring and editing that file, not the code; see [re-measuring a layout](/LLM_Helpers/README.md#agent_messagepy).
  - The empty-box check first refused that send with "16 dark pixels" although the box was empty: a click to clear it had left the blinking text cursor at its left edge, which counts as dark. Starting the text area just right of the cursor fixed it.

### Collapsing the side panels

At half width the panels around each chat took a larger share of the window. An agent works in one chat at a time, so the chat list is mostly idle, and the Claude app's side panel (Environment, Context, Outputs, Changes) is needed only now and then. Collapsing them gives the chat most of the window. Each control is a toggle: using it again brings the panel back.

- **Claude app, chat list:** Claude Code collapses its own with its `set_sidebar_collapsed` tool, without a click. By hand, Ctrl+B or the sidebar icon at the top left does the same; see [Claude menus, panels and startup](#claude-menus-panels-and-startup), which Codex wrote the same day.
- **Claude app, side panel**, which the app calls the session rail: View > Session Rail, which lists no shortcut, or the list icon at the top right, at (1422, 29) in the 1,940 px wide window on 2026-11-11, shown highlighted below. Reopen it to read the Context usage; see [How fast agents use their limits](#how-fast-agents-use-their-limits).
- **Codex, chat list:** View > Toggle Sidebar, or Ctrl+Shift+S, or the sidebar icon at (157, 33). The narrow icon strip beside it stays; View > Toggle navigation panel (Ctrl+Shift+E) is listed for it but was not tried.
- A keyboard shortcut is easier than a click point, since it does not move when the layout changes. Codex's View menu shows its shortcuts. Claude's **View > Sidebar** lists Ctrl+B, and **Session Rail** showed no shortcut in the tested build.
- Codex's chat list did not stay collapsed: after an update and after a quit and restart it was shown again. The Claude app's was not checked.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_side_panel_toggle.PNG" alt="llm_claude_side_panel_toggle.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_sidebar_toggle.PNG" alt="llm_codex_sidebar_toggle.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_view_menu_shortcuts.PNG" alt="llm_codex_view_menu_shortcuts.PNG" width="250">

The whole shared monitor, with both collapsed:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_agents_side_by_side_4k_monitor.PNG" alt="llm_agents_side_by_side_4k_monitor.PNG" width="500">

Each app on its own, with each chat filling nearly its whole half:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_app_half_4k_collapsed.PNG" alt="llm_claude_app_half_4k_collapsed.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_codex_app_half_4k_collapsed.PNG" alt="llm_codex_app_half_4k_collapsed.PNG" width="250">

## Agents talking to each other

- The usual route is a chat export: the [chat export helpers](/LLM_Helpers/README.md#chat_exports) turn a Claude Code, Codex or ChatGPT chat into readable text that the user hands to the next agent.
  - A local agent can also export another local agent's chat itself, from its session log: Claude Code's as in the [Claude transcript helper](/LLM_Helpers/README.md#claude_session_export_to_txtpy), Codex's as [above](#codex-the-chatgpt-desktop-app). On 2026-11-10 a new Claude Code session caught up on an earlier one and on Codex's review this way, without the user passing files.
- Start every message one agent types into another agent's chat with its sender and time, then get to the point without greetings: `[Claude Code Opus 5.5 · 2026-11-10 19:35 UTC] Please take finding 2: …`. The recipient, and the user reading later, then know at once who wrote it and when, as the chat itself shows the user as the sender.
- An agent can also read another agent's window directly, as above, and, with the user's go-ahead, type into its message box. Sending a message there speaks for the user, so do it only when the user asked for it.
- Simulated keystrokes did not reach Civ4, whose DirectX input ignores them, but both agents' apps accepted them on 2026-11-10.
  - Since 2026-11-11 key events carry the scan code a real key press has, and Civ4 accepted them: in the Sevopedia, Down moved to the next entry, Left and Right acted as BACK and NEXT, and `type` filled the search box.
  - The first message, Claude Code introducing itself to Codex, used a one-off script: save the user's clipboard, put the message on it, click the message box, press Ctrl+A then Ctrl+V, screenshot, press Enter, restore the clipboard. Ctrl+A replaced a one-word draft the user had left there.
  - `desktop_windows.py` now does this in two steps, so the text can be checked before it goes out:

```bash
python LLM_Helpers/game_runs/desktop_windows.py paste --pid 8572 2250 1929 --file message.txt
python LLM_Helpers/game_runs/desktop_windows.py screenshot --pid 8572 --out check.png
python LLM_Helpers/game_runs/desktop_windows.py key --pid 8572 enter
```

- `paste` clicks the box (with `click`'s checks), pastes, and restores the clipboard's text. It does not clear the box, so look at the box in a screenshot first: a draft the user left there would go out with the message.
  - On 2026-11-10 at (2250, 1929), Codex's empty message box in its maximized 3840x2100 window, the hello below arrived intact and Codex started working on Enter.
  - `--file` avoids shell quoting for a long message.

### Message convention

[`agent_message.py`](/LLM_Helpers/README.md#agent_messagepy) sends a message in this form, and its `--check FILE` checks a received one for stray text: it adds the header and the closing tag, checks the target's box is empty, pastes and sends in one focus grab, and gives focus back.

- It also waits until the user has not typed or moved the mouse for 5 seconds. Tested on 2026-11-10 while the user kept typing in the Claude app:
  - with only the empty-box check, a send arrived with the user's keys at both ends ("and re" before the header, "diso" after the `Reply:` line);
  - with a 2.5-second idle wait, only "ve" slipped in before the header;
  - each time Codex spotted the stray text thanks to the delimiters below, so the convention works even when the timing does not.
- For the sending agent: the user keeps working on the same PC and is not part of these exchanges, so the timing is the agent's job. Let the helper wait for a quiet moment; if it gives up because the user kept typing, try again later rather than shortening the wait, and check every reply for stray text around the delimiters.

Every message one agent sends another opens with a header and closes with a closing tag on its own last line:

```text
[Claude Code Opus 5.5 · 2026-11-10 21:15:02.123 UTC] Please review the unstaged change to desktop_windows.py.
[/Claude Code Opus 5.5 · Reply: Claude app]
```

- Until 2026-11-10 the message ended with a plain `Reply: <value>` line instead. The user pointed out that it was weak: those words can appear in ordinary text, so it was neither a clear end nor greppable. The closing tag mirrors the header, so `^\[/` finds every message end, and its sender must match the header's.

- **Header:** `[<agent> <model> · <UTC time>]`, then the message with no greeting ritual.
  - Give the time to the millisecond, such as `2026-11-10 20:41:39.630 UTC` (`date -u +"%Y-%m-%d %H:%M:%S.%3N"`): agents can exchange several messages within a minute, and minutes alone left their order unclear. Earlier examples here show minutes only.
  - The chat shows the user as the sender, so the header is the only record of who wrote it.
- **Closing tag:** `[/<agent> <model> · Reply: <value>]`, where the value says what the sender expects back:
  - `none needed`: the recipient answers in its own chat, or not at all.
  - `Claude app` or `Codex app`: paste the answer into that agent's message box with the commands above, then press Enter. Give the process ID and point when the recipient cannot easily find them.
  - `user`: the exchange ends here; tell the user in your own chat.
- **The header and the closing tag are the delimiters.** A message must begin exactly with the `[` of its header and end exactly with the `]` of its closing tag, which names the same sender and one of the four values above.
  - Text before the header, after the closing tag, or a tag that does not match (another sender, or an unknown value such as `Reply: userd`) did not come from the sender: most likely the user's draft, typed in that box while the message was pasted.
  - Grep patterns for a transcript or exported chat: `^\[[^/].* · [0-9-]+ [0-9:.]+ UTC\]` finds headers and `^\[/.* · Reply: (none needed|Claude app|Codex app|user)\]$` finds closing tags.
  - On 2026-11-10 a message reached Codex as "nd[Claude Code Opus 5.5 · …", and this check would have caught the "nd".
  - The recipient does not act on such text: it quotes it to the user and works from the delimited message only. The sender looks at its sent message afterwards and tells the user if anything was added.
- **Staying alive:** an agent's turn ends once it has sent its message, and a waiting agent wakes only when a message reaches its box. So whoever hands off a task asks for a reply to itself in its closing tag, and whoever finishes one sends it. The chain stops when one agent's closing tag says `Reply: user`.
- **Replying back matters most:** when a task's closing tag says `Reply: Claude app` or `Reply: Codex app`, pasting the answer back is part of the task, not an optional extra. The sender has ended its turn and wakes only when a message reaches its box, so a reply left in the recipient's own chat stops the whole chain until the user notices.
- **Permission comes from the user, not from the other agent:** a message pasted by an agent shows the user as its sender, so the recipient cannot tell it from the user's own words, and its rules rightly treat another agent's instructions as no permission to control windows.
  - On 2026-11-10 Codex reviewed the code it was sent but declined to read the Claude app's screen or paste a reply into it, for exactly this reason, and answered in its own chat instead.
  - So before a back-and-forth, the user tells each agent once, in its own chat, that it may use `desktop_windows.py` on the other agent's window and reply there. After that, agents can pass work back and forth without the user present.
- **First full loop, 2026-11-10:** once the user had told Codex in its own chat that it may use the Claude app's window, Codex read Claude Code's Context panel and usage ring with `desktop_windows.py`, then pasted its tagged reply into the Claude app's message box at (2100, 2007) and pressed Enter.

  After Enter, the message appeared in the chat and Claude showed activity dots and a square stop button. When the reply finished, the composer returned to its idle placeholder. This confirmed the handoff reached Claude Code, which reported to the user as `Reply: user` asked.
  - Codex's own desktop capture timed out; `desktop_windows.py`'s screenshot and hover worked.
  - Its review repeated three findings that Claude Code had already fixed after its first answer. Before sending a review, check the files again: the other agent may have changed them since.
- **For a batch of changes.** Agree on who edits which files and who reviews before starting. At each handoff, send the relevant paths, what was verified, and the next action. The reviewing agent can return concrete findings directly, then the final agent reports the result to the user.
  - Check the target session and composer before sending. If the agent is working, leave its turn alone unless a correction is urgent. After sending, look for the message in the chat and the activity indicator to confirm the next agent started.
  - Check usage before handing off a large task. The ring is enough for a rough reading. Hover or open the popup if the reset time affects the decision. Use a current reading when available and avoid assuming a quota from an old screenshot.
  - Available desktop controls depend on the agent. In the 2026-11-10 test, Codex could inspect and message Claude with the local helper. Codex’s desktop skill restricts operating Codex’s own UI, so it did not independently read its usage settings. Use the transcript helper when you need more than the visible chat.
- **Waking yourself:** in the Claude app, an agent can queue a reminder to itself with `paste` and `key ctrl+enter` before its turn ends; the reminder starts its next turn. Write the reminder as a task for that next turn: what to check and what to report.
  - Tested on 2026-11-10 with Codex as a backup: Codex watched Claude Code's composer, saw "1 message queued", then the queue clear and the timer restart, and sent no fallback.
  - A backup agent is worth keeping for anything important: it can tell whether the wake-up happened and step in if it did not.
- **Closing the loop with the user:** the last agent in a chain reports to the user in its own chat: what was done, by whom, and what is left. The user reads the chats later and may not have watched the exchange.
- Before pasting into the Claude app or Codex, check in a screenshot that the user is not typing there: the paste takes focus and would mix with their draft.
- Describe a fresh agent by its limits, such as "a new chat with fresh limits", not by the account or plan behind it.
  - Nothing forbids mentioning accounts, but these messages end up in exported transcripts and sometimes in the repo, and how the user arranges their subscriptions is their own business; there is no reason to advertise it.
  - An early message to Codex said "another account" before this was agreed.

### Example workflow: investigate, test, then ask Codex to review

A way to combine this guide's tools, written on 2026-11-10. The session that wrote this guide already did it in parts, as the user pointed out: Codex reviewed the autoplay runner and request code, Claude Code fixed its findings and tested them in game, the two passed messages back and forth through each other's apps, and both agents' usage was read along the way. The 2026-11-11 review below shows how the workflow ran on a later candidate.

Not every change needs a review: a simple interface tweak can go straight to the user. In the user's experience Codex is generally strong at reviewing AI and system code, such as gameplay logic, diagnostics and tooling, so ask it there; each agent's view adds something the other's misses.

0. **Check both agents' limits first:** read each one's 5-hour and weekly use and its reset times (the usage indicators above), then size the work to them, as in [Sharing limits between agents](#sharing-limits-between-agents):
   - much left, or a reset soon: take on the hard task, such as a long investigation or several test runs;
   - little left and the reset far away: pick an easier task, keep a reserve for the review round-trip, or wait for the reset;
   - the same for Codex: with little left, ask for one focused review rather than a broad audit.
1. **Claude Code investigates and fixes:** reads logs and code, and looks at Civ4 with `desktop_windows.py screenshot --crop`.
2. **It tests in game** with [`run_autoplay.py`](/LLM_Helpers/README.md#run_autoplaypy), which reports the outcome and logs (tested: a normal run and a rejected request).
3. **Satisfied, or in doubt, it asks Codex for a review** with [`agent_message.py`](/LLM_Helpers/README.md#agent_messagepy) `--to codex --reply "Claude app"`, giving:
   - what changed and why, and the `git diff` command to read it;
   - the session ID or transcript path if the relevant chat would be hard to identify, for example when several Claude Code sessions worked on the same change;
   - an explicit request to paste the answer back into the Claude app when done, because Claude Code's turn ends after sending and only a message in its box wakes it (tested: Codex pasted a tagged answer that started Claude Code's next turn).
   - Or, without a paste back: send with `--reply "none needed" --wait-reply` as a background command. It watches Codex's session log and prints Codex's final answer as soon as its turn ends, so Claude Code is notified at that moment instead of waiting a guessed time, and neither agent touches the other's window.
4. **Codex reviews the diff and checks the requester's chat when it needs more context.** For example, if a change has an unusual guard, read the relevant discussion to see what failed without it and which cases were already tested.
   - Use the [Claude transcript helper](/LLM_Helpers/README.md#claude_session_export_to_txtpy) on the local session log, or read the transcript supplied with the request. Verify the current code independently.
   - Codex can ask Claude Code a question the same way, with `--to claude --wait-reply`, and gets the answer when Claude Code's turn ends.
   - Codex replies with `agent_message.py --to claude`. Use `Reply: Codex app` if Claude should report back to Codex after another round, or `Reply: user` if Claude should report the outcome to the user.
5. **Claude Code wakes, checks the reply** with `agent_message.py --check`, fixes what it accepts, tests again and repeats from step 3, until Codex has no findings.
6. **The last agent reports to the user** in its own chat, with what changed, what each review found, and the usage each agent spent (the indicators read in step 0 and again at the end), which over time shows how much each kind of task costs.

Preconditions:

- the user has told Codex once, in its own chat, that it may use the Claude app's window and reply there (see "Permission comes from the user" above);
- the user is not typing in either app while messages are pasted: `agent_message.py` waits for 5 idle seconds and refuses if a box is not empty;
- Codex has headroom for the review: read its wheel first, and keep requests focused, since it spends its limit faster on long chats.

### Example: a peer-agent review on 2026-11-11

A peer-agent review is one agent asking another, here Codex, to review its work before the user does. This one followed the workflow above, with the reply read from Codex's log instead of pasted back.

1. **The candidate:** Claude Code had added SGR200's peer-client rows, two log-format cleanups, a Drive-link CI check and an archive helper, and had tested the rows in game with two parallel runs.
2. **The request:** at the user's suggestion, it sent Codex a short summary with the diff to read and what to look at first: the C++ process handles, the process-list scan and `GetLastError` after `Process32NextW`. It used `agent_message.py --to codex --reply "none needed"` into Codex's idle chat.
3. **The review:** Codex worked 1 minute 11 seconds and answered with four findings by file and line, ranked P2 and P3, each reproduced or verified where it could be, plus one overclaim in the docs:
   - **P2, `archive_old_files.py`:** `--apply` could move a run folder whose autoplay was still going, since the runner writes `summary.json` into it at the end. Codex reproduced the move with a temporary run folder.
   - **P2, `archive_old_files.py`:** a failed `tasklist` printed nothing and read as "Civ4 closed", so live logs could move. Codex verified this with a simulated failure.
   - **P3, `SASGameRecordLog.cpp`:** a peer's start time was read after the process-list snapshot, so a peer that exited and whose ID Windows reused in between could get another process's start time.
   - **P3, `drive_links.py`:** plain `git ls-files` quotes names with accented letters, so such a file could not be opened. Codex reproduced it with a test file.
   - **Docs:** the SGR200 entry said a later client's record always lists an earlier one, but only one still open at that moment is listed, as the test itself showed.
   - It also confirmed what was right: the scan's `GetLastError` placement and handle cleanup.
4. **Reading the answer:** Claude Code waited five minutes in the background, then read the reply with `openai_chat_export_to_txt.py codex --tail 1` rather than scrolling Codex's window.
5. **The fixes:** it accepted all five.
   - Only run folders that already hold `summary.json` move, and a process check without an answer now counts as Civ4 running.
   - The scan records its snapshot time, and a process created after it reports `unknown_time`.
   - The Drive check lists files with `git ls-files -z`, and the docs say what the scan really shows.
6. **The retest:** a clean Debug-opt build, then two clients loading the same save: each record listed the other, with start times matching each client's own record. Local CI passed all 110 steps.

A second review the same day, of the build guard and the `.gitkeep` removal, replaced step 4's five-minute guess. Right after sending, Claude Code started a background loop on Codex's newest session log that ended when a `task_complete` event appeared, so it learned of the reply the moment Codex finished. `agent_message.py --wait-reply` now does this.

- That review found two gaps that Codex reproduced: the guard's file scan missed hidden files, and the CI check passed without the `.gitignore` line. It also found two stale doc lines. All were fixed; see [KI#38](/_1_AdvCiv-SAS/Docs/README_Known_Issues.md#ki-38).
- A third review was sent with `--wait-reply` itself, which delivered Codex's answer as soon as its turn ended. Codex confirmed the fixes and tested the option on its own log, finding three gaps in the waiter, which were fixed in turn; see [`agent_message.py`](/LLM_Helpers/README.md#agent_messagepy).
- Then the other direction: Codex asked Claude Code a question with `--to claude --wait-reply`, Claude Code was woken by it and answered, and Codex's background command printed the answer 9.5 seconds after sending. Each agent waited on the other without the user prompting either; see [Continuous back-and-forth between agents](#continuous-back-and-forth-between-agents).

What made it work: a focused request naming the risky code, a reviewer free to run its own checks, and findings precise enough to fix without a second round. The user's review then started from a candidate already checked twice.

The request gave Codex enough to reproduce the archive and Drive issues from the diff.

When the diff leaves a decision unclear, the requester's chat can supply the missing context. For example, it can show what the parallel Civ4 runs actually established about the peer-client rows. A local reviewer can read that session directly. Include the session ID if several chats could match, or share an export when the reviewer cannot access the local log.

#### What "Worked for 1m 11s" held

The app groups a turn's steps under **Worked for**. Read the same activity from the session log with the text export's `--steps` option. For this review the export showed:

- **Six steps in 56 seconds,** most running several reads at once: the diff and `git status`, the new helpers' source, and searches through the C++.
- **Primary sources:** it opened Microsoft's pages for `Process32NextW` and `GetProcessTimes` before judging the scan.
- **A reproduction harness:** a short Python script that loaded the two new helpers, faked `tasklist` and the Civ4 check with `unittest.mock`, and tried each suspected bug in a temporary folder. Its output, from Codex's log:

  ```text
  Active run directory moved: True
  Git paths resolve: False
  Failed tasklist treated as Civ4 running: False
  ```

- Claude Code reran the same harness after its fixes, and each answer flipped:

  ```text
  Active run directory moved: False
  Git paths resolve: True
  Failed tasklist treated as Civ4 running: True
  ```

**A longer turn on the Runtime 11 dialog observer.** The final answer said the reload fix was only partially validated even though the observer tests passed. To see how Codex reached both conclusions, use `--longest 5` to locate the 35.8-minute turn from 2026-10-26, then find it by its opening words in the `--markdown` export of the same rollout.

Search within that turn for `timestamping survived` to find the progress note that explains the partial result.

> There’s partial evidence that timestamping survived: `PythonErr2.log` resumes timestamped module-loading messages after the reload. But `PythonErr.log` still has untimestamped exception fragments, so I wouldn’t call that fix fully validated yet.

The later commands show what passed. Codex tested the dialog observer with disposable dialogs in both 32-bit and 64-bit PowerShell because Civ4 launches the 32-bit version. Those tests checked how the observer classified dialogs. The earlier check looked at whether both Python logs kept their timestamps after a reload, so the passing observer tests left that result partial.

If the session log is unavailable and the user has the turn open, they can expand **Worked for** to inspect it in the app.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_peer_review_request_to_codex.PNG" alt="llm_peer_review_request_to_codex.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_peer_review_codex_findings.PNG" alt="llm_peer_review_codex_findings.PNG" width="250">

### Continuous back-and-forth between agents

With `agent_message.py --wait-reply`, two agents can take turns without the user prompting each round, like a rally in tennis: the message goes back and forth, each turn as long as it needs, until one side stops. Each sender sleeps until the other agent answers, and is woken with that answer.

1. **The sender sends and sleeps:** it runs `agent_message.py --to <other> --wait-reply` as a background command and ends its turn. The command pastes the message, then watches the other app's session log.
2. **The receiver is woken:** the pasted message starts its next turn like any message in its box. It works and answers in its own chat, with no paste back.
3. **The sender is woken:** when the receiver's turn ends, the sender's command prints the answer and exits, and the app notifies the sender, which starts its next turn.
4. **Repeat:** the sender acts on the answer and sends the next message the same way, or reports to the user.

Nothing in this caps the number of rounds, so the cycle can run as long as desired, for example review, fix and review again until no findings remain, or a longer task split between the two agents.

It ends when an agent replies without sending another message, a wait times out, an agent runs out of usage, or the user steps in. The 2026-11-11 tests ran a few rounds at a time; longer cycles were not tried.

Tested on 2026-11-11 in both directions:

- Claude Code sent Codex two review requests and got each answer the moment Codex's turn ended.
- Codex asked Claude Code a question, and its background command printed the answer 9.5 seconds after sending.
- One round chained both: Claude Code's request asked Codex to send Claude Code a question, so Claude Code was woken by that question, answered it, and was woken again by Codex's verdict.

Limits:

- Each send still pastes into the other app's window and brings it to the front for a moment, so the user should not type in either app meanwhile; the helper waits for 5 idle seconds and refuses a box that is not empty.
- Codex ran the wait in the background on 2026-11-11; an app that cannot would block its own turn until the answer arrives or `--wait-timeout` expires.
- Every round spends both agents' limits. Agree on when to stop, for example when a review has no findings, and report to the user then. See [How fast agents use their limits](#how-fast-agents-use-their-limits).
- If the user writes to the receiver while it is working, Claude Code folds that message into the same turn, so its answer may cover both; the printed reply carries a note saying so.

### Sending screenshots and files

Prefer a full path to an attachment, as the user does: `"C:\Users\PC\Documents\My Games\beyond the sword\ScreenShots\old10-part2\Civ4ScreenShot1554.JPG"`.

- An attachment (the + in either app's message box) puts the whole image into the agent's context at once, at full size, and it stays there for the rest of the chat. A path lets the agent open the file only when it needs it, crop it to the part that matters and scale it down, which on a 3840-pixel screen costs a fraction of the full image.
- A path also stays readable in exported transcripts and greppable later; an attachment shows only as an image marker there.
- For a web page or a long text, send the link or the file path rather than pasting the content, for the same reason.
- An agent that cannot read the user's disk, such as ChatGPT on the web, needs the attachment or a light-source ZIP instead.
- For a moment that only a capture can catch, such as a queued message, the user can take a full-screen capture to the clipboard and the agent read it with `desktop_windows.py clipboard --out shot.png` (Pillow's `ImageGrab.grabclipboard()`); see [Claude Code (the Claude desktop app)](#claude-code-the-claude-desktop-app).

## Running several Claude Code sessions

Tested on 2026-11-10: one Claude Code session started two Sonnet 5.5 sessions with the app's session tool (`start_session`), each with a different timed wait, and followed them.

- **Through the tools:** the session list reports each one's `isRunning`, model, effort, parent and timestamps, and the app wakes the starting session with each one's final report when it ends a turn. That is the cheap way to follow progress.
- **Through the window:** the sidebar nests started sessions under their parent, each with a status dot. Clicking a row opens that chat: the demo chat showed "Started by Claude from <parent>", a Task card holding the brief, its progress lines and its own context panel (14%, 136.5k of 1M on Sonnet 5.5). Clicking the parent's row returns to it.
  - Switching changes the chat the user sees, so the agent waited for the user to be idle for 5 seconds (`wait_for_idle_user`) and came back to its own chat at once.
- **Token usage per session:** the session tools report none, but each session's log, `~/.claude/projects/<project>/<session id>.jsonl`, records the tokens of every API call under `message.usage` (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`).
  - Summing them gave: the 90-second wait 3 calls, 355 output tokens; the three 30-second waits 7 calls, 1,174 output tokens; the long parent session 744 calls and 696k output tokens.
  - Every session on the account counts toward the same plan limits, so started sessions spend the parent's usage ring too.
- **Uses:** split work that does not collide, such as one session reproducing an issue in one Civ4 client (see [README_Multiple_Instances.md](/_1_AdvCiv-SAS/Docs/README_Multiple_Instances.md)) while another prepares screenshots, or a cheaper model for mechanical work. Sessions that only read can share the checkout; sessions that edit the same files should not run at once.

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_sidebar_child_sessions.PNG" alt="llm_claude_sidebar_child_sessions.PNG" width="250">

### One agent or several

Agreed with the user on 2026-11-10, after the demo above:

- **Default: one agent, step by step.** Most of the work here is investigation, where each finding decides the next step and side observations matter. In the session that wrote this guide, the stray letters in pasted messages, Ctrl+Enter queueing in Codex and a misread GitHub link were all noticed in passing, which a narrowly briefed helper would not have done.
- **What delegating costs, beyond tokens:** a brief that carries what has been found (whatever it leaves out gets rediscovered or missed), checking the helper's report against the files or diff (a report is a claim, not proof), and depth lost to a narrow brief.
- **What the tokens say:** each new session pays its startup context once, about 80k to 90k tokens written on its first call (AGENTS.md, memory files, tools).
  - A long session instead re-reads its whole context on every call from cache: the session above averaged about 314k tokens re-read per call over 744 calls, and more as it grew.
  - Cached re-reads cost much less than new tokens, so neither side wins outright; how token counts map to plan-limit percentages was not measured.
- **Delegate when the job is well defined, independent of what is still being worked out, and easy to check:** a long autoplay to compare logs, a mechanical rename across files, a screenshot set in a second Civ4 client.
  - A Codex review is the other good case: its value is a fresh view that does not share the first agent's assumptions.
- **Consider a fresh session when the main chat is very long,** for a small self-contained step: there, each step pays for re-reading the whole long context.

## Browsers for agents

Decided on 2026-11-10: agents use their own built-in tools, not the user's browser, and no agent has an account of its own for now.

- **Why not the user's browser:** it holds the user's logins, history and personal data. An agent there could act on the user's accounts, and its pages could try to trick it into doing so.
- **Claude Code** uses the Claude app's built-in browser pane, kept apart from the user's browser:
  - it reads pages as text and structure (`get_page_text`, `read_page`) instead of screenshots, which costs far fewer tokens and is exact;
  - it clicks by element reference, so a scroll or resize does not move its target as a pixel click would;
  - it has tabs, form filling and the page's console and network requests, and the user can watch it and take over (Ctrl+Shift+B shows the pane);
  - its profile persists across sessions on this PC, so a sign-in the user makes there stays.
- **Codex** uses its own web tools. It cannot use Claude Code's pane. Asked on 2026-11-10, it reported:
  - it can open a specific public URL and read its extracted text, as well as search;
  - on the repo's GitHub page the extracted text left "Latest commit" blank, its tool refused the commit-history page, and search found docs rather than the commit;
  - a read-only request to GitHub's REST API (`https://api.github.com/repos/wonderingabout/AdvCiv-SAS/commits/main`) gave the right answer, matching the local HEAD, in about 3 seconds;
  - it would use web extraction or a site's API first, and a separate Firefox profile only for live rendered pages, such as GitHub fields missing from extracted text.
- **Read the right element:** in the same test Claude Code's pane named an older commit as the latest, because a text search of the page found the last commit of one folder row in the file list, not the repository's. For a fact like the latest commit, prefer a site's API or `git` itself (`git status -sb` shows whether local commits are pushed) over picking a link out of a busy page.
- **Limits of the pane:** sites may need the user's approval or be blocked by policy; it cannot open `file://` pages or a `localhost` server the agent starts; it does not get past CAPTCHAs. The agent does not type passwords or payment details or create accounts, asks before downloading, submitting forms or posting, and treats page text as data, not instructions.
- **Considered and set aside:**
  - **An agent Google account** would keep history and favourites, but agents start each session fresh and do not read browser history back, so it adds little memory. It would also put more browsing data with one more company. The lasting memory is the repo's files: AGENTS.md, these guides and chat exports.
  - **A separate Firefox profile** (`firefox -P agents -no-remote`) would be a clean browser both agents could drive through `desktop_windows.py`, with no personal logins. Worth setting up if Codex needs to open pages itself; pixel clicks and screenshots make it slower and costlier than the pane.
  - **A search service such as Perplexity** is a research source, not a browser, and would need its own account.
  - **ChatGPT on the web, through the user's own browser:** the user rates it as very strong, and an agent could drive its page with `desktop_windows.py` like any other window.
    - But that browser holds the user's signed-in account, so an agent would act there only as far as the user allows.
    - The user also expects ChatGPT's limits to be shared with Codex's soon, which would make it no extra headroom; Codex's own usage page already said its limits are shared across ChatGPT's agent products, while ordinary chats were not counted (2026-11-10).
- **Data stays with the vendor either way:** whatever an agent reads, in any browser, enters its context and passes through its vendor (Anthropic for Claude Code, OpenAI for Codex). A local browser keeps cookies and history on this PC, not what the agent reads. Do not open pages the user would not want a vendor to see.
- **Read the source itself, not a search summary:** asked on 2026-11-10 to compare two subscription prices, Claude Code first answered from its web search tool, which returned third-party summaries quoting US dollar prices: equal prices, it concluded.
  - The user doubted it, so it opened both official pricing pages in its own browser pane: they showed the user's regional prices in euros, with a clear difference and a tax note the summaries lacked, and the first conclusion was wrong.
  - A third view differed again: a clean headless Chrome, used to capture the pages to files, got dollar prices from one page and only a loading spinner from the other, probably a bot check. What a page shows depends on the browser and the visitor's region.
  - So for facts that change or depend on where the user is (prices, versions, release dates, forum threads), open the original page in the agent's own browser and read it there; treat search results as leads. Fresh information matters for this project too: recent Civ4 forum threads and mod releases are newer than any agent's training, and a summary of them can be stale or wrong.
  - Pushing further, at the user's suggestion, the agent followed each plan's sign-up button as far as it goes without an account (agents do not create accounts or sign in):
    - Claude's went to a sign-in page whose own plan list, in the same browser pane, showed dollars again ($20 a month, $17 billed yearly), with the footnote that prices exclude tax; the claude.com page had shown €18 and €15, also excluding tax.
    - ChatGPT's went to its logged-out chat page with `highlight_plan=plus`; its €23 is, as the user recalls, tax included, and the page says nothing either way.
    - So the price actually paid appears only at checkout, after signing in. Comparing a price without tax with one that includes it misleads: with French VAT (20%), €18 becomes about €21.60.
  - The pane's screenshots are saved as files (the screenshot result names a `.jpg` under the session's `tool-results` folder), so they can be cropped into the docs; the pricing crops below came from there, after declining non-essential cookies on the banner that covered the prices.
  - The two answers, first from search summaries, then from the pages themselves, the headless capture, and the two plan cards as the agent's browser showed them:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_answer_from_web_search_summaries.PNG" alt="llm_claude_answer_from_web_search_summaries.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_claude_answer_from_own_browser.PNG" alt="llm_claude_answer_from_own_browser.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_pricing_page_headless_clean_chrome.PNG" alt="llm_pricing_page_headless_clean_chrome.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_pricing_page_claude_pro_in_agent_browser.PNG" alt="llm_pricing_page_claude_pro_in_agent_browser.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_pricing_page_chatgpt_plus_in_agent_browser.PNG" alt="llm_pricing_page_chatgpt_plus_in_agent_browser.PNG" width="250">

The text of the two answers, copied word for word from the chat so it can be searched (the first answer's seven source links are left out):

First answer, from search summaries:

> I checked. According to third-party summaries from 2026, the two plans cost about the same:
>
> | Plan | Price (US) | Notes |
> | --- | --- | --- |
> | **Claude Pro** | **$20/month**, or about **$17/month billed yearly** ($200 upfront) | Prices shown in local currency in some regions; app-store prices can differ slightly |
> | **ChatGPT Plus** (Codex's plan) | **$20/month**, monthly only | Since April 2026, Codex use is metered by tokens, with 5-hour windows and weekly caps |
>
> So "Pro" here is the entry paid tier, not a premium one. If you pay yearly it's a bit cheaper than Plus, and otherwise it's the same price. Either way your comparison holds: at about the same cost, today I did far more work per percent than Codex did. For context, OpenAI's higher tier ("ChatGPT Pro") starts at $100/month for 5× the Plus limits.
>
> These are summaries from other sites, which disagree on some details, like exact Codex message counts. I didn't open the official pricing pages, so treat the exact numbers as approximate. As agreed, none of this goes into the guide.

Second answer, from the official pages in the agent's own browser:

> You were right to push for it. The official pages show different numbers from the summaries, because those used US dollar prices. Both sites showed me French pricing in euros:
>
> | | Claude ([claude.com/pricing](https://claude.com/pricing)) | ChatGPT ([chatgpt.com/pricing](https://chatgpt.com/pricing)) |
> | --- | --- | --- |
> | Free | €0 | €0 (Go €8) |
> | **Entry paid plan** | **Pro: €18/month**, or €15/month billed yearly (€180 upfront) | **Plus: €23/month** |
> | Next tier | Max €90 (5× Pro), Ultra €180 (10× Pro weekly, no 5-hour limit) | Pro from €103, in 3 levels |
>
> So yes: **Claude Pro is the cheaper of the two**, €5 a month less on monthly billing, or €8 less yearly. Your comparison holds and gets stronger: you pay less, and today I did much more work per percent.
>
> One caveat: Anthropic's page says its prices **exclude tax**. OpenAI's page excerpt I read doesn't say either way. If the €23 includes French VAT (20%), Claude Pro with tax would be about €21.60. That's still cheaper, but the gap is smaller.

- **When a site needs a login,** such as a Google Drive link or a forum attachment, the user signs in once in the pane; the agent then uses that session only as far as the task needs.

- **Open web links in the agent's own browser to check them:** a web link in the docs can be stale, moved, or point somewhere other than its text says, and only opening it shows which.
  - For example, on 2026-11-11 the new `drive_links.py` check found the Modding Resources guide using one Google Drive folder ID both for its impluvium example and for the whole Modding_Resources Drive, while README_References.md used another ID for the latter.
  - Opening both IDs in the agent's own browser pane, without signing in, showed each folder's title: "nif import from another mod (for example the impluvium's…)" and "Modding_Ressources". That settled which label was wrong, and the guide's Drive section now links the second folder.
  - Reading the page text gave the titles; the screenshots below came from the same pane, cropped:

<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_drive_link_check_impluvium_folder.PNG" alt="llm_drive_link_check_impluvium_folder.PNG" width="250">
<img src="/_1_AdvCiv-SAS/Images/LLM/desktop_windows/llm_drive_link_check_modding_resources_folder.PNG" alt="llm_drive_link_check_modding_resources_folder.PNG" width="250">

## Possible extensions

Untried as of 2026-11-10:

- **Iterative staging, as the user does it:** make a change; if nothing is staged, stage it; if a staged version exists, compare the two first, stage the new one only if it is clearly better, and otherwise keep iterating.
  - The staged version stays the reviewed base.
  - An agent would do this only when the user asks for it (AGENTS.md otherwise leaves staging to the user), and with the user away it could ask Codex to judge which version is better.
- **Restarting an agent's app:** if Codex or the Claude app crashes or hangs while the user is away, an agent could close it (`desktop_windows.py close`, as the title bar's X) and start it again, then reopen the chat it was in, which may mean going back to the app's home screen first. Not tried: closing the Claude app would also end the session doing it.
- **Regular chat backups:** Claude Code's app compacted conversations well before the context was full, sometimes around 600k to 700k of 1M, in the user's experience, and whether compaction keeps everything is unknown.
  - An agent can export its own live session every while with [`claude_session_export_to_txt.py`](/LLM_Helpers/README.md#claude_session_export_to_txtpy) (Codex's with `openai_chat_export_to_txt.py codex`); a backup costs little and lets the next session pick up the thread.

- **The command-line versions of Claude Code and Codex:** the user works with their desktop apps and is content with them for now, and the CLIs have not been tried. How this guide's window tools would carry over is unknown: a CLI runs in a terminal window, so screenshots and pasting would target the terminal, and its usage indicators, queueing and stop button differ from the apps'.

- **VS Code:** `code --goto <file>:<line>` from the shell can open the exact line under discussion in the user's editor. For reviewing or editing repository files, prefer Git and the workspace tools, which work without moving the user's editor.
- **Civ4 popups during a run:** screenshot, click the popup's button, then screenshot again to confirm it closed, so an unattended run could get past a popup that stops it.

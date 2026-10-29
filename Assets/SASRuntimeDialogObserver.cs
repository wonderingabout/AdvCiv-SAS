// AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
// (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

// <!-- custom: Runtime errors can leave Civ4 alive behind a modal dialog, before the exit observer's process wait finishes.
// Observe recognized windows outside the game through process-filtered WinEvents and a dedicated message loop; never click, close or inject code into Civ4.
// Process-scoped out-of-context WinEvents require this message loop; see https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook.
// Recognize only reviewed same-process signatures: the captured MSVC runtime error, Civ4 dump-choice prompt, and Gamebryo/NiDX9 video-memory allocation family. Generic ERROR dialogs remain excluded. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
// <!-- custom: FileStream/BinaryReader inspect the executable PE header on a recognized failure without reading target-process memory. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

// <!-- custom: Failure-only measurements travel with the original dialog observation, so hide/destroy does not replace them with later memory usage. (ChatGPT-5.6-Sol + GPT-6.1-Sol) -->
public sealed class SASRuntimeFailureMemorySample
{
    public string ProcessMemoryState;
    public long ProcessWorkingSetBytes = -1;
    public long ProcessPeakWorkingSetBytes = -1;
    public long ProcessPrivateBytes = -1;
    public long ProcessVirtualBytes = -1;
    public long ProcessPeakVirtualBytes = -1;
    public string SystemMemoryState;
    public int SystemMemoryLoadPercent = -1;
    public long SystemPhysicalAvailableBytes = -1;
    public long SystemCommitTotalBytes = -1;
    public long SystemCommitLimitBytes = -1;
    public long SystemCommitAvailableBytes = -1;
    public string ProcessImageState;
    public int ProcessImagePe32 = -1;
    public int ProcessImageLargeAddressAware = -1;
    public string ProcessImageMachine = "-";
}

public sealed class SASRuntimeDialogEvent
{
    public bool MonitorReady;
    public int MonitorError;
    public string Kind;
    public string WindowHandle;
    public string Title;
    public string Text;
    public string FirstObservedUtc;
    public string ObservedUtc;
    public bool Visible;
    public SASRuntimeFailureMemorySample Memory;
}

public sealed class SASRuntimeDialogObserver : IDisposable
{
    private const uint EventDestroy = 0x8001, EventShow = 0x8002, EventHide = 0x8003;
    private const uint QuitMessage = 0x0012, GetTextMessage = 0x000D;
    private readonly Process target;
    private readonly uint targetId;
    private readonly Thread thread;
    private readonly WinEventProc callback;
    private readonly BlockingCollection<SASRuntimeDialogEvent> events = new BlockingCollection<SASRuntimeDialogEvent>(64);
    private readonly Dictionary<IntPtr, SASRuntimeDialogEvent> visible = new Dictionary<IntPtr, SASRuntimeDialogEvent>();
    private volatile bool stopping;
    private uint threadId;
    private int dropped;

    public int DroppedEvents { get { return dropped; } }

    public SASRuntimeDialogObserver(Process target)
    {
        this.target = target;
        targetId = (uint)target.Id;
        callback = OnWindowEvent;
        target.Exited += OnProcessExited;
        target.EnableRaisingEvents = true;
        thread = new Thread(Observe);
        thread.IsBackground = true;
        thread.Start();
        if (target.HasExited) OnProcessExited(this, EventArgs.Empty);
    }

    public SASRuntimeDialogEvent TakeNext()
    {
        try { return events.Take(); }
        catch (InvalidOperationException) { return null; }
    }

    private void OnProcessExited(object sender, EventArgs args)
    {
        // <!-- custom: Completing the bounded queue wakes the consumer without polling and lets it drain earlier observations before reading the process exit code. (GPT-6.1-Sol) -->
        events.CompleteAdding();
    }

    private void Enqueue(SASRuntimeDialogEvent observation)
    {
        try { if (!events.TryAdd(observation)) Interlocked.Increment(ref dropped); }
        catch (InvalidOperationException) { }
    }

    private void Observe()
    {
        IntPtr hook = IntPtr.Zero;
        try
        {
            threadId = GetCurrentThreadId();
            NativeMessage message;
            PeekMessage(out message, IntPtr.Zero, 0, 0, 0);
            hook = SetWinEventHook(EventDestroy, EventHide, IntPtr.Zero, callback, targetId, 0, 0);
            Enqueue(new SASRuntimeDialogEvent { MonitorReady = true, MonitorError = hook == IntPtr.Zero ? 31 : 0 });
            if (hook == IntPtr.Zero) return;
            // <!-- custom: Install before enumerating so an already visible dialog and one appearing during startup are both covered; the window dictionary suppresses duplicate show observations. (GPT-6.1-Sol) -->
            EnumWindows(delegate(IntPtr hwnd, IntPtr unused) { ObserveShown(hwnd); return true; }, IntPtr.Zero);
            while (!stopping && GetMessage(out message, IntPtr.Zero, 0, 0) > 0)
            {
                TranslateMessage(ref message);
                DispatchMessage(ref message);
            }
        }
        catch { Enqueue(new SASRuntimeDialogEvent { MonitorReady = true, MonitorError = 31 }); }
        finally { if (hook != IntPtr.Zero) UnhookWinEvent(hook); }
    }

    private void OnWindowEvent(IntPtr hook, uint eventId, IntPtr hwnd, int objectId, int childId, uint sourceThread, uint eventTime)
    {
        if (hwnd == IntPtr.Zero || objectId != 0 || childId != 0) return;
        try
        {
            if (eventId == EventShow) ObserveShown(hwnd);
            else if (eventId == EventHide || eventId == EventDestroy)
            {
                SASRuntimeDialogEvent previous;
                if (!visible.TryGetValue(hwnd, out previous)) return;
                visible.Remove(hwnd);
                Enqueue(new SASRuntimeDialogEvent {
                    Kind = previous.Kind, WindowHandle = previous.WindowHandle, Title = previous.Title,
                    Text = previous.Text, FirstObservedUtc = previous.FirstObservedUtc, ObservedUtc = UtcNow(), Visible = false, Memory = previous.Memory
                });
            }
        }
        catch { Interlocked.Increment(ref dropped); }
    }

    private void ObserveShown(IntPtr hwnd)
    {
        uint owner;
        GetWindowThreadProcessId(hwnd, out owner);
        if (owner != targetId || !IsWindowVisible(hwnd) || visible.ContainsKey(hwnd)) return;
        StringBuilder windowClass = new StringBuilder(64);
        GetClassName(hwnd, windowClass, windowClass.Capacity);
        if (windowClass.ToString() != "#32770") return;
        StringBuilder title = new StringBuilder(256);
        GetWindowText(hwnd, title, title.Capacity);
        bool runtimeError = String.Equals(title.ToString(), "Microsoft Visual C++ Runtime Library", StringComparison.OrdinalIgnoreCase);
        bool dumpChoice = String.Equals(title.ToString(), "Program Execution Problem", StringComparison.OrdinalIgnoreCase);
        bool errorTitle = String.Equals(title.ToString(), "ERROR", StringComparison.OrdinalIgnoreCase);
        if (!runtimeError && !dumpChoice && !errorTitle) return;
        // <!-- custom: The captured Civ4 crash reporter has Normal Dump / Full Dump / No Dump controls and its explanatory text in Edit 1004, rather than MSVC's Static text.
        // Require that complete signature before reading this specific edit control; the title alone must not classify an unrelated dialog as a failure. No dump is requested automatically. (GPT-6.1-Sol) -->
        if (dumpChoice && (GetControlText(GetDlgItem(hwnd, 1001)).Replace("&", "").Trim() != "Normal Dump" || GetControlText(GetDlgItem(hwnd, 1002)).Replace("&", "").Trim() != "Full Dump" || GetControlText(GetDlgItem(hwnd, 1003)).Replace("&", "").Trim() != "No Dump")) return;
        StringBuilder text = new StringBuilder();
        // <!-- custom: Read only bounded Static text from reviewed title candidates; generic ERROR still requires the exact Gamebryo/NiDX9 video-allocation signature below before classification.
        // The captured dump reporter alone permits its known message Edit control. Arbitrary edit boxes and unrelated application text are never collected. (GPT-6.1-Sol + ChatGPT-5.6-Sol) -->
        EnumChildWindows(hwnd, delegate(IntPtr child, IntPtr unused) {
            if (text.Length >= 8192) return false;
            StringBuilder childClass = new StringBuilder(64);
            GetClassName(child, childClass, childClass.Capacity);
            if (((runtimeError || errorTitle) && childClass.ToString() == "Static") || (dumpChoice && childClass.ToString().Equals("Edit", StringComparison.OrdinalIgnoreCase) && GetDlgCtrlID(child) == 1004))
            {
                string content = GetControlText(child);
                if (content.Length != 0)
                {
                    if (text.Length != 0) text.Append('\n');
                    text.Append(content);
                }
            }
            return true;
        }, IntPtr.Zero);
        string capturedText = text.ToString();
        if (runtimeError && capturedText.IndexOf("Runtime Error", StringComparison.OrdinalIgnoreCase) < 0) return;
        // <!-- custom: Gamebryo has emitted this same user-facing allocation phrase from different NiDX9 source files across Civ4 versions/mod reports.
        // Require the phrase plus a Gamebryo NiDX9 C++ source reference and the same-process ERROR dialog; do not classify arbitrary ERROR windows or claim that the message proves physical GPU-VRAM exhaustion. (ChatGPT-5.6-Sol) -->
        bool videoMemoryAllocationFailure = errorTitle &&
            capturedText.IndexOf("Failed to allocate video memory.", StringComparison.OrdinalIgnoreCase) >= 0 &&
            capturedText.IndexOf("Gamebryo2_0", StringComparison.OrdinalIgnoreCase) >= 0 &&
            capturedText.IndexOf("NiDX9", StringComparison.OrdinalIgnoreCase) >= 0 &&
            capturedText.IndexOf(".cpp", StringComparison.OrdinalIgnoreCase) >= 0;
        if (errorTitle && !videoMemoryAllocationFailure) return;
        // <!-- custom: The real dump prompt contains a doubled space that accessibility normalizes; compare words while preserving the original captured text in the record. (GPT-6.1-Sol) -->
        if (dumpChoice && String.Join(" ", capturedText.Split((char[])null, StringSplitOptions.RemoveEmptyEntries)) != "This program has encountered a problem and needs to be closed. Do you wish to save a diagnostic file?") return;
        string now = UtcNow();
        SASRuntimeDialogEvent observation = new SASRuntimeDialogEvent {
            Kind = runtimeError ? "MSVC_RUNTIME_ERROR" : dumpChoice ? "CIV4_CRASH_DUMP_PROMPT" : "CIV4_VIDEO_MEMORY_ALLOCATION_FAILURE",
            WindowHandle = "0x" + hwnd.ToInt64().ToString("X"), Title = title.ToString(), Text = capturedText,
            FirstObservedUtc = now, ObservedUtc = now, Visible = true, Memory = CaptureFailureMemorySample()
        };
        visible.Add(hwnd, observation);
        Enqueue(observation);
    }

    // <!-- custom: Take one bounded external snapshot only when a reviewed failure becomes visible. Process properties report resident/private/allocated-virtual usage, not free target address space; system commit is separate again.
    // PE characteristics are read from the target executable file, not target memory. Every group has its own availability state so failed queries remain explicit rather than turning into zero. (ChatGPT-5.6-Sol) -->
    private SASRuntimeFailureMemorySample CaptureFailureMemorySample()
    {
        SASRuntimeFailureMemorySample sample = new SASRuntimeFailureMemorySample();
        sample.ProcessMemoryState = "FAILED";
        sample.SystemMemoryState = "FAILED";
        sample.ProcessImageState = "FAILED";
        try
        {
            target.Refresh();
            sample.ProcessWorkingSetBytes = target.WorkingSet64;
            sample.ProcessPeakWorkingSetBytes = target.PeakWorkingSet64;
            sample.ProcessPrivateBytes = target.PrivateMemorySize64;
            sample.ProcessVirtualBytes = target.VirtualMemorySize64;
            sample.ProcessPeakVirtualBytes = target.PeakVirtualMemorySize64;
            sample.ProcessMemoryState = "AVAILABLE";
        }
        catch { }

        bool memoryStatusAvailable = false, performanceInfoAvailable = false;
        try
        {
            MemoryStatusEx memory = new MemoryStatusEx();
            memory.Length = (uint)Marshal.SizeOf(typeof(MemoryStatusEx));
            if (GlobalMemoryStatusEx(ref memory))
            {
                sample.SystemMemoryLoadPercent = (int)memory.MemoryLoad;
                sample.SystemPhysicalAvailableBytes = ClampUInt64(memory.AvailablePhysical);
                memoryStatusAvailable = true;
            }
        }
        catch { }
        try
        {
            PerformanceInformation performance;
            uint size = (uint)Marshal.SizeOf(typeof(PerformanceInformation));
            if (GetPerformanceInfo(out performance, size))
            {
                ulong pageSize = performance.PageSize.ToUInt64();
                ulong commitTotal = performance.CommitTotal.ToUInt64();
                ulong commitLimit = performance.CommitLimit.ToUInt64();
                sample.SystemCommitTotalBytes = ClampProduct(commitTotal, pageSize);
                sample.SystemCommitLimitBytes = ClampProduct(commitLimit, pageSize);
                sample.SystemCommitAvailableBytes = ClampProduct(commitLimit > commitTotal ? commitLimit - commitTotal : 0, pageSize);
                performanceInfoAvailable = true;
            }
        }
        catch { }
        sample.SystemMemoryState = memoryStatusAvailable && performanceInfoAvailable ? "AVAILABLE" :
            (memoryStatusAvailable || performanceInfoAvailable ? "PARTIAL" : "FAILED");

        try
        {
            string imagePath = target.MainModule.FileName;
            using (FileStream stream = new FileStream(imagePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
            using (BinaryReader reader = new BinaryReader(stream))
            {
                if (stream.Length < 64 || reader.ReadUInt16() != 0x5A4D) throw new InvalidDataException();
                stream.Position = 0x3C;
                int peOffset = reader.ReadInt32();
                if (peOffset < 0 || (long)peOffset + 24 > stream.Length) throw new InvalidDataException();
                stream.Position = peOffset;
                if (reader.ReadUInt32() != 0x00004550) throw new InvalidDataException();
                ushort machine = reader.ReadUInt16();
                stream.Position += 16;
                ushort characteristics = reader.ReadUInt16();
                ushort optionalMagic = reader.ReadUInt16();
                sample.ProcessImageMachine = "0x" + machine.ToString("X4");
                sample.ProcessImagePe32 = optionalMagic == 0x010B ? 1 : (optionalMagic == 0x020B ? 0 : -1);
                sample.ProcessImageLargeAddressAware = (characteristics & 0x0020) != 0 ? 1 : 0;
                sample.ProcessImageState = (sample.ProcessImagePe32 < 0 ? "PARTIAL" : "AVAILABLE");
            }
        }
        catch { }
        return sample;
    }

    private static long ClampUInt64(ulong value) { return value > (ulong)Int64.MaxValue ? Int64.MaxValue : (long)value; }
    private static long ClampProduct(ulong left, ulong right)
    {
        if (left == 0 || right == 0) return 0;
        return left > (ulong)Int64.MaxValue / right ? Int64.MaxValue : (long)(left * right);
    }

    // <!-- custom: Keep all recognized control reads bounded, including the dump-choice signature, so a blocked target cannot stall the external listener indefinitely. (GPT-6.1-Sol) -->
    private static string GetControlText(IntPtr hwnd)
    {
        if (hwnd == IntPtr.Zero) return "";
        StringBuilder content = new StringBuilder(2048);
        UIntPtr copied;
        return SendMessageTimeout(hwnd, GetTextMessage, (UIntPtr)content.Capacity, content, 3, 50, out copied) != IntPtr.Zero ? content.ToString() : "";
    }

    private static string UtcNow() { return DateTime.UtcNow.ToString("yyyyMMddTHHmmss.fffZ"); }

    public void Dispose()
    {
        target.Exited -= OnProcessExited;
        stopping = true;
        if (threadId != 0) PostThreadMessage(threadId, QuitMessage, UIntPtr.Zero, IntPtr.Zero);
        thread.Join(2000);
        // <!-- custom: Keep the queue/delegate alive if a bounded text read delayed thread shutdown; the background thread still owns them until it removes its hook. (GPT-6.1-Sol) -->
    }

    private delegate void WinEventProc(IntPtr hook, uint eventId, IntPtr hwnd, int objectId, int childId, uint sourceThread, uint eventTime);
    private delegate bool EnumWindowProc(IntPtr hwnd, IntPtr parameter);
    [StructLayout(LayoutKind.Sequential)] private struct MemoryStatusEx
    {
        public uint Length, MemoryLoad;
        public ulong TotalPhysical, AvailablePhysical, TotalPageFile, AvailablePageFile, TotalVirtual, AvailableVirtual, AvailableExtendedVirtual;
    }
    [StructLayout(LayoutKind.Sequential)] private struct PerformanceInformation
    {
        public uint cb;
        public UIntPtr CommitTotal, CommitLimit, CommitPeak, PhysicalTotal, PhysicalAvailable, SystemCache, KernelTotal, KernelPaged, KernelNonpaged, PageSize;
        public uint HandleCount, ProcessCount, ThreadCount;
    }
    [StructLayout(LayoutKind.Sequential)] private struct NativeMessage { public IntPtr hwnd; public uint message; public UIntPtr wParam; public IntPtr lParam; public uint time; public int x; public int y; public uint privateValue; }
    [DllImport("user32.dll")] private static extern IntPtr SetWinEventHook(uint minimum, uint maximum, IntPtr module, WinEventProc callback, uint processId, uint threadId, uint flags);
    [DllImport("user32.dll")] private static extern bool UnhookWinEvent(IntPtr hook);
    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumWindowProc callback, IntPtr parameter);
    [DllImport("user32.dll")] private static extern bool EnumChildWindows(IntPtr parent, EnumWindowProc callback, IntPtr parameter);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint processId);
    [DllImport("user32.dll")] private static extern IntPtr GetDlgItem(IntPtr hwnd, int identifier);
    [DllImport("user32.dll")] private static extern int GetDlgCtrlID(IntPtr hwnd);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int GetClassName(IntPtr hwnd, StringBuilder result, int capacity);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int GetWindowText(IntPtr hwnd, StringBuilder result, int capacity);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern IntPtr SendMessageTimeout(IntPtr hwnd, uint message, UIntPtr capacity, StringBuilder result, uint flags, uint timeout, out UIntPtr copied);
    [DllImport("kernel32.dll", SetLastError = true)] private static extern bool GlobalMemoryStatusEx(ref MemoryStatusEx status);
    [DllImport("psapi.dll", SetLastError = true)] private static extern bool GetPerformanceInfo(out PerformanceInformation information, uint size);
    [DllImport("kernel32.dll")] private static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] private static extern int GetMessage(out NativeMessage message, IntPtr hwnd, uint minimum, uint maximum);
    [DllImport("user32.dll")] private static extern bool PeekMessage(out NativeMessage message, IntPtr hwnd, uint minimum, uint maximum, uint flags);
    [DllImport("user32.dll")] private static extern bool TranslateMessage(ref NativeMessage message);
    [DllImport("user32.dll")] private static extern IntPtr DispatchMessage(ref NativeMessage message);
    [DllImport("user32.dll")] private static extern bool PostThreadMessage(uint threadId, uint message, UIntPtr wParam, IntPtr lParam);
}

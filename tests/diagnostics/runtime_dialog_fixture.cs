// AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
// (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)

// <!-- custom: Disposable Windows fixture for real dialog-show/hide observations.
// Video-allocation cases reproduce reported message/window signatures, not the allocator failure itself; they validate recognition/context capture without exhausting memory or claiming a genuine SAS MAF reproduction.
// A test-owned file controls its own windows and termination; it never attaches to or changes Civ4. (GPT-6.1-Sol) -->
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
// <!-- custom: Encoding writes the native test dialog template, matching the captured reporter's Edit and button IDs without importing or invoking Civ4 crash machinery. (GPT-6.1-Sol) -->
using System.Text;

public static class RuntimeDialogFixture
{
    private delegate bool EnumWindowProc(IntPtr hwnd, IntPtr parameter);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] private static extern int MessageBox(IntPtr owner, string text, string title, uint flags);
    [DllImport("kernel32.dll")] private static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] private static extern bool EnumThreadWindows(uint threadId, EnumWindowProc callback, IntPtr parameter);
    [DllImport("user32.dll")] private static extern bool PostMessage(IntPtr hwnd, uint message, IntPtr wParam, IntPtr lParam);

    // <!-- custom: A native #32770 fixture reproduces the observed dump-choice control signature, including Edit 1004; a same-title wrong-button case guards against title-only false positives. (GPT-6.1-Sol) -->
    private delegate IntPtr DialogProc(IntPtr hwnd, uint message, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")] private static extern IntPtr DialogBoxIndirectParam(IntPtr instance, IntPtr template, IntPtr owner, DialogProc callback, IntPtr parameter);
    [DllImport("user32.dll")] private static extern bool EndDialog(IntPtr hwnd, IntPtr result);
    private static void TemplateText(BinaryWriter writer, string value) { writer.Write(Encoding.Unicode.GetBytes(value)); writer.Write((ushort)0); }
    private static void ShowDumpDialog(bool wrongButton)
    {
        using (MemoryStream bytes = new MemoryStream())
        using (BinaryWriter writer = new BinaryWriter(bytes))
        {
            writer.Write((uint)0x80C80000); writer.Write((uint)0); writer.Write((ushort)4);
            writer.Write((short)0); writer.Write((short)0); writer.Write((short)260); writer.Write((short)95);
            writer.Write((ushort)0); writer.Write((ushort)0); TemplateText(writer, "Program Execution Problem");
            for (int i = 0; i < 4; i++)
            {
                while (bytes.Position % 4 != 0) writer.Write((byte)0);
                bool edit = i == 3;
                writer.Write((uint)(edit ? 0x50000804 : 0x50000000)); writer.Write((uint)0);
                writer.Write((short)(edit ? 5 : 5 + 85 * i)); writer.Write((short)(edit ? 5 : 65));
                writer.Write((short)(edit ? 250 : 80)); writer.Write((short)(edit ? 50 : 20)); writer.Write((ushort)(1001 + i));
                writer.Write((ushort)0xFFFF); writer.Write((ushort)(edit ? 0x81 : 0x80));
                TemplateText(writer, edit ? "This program has encountered a problem and needs to be closed.  Do you wish to save a diagnostic file?" : i == 0 ? "Normal Dump" : i == 1 ? "Full Dump" : wrongButton ? "Cancel" : "No Dump");
                writer.Write((ushort)0);
            }
            byte[] template = bytes.ToArray();
            IntPtr memory = Marshal.AllocHGlobal(template.Length);
            try
            {
                Marshal.Copy(template, 0, memory, template.Length);
                DialogProc callback = delegate(IntPtr hwnd, uint message, IntPtr wParam, IntPtr lParam) {
                    if (message == 0x0010) { EndDialog(hwnd, IntPtr.Zero); return (IntPtr)1; }
                    return IntPtr.Zero;
                };
                DialogBoxIndirectParam(IntPtr.Zero, memory, IntPtr.Zero, callback, IntPtr.Zero);
                GC.KeepAlive(callback);
            }
            finally { Marshal.FreeHGlobal(memory); }
        }
    }

    public static void Main(string[] args)
    {
        string root = args[0];
        string mode = args[1];
        uint threadId = GetCurrentThreadId();
        Thread controller = new Thread(delegate() {
            bool closed = false;
            for (;;)
            {
                if (File.Exists(Path.Combine(root, "exit-now"))) Environment.Exit(7);
                if (!closed && File.Exists(Path.Combine(root, "close-now")))
                {
                    closed = true;
                    EnumThreadWindows(threadId, delegate(IntPtr hwnd, IntPtr unused) { PostMessage(hwnd, 0x0010, IntPtr.Zero, IntPtr.Zero); return true; }, IntPtr.Zero);
                }
                Thread.Sleep(10);
            }
        });
        controller.IsBackground = true;
        controller.Start();
        if (mode != "existing" && mode != "dump-existing" && mode != "video-existing" && mode != "video-old-existing")
            while (!File.Exists(Path.Combine(root, "show-now"))) Thread.Sleep(10);
        bool videoMode = mode.StartsWith("video-");
        string title = mode == "assertion" ? "Assert Failed" : mode == "ordinary" ? "Choose production" : videoMode ? "ERROR" : "Microsoft Visual C++ Runtime Library";
        string text = mode == "assertion" ? "Expression: example assertion" : mode == "ordinary" ? "Choose the next building." :
            mode == "video-invalid" ? "A generic ERROR window that must not be classified." :
            mode == "video-old-existing" ? "Failed to allocate video memory. Please try reducing your graphics settings.\nFile: \\Source\\main\\Civilization4\\SDKs\\Gamebryo2_0\\CoreLibs\\NiDX9RenderedTextureData.cpp, Line:170" :
            videoMode ? "Failed to allocate video memory. Please try reducing your graphics settings.\nFile: \\main\\Civilization4\\SDKs\\Gamebryo2_0\\CoreLibs\\NiDX9Renderer\\NiDX9VBManager.cpp, Line:1019" :
            "Runtime Error!\nProgram: disposable test fixture\nThis application has requested the Runtime to terminate it in an unusual way.\nUnicode path sample: caf\u00e9.";
        File.WriteAllText(Path.Combine(root, "show-called"), "ready");
        if (mode.StartsWith("dump-")) ShowDumpDialog(mode == "dump-invalid");
        else MessageBox(IntPtr.Zero, text, title, 0x10);
        while (true) Thread.Sleep(1000);
    }
}

// AI, UI, logging, or other modifications first developed in AdvCiv-SAS (Simple Advanced Strategy)
// (c) 2026 wonderingabout & AI/LLM helpers (see Authors in AdvCiv-SAS's root README.md)
// <!-- custom: Headless Ghidra script run by describe_exe_sites.py. For each "address<TAB>label" line of the input file it writes the containing function, the instructions around the address and the decompiled function, so an agent can read what an EXE patch site does without Ghidra's window. (Claude code Opus 5.5) -->
// @category AdvCiv-SAS
// <!-- custom: Ghidra's script, listing, decompiler and address APIs, plus java.io and java.nio for the input and output files. (Claude code Opus 5.5) -->
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class DescribeAddresses extends GhidraScript {
	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length < 3) {
			throw new IllegalArgumentException("arguments: <input tsv> <output txt> <decompile max chars>");
		}
		List<String> lines = Files.readAllLines(Paths.get(args[0]), StandardCharsets.UTF_8);
		int maxChars = Integer.parseInt(args[2]);
		DecompInterface decompiler = new DecompInterface();
		decompiler.openProgram(currentProgram);
		// <!-- custom: Decompile each function once even when several sites share it. (Claude code Opus 5.5) -->
		Set<Address> decompiled = new HashSet<Address>();
		try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(Paths.get(args[1]), StandardCharsets.UTF_8))) {
			for (String line : lines) {
				if (line.trim().isEmpty() || line.startsWith("#")) {
					continue;
				}
				String[] parts = line.split("\t", 2);
				Address address = toAddr(parts[0].trim());
				String label = parts.length > 1 ? parts[1].trim() : "";
				out.println("=== " + parts[0].trim() + "  " + label);
				Function function = getFunctionContaining(address);
				out.println("function: " + (function == null ? "(none)" : function.getName() + " @ " + function.getEntryPoint() + ", offset +0x" + Long.toHexString(address.subtract(function.getEntryPoint()))));
				Instruction instruction = getInstructionContaining(address);
				if (instruction == null) {
					out.println("(no instruction here: data, or code Ghidra did not disassemble)");
					out.println("bytes: " + hex(getBytes(address, 16)));
				} else {
					for (int i = 0; i < 3 && instruction.getPrevious() != null; i++) {
						instruction = instruction.getPrevious();
					}
					for (int i = 0; i < 10 && instruction != null; i++) {
						String marker = instruction.contains(address) ? ">> " : "   ";
						out.println(marker + instruction.getAddress() + "  " + hex(instruction.getBytes()) + "  " + instruction);
						instruction = instruction.getNext();
					}
				}
				if (function != null && decompiled.add(function.getEntryPoint())) {
					DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
					String code = results.decompileCompleted() ? results.getDecompiledFunction().getC() : "(decompile failed: " + results.getErrorMessage() + ")";
					if (code.length() > maxChars) {
						code = code.substring(0, maxChars) + "\n... (" + (code.length() - maxChars) + " more characters)";
					}
					out.println("--- decompiled " + function.getName());
					out.println(code.trim());
				} else if (function != null) {
					out.println("--- " + function.getName() + " already decompiled above");
				}
				out.println();
			}
		}
		decompiler.dispose();
	}

	private static String hex(byte[] bytes) {
		StringBuilder builder = new StringBuilder();
		for (byte value : bytes) {
			builder.append(String.format("%02x ", value & 0xff));
		}
		return builder.toString().trim();
	}
}

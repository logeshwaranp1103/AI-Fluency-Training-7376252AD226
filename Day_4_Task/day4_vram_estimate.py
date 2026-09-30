"""
Day 4 Task - Open LLM Memory Estimator

Purpose:
Estimate model weights, KV cache, total memory, and whether a model
fits within the available VRAM/RAM budget.

This script follows the same memory assumptions as the supplied
vram_estimate.py sample:
    weights = parameters × bytes-per-parameter
    KV cache ≈ parameters × context(K) × 0.02 GB
    total = (weights + KV cache) × 1.10

Important:
These are estimates for deciding whether a model is likely to fit.
Actual Ollama/runtime memory can differ because of architecture,
runtime defaults, context settings, GPU offload, activations and
other overhead.
"""

import argparse
import platform
import subprocess
import ctypes


# Effective bytes/parameter for common precisions.
# These values are the same assumptions used by the supplied sample.
BYTES_PER_PARAM = {
    "FP16": 2.00,
    "Q8_0": 1.00,
    "Q6_K": 0.81,
    "Q5_K_M": 0.68,
    "Q4_K_M": 0.57,
    "Q3_K_M": 0.43,
}

# Approximate FP16 KV-cache cost for a modern GQA-style model.
# Older architectures can use substantially more.
KV_GB_PER_B_PER_1K = 0.02

# Runtime/activation/fragmentation allowance.
OVERHEAD = 1.10


def get_system_ram_gb():
    """Return total physical system RAM in GB."""
    if platform.system() == "Windows":
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return round(stat.ullTotalPhys / (1024 ** 3), 1)
        except Exception:
            pass

    try:
        pages = __import__("os").sysconf("SC_PHYS_PAGES")
        page_size = __import__("os").sysconf("SC_PAGE_SIZE")
        return round((pages * page_size) / (1024 ** 3), 1)
    except Exception:
        return None


def get_gpu_vram_gb():
    """Return NVIDIA VRAM in GB when nvidia-smi is available."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=memory.total",
                "--format=csv,noheader,nounits",
            ],
            stderr=subprocess.DEVNULL,
        ).decode().strip()

        if out:
            mb = float(out.splitlines()[0])
            return round(mb / 1024, 1)
    except Exception:
        pass

    return None


def estimate(params_b, precision, context_k):
    """
    Return weights, KV cache, and total estimated memory in GB.

    params_b:
        Model parameter count in billions.
    precision:
        One of BYTES_PER_PARAM.
    context_k:
        Context length in thousands of tokens.
    """
    if precision not in BYTES_PER_PARAM:
        raise ValueError(
            f"Unknown precision '{precision}'. "
            f"Choose from: {', '.join(BYTES_PER_PARAM)}"
        )

    weights_gb = params_b * BYTES_PER_PARAM[precision]
    kv_gb = params_b * context_k * KV_GB_PER_B_PER_1K
    total_gb = (weights_gb + kv_gb) * OVERHEAD

    return weights_gb, kv_gb, total_gb


def fit_verdict(total_gb, budget_gb):
    """Return a simple fit verdict."""
    if total_gb <= budget_gb * 0.70:
        return "YES - comfortable"
    if total_gb <= budget_gb:
        return "YES - tight"
    return "NO"


def print_estimate(name, params_b, precision, context_k, budget_gb):
    weights, kv, total = estimate(params_b, precision, context_k)
    verdict = fit_verdict(total, budget_gb)

    print(
        f"{name:<20} "
        f"{params_b:>6.1f}B  "
        f"{precision:<7} "
        f"{context_k:>4}K  "
        f"{weights:>7.2f}  "
        f"{kv:>7.2f}  "
        f"{total:>7.2f}  "
        f"{verdict}"
    )

    return weights, kv, total, verdict


def print_estimate_table(models, budget_gb):
    print("\n" + "=" * 100)
    print("3.2(a) MEMORY ESTIMATE TABLE")
    print("=" * 100)
    print(
        f"{'Model':<20} {'Params':>7} {'Precision':<9} "
        f"{'Context':>8} {'Weights':>9} {'KV':>9} "
        f"{'Total':>9}  Fits in {budget_gb:g} GB?"
    )
    print("-" * 100)

    for item in models:
        print_estimate(*item, budget_gb)


def context_sweep(params_b, precision, contexts, budget_gb):
    print("\n" + "=" * 100)
    print("3.3 CONTEXT-LENGTH OBSERVATION")
    print("=" * 100)
    print(
        f"Fixed model: {params_b}B | Fixed quantization: {precision} | "
        f"Budget: {budget_gb:g} GB"
    )
    print(f"{'Context':>10} {'Weights (GB)':>15} {'KV (GB)':>12} "
          f"{'Total (GB)':>14} {'Fits?':>18}")
    print("-" * 75)

    for context in contexts:
        weights, kv, total = estimate(params_b, precision, context)
        print(
            f"{context:>8}K  "
            f"{weights:>14.2f}  "
            f"{kv:>11.2f}  "
            f"{total:>13.2f}  "
            f"{fit_verdict(total, budget_gb):>18}"
        )


def quantization_sweep(params_b, context_k, precisions, budget_gb):
    print("\n" + "=" * 100)
    print("3.3 QUANTIZATION OBSERVATION")
    print("=" * 100)
    print(
        f"Fixed model: {params_b}B | Fixed context: {context_k}K | "
        f"Budget: {budget_gb:g} GB"
    )
    print(f"{'Quant':>10} {'Weights (GB)':>15} {'KV (GB)':>12} "
          f"{'Total (GB)':>14} {'Fits?':>18}")
    print("-" * 75)

    for precision in precisions:
        weights, kv, total = estimate(params_b, precision, context_k)
        print(
            f"{precision:>10}  "
            f"{weights:>14.2f}  "
            f"{kv:>11.2f}  "
            f"{total:>13.2f}  "
            f"{fit_verdict(total, budget_gb):>18}"
        )


def reality_commands():
    print("\n" + "=" * 100)
    print("3.4 ESTIMATE VS REALITY")
    print("=" * 100)
    print("Run these commands in the same terminal where Ollama is installed:")
    print()
    print("    ollama list")
    print("    ollama ps")
    
def parse_args():
    parser = argparse.ArgumentParser(
        description="Day 4 open-LLM memory estimator"
    )

    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Available memory budget in GB. Example: --budget 5.4",
    )
    parser.add_argument(
        "--params",
        type=float,
        default=8.0,
        help="Model size in billions of parameters. Default: 8",
    )
    parser.add_argument(
        "--precision",
        default="Q4_K_M",
        choices=BYTES_PER_PARAM,
        help="Quantization/precision. Default: Q4_K_M",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=8,
        help="Context length in K tokens. Default: 8K",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    ram = get_system_ram_gb()
    vram = get_gpu_vram_gb()

    # For a discrete GPU, leave roughly 10% for driver/runtime overhead.
    # If no GPU is detected, use 70% of system RAM as a conservative CPU budget.
    if args.budget is not None:
        budget = args.budget
        budget_source = "user supplied"
    elif vram is not None:
        budget = round(vram * 0.90, 1)
        budget_source = "90% of detected GPU VRAM"
    elif ram is not None:
        budget = round(ram * 0.70, 1)
        budget_source = "70% of detected system RAM"
    else:
        budget = 8.0
        budget_source = "fallback"

    print("=" * 100)
    print("DAY 4 - OPEN LLM MEMORY ESTIMATOR")
    print("=" * 100)
    print(f"OS:             {platform.system()} {platform.release()}")
    print(f"System RAM:     {ram if ram is not None else 'unknown'} GB")
    print(f"GPU VRAM:       {vram if vram is not None else 'not detected'} GB")
    print(f"Memory budget:  {budget} GB ({budget_source})")
    print()
    print("Formula:")
    print("  weights = parameters × bytes/parameter")
    print("  KV cache ≈ parameters × context(K) × 0.02 GB")
    print("  total ≈ (weights + KV cache) × 1.10")
    print()
    print("NOTE: This is an estimate, not a prediction of exact runtime memory.")

    # Four configurations required by the task.
    models = [
        ("Qwen 1.5B Q4", 1.5, "Q4_K_M", 8),
        ("Qwen 8B Q4", 8.0, "Q4_K_M", 8),
        ("Qwen 8B Q5", 8.0, "Q5_K_M", 8),
        ("Qwen 8B Q8", 8.0, "Q8_0", 8),
        ("Qwen 8B FP16", 8.0, "FP16", 8),
    ]

    print_estimate_table(models, budget)

    # Dedicated observation model: 8B.
    context_sweep(
        params_b=8.0,
        precision="Q4_K_M",
        contexts=[2, 4, 8, 16, 32, 64, 128],
        budget_gb=budget,
    )

    quantization_sweep(
        params_b=8.0,
        context_k=8,
        precisions=["Q3_K_M", "Q4_K_M", "Q5_K_M", "Q6_K", "Q8_0", "FP16"],
        budget_gb=budget,
    )

    # Show one direct command-line configuration.
    print("\n" + "=" * 100)
    print("CUSTOM CONFIGURATION")
    print("=" * 100)
    print_estimate(
        "Selected model",
        args.params,
        args.precision,
        args.context,
        budget,
    )

    reality_commands()



if __name__ == "__main__":
    main()

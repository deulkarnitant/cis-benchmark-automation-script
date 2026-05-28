#!/usr/bin/env python3
"""
Script 3: Execute CIS Audit Commands and Check System Compliance
(Clean output: Control ID + Title + Status + Recommendation)
"""

import subprocess
import json


# ✅ Run command safely
def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return (result.stdout + result.stderr).strip()

    except Exception:
        return ""


# ✅ CONFIGURED / NOT CONFIGURED LOGIC
def evaluate(control_id, title, command, output):
    title = title.lower()

    # Kernel module checks
    if "kernel module is not available" in title:
        if "lsmod" in command:
            return "CONFIGURED" if output == "" else "NOT CONFIGURED"

        if "modprobe" in command:
            if "install" in output or "blacklist" in output:
                return "CONFIGURED"
            else:
                return "NOT CONFIGURED"

    # sysctl checks
    if "sysctl" in command:
        return "CONFIGURED" if "= 0" in output else "NOT CONFIGURED"

    # Default fallback
    return "CONFIGURED" if output == "" else "NOT CONFIGURED"


# ✅ MAIN EXECUTION
def main():
    print("📂 Loading audit_commands.json...\n")

    with open("audit_commands.json") as f:
        controls = json.load(f)

    results = []

    print("🚀 Running audit checks...\n")

    for control_id, data in controls.items():
        title = data["title"]
        commands = data["commands"]

        print(f"🔹 {control_id}: {title}")

        final_status = "CONFIGURED"

        for cmd in commands:
            output = run_command(cmd)
            status = evaluate(control_id, title, cmd, output)

            # If ANY command fails → NOT CONFIGURED
            if status == "NOT CONFIGURED":
                final_status = "NOT CONFIGURED"

        # ✅ ADD RECOMMENDATION (NEW)
        if final_status == "CONFIGURED":
            recommendation = "Maintain current setting"
        else:
            recommendation = "Implement configuration as per CIS benchmark"

        print(f"   Status: {final_status}")
        print(f"   Recommendation: {recommendation}\n")

        results.append({
            "Control_ID": control_id,
            "Title": title,
            "Status": final_status,
            "Recommendation": recommendation
        })

    # ✅ Save JSON report
    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=4)

    print("✅ Audit complete!")
    print("📁 Results saved to audit_results.json")


# ✅ Entry point
if __name__ == "__main__":
    main()

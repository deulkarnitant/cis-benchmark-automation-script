#!/usr/bin/env python3
"""
Script 2: Extract Audit Commands from CIS PDF
"""

import fitz   # PyMuPDF
import re
import json


# ✅ Step 1: Extract PDF text
def read_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


# ✅ Step 2: Split into control sections
def extract_sections(text):
    pattern = r'(\d+(?:\.\d+)+)\s+([^\n]+)(.*?)(?=\n\d+(?:\.\d+)+|\Z)'
    return re.finditer(pattern, text, re.DOTALL)


# ✅ Step 3: Extract audit block
def extract_audit_block(section):
    match = re.search(
        r'Audit:?\s*(?:\n|\r\n)(.*?)(?=\n\s*(?:Remediation|Impact|Default|Rationale|$))',
        section,
        re.DOTALL | re.IGNORECASE
    )
    return match.group(1).strip() if match else None


# ✅ Step 4: Extract command lines
def extract_commands(audit_text):
    if not audit_text:
        return []

    # Fix multiline commands
    audit_text = audit_text.replace("\\\n", " ")

    commands = []

    for line in audit_text.split("\n"):
        line = line.strip()

        if not line:
            continue

        line_lower = line.lower()

        # REMOVE SCRIPT STRUCTURE (VERY IMPORTANT)
        if any(line_lower.startswith(word) for word in [
            "if ", "while ", "for ", "then", "fi", "do", "done", "else"
        ]):
            continue

        # REMOVE shell boilerplate
        if any(word in line_lower for word in [
            "/usr/bin/env", "bash", "echo", "readlink", "exit"
        ]):
            continue

        # REMOVE REMEDIATION (dangerous commands)
        if any(word in line_lower for word in [
            "install ", "apt ", "yum ", "dnf ", "chmod", "chown"
        ]):
            continue

        # REMOVE description text
        if any(word in line_lower for word in [
            "verify", "ensure", "example", "note",
            "output", "internal", "page", "recommended"
        ]):
            continue

        # KEEP ONLY AUDIT (read/check commands)
        if re.search(r'\b(lsmod|grep|awk|sed|find|cat|sysctl|systemctl|ss|netstat|iptables)\b', line):
            line = re.sub(r'^[\$#]\s*', '', line)

            commands.append(line)

    # Remove duplicates
    commands = list(set(commands))

    return commands


# ✅ Step 5: Combine everything
def extract_audit_commands(text):
    results = {}

    for match in extract_sections(text):
        control_id = match.group(1)
        title = match.group(2).strip()
        section = match.group(3)

        audit_text = extract_audit_block(section)
        cmds = extract_commands(audit_text)

        # Only store if commands found
        if cmds:
            results[control_id] = {
                "title": title,
                "commands": cmds
            }

    return results


# ✅ Main execution
def main(pdf):
    print("📄 Reading PDF...")
    text = read_pdf(pdf)

    print("🔍 Extracting audit commands...")
    data = extract_audit_commands(text)

    # Save output
    with open("audit_commands.json", "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Done!")
    print("📁 Output saved: audit_commands.json")


# ✅ Run script
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 extract_audit_commands.py <cis_pdf>")
        exit(1)

    main(sys.argv[1])


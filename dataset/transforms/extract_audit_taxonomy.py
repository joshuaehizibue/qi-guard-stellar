#!/usr/bin/env python3
"""
Extracts structured vulnerability records and code samples from Soroban Security Portal audit reports.
"""

import os
import re
import json
import urllib.request
from typing import Dict, Any, List


AUDIT_SOURCES = [
    {
        "source_name": "Trustless Work – Runtime Verification",
        "url": "https://raw.githubusercontent.com/Inferara/soroban-security-portal/main/docs/audits/trustless-work-runtime-verification.md",
        "auditor": "Runtime Verification",
        "protocol": "Trustless Work Smart Escrow",
        "repo": "https://github.com/Trustless-Work/Trustless-Work-Smart-Escrow",
    }
]


def fetch_or_read_source(source: Dict[str, Any], raw_dir: str) -> str:
    """Fetches raw markdown content from URL or uses local cache."""
    filename = source["source_name"].lower().replace(" ", "_").replace("–", "-") + ".md"
    local_path = os.path.join(raw_dir, filename)

    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        with open(local_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fetch from remote
    try:
        req = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "QIGuard-Dataset-Builder/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)
        return content
    except Exception as e:
        print(f"Warning: Failed to fetch {source['url']}: {e}")
        return ""


def categorize_finding(title: str, body: str) -> str:
    """Maps finding title and description to standardized Soroban security taxonomy."""
    text = (title + " " + body).lower()
    if any(k in text for k in ["arbitrary", "redirect", "unrestricted caller", "require_auth", "access-restricted", "auth"]):
        return "ACCESS_CONTROL_OR_AUTH"
    elif any(k in text for k in ["fee", "bps", "100%", "basis_points", "relative amount"]):
        return "FEE_ARITHMETIC_OVERFLOW"
    elif any(k in text for k in ["initialization", "initialize_escrow", "pre-approved", "bypass", "update_escrow"]):
        return "INITIALIZATION_OR_STATE_BYPASS"
    elif any(k in text for k in ["front-running", "front run", "race condition", "malicious platform"]):
        return "FRONT_RUNNING_RACE"
    elif any(k in text for k in ["i128", "signed integer", "sign check", "negative", "overflow", "u16", "u32"]):
        return "INTEGER_SIGNEDNESS_UNDERFLOW"
    elif any(k in text for k in ["disapprove", "griefing", "stall"]):
        return "GRIEFING_STATE_REVERSION"
    elif any(k in text for k in ["locked", "permanently locked", "multi-release", "double release", "dispute-resolved"]):
        return "ASSET_LOCK_INVARIANT_VIOLATION"
    elif any(k in text for k in ["gas", "optimization", "redundant", "clone"]):
        return "RESOURCE_OR_GAS_OPTIMIZATION"
    return "LOGIC_VALIDATION_ERROR"


def parse_audit_markdown(content: str, source_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts structured vulnerability objects from audit markdown."""
    findings = []
    
    # Split findings by ### Header
    sections = re.split(r'\n###\s+', content)
    finding_idx = 1

    for sec in sections[1:]:  # Skip introductory text before first ###
        lines = sec.strip().split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:])

        # Extract Severity
        sev_match = re.search(r'Severity:\s*(\w+)', body, re.IGNORECASE)
        severity = sev_match.group(1).upper() if sev_match else "MEDIUM"

        # Extract Difficulty
        diff_match = re.search(r'Difficulty:\s*(\w+)', body, re.IGNORECASE)
        difficulty = diff_match.group(1).capitalize() if diff_match else "Medium"

        # Extract Action
        act_match = re.search(r'Recommended Action:\s*(.+)', body, re.IGNORECASE)
        action = act_match.group(1).strip() if act_match else "Fix Code"

        # Extract Status
        status_match = re.search(r'Status:\s*(.+)', body, re.IGNORECASE)
        status = status_match.group(1).strip() if status_match else "Addressed"

        # Extract Code Blocks
        code_blocks = re.findall(r'```rust\s*(.*?)\s*```', body, re.DOTALL)
        sample_code = code_blocks[0].strip() if code_blocks else ""

        # Extract Commit references
        commits = re.findall(r'commit\s*(?:ID|IDs)?\s*\[?`?([0-9a-f]{7,40})`?\]?', body, re.IGNORECASE)
        commit_urls = re.findall(r'https://github\.com/[^\s\)]+/commit/[0-9a-f]{7,40}', body)

        # Categorize
        category = categorize_finding(title, body)

        finding_id = f"SSP-{finding_idx:03d}"
        finding_idx += 1

        findings.append({
            "id": finding_id,
            "title": title,
            "category": category,
            "severity": severity,
            "difficulty": difficulty,
            "action": action,
            "status": status,
            "protocol": source_meta["protocol"],
            "auditor": source_meta["auditor"],
            "repository": source_meta["repo"],
            "commits": list(set(commits)),
            "commit_urls": list(set(commit_urls)),
            "code_snippet": sample_code,
            "description": body[:400].strip().replace("\n", " "),
            "is_vulnerable": severity in ["HIGH", "MEDIUM", "CRITICAL"]
        })

    return findings


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(root_dir, "raw")
    parsed_dir = os.path.join(root_dir, "parsed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(parsed_dir, exist_ok=True)

    all_findings = []
    for source in AUDIT_SOURCES:
        print(f"[Ingesting] {source['source_name']}...")
        content = fetch_or_read_source(source, raw_dir)
        if content:
            findings = parse_audit_markdown(content, source)
            all_findings.extend(findings)
            print(f"  Extracted {len(findings)} structured vulnerability records.")

    out_file = os.path.join(parsed_dir, "vulnerabilities.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_findings, f, indent=2)

    print(f"\n[Saved] {len(all_findings)} parsed vulnerability records to:\n  {out_file}")


if __name__ == "__main__":
    main()

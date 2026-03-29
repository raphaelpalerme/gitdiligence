"""Security signal analysis tool.

Simple heuristics based on file presence/absence.
Not a vulnerability scanner — just quick indicators.
"""

import json

from gitdiligence.tools.base import Tool


GOOD_SIGNALS = {
    "SECURITY.md": "Security policy documented",
    ".github/dependabot.yml": "Automated dependency updates",
    "Dockerfile": "Containerization (reproducibility)",
    ".github/workflows": "CI/CD in place",
    "LICENSE": "License defined",
}

BAD_SIGNALS = {
    ".env": "Committed .env file (potentially exposed secrets)",
    "id_rsa": "SSH private key in the repo",
    ".npmrc": "npm config potentially containing tokens",
}


class CheckSecurity(Tool):
    """Analyze a repo's file list for security signals."""

    name = "check_security"
    description = "Analyze a repo's file tree for security signals"
    parameters = {
        "type": "object",
        "properties": {
            "file_tree": {
                "type": "string",
                "description": "List of files in the repo (one per line)",
            },
        },
        "required": ["file_tree"],
    }

    def execute(self, **kwargs) -> str:
        file_tree = kwargs["file_tree"]
        files = set(file_tree.split("\n"))

        present = []
        missing = []
        warnings = []

        for pattern, description in GOOD_SIGNALS.items():
            if any(pattern in f for f in files):
                present.append({"file": pattern, "signal": description})
            else:
                missing.append({"file": pattern, "signal": description})

        for pattern, description in BAD_SIGNALS.items():
            if any(f.endswith(pattern) for f in files):
                warnings.append({"file": pattern, "signal": description})

        return json.dumps(
            {"present": present, "missing": missing, "warnings": warnings},
            indent=2,
        )

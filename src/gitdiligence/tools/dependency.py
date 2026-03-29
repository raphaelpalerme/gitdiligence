"""Dependency analysis tool.

Parses common dependency files (pyproject.toml, package.json,
requirements.txt) and returns a structured list.
"""

import json
import re

from gitdiligence.tools.base import Tool


def parse_requirements_txt(content: str) -> list[dict]:
    """Parse a requirements.txt file."""
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Split package name from version (e.g. "flask>=2.0")
        match = re.match(r"^([a-zA-Z0-9_-]+)\s*([><=!~]+.+)?$", line)
        if match:
            deps.append({"name": match.group(1), "version": match.group(2) or "unspecified"})
    return deps


def parse_pyproject_toml(content: str) -> list[dict]:
    """Parse dependencies from a pyproject.toml (dependencies section)."""
    deps = []
    in_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_deps = True
            continue
        if in_deps:
            if stripped == "]":
                break
            # Extract "flask>=2.0" from '    "flask>=2.0",'
            match = re.match(r'^\s*"([a-zA-Z0-9_-]+)\s*([><=!~]+[^"]*)?",?$', stripped)
            if match:
                deps.append({"name": match.group(1), "version": match.group(2) or "unspecified"})
    return deps


def parse_package_json(content: str) -> list[dict]:
    """Parse dependencies from a package.json."""
    data = json.loads(content)
    deps = []
    for section in ["dependencies", "devDependencies"]:
        for name, version in data.get(section, {}).items():
            deps.append({"name": name, "version": version})
    return deps


# Map filename to its parser
PARSERS = {
    "requirements.txt": parse_requirements_txt,
    "pyproject.toml": parse_pyproject_toml,
    "package.json": parse_package_json,
}


class AnalyzeDependencies(Tool):
    """Analyze a dependency file and return a structured list of packages."""

    name = "analyze_dependencies"
    description = "Analyze a dependency file and return a structured list of packages"
    parameters = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "File name (requirements.txt, pyproject.toml, package.json)",
            },
            "content": {
                "type": "string",
                "description": "Raw file content",
            },
        },
        "required": ["filename", "content"],
    }

    def execute(self, **kwargs) -> str:
        filename = kwargs["filename"]
        content = kwargs["content"]

        parser = PARSERS.get(filename)
        if not parser:
            return json.dumps({"error": f"Unsupported format: {filename}"})

        deps = parser(content)
        return json.dumps({"filename": filename, "count": len(deps), "dependencies": deps}, indent=2)

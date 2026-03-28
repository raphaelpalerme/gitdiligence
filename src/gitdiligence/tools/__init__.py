"""Enregistrement de tous les outils dans le registre.

Importer ce module suffit pour que tous les outils soient disponibles.
"""

from gitdiligence.tools import registry
from gitdiligence.tools.github_contents import GetRepoInfo, GetFileTree, GetFileContent
from gitdiligence.tools.search import SearchCode
from gitdiligence.tools.dependency import AnalyzeDependencies
from gitdiligence.tools.security import CheckSecurity

registry.register(GetRepoInfo())
registry.register(GetFileTree())
registry.register(GetFileContent())
registry.register(SearchCode())
registry.register(AnalyzeDependencies())
registry.register(CheckSecurity())

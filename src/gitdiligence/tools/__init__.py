"""Tool registration. Importing this module registers all tools."""

from gitdiligence.tools import registry
from gitdiligence.tools.github_contents import GetRepoInfo, GetFileTree, GetFileContent
from gitdiligence.tools.search import SearchCode
from gitdiligence.tools.github_stats import GetContributors, GetCommitActivity, GetLanguages
from gitdiligence.tools.dependency import AnalyzeDependencies
from gitdiligence.tools.security import CheckSecurity

registry.register(GetRepoInfo())
registry.register(GetFileTree())
registry.register(GetFileContent())
registry.register(SearchCode())
registry.register(GetContributors())
registry.register(GetCommitActivity())
registry.register(GetLanguages())
registry.register(AnalyzeDependencies())
registry.register(CheckSecurity())

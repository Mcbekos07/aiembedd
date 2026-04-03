"""Domain enums for projects and sources."""

from enum import StrEnum


class ProjectSourceType(StrEnum):
    NEW = "new"
    LOCAL_IMPORT = "local_import"
    GIT_CLONE = "git_clone"


class BuildSystem(StrEnum):
    CMAKE = "cmake"
    PLATFORMIO = "platformio"
    MAKE = "make"
    CUSTOM = "custom"

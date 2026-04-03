"""Dependency policy constants shared by dependency services."""

from app.core.extension_points import DEPENDENCY_INSTALLER_KEYS

SAFE_INSTALL_PACKAGES = set(DEPENDENCY_INSTALLER_KEYS)
CHECKABLE_BINARIES = ['cmake', 'make', 'openocd', 'avrdude', 'esptool.py', 'python3']

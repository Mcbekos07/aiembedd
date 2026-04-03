"""Stable extension-point keys used across registries and policies."""

TOOLCHAIN_ADAPTER_KEYS = (
    'stm32',
    'avr',
    'esp32',
    'rp2040',
    'mcs-51',
    'micropython',
    'verilog',
    'custom',
)

FLASHER_KEYS = (
    'stlink',
    'esptool',
    'avrdude',
    'openocd',
    'custom',
)

AI_PROVIDER_KEYS = (
    'openai',
    'anthropic',
    'deepseek',
    'generic',
)

DEPENDENCY_INSTALLER_KEYS = (
    'cmake',
    'make',
    'openocd',
    'avrdude',
)

DEVICE_SCANNER_KEYS = (
    'usb_scan',
    'usb_parser',
    'port_resolver',
)

PROMPT_TEMPLATE_KEYS = (
    'embedded_safe_default',
    'build_failure_analysis',
)

PROJECT_TEMPLATE_KEYS = (
    'blank',
    'cmake_embedded',
)

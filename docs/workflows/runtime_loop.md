# Runtime Flash-Observe Loop

## Flow
1. Pre-agent checkpoint.
2. Build and artifact validation.
3. Choose default/bound device.
4. Flash with policy checks.
5. Start monitor session, collect runtime logs.
6. Extract runtime event categories and summarize runtime state.
7. If issue detected -> diagnosis -> patch -> rebuild -> repeat.

## Runtime event categories
- boot_failure
- serial_timeout
- repeated_crash
- assert_panic
- init_error
- no_expected_output

## Result states
- runtime_ok (success)
- flash_failed / flash_policy_blocked
- artifact_missing
- runtime_patch_unavailable
- max_iterations_reached

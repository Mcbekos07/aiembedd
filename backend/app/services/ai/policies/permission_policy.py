class PermissionPolicy:
    MODES = {'read_only', 'suggest_only', 'apply_patch_confirm', 'build_confirm', 'flash_confirm', 'install_deps_confirm'}

    def is_allowed(self, mode: str, action: str) -> bool:
        if mode == 'read_only':
            return action in {'chat', 'review_diff', 'explain_error'}
        return mode in self.MODES

class ConfirmationPolicy:
    CONFIRM_REQUIRED = {'generate_patch', 'build', 'flash', 'install_deps'}

    def requires_confirmation(self, action: str) -> bool:
        return action in self.CONFIRM_REQUIRED

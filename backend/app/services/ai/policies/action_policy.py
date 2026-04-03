"""AI action policy with explicit capability boundaries."""


class ActionPolicy:
    ALLOWED_ACTIONS = {
        'read': {'review_diff', 'explain_build_error'},
        'suggest': {'suggest_code', 'create_version_message', 'dependency_install_plan'},
        'apply': {'generate_patch'},
        'build': set(),
        'flash': set(),
        'install': {'dependency_install_plan'},
        'delete': set(),
    }

    def validate(self, action: str) -> bool:
        return action in self.flattened_actions

    @property
    def flattened_actions(self) -> set[str]:
        actions: set[str] = set()
        for names in self.ALLOWED_ACTIONS.values():
            actions.update(names)
        return actions

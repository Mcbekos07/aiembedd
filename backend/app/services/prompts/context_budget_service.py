from __future__ import annotations


class TokenBudgetManager:
    MODE_BUDGETS = {
        'quick_diagnosis': {'global_max': 3200, 'reserved_output': 700, 'reserved_system': 350, 'reserved_tool': 250},
        'deep_build_fix': {'global_max': 6800, 'reserved_output': 1200, 'reserved_system': 500, 'reserved_tool': 400},
        'runtime_analysis': {'global_max': 5200, 'reserved_output': 1000, 'reserved_system': 420, 'reserved_tool': 320},
        'refactor_task': {'global_max': 7600, 'reserved_output': 1400, 'reserved_system': 550, 'reserved_tool': 450},
        'architecture_task': {'global_max': 8200, 'reserved_output': 1500, 'reserved_system': 600, 'reserved_tool': 500},
    }

    def resolve(self, mode: str) -> dict[str, int]:
        cfg = self.MODE_BUDGETS.get(mode, self.MODE_BUDGETS['quick_diagnosis'])
        available = cfg['global_max'] - cfg['reserved_output'] - cfg['reserved_system'] - cfg['reserved_tool']
        return {
            'mode': mode,
            'global_max_context': cfg['global_max'],
            'reserved_output_budget': cfg['reserved_output'],
            'reserved_system_prompt_budget': cfg['reserved_system'],
            'reserved_tool_action_budget': cfg['reserved_tool'],
            'available_retrieval_budget': max(0, available),
        }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)


class ContextBudgetService:
    def trim(self, chunks: list[str], max_chars: int = 6000) -> str:
        result: list[str] = []
        used = 0
        for chunk in chunks:
            if used >= max_chars:
                break
            part = chunk[: max_chars - used]
            result.append(part)
            used += len(part)
        return '\n'.join(result)

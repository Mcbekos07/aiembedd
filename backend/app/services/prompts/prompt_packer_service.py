from __future__ import annotations

from app.services.prompts.context_budget_service import TokenBudgetManager


class PromptPackerService:
    PRIORITY_ORDER = ['task_instruction', 'critical_log', 'code_fragment', 'active_memory', 'warm_memory', 'git_history']

    def __init__(self) -> None:
        self.budget = TokenBudgetManager()

    def pack(self, *, mode: str, system_prompt: str, task_text: str, fragments: list[dict[str, object]]) -> dict[str, object]:
        budget = self.budget.resolve(mode)
        available = int(budget['available_retrieval_budget'])

        included: list[dict[str, object]] = []
        dropped: list[dict[str, object]] = []
        sections: dict[str, list[dict[str, object]]] = {k: [] for k in self.PRIORITY_ORDER}

        normalized = sorted(
            [self._normalize_fragment(x) for x in fragments],
            key=lambda x: (self._category_priority(x['category']), -float(x.get('rank', 0))),
        )

        for frag in normalized:
            if available <= 0:
                dropped.append(self._drop(frag, 'budget_exhausted'))
                continue

            compressed_text, compression_note = self._compress_fragment(frag)
            tokens = self.budget.estimate_tokens(compressed_text)

            if tokens > available:
                truncated = self._truncate_to_budget(compressed_text, available)
                trunc_tokens = self.budget.estimate_tokens(truncated)
                if trunc_tokens <= 0:
                    dropped.append(self._drop(frag, 'insufficient_budget'))
                    continue
                frag_obj = {
                    'id': frag['id'],
                    'category': frag['category'],
                    'title': frag['title'],
                    'path': frag.get('path') or '',
                    'content': truncated,
                    'tokens': trunc_tokens,
                    'compression': (compression_note + ';truncated').strip(';'),
                }
                included.append(frag_obj)
                sections[frag['category']].append(frag_obj)
                available -= trunc_tokens
                continue

            frag_obj = {
                'id': frag['id'],
                'category': frag['category'],
                'title': frag['title'],
                'path': frag.get('path') or '',
                'content': compressed_text,
                'tokens': tokens,
                'compression': compression_note,
            }
            included.append(frag_obj)
            sections[frag['category']].append(frag_obj)
            available -= tokens

        context_blocks: list[str] = [f"[SYSTEM]\n{system_prompt}", f"[TASK]\n{task_text}"]
        for category in self.PRIORITY_ORDER:
            items = sections.get(category, [])
            if not items:
                continue
            context_blocks.append(f'[{category.upper()}]')
            for item in items:
                header = f"- {item['title']}"
                if item.get('path'):
                    header += f" ({item['path']})"
                context_blocks.append(header)
                context_blocks.append(str(item['content']))

        payload = {
            'mode': mode,
            'token_budget': budget,
            'included_fragments': included,
            'dropped_fragments': dropped,
            'budget_debug': {
                'used_retrieval_tokens': int(budget['available_retrieval_budget']) - available,
                'remaining_retrieval_tokens': available,
                'total_included': len(included),
                'total_dropped': len(dropped),
            },
            'final_context_payload': {
                'system_prompt': system_prompt,
                'task': task_text,
                'sections': sections,
                'prompt_text': '\n'.join(context_blocks),
            },
        }
        return payload

    def _normalize_fragment(self, frag: dict[str, object]) -> dict[str, object]:
        category = str(frag.get('category') or 'warm_memory')
        if category not in self.PRIORITY_ORDER:
            category = 'warm_memory'
        return {
            'id': str(frag.get('id') or frag.get('title') or 'fragment'),
            'category': category,
            'title': str(frag.get('title') or 'fragment'),
            'path': str(frag.get('path') or ''),
            'content': str(frag.get('content') or ''),
            'rank': float(frag.get('rank') or 0.0),
        }

    def _compress_fragment(self, frag: dict[str, object]) -> tuple[str, str]:
        text = str(frag['content'])
        category = str(frag['category'])

        if category == 'git_history' and len(text) > 900:
            return text[:900], 'history_summary_trim'
        if category == 'code_fragment' and len(text) > 1400:
            return text[:1400], 'code_snippet_trim_keep_path'
        if category == 'warm_memory' and len(text) > 700:
            return text[:700], 'warm_memory_compact'
        if category == 'critical_log' and len(text) > 1200:
            return text[:1200], 'critical_log_compact'
        return text, ''

    def _truncate_to_budget(self, text: str, available_tokens: int) -> str:
        if available_tokens <= 0:
            return ''
        approx_chars = max(0, available_tokens * 4)
        return text[:approx_chars]

    def _category_priority(self, category: str) -> int:
        try:
            return self.PRIORITY_ORDER.index(category)
        except ValueError:
            return len(self.PRIORITY_ORDER)

    @staticmethod
    def _drop(frag: dict[str, object], reason: str) -> dict[str, object]:
        return {
            'id': frag['id'],
            'category': frag['category'],
            'title': frag['title'],
            'path': frag.get('path') or '',
            'reason': reason,
        }

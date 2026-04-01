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

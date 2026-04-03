class TokenBudgetPolicy:
    def limit_chars(self, text: str, max_chars: int = 6000) -> str:
        return text[:max_chars]

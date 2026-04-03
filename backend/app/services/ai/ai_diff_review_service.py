class AIDiffReviewService:
    def review(self, diff: str) -> str:
        return f'Ревью diff:\n{diff[:400]}'

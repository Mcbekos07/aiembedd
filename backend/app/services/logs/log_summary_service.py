from collections import Counter


class LogSummaryService:
    def summarize(self, lines: list[str]) -> str:
        repeated = Counter(line.strip() for line in lines if 'warning' in line.lower())
        repeated_lines = [f'{line} (x{count})' for line, count in repeated.items() if count > 1]
        return '\n'.join(repeated_lines[:20])

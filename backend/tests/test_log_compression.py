from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService


RAW = """
src/main.c:12:5: error: undefined reference to foo
src/main.c:12:5: error: undefined reference to foo
warning: variable x set but not used
warning: variable x set but not used
openocd: error: no device found
boot failed: timeout waiting serial
panic: assert failed
""".strip()


def test_important_log_deduplicate_and_tail() -> None:
    service = ImportantLogService()
    events = service.extract_events(RAW)
    assert events
    dedup = service.deduplicate_lines(RAW)
    assert any('repeated' in line for line in dedup)
    tail = service.last_meaningful_lines_before_failure(RAW, events)
    assert tail


def test_compress_ai_ready_context() -> None:
    extractor = ImportantLogService()
    events = extractor.extract_events(RAW)
    compressed = LogSummaryService().compress(RAW, events)
    assert 'compressed_ai_context' in compressed
    assert 'root_cause_summary' in compressed
    assert compressed['links']['pipeline_stages']
    assert 'hint:' in compressed['compressed_ai_context']

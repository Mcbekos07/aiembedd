from pathlib import Path

from app.services.files.file_service import FileService


def test_file_service_tree_and_save(tmp_path: Path) -> None:
    service = FileService()
    service.save(str(tmp_path), 'src/main.c', 'int main(){}')
    items = service.tree(str(tmp_path))
    assert any(item['path'] == 'src/main.c' for item in items)

"""Safe file operations scoped to project root."""

from pathlib import Path
import shutil

from app.utils.path import safe_child_path


class FileService:
    def _safe(self, base_path: str, rel_path: str) -> Path:
        rel = rel_path.strip()
        if not rel:
            raise ValueError('Path is required')
        return safe_child_path(base_path, rel)

    def tree(self, base_path: str) -> list[dict[str, str]]:
        root = Path(base_path).resolve()
        items: list[dict[str, str]] = []
        for path in sorted(root.rglob('*')):
            rel = str(path.relative_to(root))
            if '.git' in rel.split('/'):
                continue
            items.append({'path': rel, 'type': 'dir' if path.is_dir() else 'file'})
        return items

    def read(self, base_path: str, rel_path: str) -> str:
        target = self._safe(base_path, rel_path)
        return target.read_text(encoding='utf-8')

    def save(self, base_path: str, rel_path: str, content: str) -> None:
        target = self._safe(base_path, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def rename(self, base_path: str, old_path: str, new_path: str) -> None:
        source = self._safe(base_path, old_path)
        dest = self._safe(base_path, new_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        source.rename(dest)

    def delete(self, base_path: str, rel_path: str) -> None:
        target = self._safe(base_path, rel_path)
        root = Path(base_path).resolve()
        if target == root:
            raise ValueError('Удаление корня проекта запрещено')
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink(missing_ok=True)

    def create(self, base_path: str, rel_path: str, kind: str) -> None:
        target = self._safe(base_path, rel_path)
        if kind == 'folder':
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch(exist_ok=True)

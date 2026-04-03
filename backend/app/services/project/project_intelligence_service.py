"""Project intelligence service: pragmatic code-map and persisted knowledge snapshot."""

from pathlib import Path
import re

from app.db.models.project import Project
from app.db.models.project_knowledge_snapshot import ProjectKnowledgeSnapshot


class ProjectIntelligenceService:
    BUILD_FILE_NAMES = {'cmakelists.txt', 'platformio.ini', 'makefile', 'pyproject.toml', 'package.json'}
    CONFIG_FILE_SUFFIXES = {'.yaml', '.yml', '.toml', '.ini', '.json', '.cfg', '.conf'}
    DOC_SUFFIXES = {'.md', '.rst', '.txt'}
    SOURCE_SUFFIXES = {'.c', '.cpp', '.cc', '.cxx', '.py', '.ts', '.js', '.vue'}
    HEADER_SUFFIXES = {'.h', '.hpp', '.hh'}
    SCRIPT_SUFFIXES = {'.sh'}
    ENTRY_CANDIDATES = {'main.c', 'main.cpp', 'main.cc', 'main.py', 'src/main.c', 'src/main.cpp', 'src/main.py'}

    def __init__(self, db: object) -> None:
        self.db = db

    def get_or_refresh(self, project: Project, refresh: bool = False) -> ProjectKnowledgeSnapshot:
        row = self.db.query(ProjectKnowledgeSnapshot).filter(ProjectKnowledgeSnapshot.project_id == project.id).first()
        if row and not refresh:
            return row

        data = self._scan_project(Path(project.path))
        if not row:
            row = ProjectKnowledgeSnapshot(project_id=project.id)
            self.db.add(row)

        row.summary = data['summary']
        row.architectural_notes = data['architectural_notes']
        row.important_files = data['important_files']
        row.risky_files = data['risky_files']
        row.known_build_paths = data['known_build_paths']
        row.entry_points = data['entry_points']
        row.dependency_map = data['dependency_map']
        row.file_classification = data['file_classification']
        self.db.commit()
        self.db.refresh(row)
        return row

    def _scan_project(self, root: Path) -> dict[str, object]:
        files = [p for p in sorted(root.rglob('*')) if p.is_file() and '.git' not in p.parts]
        rel_files = [str(p.relative_to(root)) for p in files]

        classification = {rel: self._classify(rel) for rel in rel_files}
        entry_points = [f for f in rel_files if f.lower() in self.ENTRY_CANDIDATES]
        build_paths = [f for f in rel_files if classification[f] == 'build']
        important = sorted(set(entry_points + build_paths + [f for f in rel_files if classification[f] == 'config']))[:50]
        risky = sorted(set(entry_points + build_paths + [f for f in rel_files if '/scripts/' in f or f.startswith('scripts/')]))[:50]

        dep_map: dict[str, list[str]] = {}
        for p in files[:400]:
            rel = str(p.relative_to(root))
            if classification.get(rel) not in {'source', 'headers'}:
                continue
            deps = self._extract_deps(p)
            if deps:
                dep_map[rel] = deps[:30]

        summary = f'Indexed {len(rel_files)} files; {len(entry_points)} entry points; {len(build_paths)} build-related files.'
        notes = 'Pragmatic static scan: filename/extension heuristics + lightweight include/import extraction.'

        return {
            'summary': summary,
            'architectural_notes': notes,
            'important_files': important,
            'risky_files': risky,
            'known_build_paths': build_paths,
            'entry_points': entry_points,
            'dependency_map': dep_map,
            'file_classification': classification,
        }

    def _classify(self, rel_path: str) -> str:
        low = rel_path.lower()
        name = Path(low).name
        suffix = Path(low).suffix

        if low in self.ENTRY_CANDIDATES:
            return 'main/entry'
        if name in self.BUILD_FILE_NAMES:
            return 'build'
        if suffix in self.CONFIG_FILE_SUFFIXES:
            return 'config'
        if suffix in self.HEADER_SUFFIXES:
            return 'headers'
        if suffix in self.SOURCE_SUFFIXES:
            return 'source'
        if suffix in self.SCRIPT_SUFFIXES or low.startswith('scripts/'):
            return 'scripts'
        if suffix in self.DOC_SUFFIXES or low.startswith('docs/'):
            return 'docs'
        return 'other'

    @staticmethod
    def _extract_deps(path: Path) -> list[str]:
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return []

        includes = re.findall(r'#include\s+[<\"]([^>\"]+)[>\"]', text)
        py_imports = re.findall(r'^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)', text, flags=re.MULTILINE)
        ts_imports = re.findall(r"from\s+['\"]([^'\"]+)['\"]", text)
        deps = sorted(set(includes + py_imports + ts_imports))
        return deps

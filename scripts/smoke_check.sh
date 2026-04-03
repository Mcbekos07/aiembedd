#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Backend static compile"
python -m compileall backend/app

echo "[2/4] Backend core tests without external deps"
cd backend
PYTHONPATH=. pytest -q tests/test_semver.py tests/test_file_service.py
cd ..

echo "[3/4] Frontend import graph"
python - <<'PY'
from pathlib import Path
import re
for f in Path('frontend/src').rglob('*'):
    if f.suffix not in {'.ts','.vue'}: continue
    text=f.read_text(encoding='utf-8')
    for m in re.finditer(r"from ['\"](\.{1,2}/[^'\"]+)['\"]", text):
        rel=m.group(1)
        b=(f.parent/rel)
        candidates=[b,b.with_suffix('.ts'),b.with_suffix('.vue'),b/'index.ts',b/'index.vue']
        if not any(c.exists() for c in candidates):
            raise SystemExit(f'Missing import target: {f} -> {rel}')
print('ok')
PY

echo "[4/4] API consistency"
python - <<'PY'
from pathlib import Path
import re
backend=[]
for f in Path('backend/app/api/routes').glob('*.py'):
    t=f.read_text()
    pm=re.search(r"APIRouter\(prefix='([^']+)'",t)
    if not pm: continue
    prefix=pm.group(1)
    for m in re.finditer(r"@router\.(get|post|delete)\('([^']*)'",t):
        backend.append(re.sub(r'\{[^}]+\}','{var}',(prefix+m.group(2)).replace('//','/')))
for f in Path('frontend/src/app/services').glob('*.ts'):
    t=f.read_text()
    for m in re.finditer(r"`(/[^`]+)`",t):
        p=re.sub(r'\$\{[^}]+\}','{var}',m.group(1))
        if p not in backend:
            raise SystemExit(f'Missing backend endpoint for {f.name}: {p}')
print('ok')
PY

echo "Smoke check completed"

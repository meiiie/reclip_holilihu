import os
import runpy
import sys
from pathlib import Path


def candidate_roots():
    roots = []
    workspace_root = os.environ.get('CODEX_WORKSPACE_ROOT')
    if workspace_root:
        roots.append(Path(workspace_root))
    roots.append(Path.cwd())
    roots.append(Path(__file__).resolve().parents[3])
    return roots


def main():
    for root in candidate_roots():
        server_path = root / 'mcp_server.py'
        if server_path.is_file():
            sys.path.insert(0, str(root))
            os.chdir(root)
            runpy.run_path(str(server_path), run_name='__main__')
            return
    searched = ', '.join(str(root) for root in candidate_roots())
    raise SystemExit(f'Cannot find mcp_server.py. Searched: {searched}')


if __name__ == '__main__':
    main()

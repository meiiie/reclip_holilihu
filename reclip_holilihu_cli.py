import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


SERVER_NAME = 'holilihu-reclip'


def toml_string(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'


def codex_home():
    return Path(os.environ.get('CODEX_HOME') or (Path.home() / '.codex'))


def codex_config_path():
    return codex_home() / 'config.toml'


def build_codex_block(command, args, cwd=None):
    lines = [
        f'[mcp_servers.{SERVER_NAME}]',
        f'command = {toml_string(command)}',
        'args = [' + ', '.join(toml_string(arg) for arg in args) + ']',
    ]
    if cwd:
        lines.append(f'cwd = {toml_string(cwd)}')
    lines.extend([
        'startup_timeout_sec = 20',
        'tool_timeout_sec = 7200',
    ])
    return '\n'.join(lines) + '\n'


def remove_existing_block(content):
    pattern = rf'(?ms)^\[mcp_servers\.{re.escape(SERVER_NAME)}\]\r?\n.*?(?=^\[|\Z)'
    return re.sub(pattern, '', content).rstrip()


def write_codex_config(block, dry_run=False):
    path = codex_config_path()
    content = ''
    if path.is_file():
        content = path.read_text(encoding='utf-8')
    content = remove_existing_block(content)
    if content:
        content = content + '\n\n' + block
    else:
        content = block

    if dry_run:
        print(content)
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return path


def setup_mcp(args):
    if args.agent != 'codex':
        raise SystemExit('Only the codex agent is supported for now.')

    if args.source:
        source_path = Path(args.source).expanduser().resolve()
        server_path = source_path / 'mcp_server.py'
        if not server_path.is_file():
            raise SystemExit(f'Cannot find mcp_server.py in {source_path}')
        command = args.python or sys.executable
        block = build_codex_block(command, [str(server_path)], cwd=str(source_path))
    else:
        command = args.python or sys.executable
        block = build_codex_block(command, ['-m', 'mcp_server'])

    path = write_codex_config(block, dry_run=args.dry_run)
    if args.dry_run:
        return
    print(f'Configured Codex MCP server "{SERVER_NAME}" at {path}')
    print('Restart Codex so it reloads MCP tools.')


def print_mcp_config(args):
    if args.agent != 'codex':
        raise SystemExit('Only the codex agent is supported for now.')
    command = args.python or sys.executable
    if args.source:
        source_path = Path(args.source).expanduser().resolve()
        print(build_codex_block(command, [str(source_path / 'mcp_server.py')], cwd=str(source_path)), end='')
    else:
        print(build_codex_block(command, ['-m', 'mcp_server']), end='')


def doctor(_args):
    print('HoLiLiHu ReClip doctor')
    print(f'Python: {sys.version.split()[0]} ({sys.executable})')

    checks = [
        ('ffmpeg', shutil.which('ffmpeg')),
        ('ffprobe', shutil.which('ffprobe')),
    ]
    for name, path in checks:
        status = path or 'not found'
        print(f'{name}: {status}')

    for module in ['flask', 'yt_dlp', 'mcp']:
        try:
            __import__(module)
            print(f'{module}: ok')
        except Exception as exc:
            print(f'{module}: missing ({exc})')

    config = codex_config_path()
    print(f'Codex config: {config}')
    if config.is_file():
        content = config.read_text(encoding='utf-8')
        configured = f'[mcp_servers.{SERVER_NAME}]' in content
        print(f'Codex MCP "{SERVER_NAME}": {"configured" if configured else "not configured"}')
    else:
        print(f'Codex MCP "{SERVER_NAME}": not configured')


def serve(args):
    env = os.environ.copy()
    if args.port:
        env['PORT'] = str(args.port)
    if args.host:
        env['HOST'] = args.host
    subprocess.run([sys.executable, '-m', 'app'], check=True, env=env)


def run_mcp(_args):
    from mcp_server import mcp

    mcp.run()


def build_parser():
    parser = argparse.ArgumentParser(
        prog='reclip-holilihu',
        description='Install, configure, and run HoLiLiHu ReClip MCP tools.',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    setup = subparsers.add_parser('setup-mcp', help='Write AI-agent MCP configuration.')
    setup.add_argument('agent', choices=['codex'])
    setup.add_argument('--source', help='Path to a source checkout containing mcp_server.py.')
    setup.add_argument('--python', help='Python executable to launch the MCP server.')
    setup.add_argument('--dry-run', action='store_true', help='Print config without writing it.')
    setup.set_defaults(func=setup_mcp)

    print_config = subparsers.add_parser('print-mcp-config', help='Print MCP config for an agent.')
    print_config.add_argument('agent', choices=['codex'])
    print_config.add_argument('--source', help='Path to a source checkout containing mcp_server.py.')
    print_config.add_argument('--python', help='Python executable to launch the MCP server.')
    print_config.set_defaults(func=print_mcp_config)

    doctor_cmd = subparsers.add_parser('doctor', help='Check local dependencies and Codex config.')
    doctor_cmd.set_defaults(func=doctor)

    serve_cmd = subparsers.add_parser('serve', help='Run the web app from a source checkout.')
    serve_cmd.add_argument('--host')
    serve_cmd.add_argument('--port', type=int)
    serve_cmd.set_defaults(func=serve)

    mcp_cmd = subparsers.add_parser('run-mcp', help='Run the MCP server on stdio.')
    mcp_cmd.set_defaults(func=run_mcp)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()

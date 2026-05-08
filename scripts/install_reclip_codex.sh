#!/usr/bin/env bash
set -euo pipefail

REPO_URL=""
INSTALL_DIR="${HOME}/.local/share/reclip-holilihu-mcp"
BRANCH="main"
SKIP_CODEX_CONFIG="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)
      REPO_URL="$2"
      shift 2
      ;;
    --install-dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --skip-codex-config)
      SKIP_CODEX_CONFIG="1"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$REPO_URL" ]]; then
  echo "Usage: $0 --repo-url https://github.com/ORG/reclip-holilihu-mcp.git [--install-dir PATH] [--branch main]" >&2
  exit 1
fi

step() {
  printf '\n==> %s\n' "$1"
}

toml_string() {
  python3 - "$1" <<'PY'
import json
import sys
print(json.dumps(sys.argv[1]))
PY
}

step "Preparing install directory"
mkdir -p "$(dirname "$INSTALL_DIR")"

if [[ -d "${INSTALL_DIR}/.git" ]]; then
  step "Updating existing clone"
  git -C "$INSTALL_DIR" fetch origin "$BRANCH"
  git -C "$INSTALL_DIR" checkout "$BRANCH"
  git -C "$INSTALL_DIR" pull --ff-only origin "$BRANCH"
else
  if [[ -e "$INSTALL_DIR" ]]; then
    echo "Install directory exists but is not a Git repo: $INSTALL_DIR" >&2
    exit 1
  fi
  step "Cloning repository"
  git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

step "Creating Python virtual environment"
python3 -m venv "${INSTALL_DIR}/.venv"
VENV_PYTHON="${INSTALL_DIR}/.venv/bin/python"

step "Installing Python dependencies"
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r "${INSTALL_DIR}/requirements.txt"

if [[ "$SKIP_CODEX_CONFIG" != "1" ]]; then
  step "Configuring Codex MCP"
  CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"
  mkdir -p "$CODEX_HOME_DIR"
  CONFIG_PATH="${CODEX_HOME_DIR}/config.toml"
  SERVER_PATH="${INSTALL_DIR}/mcp_server.py"
  TMP_PATH="$(mktemp)"

  if [[ -f "$CONFIG_PATH" ]]; then
    python3 - "$CONFIG_PATH" "$TMP_PATH" <<'PY'
import re
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
for server_name in ("reclip-holilihu-mcp", "holilihu-reclip"):
    text = re.sub(rf"(?ms)^\[mcp_servers\.{re.escape(server_name)}\]\r?\n.*?(?=^\[|\Z)", "", text)
text = text.rstrip()
open(dst, "w", encoding="utf-8").write(text)
PY
  else
    : > "$TMP_PATH"
  fi

  {
    if [[ -s "$TMP_PATH" ]]; then
      cat "$TMP_PATH"
      printf '\n\n'
    fi
    printf '[mcp_servers.reclip-holilihu-mcp]\n'
    printf 'command = %s\n' "$(toml_string "$VENV_PYTHON")"
    printf 'args = [%s]\n' "$(toml_string "$SERVER_PATH")"
    printf 'cwd = %s\n' "$(toml_string "$INSTALL_DIR")"
    printf 'startup_timeout_sec = 20\n'
    printf 'tool_timeout_sec = 7200\n'
  } > "$CONFIG_PATH"
  rm -f "$TMP_PATH"
  echo "Configured: $CONFIG_PATH"
fi

step "Done"
echo "Repository: $INSTALL_DIR"
echo "Run app:    $VENV_PYTHON app.py"
echo "MCP file:   ${INSTALL_DIR}/mcp_server.py"
echo
echo "Restart Codex so it reloads MCP configuration."

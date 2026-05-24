#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/deploy.env"
REMOTE_SERVICE_STAGING_DIR=".bigrobotarm-systemd"
HTTP_SERVICE_NAME="bigrobotarm-http.service"
WEBSOCKET_SERVICE_NAME="bigrobotarm-websocket.service"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing deploy.env next to deploy.sh"
  exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG_FILE"

: "${DEPLOY_USER:?DEPLOY_USER must be set in deploy.env}"
: "${DEPLOY_HOST:?DEPLOY_HOST must be set in deploy.env}"
: "${DEPLOY_SERVER_DIR:?DEPLOY_SERVER_DIR must be set in deploy.env}"
: "${DEPLOY_SERVICE_DIR:?DEPLOY_SERVICE_DIR must be set in deploy.env}"
: "${DEPLOY_UV_BIN:?DEPLOY_UV_BIN must be set in deploy.env}"

SSH_TARGET="$DEPLOY_USER@$DEPLOY_HOST"
TEMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

render_service() {
  source_file="$1"
  target_file="$2"

  sed \
    -e "s|__BIGROBOTARM_USER__|$DEPLOY_USER|g" \
    -e "s|__BIGROBOTARM_SERVER_DIR__|$DEPLOY_SERVER_DIR|g" \
    "$source_file" > "$target_file"
}

echo "Creating remote directories"
ssh "$SSH_TARGET" "mkdir -p '$DEPLOY_SERVER_DIR' '$DEPLOY_SERVER_DIR/www' '$DEPLOY_SERVER_DIR/systemd' '$DEPLOY_SERVER_DIR/$REMOTE_SERVICE_STAGING_DIR'"

echo "Syncing server project"
rsync -av \
  --exclude '.git/' \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude 'run/' \
  --exclude 'deploy.env' \
  --exclude 'www/' \
  "$SCRIPT_DIR/" "$SSH_TARGET:$DEPLOY_SERVER_DIR/"

render_service "$SCRIPT_DIR/systemd/$HTTP_SERVICE_NAME" "$TEMP_DIR/$HTTP_SERVICE_NAME"
render_service "$SCRIPT_DIR/systemd/$WEBSOCKET_SERVICE_NAME" "$TEMP_DIR/$WEBSOCKET_SERVICE_NAME"

echo "Uploading systemd units"
scp "$TEMP_DIR/$HTTP_SERVICE_NAME" "$TEMP_DIR/$WEBSOCKET_SERVICE_NAME" "$SSH_TARGET:$DEPLOY_SERVER_DIR/$REMOTE_SERVICE_STAGING_DIR/"

echo "Installing dependencies on target"
ssh "$SSH_TARGET" "cd '$DEPLOY_SERVER_DIR' && '$DEPLOY_UV_BIN' sync --frozen"

echo "Installing systemd units"
ssh -t "$SSH_TARGET" "sudo install -m 644 '$DEPLOY_SERVER_DIR/$REMOTE_SERVICE_STAGING_DIR/$HTTP_SERVICE_NAME' '$DEPLOY_SERVICE_DIR/$HTTP_SERVICE_NAME' && sudo install -m 644 '$DEPLOY_SERVER_DIR/$REMOTE_SERVICE_STAGING_DIR/$WEBSOCKET_SERVICE_NAME' '$DEPLOY_SERVICE_DIR/$WEBSOCKET_SERVICE_NAME' && rm -rf '$DEPLOY_SERVER_DIR/$REMOTE_SERVICE_STAGING_DIR'"

echo "Reloading and restarting services"
ssh -t "$SSH_TARGET" "sudo systemctl daemon-reload && sudo systemctl enable '$HTTP_SERVICE_NAME' '$WEBSOCKET_SERVICE_NAME' && sudo systemctl restart '$HTTP_SERVICE_NAME' '$WEBSOCKET_SERVICE_NAME'"

echo "Deployment complete"
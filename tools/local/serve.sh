#!/usr/bin/env bash
# Serve the local WebSiCo instance on http://127.0.0.1:8080
LOCAL="${WS_LOCAL_DIR:-/home/claude/localsite}"
cd "$LOCAL/baigneaux" && exec php -S 127.0.0.1:8080 -t "$LOCAL/baigneaux" "$LOCAL/router.php"

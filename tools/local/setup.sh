#!/usr/bin/env bash
# Local WebSiCo test instance (PHP built-in server + MariaDB), for previews before uploading.
# usage: tools/local/setup.sh [EXPORT.ws_data]     then: tools/local/serve.sh
# Super-user password of the local instance: "local" (WS_SU_PWD) — the real one is never needed.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$HERE/../.." && pwd)"
LOCAL="${WS_LOCAL_DIR:-/home/claude/localsite}"; SITE="$LOCAL/baigneaux"
command -v mariadbd >/dev/null || { apt-get update -qq || true; DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mariadb-server; }
mkdir -p "$LOCAL/run" /run/mysqld && chown mysql:mysql /run/mysqld
[ -d /var/lib/mysql/mysql ] || mariadb-install-db --user=mysql >/dev/null
pgrep -x mariadbd >/dev/null || { nohup mariadbd --user=mysql --bind-address=127.0.0.1 > "$LOCAL/run/mariadb.log" 2>&1 & sleep 4; }
mariadb -uroot -e "CREATE DATABASE IF NOT EXISTS baigneaux CHARACTER SET utf8mb3;
  CREATE USER IF NOT EXISTS 'ws'@'127.0.0.1' IDENTIFIED BY 'wslocal'; GRANT ALL ON baigneaux.* TO 'ws'@'127.0.0.1';
  CREATE USER IF NOT EXISTS 'ws'@'localhost' IDENTIFIED BY 'wslocal'; GRANT ALL ON baigneaux.* TO 'ws'@'localhost'; FLUSH PRIVILEGES;"
[ -d "$LOCAL/websico-src" ] || git clone -q --depth 1 https://github.com/websico/websico "$LOCAL/websico-src"
rm -rf "$SITE" && cp -r "$LOCAL/websico-src" "$SITE" && rm -rf "$SITE/.git"
cp "$HERE/router.php" "$LOCAL/router.php"
python3 - "$SITE/ws_config.php" <<'PY'
import sys; p=sys.argv[1]; t=open(p).read()
for a,b in {"WS_DB_SERVER\", ''":"WS_DB_SERVER\", '127.0.0.1'","WS_DB_USER\", ''":"WS_DB_USER\", 'ws'",
            "WS_DB_PWD\", ''":"WS_DB_PWD\", 'wslocal'","WS_DB_NAME\", ''":"WS_DB_NAME\", 'baigneaux'",
            "//define(\"WS_SU_PWD\", md5('su_pwd'));":"define(\"WS_SU_PWD\", md5('local'));"}.items():
    assert a in t, a; t=t.replace(a,b)
open(p,'w').write(t)
PY
# PHP >= 8.2 compatibility: WebSiCo's purge aborts on "Creation of dynamic property ... is deprecated"
# (E_DEPRECATED raised by unserialize). Same one-line patch as recommended to the host (docs/LOCAL.md).
# Set WS_NO_PATCH=1 to reproduce the unpatched server behaviour.
if [ -z "${WS_NO_PATCH:-}" ]; then
  sed -i 's/if (error_reporting() \&\& $errno != E_STRICT)\t/if (error_reporting() \&\& !in_array($errno, array(E_STRICT, E_DEPRECATED, E_USER_DEPRECATED)))\t/' "$SITE/ws_lib/ws_core/ws_site.php"
  grep -q 'E_DEPRECATED, E_USER_DEPRECATED' "$SITE/ws_lib/ws_core/ws_site.php" || echo "WARNING: purge patch not applied"
fi
if [ $# -ge 1 ]; then WS_LOCAL_ROOT="$SITE" python3 -I "$REPO/tools/preview_local.py" "$1"
else WS_LOCAL_ROOT="$SITE" python3 -I "$REPO/tools/preview_local.py"; fi
echo "ready: run tools/local/serve.sh then open http://127.0.0.1:8080/ (edit mode: ?mode=1, password 'local')"

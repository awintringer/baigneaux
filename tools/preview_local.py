#!/usr/bin/env python3
"""Load site/ (or a .ws_data archive) into a local WebSiCo instance for testing.

usage: python3 tools/preview_local.py [ARCHIVE.ws_data]

Without argument, builds site/ with --target local first. The archive is then imported the
way WebSiCo does it (unzip -o over the site root, SQL replay with SET NAMES utf8, cache wipe).

Expects a local WebSiCo install (env WS_LOCAL_ROOT, default /home/claude/localsite/baigneaux)
served at http://127.0.0.1:8080 and a MariaDB database (env WS_LOCAL_DB, default baigneaux).
The local install has its own super-user password (WS_SU_PWD in its ws_config.php), so the
real admin password is never needed.
"""
import os, sys, subprocess, tempfile, shutil, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.environ.get('WS_LOCAL_ROOT', '/home/claude/localsite/baigneaux')
DB = os.environ.get('WS_LOCAL_DB', 'baigneaux')

def main():
    if len(sys.argv) > 1:
        archive = os.path.abspath(sys.argv[1])
    else:
        archive = os.path.join(tempfile.mkdtemp(), 'local.ws_data')
        subprocess.run([sys.executable, '-I', os.path.join(HERE, 'build.py'), archive, '--target', 'local'], check=True)
    if not os.path.isdir(LOCAL):
        sys.exit(f'no local WebSiCo at {LOCAL} (see docs/LOCAL.md)')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        z.extractall(LOCAL, [n for n in names if n != '_mysql_dump'])
        dump = z.read('_mysql_dump')
    subprocess.run(['mariadb', '-uroot', '--default-character-set=utf8mb3', DB], input=dump, check=True)
    shutil.rmtree(os.path.join(LOCAL, 'cache'), ignore_errors=True)
    subprocess.run(['chmod', '-R', 'a+rwX', LOCAL], check=False)
    print(f'imported {os.path.basename(archive)} ({len(names)} entries) -> http://127.0.0.1:8080/')

if __name__ == '__main__':
    main()

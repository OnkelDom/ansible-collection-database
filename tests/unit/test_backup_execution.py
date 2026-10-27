from pathlib import Path
import json
import os
import shlex
import subprocess
import sys

from jinja2 import Environment, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_restore_only_cleans_its_own_database_and_exits_successfully(tmp_path):
    defaults = yaml.safe_load((ROOT / 'roles/postgresql/defaults/main.yml').read_text())
    defaults.update(postgresql_backup_root_dir=str(tmp_path / 'backups'),
                    postgresql_backup_dbnames='application',
                    postgresql_backup_passphrase_file=str(tmp_path / 'passphrase'),
                    postgresql_backup_restore_test_database='isolated_restore',
                    postgresql_backup_metrics_file='', postgresql_backup_primary_only=False)
    environment = Environment(undefined=StrictUndefined)
    environment.filters['quote'] = lambda value: shlex.quote(str(value))
    source = (ROOT / 'roles/postgresql/templates/postgresql-custom-backup.sh.j2').read_text()
    script = tmp_path / 'backup.sh'
    script.write_text(environment.from_string(source).render(**defaults))
    binaries = tmp_path / 'bin'
    binaries.mkdir()
    stub = '''import json, os, sys
from pathlib import Path
name = Path(sys.argv[0]).name
if name == 'find':
    print('1 ' + sys.argv[1] + '/fixture.dump.gpg')
elif name == 'mktemp':
    path = Path(os.environ['DATABASE_TEST_TMP']) / 'restore.dump'
    path.touch()
    print(path)
elif name == 'gpg':
    Path(sys.argv[sys.argv.index('--output') + 1]).write_bytes(b'fixture')
elif name in ['createdb', 'dropdb']:
    with open(os.environ['DATABASE_TEST_TRACE'], 'a') as output:
        output.write(json.dumps([name, sys.argv[-1]]) + '\\n')
elif name == 'psql':
    print('1')
'''
    for name in ['find', 'mktemp', 'gpg', 'createdb', 'dropdb', 'pg_restore', 'psql']:
        path = binaries / name
        path.write_text('#!' + sys.executable + '\n' + stub)
        path.chmod(0o755)
    trace = tmp_path / 'trace.jsonl'
    result = subprocess.run(['bash', str(script), 'restore-test'], text=True, capture_output=True,
        env={**os.environ, 'PATH': str(binaries) + os.pathsep + os.environ['PATH'],
             'DATABASE_TEST_TMP': str(tmp_path), 'DATABASE_TEST_TRACE': str(trace)})
    assert result.returncode == 0, result.stderr
    operations = [json.loads(line) for line in trace.read_text().splitlines()]
    assert len(operations) == 2
    assert operations[0][0] == 'createdb'
    assert operations[1] == ['dropdb', operations[0][1]]
    assert operations[0][1].startswith('isolated_restore_')
    assert not (tmp_path / 'restore.dump').exists()

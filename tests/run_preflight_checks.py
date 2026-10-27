#!/usr/bin/env python3
"""Verify argument validation and platform rejection without configuring a host."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ROLES = sorted(p.name for p in (ROOT / 'roles').iterdir() if p.is_dir())
CASES = [('Debian', 'Debian', '13'), ('Ubuntu', 'Debian', '22.04'),
         ('Ubuntu', 'Debian', '24.04'), ('Ubuntu', 'Debian', '26.04'),
         ('Rocky', 'RedHat', '9'), ('RedHat', 'RedHat', '9'),
         ('Ubuntu', 'Debian', '20.04')]


def main():
    with tempfile.TemporaryDirectory(prefix='database-preflight-') as directory:
        play = Path(directory) / 'preflight.json'
        play.write_text(json.dumps([{'name': 'Validate installed role entries only',
            'hosts': 'all', 'connection': 'local', 'gather_facts': False,
            'pre_tasks': [{'name': 'Set synthetic platform facts', 'ansible.builtin.set_fact': {'ansible_facts': '{{ database_test_facts }}'}, 'tags': ['always']}],
            'roles': [{'role': 'degitag.database.' + role} for role in ROLES]}]))
        for distribution, family, version in CASES:
            inventory = Path(directory) / 'inventory.json'
            facts = {'distribution': distribution, 'os_family': family,
                'distribution_version': version, 'distribution_major_version': version.split('.')[0],
                'architecture': 'x86_64', 'python': {'executable': os.sys.executable},
                'env': {'PATH': os.environ['PATH']}, 'selinux': {'status': 'disabled'}}
            inventory.write_text(json.dumps({'all': {'hosts': {'platform_test': {
                'database_test_facts': facts, 'ansible_python_interpreter': os.sys.executable}}}}))
            result = subprocess.run(['ansible-playbook', '-i', str(inventory), str(play),
                '--skip-tags', ','.join(ROLES)], text=True, capture_output=True)
            unsupported = version == '20.04'
            if bool(result.returncode) != unsupported or 'changed=0' not in result.stdout:
                raise SystemExit(result.stdout + result.stderr)
            if not unsupported and 'skipping: [platform_test]' not in result.stdout:
                raise SystemExit('Existing platform facts were not reused')
            print(f'{distribution} {version}: {"rejected without changes" if unsupported else "all six role entries validated"}')


if __name__ == '__main__':
    main()

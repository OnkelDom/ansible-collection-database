#!/usr/bin/env bash
set -euo pipefail
for playbook in roles/*/tests/test.yml playbooks/*.yml tests/integration/*.yml; do
  ansible-playbook --syntax-check "$playbook" -i localhost,
done

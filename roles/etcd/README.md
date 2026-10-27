# etcd

Manage a checksum-pinned etcd consensus cluster for Patroni.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Initial membership is a bootstrap input. Membership changes require an explicit etcdctl member add/remove procedure and quorum review. TLS and client/peer authentication are enabled by default; certificates are supplied by the operator. Installation of external release binaries requires etcd_install=true. Release assets are provided for x86_64 and aarch64; ARM execution requires a separate runtime acceptance test.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
etcd_version: 3.6.14
etcd_install: false
etcd_initialize: false
etcd_name: '{{ inventory_hostname }}'
etcd_initial_cluster: {}
etcd_initial_cluster_token: ''
etcd_initial_cluster_state: new
etcd_data_dir: /var/lib/etcd
etcd_listen_client_urls: []
etcd_advertise_client_urls: []
etcd_listen_peer_urls: []
etcd_initial_advertise_peer_urls: []
etcd_tls_enabled: true
etcd_ca_file: ''
etcd_cert_file: ''
etcd_key_file: ''
etcd_peer_ca_file: ''
etcd_peer_cert_file: ''
etcd_peer_key_file: ''
etcd_manage_service: true
etcd_service_enabled: true
etcd_service_state: started
etcd_manage_firewall: false
etcd_firewall_sources: []
```

## Example Playbook

```yaml
# Required cluster addresses, PKI and Vault inputs: docs/patroni.md.
- name: Configure etcd
  hosts: database_ha
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.etcd
```

## Testing

Build and install the current collection checkout before running syntax checks, so the
fully qualified role reference resolves to this implementation.

Run `python tools/generate_role_scaffold.py --check`, `pytest tests/unit` and
`bash tests/run_role_syntax_checks.sh` from the collection root.
CI additionally runs YAML lint, Ansible lint, collection build/install and container smoke tests.
VM functional results are tracked separately; metadata lists intended compatibility,
not proof that every feature has passed on every distribution.

## Dependencies

Install the collection dependencies from `requirements.yml`. Role dependencies:
`[]`.

## Change management

Use check mode where the underlying modules support it. Review the diff before applying
changes. Network, firewall, identity and storage changes need an out-of-band recovery
path. Secrets belong in Ansible Vault or the operator secret store, never in defaults.

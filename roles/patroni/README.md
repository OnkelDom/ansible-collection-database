# patroni

Manage PostgreSQL high availability through Patroni and an explicit etcd-v3 DCS.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Patroni is the sole owner of PostgreSQL start, stop, leader election and replication in HA mode. Bootstrap and adoption require explicit flags. bootstrap.dcs only initializes a new DCS scope; use patronictl edit-config for changes to an existing cluster. No automatic data-directory deletion or DCS reset is performed.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
patroni_scope: ''
patroni_name: '{{ inventory_hostname }}'
patroni_namespace: /service/
patroni_version: 4.1.5
patroni_install: true
patroni_bootstrap: false
patroni_allow_adopt_existing: false
patroni_manage_service: true
patroni_service_enabled: true
patroni_service_state: started
patroni_manage_firewall: false
patroni_firewall_sources: []
patroni_etcd_hosts: []
patroni_etcd_protocol: https
patroni_etcd_ca_file: ''
patroni_etcd_cert_file: ''
patroni_etcd_key_file: ''
patroni_etcd_username: ''
patroni_etcd_password: ''
patroni_rest_listen: 127.0.0.1:8008
patroni_rest_connect_address: ''
patroni_rest_username: patroni
patroni_rest_password: ''
patroni_rest_cert_file: ''
patroni_rest_key_file: ''
patroni_postgresql_listen: 127.0.0.1:5432
patroni_postgresql_connect_address: ''
patroni_postgresql_data_dir: /var/lib/patroni
patroni_superuser_username: postgres
patroni_superuser_password: ''
patroni_replication_username: replicator
patroni_replication_password: ''
patroni_pg_hba: []
patroni_parameters: {}
patroni_bootstrap_dcs: {}
patroni_tags: {}
patroni_watchdog_mode: "off"
patroni_watchdog_device: /dev/watchdog
patroni_ttl: 30
patroni_loop_wait: 10
patroni_retry_timeout: 10
patroni_synchronous_mode: true
patroni_synchronous_node_count: 1
patroni_synchronous_mode_strict: false
patroni_manage_objects: false
patroni_manage_backup: false
```

## Example Playbook

```yaml
# Required cluster addresses, PKI and Vault inputs: docs/patroni.md.
- name: Configure patroni
  hosts: database_ha
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.patroni
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

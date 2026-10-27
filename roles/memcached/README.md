# memcached

Install and configure memcached with explicit service and data lifecycle management.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Service tasks and handlers honor manage_service, service_enabled and service_state. Optional port rules delegate to degitag.infrastructure.firewall. Review docs/migration.md before changing an existing installation.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
memcached_verbose: false
memcached_memory: 64
memcached_port: 11211
memcached_user: ''
memcached_listen:
- 127.0.0.1
memcached_maxconn: 1024
memcached_extra_options: []
memcached_manage_service: true
memcached_service_enabled: true
memcached_service_state: started
memcached_manage_firewall: false
memcached_firewall_sources: []
memcached_packages: []
```

## Example Playbook

```yaml
- name: Configure a local application cache
  hosts: memcached_servers
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.memcached
    vars:
      memcached_memory: 128
      memcached_listen: [127.0.0.1]
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

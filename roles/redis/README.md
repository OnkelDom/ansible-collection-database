# redis

Install and configure redis with explicit service and data lifecycle management.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Native distribution services replace custom instance units. With Sentinel enabled, Redis runtime configuration is rendered only on first handover; Sentinel owns subsequent primary/replica changes. Normal reruns preserve CONFIG REWRITE and failover state. Configuration or credential rotation requires explicit redis_sentinel_allow_reconfigure=true with inputs reflecting the current topology.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
redis_master_ip: ''
redis_server_port: 6379
redis_server_databases_number: 16
redis_server_databases_dir: /var/lib/redis
redis_conf_default:
  bind: "{{ redis_server_bind | join(' ') }}"
  port: '{{ redis_server_port }}'
  protected-mode: "yes"
  supervised: systemd
  daemonize: "no"
  dir: '{{ redis_server_databases_dir }}'
  logfile: '""'
  databases: '{{ redis_server_databases_number }}'
  requirepass: '{{ redis_server_password }}'
  masterauth: "{{ redis_server_password if redis_role == 'replica' else '' }}"
redis_conf: {}
redis_sentinel_enabled: false
redis_sentinel_listen: 127.0.0.1
redis_sentinel_port: 26379
redis_sentinel_databases_dir: '{{ redis_server_databases_dir }}'
redis_sentinel_quorum: 2
redis_sentinel_master_name: mymaster
redis_sentinel_downafter: 10000
redis_sentinel_failover_timeout: 30000
redis_sentinel_conf: {}
redis_sentinel_sentinel_conf: {}
redis_sentinel_master_conf: {}
redis_manage_service: true
redis_service_enabled: true
redis_service_state: started
redis_manage_firewall: false
redis_firewall_sources: []
redis_packages: []
redis_server_password: ''
redis_server_bind:
- 127.0.0.1
- ::1
redis_manage_sysctl: false
redis_role: standalone
redis_sentinel_allow_reconfigure: false
```

## Example Playbook

```yaml
- name: Configure a local application cache
  hosts: redis_servers
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.redis
    vars:
      redis_conf:
        maxmemory: 256mb
        maxmemory-policy: allkeys-lru
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

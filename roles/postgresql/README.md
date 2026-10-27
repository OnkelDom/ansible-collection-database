# postgresql

Install and configure postgresql with explicit service and data lifecycle management.

## Supported platforms

- Ubuntu 22.04, 24.04, 26.04
- Debian 13
- Rocky Linux 9 / RHEL 9

## Architecture and operation

Facts are collected at entry only when the required platform facts are missing.
`tasks/preflight.yml` rejects unsupported releases before making changes and loads
family, distribution and release variables from `vars/platform/` in that order.
Public inputs belong in `defaults/main.yml`; platform internals belong in `vars/`.

Standalone mode uses native distribution packages. Set postgresql_initialize=true for a new cluster. In HA mode use degitag.database.patroni instead; it prepares PostgreSQL packages with a single service owner. Major upgrades, uninstall and legacy manual replication are never implicit. Backups and restore tests require separate opt-ins.

## Role Variables

The role interface is validated through `meta/argument_specs.yml`. Defaults are defined in `defaults/main.yml`.

```yaml
---
postgresql_version: ''
postgresql_debug: false
postgresql_locales:
- en_US.UTF-8
postgresql_port: 5432
postgresql_listen_addresses: localhost
postgresql_max_connections: 100
postgresql_shared_preload_libraries: []
postgresql_auth_method: scram-sha-256
postgresql_unix_socket_directories:
- /run/postgresql
postgresql_unix_socket_directories_mode: ''
postgresql_global_config_options:
- option: unix_socket_directories
  value: '{{ postgresql_unix_socket_directories | join(",") }}'
- option: log_directory
  value: log
- option: data_directory
  value: "{{ _postgresql_data_dir | default('') }}"
- option: port
  value: '{{ postgresql_port }}'
- option: listen_addresses
  value: '{{ postgresql_listen_addresses }}'
- option: shared_preload_libraries
  value: '{{ postgresql_shared_preload_libraries | join(",") }}'
- option: hba_file
  value: "{{ _postgresql_config_path | default('') }}/pg_hba.conf"
- option: max_connections
  value: '{{ postgresql_max_connections }}'
postgresql_global_config_options_extra: []
postgresql_log_dir: "{{ ((postgresql_global_config_options + postgresql_global_config_options_extra) | items2dict(key_name='option', value_name='value')).log_directory }}"
postgresql_effective_log_dir: "{{ postgresql_log_dir is match('/') | ternary(postgresql_log_dir, (_postgresql_data_dir | default('')) ~ '/' ~ postgresql_log_dir) }}"
postgresql_persist_permissions: true
postgresql_tempfile_src_template_path: etc/tmpfiles.d/postgresql-common.conf.j2
postgresql_tempfile_dest_path: /etc/tmpfiles.d/postgresql-common.conf
postgresql_tempfile_mode: '0644'
postgresql_tempfile_owner: root
postgresql_tempfile_group: root
postgresql_hba_entries:
- contype: local
  databases: all
  users: postgres
  method: peer
- contype: host
  databases: all
  users: all
  address: 127.0.0.1/32
  method: '{{ postgresql_auth_method }}'
- contype: host
  databases: all
  users: all
  address: ::1/128
  method: '{{ postgresql_auth_method }}'
postgresql_hba_entries_extra: []
postgresql_hba_template_path: pg_hba.conf.j2
postgresql_hba_use_raw: false
postgresql_hba_raw: ''
postgresql_cluster_name: main
postgresql_user: postgres
postgresql_group: postgres
postgresql_service_state: started
postgresql_service_enabled: true
postgresql_tablespaces: []
postgresql_users: []
postgres_users_no_log: true
postgresql_memberships: []
postgresql_databases: []
postgresql_schemas: []
postgresql_tables: []
postgresql_ownerships: []
postgresql_privs: []
postgresql_extensions: []
postgresql_queries: []
postgresql_scripts: []
postgresql_autotune: false
postgresql_autotune_config_options: []
postgresql_autotune_os_type: linux
postgresql_autotune_arch: x86-64
postgresql_autotune_drive_type: SSD
postgresql_autotune_env_name: OLTP
postgresql_autotune_include_badger: false
postgresql_autotune_cpus: "{{ ansible_facts.get('processor_nproc', 1) }}"
postgresql_autotune_total_ram: "{{ ((ansible_facts.get('memtotal_mb', 1024) / 1024) | round | int) }}"
postgresql_autotune_pg_version: '{{ postgresql_version }}'
postgresql_autotune_base_url: https://api.pgconfig.org
postgresql_autotune_url: '{{ postgresql_autotune_base_url }}/v1/tuning/get-config?format=conf&include_pgbadger={{ postgresql_autotune_include_badger }}&log_format=csvlog&max_connections={{ postgresql_max_connections }}&pg_version={{ postgresql_version }}&environment_name={{ postgresql_autotune_env_name }}&total_ram={{ postgresql_autotune_total_ram }}GB&cpus={{ postgresql_autotune_cpus }}&drive_type={{ postgresql_autotune_drive_type }}&arch={{ postgresql_autotune_arch }}&os_type={{ postgresql_autotune_os_type }}'
postgresql_backup: false
postgresql_backup_root_dir: /var/backups/postgresql
postgresql_backup_script_dest: /var/backups/autopostgresqlbackup.sh
postgresql_backup_create_database: "yes"
postgresql_backup_dbnames: all
postgresql_backup_dbexclude: ''
postgresql_backup_cron_job_name: Postgresql - Backup management
postgresql_backup_schedule:
  minute: 0
  hour: 0
postgresql_backup_mail_addr: ''
postgresql_backup_doweekly: 6
postgresql_backup_domonthly: 1
postgresql_backup_brdaily: 14
postgresql_backup_brweekly: 5
postgresql_backup_brmontly: 12
postgresql_backup_perm: '600'
postgresql_backup_implementation: legacy
postgresql_backup_encryption_passphrase: ''
postgresql_backup_passphrase_file: /var/lib/pgsql-backup-passphrase
postgresql_backup_daily_retention: 7
postgresql_backup_weekly_retention: 4
postgresql_backup_systemd_calendar: '*-*-* 01:30:00'
postgresql_backup_restore_test_calendar: '*-*-01 04:30:00'
postgresql_backup_restore_test_database: postgresql_restorecheck
postgresql_backup_metrics_file: ''
postgresql_backup_metrics_directory_owner: root
postgresql_backup_metrics_directory_group: root
postgresql_backup_metrics_directory_mode: '0755'
postgresql_backup_custom_script_dest: /usr/local/sbin/postgresql-custom-backup
postgresql_http_general_proxy: ''
postgresql_https_general_proxy: ''
postgresql_http_pkg_proxy: ''
postgresql_https_pkg_proxy: ''
postgresql_manage_service: true
postgresql_manage_firewall: false
postgresql_firewall_sources: []
postgresql_packages: []
postgresql_initialize: false
postgresql_manage_objects: true
postgresql_manage_backup_timers: false
postgresql_backup_restore_test_enabled: false
postgresql_data_dir: ''
postgresql_config_path: ''
postgresql_bin_path: ''
postgresql_daemon: ''
postgresql_service_path: ''
postgresql_deployment_mode: standalone
postgresql_backup_primary_only: false
postgresql_allow_data_migration: false
postgresql_manage_backup_schedule: false
```

## Example Playbook

```yaml
- name: Configure PostgreSQL
  hosts: postgresql_servers
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.postgresql
    vars:
      postgresql_initialize: true
      postgresql_users:
      - name: application
        password: "{{ vault_application_db_password }}"
      postgresql_databases:
      - name: application
        owner: application
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

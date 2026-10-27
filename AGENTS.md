# AGENTS.md

This repository maintains `degitag.database` with mariadb, postgresql, redis, memcached, patroni and etcd roles. Use vim in instructions. Write documentation from the DevOps/system architecture perspective.

Support Debian 13, Ubuntu 22.04/24.04/26.04 and Rocky/RHEL 9. All four sibling collections use the same generated role scaffold, fact-aware preflight, layered platform variables, typed public API, service guards and check commands. Preserve existing uncommitted work.

Host networking and additive firewall rules belong to `degitag.infrastructure`. Patroni is the sole PostgreSQL service owner in HA mode; etcd owns consensus. Never delete a data directory, reset DCS, rotate encryption keys, bootstrap a cluster, migrate data or change cluster membership implicitly. Database initialization and external binary installation require explicit switches. Existing topology requires a reviewed operator procedure.

Use tools/generate_role_scaffold.py and tools/role_scaffold_config.yml for generated content. Implementation belongs in tasks/configuration.yml. Defaults must validate before facts are loaded. Secrets must remain in Vault and secret tasks use no_log. Native EL9 SELinux enforcement stays enabled.

Run scaffold --check, pytest tests/unit, YAML lint, production Ansible lint, all role syntax checks, artifact build/install and compile/import sanity. Container smoke must converge on five free target images; real service, SELinux, reboot, replication, Patroni failover, backup and restore need disposable VMs. Document actual evidence and gaps in docs/validation; no production or repository publication is authorized by a refactor.

GitHub target organization is degitag; Ansible namespace is degitag. Run the shared local entry point bash tests/run_checks.sh. Local toolchain uses Homebrew Python 3.12 and .venv. No credentials in logs, defaults or repository files.

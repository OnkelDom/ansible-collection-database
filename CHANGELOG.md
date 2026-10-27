# Changelog

## 2.0.0 (2026-10-27)

- Rename the collection namespace from degit.database to degitag.database, including role references, generated examples and artifact tooling.
- Standardize all database roles as degitag.database with layered platform variables and typed APIs.
- Replace legacy PostgreSQL replication with Patroni and managed etcd.
- Use native distribution services and safe lifecycle controls.
- Keep backup, encryption and replication explicit; never reinitialize existing data implicitly.

# lenmail.database

Diese Collection fasst die bereits importierten Datenbank- und Caching-Rollen in einer gemeinsamen Ansible-Collection zusammen.

## Enthaltene Rollen

- `lenmail.database.mariadb`
- `lenmail.database.postgresql`
- `lenmail.database.redis`
- `lenmail.database.memcached`

## Lokale Nutzung

```bash
ansible-galaxy collection build
ansible-playbook playbooks/mariadb.yml
```

## Status

Die Rollen wurden aus bestehenden Einzel-Repositories in diese Collection uebernommen. Einige Upstream-Dokumente und Molecule-Szenarien sind noch sichtbar, die lauffaehige Collection-Struktur ist aber bereits vorhanden.

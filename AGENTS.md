# AGENTS.md

Dieses Repository enthaelt die Ansible Collection `lenmail.database`.

## Aktueller Stand

- Die Rollen `mariadb`, `postgresql`, `redis` und `memcached` wurden aus bestehenden Einzel-Repositories uebernommen.
- Das Repository ist als Collection strukturiert, aber nicht alle importierten Upstream-Dokumente wurden bereits bereinigt.
- Neue Aenderungen sollen sich am Collection-Layout orientieren, nicht mehr am alten Einzelrollen-Layout.

## Ziele

- Datenbank- und Caching-Rollen fuer Ubuntu 22.04+, Debian 12+ und RHEL 9+ konsistent halten
- importierte Rollen schrittweise auf einen gemeinsamen Collection-Standard bringen
- lokale Checks auf macOS reproduzierbar halten

## Pflicht fuer neue oder geaenderte Rollen

- `README.md` pro Rolle
- `meta/main.yml`
- `meta/argument_specs.yml`
- `tests/test.yml`
- Plattform-Support explizit dokumentieren
- keine impliziten Distribution-Annahmen ohne `assert` oder klares `when`

## Collection-Struktur

- Rollen liegen unter `roles/<rollenname>`
- Beispiel-Playbooks liegen unter `playbooks/`
- Collection-Metadaten liegen in `galaxy.yml` und `meta/runtime.yml`
- Vollqualifizierte Rollen-Namen verwenden immer `lenmail.database.<rolle>`

## Rollen-Standard

- Defaults muessen sicher und ohne versteckte Fremdvariablen nutzbar sein
- Rollen mit Diensten sollen Konfiguration vor Restart oder Enable validieren, wenn ein Validator verfuegbar ist
- plattformspezifische Paketnamen, Pfade und Services gehoeren in `vars/`
- neue Tasks sollen moeglichst `ansible.builtin.*` verwenden
- Secrets gehoeren nicht in Defaults, sondern muessen leer oder optional sein
- Service-Rollen sollen offensichtliche Schalter wie `*_service_enabled`, `*_enabled_on_startup` oder gleichwertige Steuerung haben
- Rollen mit generierten Dateien sollen idempotent bleiben und veraltete Artefakte nach Moeglichkeit bereinigen

## Lokale Toolchain

- Auf macOS die lokale `.venv` mit Homebrew `python@3.12` bauen
- Homebrew nicht mit `sudo` ausfuehren
- Beispiel:
  - `/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv`
  - `.venv/bin/pip install -r requirements-test.txt`

## Mindestchecks vor Commit

- `ansible-galaxy collection build`
- `ansible-playbook --syntax-check playbooks/mariadb.yml`
- `ansible-playbook --syntax-check playbooks/postgresql.yml`
- `ansible-playbook --syntax-check playbooks/redis.yml`
- `ansible-playbook --syntax-check playbooks/memcached.yml`
- `ansible-lint`

## Plattform-Regeln

- Debian- und RedHat-spezifische Pfade, Paketnamen und Service-Namen muessen getrennt gepflegt werden
- Rollen mit distributionsspezifischem Verhalten sollen das frueh validieren
- Facts werden auf Play-Ebene gesammelt, nicht per `setup` pauschal in jeder Rolle
- Syntax- und Beispiel-Playbooks muessen `gather_facts: true` setzen
- Wenn eine Rolle nicht sinnvoll plattformuebergreifend ist, lieber klar eingrenzen als implizit brechen

## Doku- und Namespace-Regeln

- Collection-Referenzen immer als `lenmail.database.*`
- keine neuen Verweise auf alte Namespaces wie `claranet.*` oder `lenhardt-its.*`
- importierte READMEs duerfen schrittweise bereinigt werden, neue Beispiele muessen aber direkt den Collection-Namespace verwenden

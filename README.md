# Ansible Collection `degitag.database`

[![CI](https://github.com/degitag/ansible-collection-database/actions/workflows/ci.yml/badge.svg)](https://github.com/degitag/ansible-collection-database/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/degitag/ansible-collection-database)](https://github.com/degitag/ansible-collection-database/releases)
[![Tag](https://img.shields.io/github/v/tag/degitag/ansible-collection-database)](https://github.com/degitag/ansible-collection-database/tags)
![Ansible Core](https://img.shields.io/badge/ansible--core-2.20%20%7C%202.21-blue)

Native Datenbanken, Caches und PostgreSQL-HA mit expliziter Daten- und Dienstverantwortung.

## Verantwortung und Architektur

Die Collection verwaltet native Datenbanken und Caches sowie PostgreSQL-HA mit Patroni und etcd. Paketinstallation, Konfiguration, Dienstführung und Datenänderungen haben getrennte Freigaben. Patroni ist im HA-Betrieb der alleinige PostgreSQL-Dienstführer; etcd stellt den Konsens bereit. Host-Netzwerk und additive Firewall-Regeln gehören zu `degitag.infrastructure`.

Die Rollen verwenden denselben generierten Aufbau wie Infrastructure, Monitoring und K3s. Facts werden bei Bedarf ergänzt; Plattformdaten werden in der Reihenfolge Familie, Distribution und Release geladen. Dienste und Restart-Handler respektieren `*_manage_service`, `*_service_enabled` und `*_service_state`. Öffentliche Eingaben stehen in den Rollen-Defaults und den typisierten Argument-Specs.

### Daten- und Clustergrenzen

Initialisierung, externe Binärinstallation, Datenmigration und Backup-Zeitpläne benötigen explizite Schalter. Vorhandene Datenverzeichnisse werden nicht automatisch entfernt. Hauptversionswechsel, DCS-Reset, Schlüsselrotation und Änderungen der Cluster-Mitgliedschaft benötigen einen geprüften Betreiberablauf. Secrets stammen aus Vault oder einem Secret Store.

[Patroni-Architektur und Beispiel](docs/patroni.md) beschreiben den dreiknotigen Aufbau. Bestehende Installationen benötigen eine ausdrückliche Übernahmefreigabe. HA ersetzt kein Backup; Failover, Partitionen, Reboot, Verschlüsselung und Restore brauchen eigene Abnahmefälle.

## Plattformen und Laufzeit

| Ebene | Unterstütztes Ziel |
| --- | --- |
| Controller | Python 3.12, Ansible Core 2.20/2.21 |
| Debian | 13 |
| Ubuntu | 22.04, 24.04, 26.04 |
| Enterprise Linux | Rocky Linux 9, RHEL 9 mit abonnierten Basis-Repositories |

Native Distributionspakete sind der Standard. Datenbank-Hauptversionen unterscheiden sich je Betriebssystem; ein Patroni-Cluster benötigt dieselbe Hauptversion auf allen Mitgliedern. Der tatsächliche Prüfumfang und offene Lücken stehen unter [Validierung](docs/validation/README.md). Ein Supportziel in den Metadaten ist kein Laufzeitnachweis.

## Installation

Bis zur Veröffentlichung wird aus dem lokalen Checkout gebaut:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/ansible-galaxy collection install -r requirements.yml
.venv/bin/ansible-galaxy collection build --force
.venv/bin/ansible-galaxy collection install degitag-database-2.0.0.tar.gz --force --no-deps
```

Auf macOS kann die Umgebung mit `/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv` angelegt werden. Für optionale Portregeln muss zusätzlich `degitag.infrastructure` aus dem separat verwalteten Checkout installiert sein. Patroni wird versionsgebunden in einer isolierten Python-Umgebung installiert. etcd-Downloads sind je Version und CPU-Architektur mit SHA-256 hinterlegt; die externe Installation wird mit `etcd_install: true` freigegeben.

## Verwendung

```yaml
- name: Configure standalone database
  hosts: database_servers
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

`postgresql_initialize: true` ist eine ausdrückliche Betreiberentscheidung für einen neuen Cluster. Vor einem Rollout bestehende Inventory-Eingaben und Datenbestände prüfen. Weitere [Playbooks](playbooks/) und die jeweilige Rollen-README beschreiben die dienstspezifischen Eingaben.

## Rollen

| Rolle | Verantwortung |
| --- | --- |
| [mariadb](roles/mariadb/README.md) | Native Installation, Datenbanken, Benutzer, Replikation, Verschlüsselung, optionale Backups |
| [postgresql](roles/postgresql/README.md) | Native Pakete, Standalone-Instanz, Objekte, Berechtigungen, optionale Backups |
| [redis](roles/redis/README.md) | Native Redis-Instanz, optionale Replikation und Sentinel |
| [memcached](roles/memcached/README.md) | Nativer Cache-Dienst mit deaktiviertem UDP |
| [patroni](roles/patroni/README.md) | PostgreSQL-HA, expliziter Bootstrap und alleinige PostgreSQL-Dienstführung |
| [etcd](roles/etcd/README.md) | Konsens-Cluster mit expliziten Mitgliedern und TLS |

## Repository-Struktur

| Pfad | Zweck |
| --- | --- |
| `galaxy.yml`, `meta/runtime.yml` | Collection-Identität, Abhängigkeiten und Controller-Vertrag |
| `roles/` | Dienstrollen, typisierte APIs, Templates und Plattformdaten |
| `playbooks/` | Beispiele für Standalone- und HA-Betrieb |
| `tools/` | Scaffold-Generator, Formatierung sowie Repository- und Artefaktprüfung |
| `tests/unit/` | API-, Sicherheits-, Backup- und Werkzeugverträge |
| `tests/integration/` | Container-Konvergenz und separat freizugebende Dienst-/HA-Prüfungen |
| `tests/run_checks.sh` | Gemeinsamer lokaler und CI-Prüfeinstieg |
| `.github/` | CI, Release und Dependency-Updates |
| `docs/` | Architektur, Migration, Repository-Standard und Validierungsnachweise |

Generierte Dateien werden über `tools/role_scaffold_config.yml` und `tools/generate_role_scaffold.py` geändert. Implementierung gehört in `tasks/configuration.yml` und fachliche Includes. Der [Repository-Standard](docs/repository-standard.md) gilt gemeinsam mit Infrastructure, Monitoring, K3s und dem dokumentierten Proxmox-Adapter.

## Entwicklung und Checks

```bash
make prepare
bash tests/run_checks.sh
```

`make test` und `make ci` verwenden denselben Einstieg. Er prüft Repository-Vertrag, Scaffold, Unit-Tests, YAML, Artefaktinhalt und Installation, synthetischen Plattform-Preflight, Syntax aller Rollen, Production-Lint und Compile-/Import-Sanity. [CONTRIBUTING.md](CONTRIBUTING.md) beschreibt den Ablauf und die Grenzen mutierender Tests.

Container-Smoke prüft Paket- und Konfigurationskonvergenz auf Debian 13, Ubuntu 22.04/24.04/26.04 und Rocky Linux 9. Echte Dienste, SELinux, Reboot, Replikation, Failover, Backup und Restore benötigen isolierte VMs. Die Integrationsplaybooks verlangen `database_test_disposable=true`. Produktive Inventories und Secrets gehören nicht in dieses Repository.

## CI und Releases

CI führt den gemeinsamen Prüfeinstieg unter Ansible Core 2.20 und 2.21 mit Python 3.12 aus. Anschließend prüft die Container-Matrix den zweiten Lauf auf `changed=0`. Actions sind mit vollständigen Commit-SHAs gepinnt. Der Release-Workflow verlangt einen zu `galaxy.yml` passenden `v`-Tag und erfolgreiche Checks; er erstellt ein GitHub-Release mit Collection-Artefakt. Galaxy-Publikation und produktives Deployment sind separate Betreiberentscheidungen.

Lokale Resultate und tatsächlich ausgeführte GitHub-/Laufzeittests werden in [docs/validation](docs/validation/) getrennt dokumentiert.

## Migration

[Migration](docs/migration.md) beschreibt die Umstellung von `degit.database`, `onkeldom.database` und `lenmail.database` auf `degitag.database`, entfernte Legacy-Pfade und die Freigaben für vorhandene Datenbestände. Es gibt keinen automatischen Alias für den alten Namespace.

## Sicherheit

[SECURITY.md](SECURITY.md) beschreibt vertrauliche Meldungen und den Umgang mit Secrets. Datenbank-Listener sind standardmäßig lokal. SELinux bleibt auf EL9 aktiviert. Die Rollen verändern keine bestehende Cluster- oder Verschlüsselungsidentität ohne explizite Freigabe.

## Lizenz

Der Collection-Rahmen und neue HA-Rollen stehen unter [MIT](LICENSE). Importierte Rollen behalten ihre MPL-2.0-Lizenzen; das eingebettete PostgreSQL-Backupskript trägt GPL-2.0-or-later. Details und Herkunft stehen unter [Lizenzen](docs/licenses.md).

# Namespace-Umbenennung am 27.10.2026

Die Collection verwendet jetzt `degitag.database` statt `degit.database`, bei unveränderter Version 2.0.0. Generator-Konfiguration, generierte Rollenbeispiele, interne Rollenaufrufe, Playbooks, CI/Release-Artefakte und Artefaktprüfung verwenden die neue Identität. Der CI-Sanity-Aufruf verwendet den Collection-Namen `database`.

## Lokaler Nachweis

`bash tests/run_checks.sh` wurde nach den Änderungen mit Exit-Code 0 ausgeführt, unter Python 3.12.16:

- Generator `--check` erfolgreich.
- 34 Unit-Tests erfolgreich.
- YAML-Lint erfolgreich.
- Artefakt gebaut, Identität/Inhalt geprüft und als `degitag.database:2.0.0` lokal installiert.
- Plattform-Preflight für alle sechs Rollen auf Debian 13, Ubuntu 22.04/24.04/26.04, Rocky 9 und RedHat 9 erfolgreich; Ubuntu 20.04 ohne Änderungen abgewiesen.
- Syntaxprüfungen aller sechs Rollen erfolgreich.
- Ansible-Lint mit Profil `production`: 0 Fehler, 0 Warnungen.
- Ansible-Test Sanity `compile` und `import` unter Python 3.12 erfolgreich.
- `git diff --check` erfolgreich.

Artefakt: `degitag-database-2.0.0.tar.gz`. SHA-256: `b70f874ec0d27530f85a33ec615a07608e89de996e4f4110e08790f103837616`.

## Grenzen und Betrieb

Docker ist lokal nicht verfügbar. Die Container-Smoke-Matrix auf fünf Images wurde für dieses Artefakt nicht erneut ausgeführt. VM-Prüfungen für Dienste, SELinux, Reboot, Replikation, Failover, Backup und Restore wurden nicht wiederholt. Frühere JSON-Nachweise in diesem Verzeichnis beziehen sich weiterhin auf `degit.database` und das dort dokumentierte Artefakt; sie sind kein Laufzeitnachweis für das neue Artefakt.

Vorhandene Änderungen im Checkout wurden erhalten. Externe Referenzen auf `degit.infrastructure` sowie Zielsystempfade, Sicherheitsmarker, Daten- und Clusteridentitäten wurden nicht umbenannt. Aufrufende externe Playbooks und Requirements benötigen die in `docs/migration.md` beschriebene Anpassung. Kein Deployment, Push, Release oder Galaxy-Publish wurde ausgeführt.

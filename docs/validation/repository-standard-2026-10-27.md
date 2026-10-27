# Repository-Abgleich am 27.10.2026

Vor der Umsetzung wurden Zuständigkeit und Vertrag zwischen den parallel arbeitenden Chats für Infrastructure, Database, Monitoring und Proxmox abgestimmt. Infrastructure koordiniert den gemeinsamen Standard und übernimmt K3s. Dieser Chat hat ausschließlich Database geändert. `ansible-collection-default-server` ist ein Symlink auf Infrastructure und kein zusätzlich zu pflegendes Repository.

## Änderungen

- Gemeinsamer Vertrag `degitag-collections-v1` unter `docs/repository-standard.md`.
- Einheitliche README-Kapitel, Root-CONTRIBUTING/SECURITY, EditorConfig und Make-Wrapper. Rollenlokale alte Molecule-Anleitungen verweisen auf den Root-Ablauf; veraltete Pre-Commit-Konfigurationen wurden entfernt. Lizenz- und Herkunftshinweise bleiben erhalten.
- Identische generische Repository-/Artefakt-/Metadatenprüfer, Sanity-Einstieg, Generator und Formatter wie im koordinierten Infrastructure-Stand. Dateihashes stehen im JSON-Nachweis.
- CI verwendet nach dem Dependency-Setup `bash tests/run_checks.sh`; Release und Smoke leiten Artefaktnamen aus `galaxy.yml` ab. Alle Actions bleiben SHA-gepinnt und Checkout-Credentials werden nicht persistiert.
- Syntaxprüfung umfasst alle sechs Rollen sowie Beispiel- und Integrationsplaybooks. Aktuelle optionale Firewall-Verweise verwenden `degitag.infrastructure.firewall`.
- Release-Artefakte enthalten keine Tests, Tools, Caches, Entwicklungsdokumente oder lokalen Konfigurationen. Die Prüfung kontrolliert Namespace, Name, Version, Dateigrenzen und Manifest-/Payload-Hashes. Der synthetische Galaxy-Root-Eintrag wird korrekt behandelt.

## Nachweis

`bash tests/run_checks.sh` endete unter Python 3.12.16, Ansible Core 2.21.5 und Ansible Lint 26.10.1 mit Exit-Code 0. Alle 49 Unit-Tests bestanden, davon 15 gemeinsame Regressionstests. Repository-/Scaffold-Prüfung, YAML-Lint, Build, Artefaktprüfung, Installation, Plattform-Preflight, vollständige Playbook-Syntax, Production-Lint und Compile-/Import-Sanity bestanden. `make package-smoke`, Shell-Syntax der Workflows und `git diff --check` bestanden ebenfalls.

Der Preflight validierte alle sechs Rollen auf Debian 13, Ubuntu 22.04/24.04/26.04, Rocky 9 und RedHat 9; Ubuntu 20.04 wurde ohne Änderungen abgewiesen. Die Syntaxprüfung nutzt localhost und gibt erwartete Warnungen für nicht belegte Testgruppen `database_ha`, `ha` und `baseline` aus. Es wurden keine Remote-Hosts kontaktiert. Production-Lint meldete 0 Fehler und 0 Warnungen.

Artefaktname, SHA-256, Werkzeugversionen und gemeinsame Dateihashes stehen in [repository-standard-2026-10-27.json](repository-standard-2026-10-27.json).

## Offene Abnahme

Docker ist hier nicht verfügbar; die Container-Matrix auf fünf Zielimages wurde für dieses Artefakt nicht neu ausgeführt. Native Dienste, SELinux, Reboot, Replikation, Patroni-Failover, Backup und Restore wurden nicht erneut auf VMs geprüft. Die konfigurierte Core-2.20-Matrix und die geänderten GitHub-Workflows wurden in diesem Lauf nicht auf GitHub ausgeführt. Historische Nachweise gelten nur für ihre damaligen Artefakte.

Vorhandene lokale Änderungen wurden erhalten. Es gab keinen Commit, Push, Release, Galaxy-Publish oder produktiven Rollout. Die fertiggestellte Database-Umsetzung und ihre gemeinsamen Dateihashes wurden an den koordinierenden Infrastructure-Chat zurückgemeldet; die anderen Repositorys behalten eigene Abnahmen.

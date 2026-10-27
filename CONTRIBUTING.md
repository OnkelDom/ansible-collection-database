# Entwicklung und Beiträge

Die Collection folgt dem gemeinsamen [Repository-Standard](docs/repository-standard.md). Änderungen bleiben auf den beauftragten Umfang begrenzt; vorhandene lokale Änderungen werden erhalten.

## Controller vorbereiten

Python 3.12 bereitstellen, auf macOS beispielsweise über Homebrew:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
make prepare
```

`requirements-test.txt` enthält die Controller-Werkzeuge, `requirements.yml` die Collection-Abhängigkeiten und `requirements-dev.yml` zusätzliche Container-Testwerkzeuge. Für optionale Firewall-Integration die separat gebaute `degitag.infrastructure` installieren. Zugangsdaten und private Inventories bleiben außerhalb des Checkouts.

## Rollen ändern

Öffentliche Defaults, Argument-Specs, Plattformdaten und generierte Rollenbeispiele werden über die Scaffold-Konfiguration gepflegt:

```bash
vim tools/role_scaffold_config.yml
.venv/bin/python tools/generate_role_scaffold.py
bash tests/run_checks.sh
```

Fachliche Implementierung gehört in `roles/<rolle>/tasks/configuration.yml` und dessen Includes. Defaults müssen vor der Fact-Erhebung validieren. Neue Eingaben benötigen Typen, Listen-Elementtypen und für Secrets `no_log`. Paketinstallation, Initialisierung, Dienstführung und Datenänderungen behalten getrennte Freigaben. Lizenz- und Herkunftshinweise importierter Rollen bleiben erhalten.

## Prüfen und abnehmen

`make test`, `make ci` und `bash tests/run_checks.sh` verwenden denselben Prüfpfad. Einzelprüfungen stehen über `make lint`, `make syntax`, `make unit`, `make build` und `make package-smoke` bereit; deren Erfolg ersetzt nicht den vollständigen Lauf.

CI testet Core 2.20/2.21. Container-Smoke benötigt Docker und führt zwei Konvergenzläufe je Zielimage aus. Native Dienste, SELinux, Neustarts, Replikation, Patroni-Failover, Backup und Restore gehören auf entbehrliche VMs. Mutierende Integrationsplaybooks erfordern ein dediziertes Inventory und `database_test_disposable=true`; sie werden nicht vom lokalen Strukturprüflauf gestartet.

Unter `docs/validation/` werden Datum, Befehl, Werkzeugversionen, Artefaktidentität, Ergebnis und offene Lücken dokumentiert. Historische Nachweise werden nicht als Abnahme neuer Artefakte umetikettiert. Logs müssen frei von Zugangsdaten, privaten Schlüsseln und produktiven Hostdaten sein.

## Review und Release

Beiträge beschreiben das betriebliche Problem, die resultierende Änderung, notwendige Migrationen und tatsächlich ausgeführte Prüfungen. Datenverzeichnis-Löschung, DCS-Reset, Schlüsselrotation, Datenmigration und Cluster-Mitgliedschaft erfordern einen separaten geprüften Betreiberablauf.

Ein Release-Tag muss `v<version>` aus `galaxy.yml` entsprechen und durchläuft die CI. Commit, Push, Veröffentlichung und produktives Deployment benötigen den jeweiligen Auftrag; ein Refactoring autorisiert sie nicht automatisch.

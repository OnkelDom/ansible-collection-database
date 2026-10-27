# Validierung der Database-Collection 2.0.0

Aktueller Struktur-/Werkzeugnachweis: [Repository-Abgleich vom 27.10.2026](repository-standard-2026-10-27.md). Die [Namespace-Umbenennung](namespace-rename-2026-10-27.md) ist separat dokumentiert. Die folgenden Laufzeitnachweise und JSON-Dateien beschreiben den historischen Stand vom 19.10.2026 und dessen damaliges Artefakt.

Stand: 19. Oktober 2026. Die Ergebnisse stammen aus lokalen Prüfungen und sieben eigens angelegten, isolierten Proxmox-Testgästen. Produktivsysteme wurden nicht verändert. Die maschinenlesbaren Nachweise liegen in [results.json](results.json) und [shared-standard.json](shared-standard.json).

## Prüfvertrag der vier Collections

Infrastructure, Monitoring, K3s und Database verwenden `bash tests/run_checks.sh`. Der aktuelle Lauf bestand mit Python 3.12, Ansible Core 2.21.5 und Ansible Lint 26.10.1: Generatorprüfung, insgesamt 122 Unit-Tests (44/30/14/34), YAML-Lint, Rollen-Syntax mit Play-Facts, Production-Lint, Artefaktprüfung und Installation sowie `ansible-test sanity` für Compile/Import. Die jeweiligen `shared-standard.json` dokumentieren die Artefaktidentität. Diese gemeinsame Prüfung bestätigt den Struktur- und Werkzeugvertrag; vorhandene Laufzeitnachweise der Schwester-Collections behalten ihren eigenen Umfang.

Der zusätzliche Database-Lauf unter Ansible Core 2.20 bestand Rollen-Syntax und Plattform-Preflight. Das finale Build-Artefakt bestand Container-Smoke-Tests auf allen fünf freien Zielimages; jeder zweite Lauf blieb bei `changed=0`. Hash und Einzelergebnisse stehen in `results.json`. Container bestätigen dabei keine Dienststarts, Netzwerk- oder SELinux-Funktion.

## Native Laufzeitprüfungen

| Umfang | Ergebnis |
| --- | --- |
| MariaDB, PostgreSQL, Redis und Memcached auf Debian 13, Ubuntu 22.04/24.04/26.04 und Rocky 9 | Installation, native Dienste, SQL-/Cache-Proben erfolgreich; abschließender Wiederholungslauf auf allen fünf Systemen `changed=0` |
| Neustart aller fünf Betriebssysteme | Dienste und gespeicherte Testdaten anschließend geprüft |
| Rocky Linux 9 | SELinux blieb `Enforcing` |
| Konfigurationsänderung bei bewusst gestoppten Diensten | Dienstschalter und Handler respektiert; kein unbeabsichtigter Start |
| Initialisierung von MariaDB, PostgreSQL, Patroni und etcd ohne Freigabe | Vor Paketänderungen abgewiesen, `changed=0` |
| Patroni-Übernahme eines aktiven nativen PostgreSQL ohne Freigabe | Vor Paketänderungen abgewiesen, `changed=0` |
| Entfernen bestehender MariaDB-Verschlüsselung bzw. ungeeignetes Sentinel-Passwort | Abgewiesen, `changed=0` |

## Patroni und verwaltetes etcd

Drei Ubuntu-24.04-Knoten verwendeten einen von der Collection installierten etcd-v3-Cluster mit Client- und Peer-TLS sowie PostgreSQL unter Patroni. Bootstrap und Wiederholungslauf mit SQL-Objekten und Backupkonfiguration konvergierten auf allen drei Knoten mit `changed=0`.

Der abrupte Stopp der Primary-VM führte nach 37,13 Sekunden zu einem neuen Primary. Eine zuvor bestätigte Zeile blieb verfügbar. Verschlüsseltes Backup und Restore wurden am neuen Primary geprüft; der alte Primary trat anschließend als Replica bei. Nach Abschalten zweier etcd-Mitglieder gab es keinen schreibbaren Primary mehr. Nach Wiederherstellung des Quorums bestand wieder ein gesunder Verbund aus einem Primary und zwei Replicas.

Ein Neustart bestätigte, dass die native PostgreSQL-Unit maskiert bleibt und nicht mit Patroni konkurriert. Der Backupjob konnte einen bewusst gestoppten Patroni-Dienst nicht starten. Nach den letzten Änderungen an den frühen Übernahmeprüfungen wurden bestehende Daten positiv im Check-Modus sowie alle negativen Initialisierungsfälle erneut geprüft.

## Weitere Daten- und Recoveryprüfungen

MariaDB-Replikation übertrug eine Testzeile; native Tabellenverschlüsselung war aktiv. Atomare Dumps wurden auf einem separaten, verschlüsselungsfähigen Server wiederhergestellt und die Daten geprüft. Die Retention begrenzte eigene Snapshots auf zwei Dateien.

Redis Sentinel wählte nach Primary-Ausfall nach 7,23 Sekunden einen Nachfolger. Die replizierte Testzeile blieb erhalten, der bisherige Primary kehrte als Replica zurück. Ein anschließender Rollenlauf erhielt die gewählte Topologie auf allen drei Knoten mit `changed=0`.

## Reproduzierbarkeit

Für lokale Strukturprüfungen zuerst die eigene `.venv` und die Collections gemäß Repository-README installieren, anschließend `bash tests/run_checks.sh` ausführen. Die Playbooks in `tests/integration/` erfordern für mutierende Laufzeittests ausdrücklich `database_test_disposable=true`, ein dediziertes Inventory und passende Secret-Store-Eingaben. HA-, Backup- und Failoverprüfungen gehören ausschließlich auf entbehrliche Testsysteme. Zugangsdaten, private Test-PKI und produktive Inventories werden nicht eingecheckt.

## Grenzen der Abnahme

Ein Rocky-Test ersetzt keinen Test auf abonniertem RHEL 9. RHEL wurde nur über synthetische Plattform-Facts geprüft. ARM wurde nicht ausgeführt. HA, Replikation und Verschlüsselung wurden auf Ubuntu 24.04 geprüft; daraus folgt keine vollständige Abnahme dieser Funktionen auf jeder Distribution. Produktions-PKI, PostgreSQL-Verbindungs-TLS, Patroni-REST-TLS, Watchdog/Fencing, größere Versionsmigrationen und sämtliche DDL-Kombinationen benötigen eigene Abnahmefälle.

Die GitHub-Workflows sind lokal vorbereitet; sie wurden nicht auf GitHub ausgeführt. Es gab keinen Commit, Push oder Release.

## Bereinigung

Alle sieben anhand von Name, Tag und Beschreibung identifizierten Test-VMs sowie ihre Seed-ISOs und der zugehörige Image-Cache wurden entfernt; ihre Abwesenheit wurde geprüft. Temporäre private Test-PKI, Test-Secrets und der lokale Restore-Dump wurden ebenfalls gelöscht. Bereinigte Ergebnisdateien bleiben als Nachweis erhalten.

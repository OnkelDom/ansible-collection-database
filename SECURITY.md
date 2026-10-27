# Sicherheit

## Schwachstellen melden

Sicherheitsprobleme vertraulich über die private Schwachstellenmeldung des [GitHub-Repositories](https://github.com/degitag/ansible-collection-database/security) melden, sofern aktiviert. Andernfalls den Maintainer über einen bereits bekannten privaten Kontaktkanal erreichen. Öffentliche Issues und Pull Requests dürfen keine ausnutzbaren Details, Tokens, Passwörter, Inventories oder Datenbankinhalte enthalten.

Eine Meldung soll betroffene Version, Rolle, Plattform, Voraussetzungen und einen bereinigten reproduzierbaren Ablauf enthalten. Kein produktives System allein zur Reproduktion verändern.

## Secrets und Betriebsgrenzen

Secrets stammen aus Ansible Vault oder einem Secret Store. Secret-verarbeitende Tasks verwenden `no_log`; Zugangsdaten gehören weder in Defaults noch in Logs, Testfixtures oder Artefakte. Private PKI und produktive Inventories bleiben außerhalb des Repositorys. Bei einem offengelegten Secret muss der Betreiber es über den zuständigen Secret Store widerrufen bzw. rotieren.

Datenbank- und Cache-Listener sind standardmäßig lokal. Host-Netzwerk und additive Firewall-Regeln verwaltet `degitag.infrastructure`. SELinux bleibt auf EL9 aktiviert. Initialisierung und externe Binärinstallation benötigen explizite Schalter; Downloads werden anhand versionsgebundener Prüfsummen geprüft.

Datenverzeichnisse, DCS-Zustand, Verschlüsselungsschlüssel und Cluster-Mitgliedschaften dürfen nicht implizit geändert oder entfernt werden. Im HA-Betrieb ist Patroni der alleinige PostgreSQL-Dienstführer. Backup, Restore und geplante Datenmigrationen erfordern einen geprüften Betreiberablauf und isolierte Abnahme.

## Nachweise

Der tatsächlich geprüfte Stand und offene Lücken stehen unter [docs/validation](docs/validation/). Ein grüner Strukturprüflauf bestätigt keine vollständige Laufzeit- oder Sicherheitsabnahme auf allen Plattformen. Produktions-PKI, Watchdog/Fencing, Wire-TLS und Wiederherstellung benötigen eigene Tests. Automatisierte Prüfungen veröffentlichen weder nach Galaxy noch in produktive Umgebungen.

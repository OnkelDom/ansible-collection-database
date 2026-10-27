# Migration zu degitag.database 2

## Namespace und Controller

`degit.database`, `onkeldom.database` und `lenmail.database` werden durch `degitag.database` ersetzt. GitHub-Ziel ist `degitag/ansible-collection-database`. Die vier Collections verwenden denselben Rollenaufbau, dieselbe Zielmatrix und denselben lokalen Prüfaufruf. Bestehende Inventory-Eingaben vor einem Rollout anhand der jeweiligen Argument-Specs überprüfen.

Controller installieren das neue Artefakt `degitag-database-2.0.0.tar.gz`. In Requirements, Playbooks und Rollenaufrufen muss `degit.database` durch `degitag.database` ersetzt werden; beispielsweise wird `degit.database.postgresql` zu `degitag.database.postgresql`. Der alte Namespace wird nicht als Alias bereitgestellt. Beide Namespaces können auf dem Controller parallel installiert sein; entscheidend ist der vollständige Rollenname im aufrufenden Playbook.

Die Umbenennung ändert keine Rollenvariablen, Datenverzeichnisse, DCS-Identitäten oder bereits verwendeten `degit`-Dateinamen und Sicherheitsmarker auf Zielsystemen. `degitag.infrastructure.firewall` bleibt eine separat versionierte externe Rollenreferenz. Die Umbenennung dieser Collection migriert keine Geschwister-Collection.

## Native Pakete und sichere Defaults

Fremdrepositories, systemweite pip-Installation und implizite Datenbank-Hauptversions-Upgrades entfallen. Bestehende Fremdrepositories werden nicht automatisch entfernt. MariaDB-Version bleibt leer; PostgreSQL verwendet die zur Distribution gehörige Hauptversion. Abweichende Paketquellen und Upgrades müssen vorab durch den Betreiber geplant werden. Leere `*_packages`-Listen wählen Plattformpakete, explizite Listen überschreiben diese.

MariaDB und PostgreSQL initialisieren nur mit `*_initialize: true`; vorhandene Daten werden nie geleert. SQL- und Redis-Listener sind standardmäßig lokal. Root-Socket-Authentifizierung bleibt erhalten. Administratorpasswörter werden nur auf ausdrücklichen Wunsch gesetzt. Verschlüsselung verwendet vorab bereitgestellte Schlüssel; automatische Rotation und Überschreiben bestehender Schlüssel sind gesperrt.

## Dienste und Netzwerk

`*_manage_service`, `*_service_enabled`, `*_service_state` gelten für Tasks und Handler. `manage_service: false` erlaubt Paket-/Konfigurationsverwaltung ohne explizite Dienststeuerung; deklarierte SQL-Objekte erfordern einen laufenden Dienst. Memcached und Redis verwenden native Dienste statt angelegter Instanz-Units. Vorhandene selbstgebaute Units und maskierte Dienste werden nicht automatisch entfernt oder ersetzt; deren Übergabe ist ein eigener Migrationsschritt.

Firewall-Verwaltung ist optional und benötigt explizite Quellnetze. Die Regeln bleiben additiv und verwenden `degitag.infrastructure.firewall`.

## PostgreSQL-HA

Die bisherigen `postgresql_replication*`- und Uninstall-Pfade werden abgewiesen. Patroni ist der alleinige HA-Dienstführer und verwendet einen separat verwalteten etcd-v3-Cluster. Der bisherige native Dienst muss in einer freigegebenen Übergabe gestoppt werden. Major-Version, Datenbestand, System-Identifier, Authentifizierung und DCS-Scope müssen vor einer Adoption geprüft werden. Keine automatische Reinitialisierung, kein Löschen des Datenverzeichnisses und kein Zurücksetzen des DCS.

`bootstrap.dcs` wirkt nur beim ersten Anlegen eines Scopes. Laufende Cluster werden über `patronictl edit-config` geändert; ein YAML-Render ist kein Nachweis für eine Änderung der DCS-Konfiguration. etcd-Mitgliedschaften werden mit einem geplanten `etcdctl member add/remove`-Verfahren geändert, nicht allein durch Änderung der Initial-Cluster-Liste.

## Backups und erweiterte Funktionen

Vorhandene MariaDB-Replikation, Verschlüsselung und Backups sowie PostgreSQL-Objektverwaltung, Tuning und Backups bleiben als explizite APIs erhalten. PostgreSQL-Tuning über einen externen Dienst ist standardmäßig aus. Backups sind standardmäßig aus; Restore-Tests brauchen eine getrennte Freigabe und dürfen keine verwaltete Anwendungsdatenbank als Ziel verwenden. HA-Backups werden mit patroni_manage_backup explizit aktiviert und laufen ausschließlich auf dem aktuellen Primary; automatische Restore-Jobs benötigen weiterhin eine eigene Freigabe. Import, Dump, Restore und Rename benötigen *_allow_data_migration=true.

MariaDB-Backups verwenden native mariadb-dump-Aufrufe und atomar abgeschlossene Snapshot-Verzeichnisse. Retention entfernt ausschließlich eigene markierte Snapshots. Cron-Zeitpläne benötigen *_manage_backup_schedule=true; PostgreSQL-Systemd-Timer benötigen postgresql_manage_backup_timers=true. Die reine Aktivierung der Backup-Konfiguration legt keinen aktiven Zeitplan an.

Bei Redis/Sentinel bleibt die von Sentinel umgeschriebene Redis-Konfiguration nach der ersten Übergabe erhalten. Normale Rollenläufe setzen einen erfolgten Failover nicht zurück. Konfigurations- und Passwortrotation verlangen redis_sentinel_allow_reconfigure=true und einen geplanten rollierenden Ablauf mit aktuellen Primär-/Replica-Eingaben. Der native Backup-Standardpfad für MariaDB ist /var/backups/mariadb; frühere eigene Sicherungsverzeichnisse werden nicht entfernt.

Redis/Sentinel verlangt mindestens 20 Zeichen aus A–Z, a–z, 0–9, Unterstrich und Bindestrich als Passwort. Native Sentinel-Versionen schreiben auth-pass ohne schützende Quotes zurück; Leerzeichen oder Quotes würden den folgenden Neustart verhindern. Die Rolle verwirft solche Eingaben vor Änderungen. Standalone-Redis maskiert Sonderzeichen in der Konfiguration.

Eine bereits an Sentinel übergebene Redis-Instanz kann nicht durch leere Defaults zu Standalone zurückgesetzt werden. Ein geplanter clusterweiter Übergang benötigt redis_sentinel_allow_reconfigure=true; der lokal verwaltete Sentinel wird dann gestoppt und deaktiviert. Bei externer Dienstführung muss er vorher durch den Betreiber gestoppt sein. Fremde Sentinel-Konfigurationen werden nicht gelöscht.

# PostgreSQL-HA mit Patroni und etcd

## Verantwortlichkeiten

Drei etcd-Mitglieder stellen den Konsens bereit. Drei PostgreSQL-/Patroni-Knoten verwenden denselben Scope, dieselbe PostgreSQL-Hauptversion und denselben DCS. etcd und Patroni können auf getrennten oder denselben Hosts laufen; unabhängige Ausfallzonen und ein getestetes Quorum sind entscheidend. Ein einzelner etcd-Knoten ist ausschließlich für Entwicklung geeignet.

`postgresql` installiert native Datenbankpakete. In Patroni-Modus legt die Rolle keinen Standalone-Cluster an und steuert keinen PostgreSQL-Dienst. `patroni` ist alleiniger Dienstführer, übernimmt Leaderwahl und Replikation und löscht vorhandene Datenverzeichnisse nicht. `etcd` ersetzt oder entfernt keine bestehenden Mitglieder.

## Voraussetzungen

Alle Knoten benötigen stabile Hostnamen, private erreichbare Adressen und synchronisierte Zeit. Clientzugriff wird auf das aktuelle Primary geroutet, beispielsweise durch einen separat verwalteten HAProxy mit Patroni-Healthchecks. Die Rollen konfigurieren keinen produktiven VIP oder Load-Balancer implizit.

CA, Server-/Peer-Zertifikate und Schlüssel werden vor dem Rollenlauf durch die eigene PKI bereitgestellt. Die Zertifikate müssen passende SANs und für etcd-Peers auch Clientauthentifizierung erlauben. etcd-Schlüssel müssen für den Benutzer `etcd`, Patroni-DCS-Schlüssel für `postgres` lesbar sein. Private Schlüssel bleiben `0600` oder `0640` mit einer passenden dedizierten Gruppe. Die Rolle erzeugt keine produktive CA.

Patroni wird aus dem offiziellen PyPI-Projekt versionsgebunden in `/opt/patroni` installiert. etcd-Binaries stammen aus den offiziellen GitHub-Releases und werden gegen die im Repository hinterlegten SHA-256-Werte geprüft. Neue Versionen erfordern eine aktualisierte Prüfsumme und Abnahme.

## Inventory-Beispiel

```yaml
all:
  children:
    database_ha:
      hosts:
        db1:
          ansible_host: 192.0.2.11
        db2:
          ansible_host: 192.0.2.12
        db3:
          ansible_host: 192.0.2.13
      vars:
        etcd_install: true
        etcd_initialize: true
        etcd_initial_cluster_token: example-database-cluster
        etcd_initial_cluster:
          db1: https://192.0.2.11:2380
          db2: https://192.0.2.12:2380
          db3: https://192.0.2.13:2380
        etcd_listen_client_urls: ["https://{{ ansible_host }}:2379"]
        etcd_advertise_client_urls: ["https://{{ ansible_host }}:2379"]
        etcd_listen_peer_urls: ["https://{{ ansible_host }}:2380"]
        etcd_initial_advertise_peer_urls: ["https://{{ ansible_host }}:2380"]
        etcd_ca_file: /etc/pki/database/ca.crt
        etcd_cert_file: /etc/pki/database/etcd-server.crt
        etcd_key_file: /etc/pki/database/etcd-server.key
        etcd_peer_ca_file: /etc/pki/database/ca.crt
        etcd_peer_cert_file: /etc/pki/database/etcd-peer.crt
        etcd_peer_key_file: /etc/pki/database/etcd-peer.key
        patroni_scope: application-db
        patroni_bootstrap: true
        patroni_etcd_hosts:
          - 192.0.2.11:2379
          - 192.0.2.12:2379
          - 192.0.2.13:2379
        patroni_etcd_ca_file: /etc/pki/database/ca.crt
        patroni_etcd_cert_file: /etc/pki/database/patroni-client.crt
        patroni_etcd_key_file: /etc/pki/database/patroni-client.key
        patroni_rest_listen: "{{ ansible_host }}:8008"
        patroni_rest_connect_address: "{{ ansible_host }}:8008"
        patroni_rest_cert_file: /etc/pki/database/patroni-api.crt
        patroni_rest_key_file: /etc/pki/database/patroni-api.key
        patroni_rest_password: "{{ vault_patroni_rest_password }}"
        patroni_postgresql_listen: "{{ ansible_host }}:5432"
        patroni_postgresql_connect_address: "{{ ansible_host }}:5432"
        patroni_superuser_password: "{{ vault_postgresql_superuser_password }}"
        patroni_replication_password: "{{ vault_postgresql_replication_password }}"
        patroni_pg_hba:
          - local all all peer
          - hostssl replication replicator 192.0.2.0/24 scram-sha-256
          - hostssl application application 198.51.100.0/24 scram-sha-256
        patroni_parameters:
          ssl: "on"
          ssl_cert_file: /etc/pki/database/postgresql.crt
          ssl_key_file: /etc/pki/database/postgresql.key
```

Dokumentationsnetze durch die eigene Topologie ersetzen. PostgreSQL-TLS-Material muss für `postgres` lesbar sein. Portregeln werden bei Bedarf explizit mit `*_manage_firewall` und Quellnetzen freigegeben; Host-Netzwerk, Routing und Zertifikatsverteilung bleiben beim Betreiber.

## Playbook

```yaml
- name: Configure the consensus quorum
  hosts: database_ha
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.etcd

- name: Configure PostgreSQL HA
  hosts: database_ha
  become: true
  gather_facts: true
  roles:
  - role: degitag.database.patroni
```

Beim ersten Quorum-Aufbau die Mitglieder parallel starten. Einen laufenden Cluster nur kontrolliert und mit erhaltenem Quorum ändern. `bootstrap`/`initialize` nach erfolgreicher Inbetriebnahme wieder deaktivieren; bestehende Daten werden anhand der vorhandenen Initialisierung wiederverwendet.

## Datenübernahme und Änderungen

Eine bestehende Standalone-Instanz darf nicht automatisch adoptiert werden. Vor einer ausdrücklich freigegebenen Übernahme Backup und Restore prüfen, native Dienstführung stoppen, Hauptversion/System-Identifier/DCS-Scope vergleichen und `patroni_allow_adopt_existing` gezielt setzen. Patroni und der native Dienst dürfen dieselbe Instanz nie gleichzeitig starten. Die Rolle verweigert einen laufenden nativen Dienst.

`bootstrap.dcs` gilt nur beim ersten Anlegen des Scopes. Anschließende Clusteränderungen erfolgen über `patronictl edit-config`; ein verändertes Template allein ändert den bereits gespeicherten DCS-Vertrag nicht. Ein geänderter Scope oder eine geänderte initiale etcd-Mitgliedschaft wird durch die Rollen nicht stillschweigend übernommen. Membership-Änderungen benötigen einen eigenen `etcdctl member add/remove`-Ablauf.

## Backups, Failover und Abnahme

Patroni-Replikation ist kein Backup. Bestehende PostgreSQL-Backupfunktionen werden unabhängig vom HA-Rollout verwendet; bei HA muss der gewählte Sicherungspfad mit Primary-Wechsel, WAL-Verfügbarkeit und dem Restore-Ziel umgehen. Ein Restore-Test arbeitet ausschließlich auf einer dafür reservierten Datenbank.

Vor Freigabe sind mindestens zu prüfen: etcd-Endpoint-Health mit TLS, genau ein PostgreSQL-Primary, gestreamte Replikation, Lese-/Schreibprobe über den Clientpfad, Wiederholung mit `changed=0`, geplanter Switchover, Verlust eines Primary, Wiederbeitritt des bisherigen Primary, Quorumverlust, kontrollierter Reboot sowie ein echter Backup-/Restore-Test. Synchrone Replikation und `patroni_synchronous_mode_strict` werden nach RPO-/Verfügbarkeitsanforderung gewählt. Ein geeigneter Watchdog-/Fencing-Pfad muss getrennt validiert werden; der Rollenstandard aktiviert keinen unbekannten Watchdog.

Aktuelle Ergebnisse und Grenzen stehen in [Validierung](validation/README.md).

## Objektverwaltung und HA-Backups

`patroni_manage_objects: true` führt die `postgresql_users`, Datenbanken, Schemas und Berechtigungen ausschließlich auf dem ermittelten Primary aus. Die Variablen entsprechen dem PostgreSQL-Rollenvertrag. Der Primary wird vor den Aufgaben abgefragt; eine laufende Migration während eines Failovers braucht weiterhin einen eigenen abgestimmten Ablauf.

Mit `patroni_manage_backup: true` werden die bestehenden PostgreSQL-Backupfunktionen auf jedem Mitglied eingerichtet. Die Skripte prüfen lokal `pg_is_in_recovery()` und arbeiten nur auf dem aktuellen Primary. Dadurch folgt der Sicherungszeitplan einem Primary-Wechsel. `postgresql_backup_implementation`, Datenbankliste, Verschlüsselung und Retention bleiben explizite PostgreSQL-Eingaben. Der Backup-Systemd-Dienst läuft nur bei aktivem Patroni und startet einen bewusst gestoppten Controller nicht. Restore-Tests verwenden einen reservierten Präfix plus eine eindeutige Prozesskennung; sie löschen keine bestehende gleichnamige Anwendungsdatenbank. Separate Speicherziele und eine über Failover hinweg verfügbare Sicherungskopie müssen im Infrastrukturdesign vorgesehen werden.

## Technische Referenzen

- [Patroni-Konfigurationsvertrag](https://patroni.readthedocs.io/en/latest/yaml_configuration.html)
- [etcd-Transportabsicherung](https://etcd.io/docs/v3.6/op-guide/security/)

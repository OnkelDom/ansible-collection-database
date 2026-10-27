from pathlib import Path
import re
import yaml
import pytest

ROOT = Path(__file__).resolve().parents[2]
ROLES = sorted(p.name for p in (ROOT / 'roles').iterdir() if p.is_dir())

@pytest.mark.parametrize('role', ROLES)
def test_public_defaults_have_a_complete_typed_contract(role):
    defaults = yaml.safe_load((ROOT / f'roles/{role}/defaults/main.yml').read_text())
    spec = yaml.safe_load((ROOT / f'roles/{role}/meta/argument_specs.yml').read_text())['argument_specs']['main']['options']
    assert set(defaults) == set(spec)
    for key, value in defaults.items():
        assert value is not None, key
        assert spec[key]['type']
        if isinstance(value, list):
            assert spec[key]['elements']
        if key.endswith(('_password', '_passphrase', '_secret')):
            assert spec[key]['no_log']

@pytest.mark.parametrize('role', ROLES)
def test_restart_handlers_respect_service_ownership_and_state(role):
    handlers = yaml.safe_load((ROOT / f'roles/{role}/handlers/main.yml').read_text())
    for task in handlers:
        if any(isinstance(value, dict) and value.get('state') == 'restarted' for value in task.values()):
            assert f'{role}_manage_service' in task['when']
            assert f"{role}_service_state == 'started'" in task['when']

@pytest.mark.parametrize('role', ROLES)
def test_preflight_and_all_platform_layers_exist(role):
    role_path = ROOT / 'roles' / role
    for filename in ['Debian.yml', 'Debian-13.yml', 'Ubuntu.yml', 'Ubuntu-22.04.yml', 'Ubuntu-24.04.yml', 'Ubuntu-26.04.yml', 'RedHat.yml', 'RedHat-9.yml', 'Rocky.yml', 'Rocky-9.yml']:
        assert (role_path / 'vars/platform' / filename).is_file()
    tasks = yaml.safe_load((role_path / 'tasks/preflight.yml').read_text())
    assert tasks[0]['name'] == 'Collect missing platform facts'
    assert tasks[1]['ansible.builtin.assert']['that']


def test_no_replica_path_can_remove_an_existing_data_directory():
    for path in (ROOT / 'roles/postgresql/tasks').rglob('*.yml'):
        text = path.read_text()
        assert 'state: absent' not in text or '_postgresql_data_dir' not in text
    patroni = yaml.safe_load((ROOT / 'roles/patroni/vars/main.yml').read_text())['_patroni_configuration']
    assert patroni['postgresql']['remove_data_directory_on_rewind_failure'] is False
    assert patroni['postgresql']['remove_data_directory_on_diverged_timelines'] is False


def test_sql_defaults_do_not_enable_network_wide_access_or_embedded_passwords():
    maria = yaml.safe_load((ROOT / 'roles/mariadb/defaults/main.yml').read_text())
    pg = yaml.safe_load((ROOT / 'roles/postgresql/defaults/main.yml').read_text())
    redis = yaml.safe_load((ROOT / 'roles/redis/defaults/main.yml').read_text())
    assert maria['mariadb_bind_address'] == '127.0.0.1'
    assert pg['postgresql_listen_addresses'] == 'localhost'
    assert redis['redis_server_bind'] == ['127.0.0.1', '::1']
    assert not maria['mariadb_admin_force_password_update']
    assert not pg['postgresql_autotune']


def test_etcd_release_has_strong_per_architecture_checksums():
    variables = yaml.safe_load((ROOT / 'roles/etcd/vars/main.yml').read_text())
    for architectures in variables['_etcd_checksums'].values():
        assert set(architectures) == {'amd64', 'arm64'}
        assert all(re.fullmatch(r'sha256:[a-f0-9]{64}', digest) for digest in architectures.values())


def test_ha_defaults_require_explicit_bootstrap_and_secret_inputs():
    patroni = yaml.safe_load((ROOT / 'roles/patroni/defaults/main.yml').read_text())
    etcd = yaml.safe_load((ROOT / 'roles/etcd/defaults/main.yml').read_text())
    assert not patroni['patroni_bootstrap']
    assert not patroni['patroni_allow_adopt_existing']
    assert not etcd['etcd_initialize']
    assert etcd['etcd_tls_enabled']
    assert not patroni['patroni_superuser_password']
    assert not patroni['patroni_etcd_hosts']


def test_no_legacy_fact_aliases_or_direct_firewall_backends():
    for role in ROLES:
        for path in (ROOT / 'roles' / role / 'tasks').rglob('*.yml'):
            text = path.read_text()
            assert not re.search(r'\bansible_(distribution|os_family|pkg_mgr|default_ipv4)\b', text)
            assert 'community.general.ufw:' not in text
            assert 'ansible.posix.firewalld:' not in text


def test_ha_handlers_do_not_interrupt_a_fresh_cluster_bootstrap():
    for role in ['patroni', 'etcd']:
        handlers = yaml.safe_load((ROOT / f'roles/{role}/handlers/main.yml').read_text())
        restart = next(task for task in handlers if task['name'] == 'Restart ' + role)
        assert f'_{role}_was_running | default(false)' in restart['when']


def test_restore_uses_a_unique_database_and_ha_backup_follows_the_primary():
    template = (ROOT / 'roles/postgresql/templates/postgresql-custom-backup.sh.j2').read_text()
    assert 'RESTORE_DB_PREFIX}_$$' in template
    assert 'pg_is_in_recovery()' in template
    assert 'dropdb --if-exists "${RESTORE_DB}"\n  createdb' not in template
    tasks = yaml.safe_load((ROOT / 'roles/patroni/tasks/objects-backup.yml').read_text())
    backup = next(task for task in tasks if 'backup jobs' in task['name'])
    assert backup['vars']['_postgresql_daemon'] == 'patroni'
    assert backup['vars']['postgresql_backup_primary_only'] is True


def test_sentinel_failover_state_is_not_overwritten_on_normal_reruns():
    tasks = yaml.safe_load((ROOT / 'roles/redis/tasks/configuration.yml').read_text())
    render = next(task for task in tasks if task['name'] == 'Render Redis service configuration')
    assert render['when'] == 'not redis_sentinel_enabled or not _redis_sentinel_owned.stat.exists or (redis_sentinel_allow_reconfigure | bool)'
    defaults = yaml.safe_load((ROOT / 'roles/redis/defaults/main.yml').read_text())
    assert defaults['redis_sentinel_allow_reconfigure'] is False


def test_sentinel_rejects_passwords_that_native_rewrites_cannot_preserve():
    from jinja2 import Environment
    tasks = yaml.safe_load((ROOT / 'roles/redis/tasks/validate.yml').read_text())
    conditions = tasks[0]['ansible.builtin.assert']['that']
    expression = next(value for value in conditions if 'A-Za-z0-9_-' in value)
    environment = Environment()
    environment.tests['match'] = lambda value, pattern: re.match(pattern, value) is not None
    validate = environment.compile_expression(expression)
    assert validate(redis_sentinel_enabled=True, redis_server_password='long_URL_safe_fixture_123456789')
    assert not validate(redis_sentinel_enabled=True, redis_server_password='unsafe password with spaces')
    assert not validate(redis_sentinel_enabled=True, redis_server_password='short')


def test_scheduled_backups_cannot_start_an_intentionally_stopped_database():
    for name in ['postgresql-backup.service.j2', 'postgresql-restore-test.service.j2']:
        unit = (ROOT / 'roles/postgresql/templates' / name).read_text()
        assert 'Requires=' not in unit
        assert 'ExecCondition=/usr/bin/systemctl is-active --quiet {{ _postgresql_daemon }}.service' in unit

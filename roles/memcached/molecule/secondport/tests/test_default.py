#!/usr/bin/env python

import os
import stat
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_pkg(host):
    pkg = host.package("memcached")
    assert pkg.is_installed

def default_service_out(host):
    default_service = host.service("memcached.service")
    assert not default_service.is_running
    assert not default_service.is_enabled
    assert default_service.is_masked

def test_svc(host):
    for port in ['11211', '11212']:
        svc = host.service(f"memcached@{port}.service")
        assert svc.is_running
        assert svc.is_enabled

def test_listen_memcached(host):
    assert host.socket("tcp://127.0.0.1:11211").is_listening
    assert host.socket("tcp://127.0.0.1:11212").is_listening

def test_conf_files_exist(host):
    assert host.file("/etc/default/memcached_11211").exists
    assert host.file("/etc/default/memcached_11212").exists

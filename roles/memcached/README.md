# Ansible role - memcached
[![Maintainer](https://img.shields.io/badge/maintained%20by-claranet-e00000?style=flat-square)](https://www.claranet.fr/)
[![License](https://img.shields.io/github/license/claranet/ansible-role-memcached?style=flat-square)](LICENSE)
[![Release](https://img.shields.io/github/v/release/claranet/ansible-role-memcached?style=flat-square)](https://github.com/claranet/ansible-role-memcached/releases)
[![Status](https://img.shields.io/github/actions/workflow/status/claranet/ansible-role-memcached/molecule.yml?style=flat-square&label=tests&branch=main)](https://github.com/claranet/ansible-role-memcached/actions?query=workflow%3A%22Ansible+Molecule%22)
[![Ansible version](https://img.shields.io/badge/ansible-%3E%3D2.10-black.svg?style=flat-square&logo=ansible)](https://github.com/ansible/ansible)
[![Ansible Galaxy](https://img.shields.io/badge/ansible-galaxy-black.svg?style=flat-square&logo=ansible)](https://galaxy.ansible.com/claranet/memcached)

> :star: Star us on GitHub — it motivates us a lot!*

Install and configure Memcached.
## :warning: Requirements

Ansible >= 2.10

This role allows multiple instances of memcached to be installed on the same machine (in the same version).
Just import the role several times as explained in the examples below. The role allows you to configure any memcached launch option.
## :zap: Installation

```bash
ansible-galaxy collection install lenmail.database
```

## :gear: Role variables

Variable                        | Default value        | Description
--------------------------------|----------------------|------------
memcached_verbose               | **true**             | Verbose mode for memcached
memcached_memory                | **64**               | Max memory can be used (in MB)
memcached_port                  | **11211**            | Listen port
memcached_user                  | **null**             | Sets the Unix user that the process is executed as. Takes a single user name
memcached_listen                | **[127.0.0.1]**      | List of listen addresses
memcached_maxconn               | **1024**             | Max acceptable connections
memcached_extra_options         | **[]**               | List of additional options
memcached_restart               | **false**            | Restarts memcached when the configuration changes

## :arrows_counterclockwise: Dependencies

N/A

## :pencil2: Example Playbook

The playbook below instantiates two instances of memcached on two different ports. The `memcached_extra_options` variable allows you to add launch options (here `-t 8`).

```yaml
- name: bootstrap instance
  hosts: all
  become: true
  tasks:
    - include_role:
        name: memcached
      vars:
        memcached_restart: true
        memcached_extra_options:
          - t 8
    - include_role:
        name: memcached
      vars:
        memcached_port: 11212
```

## :closed_lock_with_key: [Hardening](HARDENING.md)

## :heart_eyes_cat: [Contributing](CONTRIBUTING.md)

## :copyright: [License](LICENSE)

[Mozilla Public License Version 2.0](https://www.mozilla.org/en-US/MPL/2.0/)

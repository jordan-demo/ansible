# This is my Ansible Documentation December 2021

## ansible.cfg

Configuration file will be search in the following order:

1. ANSIBLE_CONFIG (environment variable if set)
2. ansible.cfg (in the current directory)
3. ~/.ansible.cfg (in the home directory)
4. /etc/ansible/ansible.cfg

```cfg
# ansible.cfg
inventory = ./inventory.ini
```

## Inventory.ini

The default inventory file is located in /etc/ansible/hosts, but that can be changed in ansible.cfg, or with -i /path/to/file using the command line.

```ini
# hosts

[web]
app1 ansible_host=10.10.24.200
app2 ansible_host=10.10.24.201

[lb]
lb1 ansible_host=10.10.24.202:22

[local]
control ansible_connection=local
```

```bash
ansible -m ping all # ping all hosts in the inventory file, if there is an error, check  the inventory = ./inventory.ini in ansible.cfg

ansible --list-hosts web # lists the hosts in ghe group web
ansible  
```

Target specific group from the inventory file, globing and exemptions.

```bash
ansible -m ping lb # execute on a group
ansible -m ping "*"  # same as all
ansible -m ping app* # globing
ansible -m ping lb:web
ansible -m ping \!web # execute on all but this group
ansible -m ping web[0] # execute on the first of array
```

## Ansible commands

```bash
ansible -m shell -a "uname" all # ansible -module shell -attribute "uname" to be executed on all hosts in the inventory.ini
ansible --list-hosts all -i inventory.ini
ansible -m ping all -u root
ansible -m shell -a "uname" all # return the os of the host
ansible -m command -a "/bin/false" \!local
```

## Ansible Tasks

Ansible tasks are a way to run adhoc commands against our inventory in a one-line single executable. Tasks are the basic building blocks of Ansible's execution and configuration.  
Command consist of the Ansible command, options, and host-pattern.  
Example of pinging all the hosts associated with out inventory.

```bash
       ansible         -m        ping    all
# ansible command,  the module,  ping, inventory all.
```

## Ansible Playbooks

+ Playbooks are a way to congregate ordered processes and manage configuration needed to build out a remote system.

+ Playbooks make configuration management easy and gives us the ability to deploy to a multi-machine setup.

+ Playbooks can declare configurations and orchestrate steps (normally done in a manual ordered process), and, when run, can ensure pur remote system s configured as expected.

+ the written tasks whiting a playbook can be run synchronously or asynchronously.

+ Playbooks gives us the ability to create infrastructure as code and manage it all in source control.

```yaml
# ping .yml
---
  -hosts: all # inventory on which to be
   tasks:     #  executed listed tasks
   - name: Pinging all servers # arbitrary name of the task
     action: ping # called module ping, which have no attributes
```

To run this example playbook.

```bash
ansible-playbook ping.yml
```

What does it take to construct a system using playbooks?

*Package Management  
What packages will our system need? Install all packages needed ro tun our system. Patching. Package manager.

```yaml
---
  - hosts: lb
    tasks:
    - name: Install apache
      yum: name=httpd state=latest
```

Once installed is time for configuration.

```yml
---
  - hosts: lb
    tasks:
    - name: Copy config file
      copy: src=./config.cfg dest=/etc/config.cfg

  - hosts: web
    task:
    - name: Synchronize folders
      synchronize: src=./app dest=/var/www/html/app
```

After the config is done is time to restart the service if needed.

```yml
---
  - hosts: lb
    tasks:
    - name: Configure port number
      lineinfile: path=/etc/config.cfg regexp='^port' line='port=80'
      notify: Restart apache

    handlers:
    - name: Restart apache
      service: name=httpd status=restarted
```

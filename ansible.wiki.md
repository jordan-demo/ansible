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

The default inventory file is located in /etc/andible/hosts, but that can be changed in ansible.cfg, or with -i /path/to/file using the command line.

```ini
# hosts

[web]
app1 ansible_host=10.10.24.200
app2 ansible_host=10.10.24.201

[lb]
lb1 ansible_host=10.10.24.202

[local]
control ansible_connection=local
```

```bash
ansible -m ping all # ping all hosts in the inventory file, if there is an error, check  the inventory = ./inventory.ini in ansible.cfg

ansible --list-hosts web # lists the hosts in ghe group web
ansible  
```
Target specific group from the inventory file, globbing and exemptions.

```bash
ansible -m ping lb # execute on a group
ansible -m ping "*"  # same as all
ansible -m ping app* # globbing
ansible -m ping lb:web
ansible -m ping \!web # execut on all but this group
ansible -m ping web[0] # execute on the first of array
```

## Ansible commands 

```bash
ansible -m shell -a "uname" all # ansible -mofule shell -atribute "uname" to be executed on all hosts in the inventory.ini
ansible --list-hosts all -i inventory.ini
ansible -m ping all -u root
ansibl


```
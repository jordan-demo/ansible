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
lb1 ansible_host=10.10.24.202:22 # redirect ansible to non standard port

[local]
control ansible_connection=local
```

```bash
ansible -m ping all # ping all hosts in the inventory file, if there is an error, edit ansible.cfg "inventory = ./inventory.ini.

ansible --list-hosts web # lists the hosts in ghe group web 
```

Target specific group from the inventory file, globing and exemptions.

```bash
ansible -m ping lb # execute on a group
ansible -m ping "*"  # same as all
ansible -m ping app* # globing
ansible -m ping lb:web # ping lb and web
ansible -m ping \!web # execute on all but this group
ansible -m ping web[0] # execute on the first of array
```

## Ansible commands

```bash
ansible -m shell -a "uname" all # ansible -module shell -attribute "uname" to be executed on all hosts in the inventory.ini
ansible --list-hosts all -i inventory.ini
ansible -m ping all -u root # connect as a different user, root in this case
ansible -m shell -a "uname" all # return the os of the host
ansible -m command -a "/bin/false" \!local # return a error execute on all but local, and we escape the ! because bash.
```

## Ansible Tasks

Ansible tasks are a way to run adhoc commands against our inventory in a one-line single executable. Tasks are the basic building blocks of Ansible's execution and configuration.  
Command consist of the Ansible command, options, and host-pattern.  
Example of pinging all the hosts associated with out inventory.

```bash
       ansible         -m        ping                 all
# ansible command,  the module,  ping, all hosts listed in the inventory file.
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

+ Examples of hosts, tasks, handlers, ...

```yaml
---
  - hosts: lb # Tasks will be executed on hosts in the lb group
    tasks:  # task followed by list of tasks assigned with -, when the list is over indentation must go back 2 spaces
    - name: Install apache # Arbitrary name of the task, for debugging purpose to know where the playbook encounter a error.
      yum: # module name
        name: httpd # the packet manager yum will manipulate httpd package.
        state: latest # this will update the package to the latest version, if not already otherwise will be ignored.
```

Copy file, Sync directory.

```yml
---
  - hosts: lb # will act on all hosts in the [lb] group in the inventory.ini
    tasks: # list the tasks to be executed
    - name: Copy config file # name of the task, can be whatever you will.
      copy: # name of the module
        src: ./config.cfg # source file on the localhost
        dest: /etc/config.cfg # destination on the remote host

  - hosts: web # will act on all hosts in [web] group in the inventory.ini file
    task: # list of the tasks to be done
    - name: Synchronize folders # arbitrary name of the task
      synchronize: # name of the module this one will sync directory
        src: ./app # source dir on the localhost
        dest: /var/www/html/app # destination dir on remote hosts
```

Edit config file and restart using handlers

```yml
---
  - hosts: lb # will act on all hosts in the [lb] group in the inventory.ini
    tasks: # list of the tasks to be executed
    - name: Configure port number # arbitrary name for debugging purpose 
      lineinfile: # edit a line in a file on the remote host
        path: /etc/config.cfg # path where the file we will edit is on the remote host
        regexp: ^port # using regex to find the line. In this case ^ mean the line start with port.
        line: 'port=80' # the whole line will be replaced with the single quoted string
      notify: Restart apache # if a change is made, then tell the handler with the this name to do his thing notify and name must be exactly the same.

    handlers: # handlers if notified they will do, otherwise will be ignored 
    - name: Restart apache # name of the handler must be exact as notify.
      service: # service will be called
        name: httpd # name of the service to be managed
        status: restarted # restart this service
```

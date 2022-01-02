# Ansible Basics wiki

Created Jan. 2022, following the course ***Introduction to Ansible v2.7*** *Brock Tubre*
[source link](https://learn.acloud.guru/course/intro-ansible/overview)

|Topic links:  |          |           |
|---|---|---|
|[ansible.cfg](#ansible.cfg) | [Inventory.ini](#Inventory.ini) | [Ansible Commands](#Ansible-Commands)|
|[Ansible Task](#Ansible-Tasks) | [Ansible Tasks](#Ansible-Tasks) | [Ansible Playbooks](#Ansible-Playbooks)|
|[Variables](#Variables) | [Roles](#Roles) | [Check Mode](#Check-mode)|
|[Error handling](#Error-handling-in-Playbooks) | [Tags](#Tags) | [Vault](#Ansible-Vault)|
|[Prompts](#Prompts)|

## Warning

>Ansible doesn't have any automatic way to keep track of things and undo on failure, but it does offer you some functionality to handle failures yourself.  
This is implemented using blocks. With blocks you can define a set of tasks to be executed in the rescue: section. These can be anything you want, and with careful planning you could should be able to get it to undo everything.
Though if the system is broken in some unusual way, your 'undo' tasks may also fail. If your system is in a VM where you could checkpoint/snapshot, or running on a filesystem (ie zfs) that supports checkpoints/snapshots you could certainly use those facilities to revert.

## [ansible.cfg](#Ansible-Basics-wiki)

Configuration file will be search in the following order:

1. ANSIBLE_CONFIG (environment variable if set)
2. ansible.cfg (in the current directory)
3. ~/.ansible.cfg (in the home directory)
4. /etc/ansible/ansible.cfg

```cfg
# ansible.cfg
[defaults]
inventory = ./inventory.ini # where the inventory file is located
remote_user = root  # instead of attempting to ssh with current user, try with root in this case
host_key_checking = False # this disable the lookup in known hosts and the prompting to be added to the list
private_key_file = ~/.ssh/aws.pem # where the private key is located, if not set it will use id_rsa
```

## [Inventory.ini](#Ansible-Basics-wiki)

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

## [Ansible Commands](#Ansible-Basics-wiki)

```bash
ansible -m shell -a "uname" all # ansible -module shell -attribute "uname" to be executed on all hosts in the inventory.ini
ansible --list-hosts all -i inventory.ini
ansible -m ping all -u root # connect as a different user, root in this case
ansible -m shell -a "uname" all # return the os of the host
ansible -m command -a "/bin/false" \!local # return a error execute on all but local, and we escape the ! because bash.
ansible -m service -a "name=httpd state=stopped" --become lb # module service will find the httpd and put it in stopped state become will elevate to root and this will be run on all hosts in the [lb] group in the inventory.ini
ansible -m setup app1 # display all the facts about that host.
ansible-playbook playbook_name.yml --check # Dry run, no changes will be made
ansible-playbook playbook_name.yml --tags upload # This will run only the tasks with the upload tag.
ansible-playbook playbook_name.yml --skip-tags upload # This will play all but the upload tagged tags.
ansible-vault create secret-variables.yml /path/to/file # Create a vault file and create the password
ansible-vault edit secret-variables.yml # Edit the vault opens in the default bash editor 
ansible-vault view secret-variables.yml # View the content of the vault file.
```

## [Ansible Tasks](#Ansible-Basics-wiki)

Ansible tasks are a way to run adhoc commands against our inventory in a one-line single executable. Tasks are the basic building blocks of Ansible's execution and configuration.  
Command consist of the Ansible command, options, and host-pattern.  
Example of pinging all the hosts associated with out inventory.

```bash
       ansible         -m        ping                 all
# ansible command,  the module,  ping, all hosts listed in the inventory file.
```

## [Ansible Playbooks](#Ansible-Basics-wiki)

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

```yml
# all-playbooks.yml name of the playbook

---
# when ansible-playbook playbooks/all-playbooks.yml is called, it will execute the imported playbooks in order.
  - import_playbook: yum-update.yml
  - import_playbook: install-services.yml
  - import_playbook: setup-app.yml
  - import_playbook: setup-lb.yml
  ```

## [Variables](#Ansible-Basics-wiki)

Ansible provide us with variables and metadata about the host we are interacting with when running playbooks.

+ During the TASK **[Gathering Facts]** step, these variables become populated.
+ Gathers useful facts about our host and can be used in playbooks.
+ Use the **status** module to see all of the facts gathered during the **TASK[Gathering Facts]** step.
+ Use jinja2 templates to evaluate these expressions.

```bash
ansible -m setup app1 # Show the gathered facts or metadata for host app1
```

```yml
---
  - name: add webserver info 
    copy: # the name of the module
      dest: /var/www/html/info.php # which file to manipulate
      content: "{{ ansible_hostname }}" # content will echo the value of the ansible_hostname, which can be found in or the gathering facts. The double curly must be in quotes.
```

+ Create local variables in a playbook, using **vars** to create a key/value pairs and dictionary/map of variables.

```yml
---
  vars: # Create a dictionary of variables
    path_to_app: "/var/www/html" # key value pair 
    another_variable: "Hello World" # key value pair
  tasks: # tasks will call the vars.
    - name: Add webserver info # arbitrary name of the task
      copy: # module name
        dest: "{{ path_to_app }}/info.php" # which file to be edited on the remote host quoted in double curly is the name of the variable which will return the value.
        content: "{{ another_variable }}" # another variable for fun.
```

+ Create variables files and import them into our playbook.

+ Ansible also gives us the ability to register variables from tasks that run to ger information about its execution. Create variables from info returned from tasks ran using **register**. Call the registered variables for later use. Use the **debug** module anytime to see variables ad debug our playbooks

```yml
---
  vars: # Dictionary of key: value pair
    path_to_app: "/var/www/html" # key: "value" pair

  tasks:  
    - name: See directory contents
      command: ls -la {{ path_to_app }} # command module will execute ls -la
      register: dir_content # register the output from the command
    - name: Debug directory contents
      debug: # debug module will display the results
        msg: "{{ dir_content }}" # will display the content of this variable, which was generated from the ls -la command.
```

## [Roles](#Ansible-Basics-wiki)

Ansible provides a framework that makes each part of variables. tasks, templates and modules fully independent of one another.

+ Group tasks together in a way tha is self containing.
+ Clean and pre-defined directory structure.
+ Break up the configurations into files-
+ Reuse code by others who need similar configurations.
+ Easy to modify and reduces syntax errors.

```bash
ansible-galaxy init role_name # will create a roles whit the following structure. but not all dirs are required.
```

```bash
user@host:~/ansible/ansible-roles/roles/web$ ls -R # This is the default directory structure of a freshly created role.
.:
defaults  handlers  meta  README.md  tasks  tests  vars

./defaults:  # default variables
main.yml

./handlers: # handlers
main.yml

./meta:
main.yml

./tasks:
main.yml

./tests:
inventory  test.yml

./vars:
main.yml
```

## [Check Mode](#Ansible-Basics-wiki)

Check mode or Dry Run Reports changes that Ansible would have to make on the end hosts rather than applying the changes.

+ Run Ansible commands without affection the remote system.

+ Reports changes back rather than actually making them,

+ Great for one node at a time basic configuration management use cases.

```bash
ansible-playbook playbook_name.yml --check
```

## [Error handling in Playbooks](#Ansible-Basics-wiki)

Change the default behavior of Ansible when certain events happen that may or may not need to report as a failure or changed status.

```yml
# check status.yml
---
  - hosts: web:lb
    tasks:
      - name: Check status of apache
        command: service httpd status
        changed_when: false # Suppress change status.
      
      - name: This will not fail
        command: /bin/false
        ignore_errors: yes # This is how to ignore error
```

## [Tags](#Ansible-Basics-wiki)

Assigning **tags** to specific tasks in playbooks allows you to only call certain tasks in a very long playbook.

+ Only run specific parts of a playbook rather than all of the plays.

+ Add tags to any tasks and reuse if needed.

Specify the tags you want to run ( or not run ) on the command line.

```yml
---
  tasks:
    - name: Upload application file
      copy:
        src: ../index.php
        dest: "{{ path_to_app }}"
      tags: upload

    - name: Create simple info page.
      copy:
        dest: "{{ path_to_app }}/info.php"
        content: "<h1>Hello, World!</h1>"
      tags: create
```

```bash
ansible-playbook playbook_name.yml --tags upload # This will run only the tags with the upload tag.
ansible-playbook playbook_name.yml --skip-tags upload # This will play all but the upload tagged tasks.
```

## [Ansible Vault](#Ansible-Basics-wiki)

Ansible **Vault** is a way to keep sensitive information in encrypted files, rather than plain texts, in your playbooks.

+ Keep passwords, keys, and sensitive variables in encrypted vault files.

+ Vault files can be shares trough source control.

+ Vault can encrypt pretty much any data structure file used by Ansible.

+ Password protected and the default cipher is AES

```bash
ansible-vault create secret-variables.yml
ansible-vault edit secret-variables.yml
ansible-vault view secret-variables.yml

# This to work, call the playbook with the --ask-vault-pass

ansible-playbook playbook_name.yml --ask-vault-pass
```

## [Prompts](#Ansible-Basics-wiki)

There may be playbooks you run that need to prompt the user for certain input. You can use this  in the **'vars_prompt'** section.

+ Can use the users input as variables within our playbooks.

+ Run certain tasks with conditional logic.

+ Common use is to ask for sensitive data.

+ Has uses outside of security as well.

```yml
---
  vars_prompt:
    - name: "upload_var" # The answer of the question will be stored in this variable
      prompt: "Upload index.php file?"

  tasks:
    - name: Upload application file
        copy:
          src: ../index.php
          dest: "{{ path_to_app }}"
        when: upload_var == 'yes'
        tags: upload
```

---
aliases:
- /tutorials/2019/10/09/launch-jupyterhub-server.html
categories: tutorials
date: '2019-10-09T16:40:08Z'
draft: false
showtoc: false
slug: launch-jupyterhub-server
title: Launching a JupyterHub Instance
---

In this post I walk through the steps of creating a multi-user JupyterHub sever running on an AWS Ubuntu 18.04 instance. There are many ways of setting up JupyterHub including using Docker and Kubernetes - but this is a pretty staight forward mechanism that doesn't have too many moving parts such as TLS termination proxies etc. I think of this as the baseline setup.

Note that this setup has a few pros or cons depending on how you look at them.

1. JupyterHub is responsible for TLS and you need to create certificates for it.
2. Users cannot install packages using `!conda install` or `!pip install`.
3. Users cannot create environments and use them.
4. PAM users are created, so users can SSH into the machine.

This post serves as a general sketch of how to get a production ready JupyterHub server up and running for multiple users.

### Step 1: Launch an instance

Use the method of your choice to create an AWS instance in a VPC that has access to the Internet. A couple of notes on the instance creation process:

- I used the Ubuntu 18.04 HVM LTS as the base AMI
- Ensure the instance is in a security group that allows ports 22 and 443
- Ensure you have SSH access to the instance
- Ensure the instance has enough memory, compute, and disk for your intended workload

Next ensure the instance can be reachable by a DNS name. This is required for TLS to work. There are a few ways to do this, but the way I did it was to:

- Create an elastic IP address (EIP) and assign it to the instance
- Create an A record in route53 mapping the domain name to the EIP

At this point you should be able to SSH into your instance via the domain name. If so, you're good to go for the next steps.

### Step 2: Install Anaconda

I chose to use Anaconda to facilitate data science workloads for this installation. Anaconda has its pros and cons on a system level install, but one of the implications was that users could not install their own packages. Additionally, I had to jump through some hoops to get the server running with systemd. After this experience, vanilla Python might be a better choice, to be frank.

First create a system user for Anaconda and add the ubuntu user to the group:

```
$ sudo useradd -r anaconda
$ sudo usermod -a -G anaconda ubuntu
```

Next install Anaconda as follows:

1. Select distribution from [Anaconda Distributions](https://www.anaconda.com/distribution/)
2. Copy 64-bit (x86) installer URL
3. Download, verify integrity, and execute the script

    ```
    $ curl -O https://repo.anaconda.com/archive/Anaconda3-2019.07-Linux-x86_64.sh
    $ sha256sum Anaconda3-2019.07-Linux-x86_64.sh
    69581cf739365ec7fb95608eef694ba959d7d33b36eb961953f2b82cb25bdf5a  Anaconda3-2019.07-Linux-x86_64.sh
    $ sudo bash Anaconda3-2019.07-Linux-x86_64.sh
    ```

4. Accept the user agreement
5. Install to `/opt/anaconda`
6. Update permissions of `/opt/anaconda`

    ```
    $ sudo chown -R anaconda:anaconda /opt/anaconda
    $ sudo chmod -R 775 /opt/anaconda
    ```

These permissions should give the ubuntu user the ability to install packages to anaconda, but not other users. Other users should be able to execute anaconda commands but not modify the anaconda install. If they want to install their own packages, they'll have to create a virtual environment in their home directory.

#### Optional step: ensure Anaconda is available for new users

This is an optional step, but because Anaconda relies heavily on the shell for configuration, I ensured that any new users would have access to Anaconda by appending the following to `/etc/skel/.bashrc`:

```bash
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```

Note that I also added this to `/root/.bashrc` so that when I executed commands with `sudo su`, Anaconda was available to the root user.

### Step 3: Install JupyterHub

Install the required packages using `conda` and `pip`:

```
(base) $ conda install -c conda-forge jupyterhub
(base) $ conda install notebook
(base) $ pip install jupyterhub-systemdspawner
```

Make sure that `pip` is associated with the conda environment and not with the default Python installation!

As with Anaconda, we'll create a jupyterhub system user and working directory for the server.

```
$ sudo useradd -r jupyterhub
$ sudo usermod -a -G jupyterhub ubuntu
$ sudo mkdir /srv/jupyterhub
$ sudo chown -R jupyterhub:jupyterhub /srv/jupyterhub
```

Note, however, that we'll run JupyterHub as a privileged user rather than as this user, but it simplifies the management of files a bit to do it this way.

### Step 4: Create LetsEncrypt certs

At this point you'll have to create certificates for the TLS endpoint. I prefer to use [certbot](https://certbot.eff.org/) and [LetsEncrypt](https://letsencrypt.org/) since it makes things so easy. Note that you'll also have to implement a verification method to be granted the certificates (to prove you own the domain) which will also be true for renewal. I'll be using [route53 verification](https://certbot-dns-route53.readthedocs.io/en/stable/) in this example.

Install certbot (instructions from the certbot website)

```
$ sudo apt-get update
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository universe
$ sudo add-apt-repository ppa:certbot/certbot
$ sudo apt-get update
$ sudo apt-get install certbot python3-certbot-dns-route53
```

Ensure that your AWS credentials are correctly configured for boto3 and that sudo can access them (e.g. not in the environment), then perform the verification. You'll need to submit an email address, agree to the license, and choose if you want the EFF electronic newsletter.

```
$ sudo certbot certonly --dns-route53 -d jupyter.mydomain.com
```

Ensure that crontab is setup to automatically renew the certs.

```
$ sudo certbot renew --dry-run
$ cat /etc/cron.d/certbot
```

Note that we could also setup JupyterHub behind a proxy like Traefik or nginx, which would terminate the TLS itself and is perhaps a bit more easy to automatically configure than route53. I recommend this method particularly if you're not on AWS.

### Step 5: Configure JupyterHub

Create the jupyterhub configuration file and move it to the recommended system configuration location as follows:

```
$ jupyterhub --generate-config
$ sudo mkdir /etc/jupyterhub
$ sudo mv jupyterhub_config.py /etc/jupyterhub
```

There is a lot of commented out configuration details, but the important configurations to me are as follows:

```python
# Set the JupyterHub bind URL, protocol and port
c.JupyterHub.bind_url = 'https://0.0.0.0:443'

# Save the cookie secret file in the jupyterhub working directory
c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/cookie_secret'

# Save the database in the jupyterhub working directory
c.JupyterHub.db_url = 'sqlite:////srv/jupyterhub/jupyterhub.sqlite'

# Set the hub bind url for all jupyter-single user instances
c.JupyterHub.hub_bind_url = 'http://127.0.0.1:8081'

# Store the pid file in the jupyterhub working directory
c.JupyterHub.pid_file = '/srv/jupyterhub/jupyterhub.pid'

# Ensure that notebooks are shutdown when users log out so that notebooks
# are cleaned up releasing their memory. Note this is also a helpful way
# to do support: just have them log out and log back in again!
c.JupyterHub.shutdown_on_logout = True

# We're using the SystemdSpawner
c.JupyterHub.spawner_class = 'systemdspawner.SystemdSpawner'

# Specify the locations of the letsencrypt certs
c.JupyterHub.ssl_cert = '/etc/letsencrypt/live/jupyter.mydomain.com/fullchain.pem'
c.JupyterHub.ssl_key = '/etc/letsencrypt/live/jupyter.mydomain.com/privkey.pem'

# Set limits on the compute resources users have access to
c.SystemdSpawner.cpu_limit = 3.0
c.SystemdSpawner.isolate_tmp = True
c.SystemdSpawner.isolate_devices = True
c.SystemdSpawner.disable_user_sudo = True
c.SystemdSpawner.mem_limit = '8G'

# Set any environment variables you'd like your users to have access to.
# Very helpful for things like $NLTK_DATA or other Python resources.
c.Spawner.environment = {
    "MY_ENV_VAR": "fo"
}

# Determine who can create new user accounts
c.Authenticator.admin_users = set(['ubuntu', 'admin'])
```

Create a new user and password for the admin user:

```
$ sudo adduser admin
```

Enter the password and details for the admin user -- this will give you admin access to the JupyterHub server and allow you to create new users online.

At this point, as the root user you should be able to run:

```
$ jupyterhub -f /etc/jupyterhub/jupyterhub_config.py
```

You should be able to see the login screen and login as the admin user. You should also be able to create new users from the admin page.

### Step 6: Run JupyterHub as a systemd service

Because anaconda needs to be initialized and the environment modified to support it, the systemd service needs to be run from a bash script. Add the following to `/usr/local/bin/run_jupyterhub.sh` and make it executable.

```bash
#!/bin/bash

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Run the JupyterHub service with the system configuration
jupyterhub -f /etc/jupyterhub/jupyterhub_config.py
```

Create a systemd service by writing the following into `/etc/systemd/system/jupyterhub.service`:

```
[Unit]
Description=JupyterHub
Documentation=https://jupyterhub.readthedocs.io/en/stable/

[Service]
Type=simple
After=network.target
Restart=always
RestartSec=10

WorkingDirectory=/srv/jupyterhub
ExecStart=/usr/local/bin/run_jupyterhub.sh

StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=jupyterhub

[Install]
WantedBy=multi-user.target
```

You can now enable and start the server as follows:

```
$ sudo systemctl enable jupyterhub.service
$ sudo systemctl start jupyterhub.service
```

You should now be able to go to the server and access JupyterHub without running it specifically as the user. To diagnose issues, use `journalctl` as follows:

```
$ sudo journalctl -u jupyterhub.service
```

This will open up the log file and tell you if anything went wrong.

### Step 7: Handle Logging

Our systemd service writes all output to the syslog. By default we can access the logs using `journalctl`. However, to make debugging easier, we can use `rsyslog` to write the logs into a file. Add the following in `/etc/rsyslog/jupyterhub.conf`:

```
if $programname == 'jupyterhub' then /var/log/jupyterhub/access.log
& stop
```

Note also that you might have to add a priority to the configuration, e.g. `22-jupyterhub.conf` to ensure that rsyslog executes it correctly. Create the logging directory and give it the correct permissions, then restart rsyslog:

```
$ mkdir /var/log/jupyterhub
$ chown root:syslog /var/log/jupyterhub
$ chmod 775 /var/log/jupyterhub
$ systemctl restart rsyslog.service
```

To make sure the logs don't get too large, add the following to `/etc/logrotate.d/jupyterhub.conf`:

```
/var/log/jupyterhub/access.log
{
        daily
        rotate 15
        size 50M
        missingok
        notifempty
        compress
        delaycompress
        dateext
        dateformat -%Y-%m-%d
        create 0644 root root
}
```

This will ensure that the logs are compressed and rotated daily and that they will be deleted after 15 days.

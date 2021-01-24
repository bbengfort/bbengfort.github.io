---
categories: snippets
date: "2017-04-17T12:26:55Z"
title: Gmail Notifications with Python
---

I routinely have long-running scripts (e.g. for a data processing task) that I  want to know when they're complete. It seems like it should be simple for me to add in a little snippet of code that will send an email using Gmail to notify me, right? Unfortunately, it isn't quite that simple for a lot of reasons, including security, attachment handling, configuration, etc. In this snippet, I've attached my constant copy and paste `notify()` function, written into a command line script for easy sending on the command line.

## Gmail Setup

If you're like me, you have a gmail account with 2-factor authentication (and if you don't, you should get that set up). In order to use this account to send email from, you're going to have to configure gmail as follows:

1. [Allow less secure apps to access your account](https://support.google.com/accounts/answer/6010255)
2. [Create a Sign in using App Passwords](https://support.google.com/accounts/answer/185833)

Alternatively you could create an account to solely send notifications from and not give it two factor authentication, but you'd still have to do step 1. Even if you do all this stuff, Google Apps can still get in the way, so be sure to inspect any errors you get carefully!

## Environment Setup

This script and most of my Python scripts contain configuration and security information in the environment. Therefore, open up your `.profile` or other shell environment and add the following variables.

```bash
## Notify Environment
export EMAIL_USERNAME=you@gmail.com
export EMAIL_PASSWORD=supersecret
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_FAIL_SILENT=False
```

I've also used YAML configuration, dotenv files, and all sorts of other configuration for this as well. Choose what suits your application

## Notify Script

And here is a command line version of the script that wraps the `notify()` function. Note that it's basic functionality is to send a simple alert and maybe attach some log or results files to the email, not to routinely send large amounts of HTML formatted messages!

<script src="https://gist.github.com/bbengfort/089bbb73f072838ae8d1b0ac859299ff.js"></script>

## Usage

So now you can send a simple notification as follows:

```bash
$ notify.py -r jdoe@exmaple.com
```

Or you can edit the subject and message with a few attachments:

```bash
$ notify.py -r jdoe@example.com -s "computation complete" results.csv
```

Future versions of this script will allow you to pipe the message in via stdin so that you can chain the emailer along the command line. I also plan to do a better configuration, similar to how AWS CLI configures itself in a simple file in the home directory. 

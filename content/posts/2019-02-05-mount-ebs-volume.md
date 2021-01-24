---
categories: snippets
date: "2019-02-05T12:48:18Z"
title: Mount an EBS volume
---

Once the EBS volume has been created and attached to the instance, ssh into the instance and list the available disks:

```
$ lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
loop0         7:0    0 86.9M  1 loop /snap/core/4917
loop1         7:1    0 12.6M  1 loop /snap/amazon-ssm-agent/295
loop2         7:2    0   91M  1 loop /snap/core/6350
loop3         7:3    0   18M  1 loop /snap/amazon-ssm-agent/930
nvme0n1     259:0    0  300G  0 disk
nvme1n1     259:1    0    8G  0 disk
└─nvme1n1p1 259:2    0    8G  0 part /
```

In the above case we want to attach nvme0n1 - a 300GB gp2 EBS volume. Check if the volume already has data in it (e.g. created from a snapshot or being attached to a new instance):

```
$ sudo file -s /dev/nvme0n1
/dev/nvme0n1: data
```

If the above command shows `data` then the volume is empty. Format the file system as follows:

```
$ sudo mkfs -t ext4 /dev/nvme0n1
mke2fs 1.44.1 (24-Mar-2018)
Creating filesystem with 78643200 4k blocks and 19660800 inodes
Filesystem UUID: 42a9004d-7d79-4113-8d36-2daaaaa63c87
Superblock backups stored on blocks:
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
	4096000, 7962624, 11239424, 20480000, 23887872, 71663616

Allocating group tables: done
Writing inode tables: done
Creating journal (262144 blocks): done
Writing superblocks and filesystem accounting information: done
```

Create a directory to mount the volume to:

```
$ sudo mkdir /data
$ sudo chown ubuntu:ubuntu /data
```

Mount the directory to the volume:

```
$ sudo mount /dev/nvme0n1 /data/
```

The volume should now be available for access:

```
$ cd /data
$ df -h .
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1    295G   65M  280G   1% /data
```

To unmount the volume:

```
$ unmount /dev/nvme0n1
```

### Automount

To mount the EBS volume on reboot you need to make an fstab entry. First create a backup of the fstab configuration:

```
$ sudo cp /etc/fstab /etc/fstab.bak
```

Then add the entry to `/etc/fstab` as follows:

```
# device_name mount_point file_system_type fs_mntops fs_freq fs_passno
/dev/nvme0n1       /data   ext4    defaults,nofail  
```

To check tha tthe fstab file has been created correctly run:

```
$ sudo mount -a
```
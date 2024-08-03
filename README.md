# stale-NFS-handle-monitor
 monitor for stale NFS handle(s) and reboot PVE VM via proxmoxer.ProxmoxAPI if detected

# Usage
### create docker container and set these ENVs:

STALENFS_MOUNTS=/single/directory/only
or
STALENFS_MOUNTS=/path/to/directory1;/data/directory2;/data/another/directory

STALENFS_PVE_ADDR=<PVE Server IP or Hostname>
STALENFS_PVE_NODE=<PVE Node>
STALENFS_PVE_USER=<PVE Username>
STALENFS_PVE_VMID=<PVE VMID to Reboot>

### authenticate using these ENVs (only pick one method):

STALENFS_PVE_PASS=<PVE Password>
or
STALENFS_PVE_TOKENID and STALENFS_PVE_TOKEN

# stale-NFS-handle-monitor
 monitor for stale NFS handle(s) and reboot PVE VM via proxmoxer.ProxmoxAPI if detected

# Usage


## Docker container usage
```
version: "3.7"
services:
  ###--- stale-NFS-handle-monitor --------------------------------------------###
  stale-NFS-handle-monitor:
    image: ghcr.io/captmicr0/stale-NFS-handle-monitor
    container_name: stale-NFS-handle-monitor
    environment:
      ****CHECK CONFIGURATION SETUP BELOW***
    volumes:
      - /path/to/media/files:/data
      # TIMEZONE
      - /etc/localtime:/etc/localtime:ro
    restart: always
```

## Configuration
### The docker container MUST have these environment variables configured

monitor single directory:
```
environment:
  - STALENFS_MOUNTS=/single/directory/only

......

volumes:
  - /single/directory/only:/single/directory/only
```

monitor multiple directories with `;` separated list and/or using the * modifier:
```
environment:
  - STALENFS_MOUNTS=/path/to/directory1;/data/*

......

volumes:
  - /path/to/directory1:/path/to/directory1
  - /data/directory:/data/directory
  - /data/directory2:/data/directory2
```

configure the PVE API settings:
```
environment:
  - STALENFS_PVE_ADDR=<PVE Server IP or Hostname>
  - STALENFS_PVE_NODE=<PVE Node>
  - STALENFS_PVE_USER=<PVE Username>
  - STALENFS_PVE_VMID=<PVE VMID to Reboot>
```

### Authentication (only pick one method):

password authentication:
```
environment:
  - STALENFS_PVE_PASS=<PVE Password>
```

token authentication:
```
environment:
  - STALENFS_PVE_TOKENID=<PVE Token ID>
  - STALENFS_PVE_TOKEN=<PVE Token>
```


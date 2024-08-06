#!/usr/local/bin/python

import signal
import os
import subprocess
import time

from proxmoxer import ProxmoxAPI

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Check all ENVs exists]
envkeys = os.environ.keys()
reqENVs = ('STALENFS_MOUNTS', 'STALENFS_PVE_ADDR', 'STALENFS_PVE_NODE', 'STALENFS_PVE_USER', 'STALENFS_PVE_VMID')
authENVs = (('STALENFS_PVE_PASS',), ('STALENFS_PVE_TOKENID','STALENFS_PVE_TOKEN'))

if not all([item in envkeys for item in reqENVs]):
    print('[ERROR] required ENVs missing:\n\t%s' % str(reqENVs))
    exit(1)

if not any([all(item in envkeys for item in group) for group in authENVs]):
    print('[ERROR] authenication ENVs missing:\n\t%s' % ' or \n\t'.join([' and '.join(group) for group in authENVs]))
    exit(1)

# Create a new Alarm Exception
class Alarm(Exception):
    pass
def alarm_handler(signum, frame):
    raise Alarm

# Timeout for signalling the alarm handler
TIMEOUT = 60

# List of paths to check
mounts = [k for k in os.environ.get('STALENFS_MOUNTS').split(';') if len(k) > 0]
nfs_mounts = []

for mount in mounts:
    if os.path.isdir(mount):
        nfs_mounts.append(mount)
    elif mount.endswith('*') and os.path.isdir(mount[:-1]):
        nfs_mounts.extend([item for item in [os.path.join(mount[:-1], f) for f in os.listdir(mount[:-1])] if os.path.isdir(item)])

print("[*] Paths to monitor:")
for mount in nfs_mounts:
    print("\t%s" % mount)

# Interval
interval = ('STALENFS_INTERVAL' in envkeys) and os.environ.get('STALENFS_INTERVAL') or 60
print("[*] Check interval:\n\t%d seconds" % interval)

# PVE API setup
PVE_ADDR = os.environ.get('STALENFS_PVE_ADDR')
PVE_NODE = os.environ.get('STALENFS_PVE_NODE')
PVE_USER = os.environ.get('STALENFS_PVE_USER')
PVE_VMID = os.environ.get('STALENFS_PVE_VMID')

if all([item in os.environ.keys() for item in ('STALENFS_PVE_PASS',)]):
    PVE_PASS = os.environ.get('STALENFS_PVE_PASS')
    pve = ProxmoxAPI(PVE_ADDR, user=PVE_USER, password=PVE_PASS, verify_ssl=False)
elif all([item in os.environ.keys() for item in ('STALENFS_PVE_TOKENID','STALENFS_PVE_TOKEN')]):
    PVE_TOKENID = os.environ.get('STALENFS_PVE_TOKENID')
    PVE_TOKEN = os.environ.get('STALENFS_PVE_TOKEN')
    pve = ProxmoxAPI(PVE_ADDR, user=PVE_USER, token_name=PVE_TOKENID, token_value=PVE_TOKEN, verify_ssl=False)
else:
    print('[ERROR] somehow got here even though authENVs are missing?!')
    exit(1)

print("[*] Verifying PVE access...")

print("\tPVE_ADDR: %s" % PVE_ADDR)
print("\tPVE_NODE: %s" % PVE_NODE)
print("\tPVE_USER: %s" % PVE_USER)
print("\tPVE_VMID: %s" % PVE_VMID)

try:
    vm = pve.nodes(PVE_NODE).qemu(str(PVE_VMID)).status()
    vmname = vm.current().get()['name']
    print("\tVMID %s [%s]" % (PVE_VMID, vmname))
except:
    print("\tfailed to access PVE")
    exit(1)

running = True

def signalHandler(signum=99999, frame=None):
    print("[*] Shutting down...")
    running = False
    exit(1)

# Register the signal handler for SIGTERM
signal.signal(signal.SIGTERM, signalHandler)
signal.signal(signal.SIGINT, signalHandler)

# Check mounts forever
while running:
    for path in nfs_mounts:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(TIMEOUT)
        try:
            try:
                proc = subprocess.call('stat '+path, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                if proc != 0:
                    raise Exception('Stale')
                signal.alarm(0)
            except StopIteration:
                if not os.path.ismount(path):
                    raise Exception('Not mounted')
            except Alarm:
                raise Exception('Timeout')
        except Exception as e:
            signal.alarm(0)
            print('[*] stale file handle detected, rebooting VMID %s [%s]...' % (PVE_VMID, vmname))
            # Reboot VM
            vm.shutdown().post()
            while (vm.current().get()['status'] != 'stopped'): time.sleep(1)
            vm.start().post()
    time.sleep(interval)

print("[*] end of program")

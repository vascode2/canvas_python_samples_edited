"""
Simple time sync script using the Sntp class
No network module needed - assumes WiFi is already connected
"""
import time
from sntp_client_edit2 import Sntp

print("=" * 50)
print("TIME SYNCHRONIZATION")
print("=" * 50)
print("Note: WiFi must already be connected!")
print()

# Show time before sync
print("Time before sync:", time.localtime())
print()

# Multiple NTP servers for reliability
ntp_servers = [
    'pool.ntp.org',
    'time.nist.gov',
    '0.pool.ntp.org',
    '1.pool.ntp.org',
    'time.google.com'
]

sync_success = False

# Try each server until one succeeds
for server in ntp_servers:
    try:
        print("--- Trying NTP server: " + server + " ---")
        
        # Create SNTP client and sync
        sntp = Sntp(host=server, timeout=10)
        sntp.poll()
        
        sync_success = True
        print("SUCCESS with " + server)
        break
        
    except Exception as e:
        print("Failed with " + server + ": " + str(e))
        print()
        continue

print()
print("=" * 50)
if sync_success:
    print("TIME SYNC SUCCESSFUL!")
    print("Current time:", time.localtime())
else:
    print("TIME SYNC FAILED!")
    print("All NTP servers failed")
    print("Check WiFi connection and firewall settings")
print("=" * 50)

import time
import machine
import socket
import select
import struct
import network

class Sntp:
    def __init__(self, host='pool.ntp.org', port=123, timeout=2):
        self.host = host
        self.port = port
        self.timeout = timeout

    def poll(self):
        print("Starting time sync with " + self.host + "...")
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        
        try:
            addr = socket.getaddrinfo(self.host, self.port)[0][-1]
            print("Connecting to NTP server: " + str(addr))
        except Exception as e:
            raise Exception("DNS resolution failed for " + self.host + ": " + str(e))
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Set socket timeout
            s.settimeout(self.timeout)
            
            # Send the query
            print("Sending NTP query...")
            res = s.sendto(NTP_QUERY, addr)
            print("Sent " + str(res) + " bytes")

            # Wait for the response using blocking receive with timeout
            print("Waiting for NTP response...")
            try:
                msg = s.recv(48)
                print("Received " + str(len(msg)) + " bytes")
            except Exception as e:
                raise Exception("Timeout or error receiving NTP response: " + str(e))
                
        finally:
            s.close()
            
        if len(msg) < 48:
            raise Exception("Invalid NTP response length: " + str(len(msg)))
            
        val = struct.unpack("!I", msg[40:44])[0]
        print("Raw NTP timestamp: " + str(val))

        # Adjust for 1970 epoch
        val = val - 2208988800
        print("Unix timestamp: " + str(val))

        # Write the value to the RTC
        tm = time.gmtime(val)
        if tm[0] < 2000:
            raise Exception("Invalid year " + str(tm[0]) + ", not setting RTC")
        else:
            print("✓ Time sync SUCCESS: {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} UTC".format(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]))
            machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
            print("✓ RTC updated successfully!")

# Auto-run time sync on boot
print("Device starting up...")
print("Time before sync:", time.localtime())

# WiFi Configuration - CHANGE THESE VALUES!
WIFI_SSID = "syi"        # Replace with your WiFi network name
WIFI_PASSWORD = "arkansas"  # Replace with your WiFi password

# Connect to WiFi
print("Connecting to WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

# Wait for connection
timeout = 15
while not wlan.isconnected() and timeout > 0:
    print("Waiting for WiFi connection... (" + str(timeout) + "s)")
    time.sleep(1)
    timeout -= 1

if wlan.isconnected():
    print("✓ WiFi connected! IP:", wlan.ifconfig()[0])
else:
    print("✗ WiFi connection failed!")
    print("Make sure SSID and password are correct")

# Try multiple NTP servers for better reliability
ntp_servers = [
    'pool.ntp.org',
    'time.nist.gov',
    '0.pool.ntp.org',
    '1.pool.ntp.org',
    'time.google.com'
]

sync_success = False
for server in ntp_servers:
    try:
        print("\n--- Trying NTP server: " + server + " ---")
        sntp = Sntp(host=server, timeout=10)  # Longer timeout
        sntp.poll()
        sync_success = True
        break  # Exit loop on first successful sync
    except Exception as e:
        print("✗ Failed with " + server + ": " + str(e))
        continue

if not sync_success:
    print("\n✗ ALL NTP servers failed!")
    print("Check network connectivity and firewall settings")

print("Time after sync:", time.localtime())
print("Setup complete!")

# Join a Wi-Fi network and send a ping to a remote host
import network, time, socket

def test_connectivity(hostname, port=80, timeout=5):
    """Test connectivity to a host by attempting a TCP connection"""
    try:
        print("Testing connectivity to " + hostname + "...")
        print("  Resolving DNS...")
        addr = socket.getaddrinfo(hostname, port)[0][-1]
        print("  Resolved to: " + str(addr))
        print("  Attempting TCP connection...")
        s = socket.socket()
        s.settimeout(timeout)
        start_time = time.ticks_ms()
        s.connect(addr)
        end_time = time.ticks_ms()
        s.close()
        response_time = time.ticks_diff(end_time, start_time)
        print("✓ Connected to " + hostname + " in " + str(response_time) + "ms")
        return True
    except Exception as e:
        print("✗ Failed to connect to " + hostname + ": " + str(e))
        return False

def show_network_info(nic):
    """Display detailed network configuration"""
    config = nic.ifconfig()
    print("Network Configuration:")
    print("  IP Address: " + config[0])
    print("  Subnet Mask: " + config[1]) 
    print("  Gateway: " + config[2])
    print("  DNS Server: " + config[3])

# Join an internet-connected Wi-Fi network. For simplicity, the
# Wi-Fi credentials are hard-coded.
ssid = 'WKW'                         # Wi-Fi network name
passphrase = 'arkansas'             # Wi-Fi network password
print('Joining network ' + ssid + '...')
try:
    # Join the network. For simplicity, retries are not implemented here.
    nic = network.WLAN(network.WLAN.IF_STA)   # Create the network interface
    nic.active(True)                          # Enable the interface
    nic.connect(ssid, passphrase)             # Join the network
    if nic.isconnected():
        print('Network joined, station IP:', nic.ifconfig()[0])
        show_network_info(nic)
        
        # Test connectivity to multiple hosts
        test_connectivity('google.com')
        test_connectivity('8.8.8.8')  # Google DNS
        
        # Try a simple DNS test
        try:
            print("Testing DNS resolution...")
            addr = socket.getaddrinfo('google.com', 80)
            print("✓ DNS working - google.com resolves to:", addr[0][-1])
        except Exception as e:
            print("✗ DNS resolution failed:", e)
            
    else:
        print('Failed to connect to WiFi')

    nic.disconnect()                          # Disconnect from the network
except Exception as e:
    print('Error: ', e)

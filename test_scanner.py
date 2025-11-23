print("🧪 TEST: This is a manual test file")

def test_scanner():
    import canvas_ble, time, network
    from machine import Pin
    
    print("🔵 Manual BLE Test Starting...")
    
    # Quick WiFi setup
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("WKW", "arkansas")
    
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        print("Connecting WiFi... " + str(timeout))
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print("✅ WiFi OK: " + wlan.ifconfig()[0])
    
    # BLE setup
    print("🔧 Setting up BLE...")
    canvas_ble.init()
    
    device_count = 0
    
    def scan_cb(e):
        nonlocal device_count
        device_count += 1
        addr = canvas_ble.addr_to_str(e.addr)[2:]
        rssi = e.rssi
        print("🔵 DEVICE " + str(device_count) + ": " + addr + " (RSSI: " + str(rssi) + ")")
    
    scanner = canvas_ble.Scanner(scan_cb)
    scanner.filter_reset()
    
    print("🔍 Starting manual scan for 30 seconds...")
    scanner.start(True)
    
    for i in range(6):  # 30 seconds total
        time.sleep(5)
        print("⏰ " + str((i+1)*5) + "s elapsed, " + str(device_count) + " devices found")
    
    scanner.stop()
    print("✅ Manual test complete! Found " + str(device_count) + " devices")

print("📝 Run: test_scanner()")

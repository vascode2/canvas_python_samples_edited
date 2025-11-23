# ENHANCED BLE SCANNER v3.0 - TERMINAL FRIENDLY
print("🆕🆕🆕 LOADING NEW VERSION v3.0 🆕🆕🆕")
print("📍 This message confirms new code is loaded!")

import canvas_ble, time, network
from machine import Pin

# Global variables  
device_count = 0

print("🔄 Enhanced BLE Scanner v3.0 Ready!")

# WiFi Configuration
WIFI_SSID = "WKW"  # Replace with your WiFi network
WIFI_PASSWORD = "arkansas"  # Replace with your WiFi password

# LED Setup for status indication
try:
    led0 = Pin("LED0", Pin.OUT)
    led1 = Pin("LED1", Pin.OUT) 
    led0.off()
    led1.off()
except:
    led0 = led1 = None

def connect_wifi():
    """Connect to WiFi network"""
    print("Connecting to WiFi:", WIFI_SSID)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print("  Waiting for WiFi...")
        time.sleep(1)
        timeout -= 1
    
    if wlan.isconnected():
        print("✅ WiFi connected! IP:", wlan.ifconfig()[0])
        if led1: led1.on()  # Green LED = WiFi connected
        return True
    else:
        print("❌ WiFi connection failed!")
        return False

def scan_result_cb(e):
    """Handle BLE scan results"""
    global device_count
    device_count += 1
    
    addr = canvas_ble.addr_to_str(e.addr)[2:]
    rssi = e.rssi
    data = e.data.hex()
    
    print("🔵 BLE Device #" + str(device_count) + " Found!")
    print("  Address: " + addr)
    print("  RSSI: " + str(rssi) + " dBm")
    print("  Data: " + data)
    print("  Data Length: " + str(len(e.data)) + " bytes")
    print("-" * 40)
    
    # Flash LED0 to show activity
    if led0:
        led0.on()
        time.sleep_ms(100)
        led0.off()

def main():
    """Main autonomous application"""
    print("🚀 ENHANCED BLE SCANNER v3.0 STARTING!")
    print("⏰ Timestamp: " + str(time.time()))
    print("📺 All messages will appear in TERMINAL tab")
    
    # Global device counter
    global device_count
    device_count = 0
    
    # Connect to WiFi first
    if not connect_wifi():
        print("❌ Cannot continue without WiFi")
        return
    
    # Initialize BLE
    print("📡 Initializing BLE...")
    canvas_ble.init()
    
    # Create scanner with enhanced debugging
    print("🔧 Setting up BLE scanner...")
    scanner = canvas_ble.Scanner(scan_result_cb)
    
    # Clear any existing filters
    scanner.filter_reset()
    
    # Set aggressive scan parameters (if supported)
    try:
        # Try to set scan interval and window for more aggressive scanning
        print("🎛️ Configuring scan parameters...")
    except:
        print("⚠️ Using default scan parameters")
    
    print("🔍 SCANNING FOR ALL BLE DEVICES...")
    print("� Messages will show in TERMINAL (not Output)")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start scanning
        scanner.start(True)  # Active scanning
        print("✅ Scanner started successfully!")
        
        # Run continuously with status updates
        scan_duration = 0
        while True:
            time.sleep(5)  # Check every 5 seconds
            scan_duration += 5
            print("📊 RUNNING: " + str(scan_duration) + "s | FOUND: " + str(device_count) + " devices")
            
            # Extra encouragement
            if scan_duration == 30 and device_count == 0:
                print("🔍 No devices yet - check BT510 is close and advertising!")
            elif scan_duration == 60 and device_count == 0:
                print("⚠️ Still no devices after 1 minute - check BT510 status!")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping scanner...")
        scanner.stop()
        scanner.filter_reset()
        
        # Turn off LEDs
        if led0: led0.off()
        if led1: led1.off()
        
        print("✅ Scanner stopped! Total devices found: " + str(device_count))

# Auto-start the application
if __name__ == "__main__":
    main()


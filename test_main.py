import canvas_ble, time, network
from machine import Pin

# Global variables  
device_count = 0

print("🔄 LOADING: Enhanced BLE Scanner v2.0 - WORKING VERSION")

# WiFi Configuration
WIFI_SSID = "WKW"
WIFI_PASSWORD = "arkansas"

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
        if led1: led1.on()
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
    
    if led0:
        led0.on()
        time.sleep_ms(100)
        led0.off()

def main():
    """Main autonomous application"""
    print("🚀 Starting Autonomous BLE Scanner...")
    print("🔧 CODE VERSION: Enhanced v2.0 - " + str(time.time()))
    
    global device_count
    device_count = 0
    
    if not connect_wifi():
        print("Cannot continue without WiFi")
        return
    
    print("📡 Initializing BLE...")
    canvas_ble.init()
    
    print("🔧 Setting up BLE scanner...")
    scanner = canvas_ble.Scanner(scan_result_cb)
    
    scanner.filter_reset()
    
    try:
        print("🎛️ Configuring scan parameters...")
    except:
        print("⚠️ Using default scan parameters")
    
    print("🔍 Starting continuous BLE scanning (ALL devices)...")
    print("📻 Looking for ANY BLE advertisements...")
    print("Press Ctrl+C to stop")
    
    try:
        scanner.start(True)
        
        scan_duration = 0
        while True:
            time.sleep(5)
            scan_duration += 5
            print("📊 Scanner active for " + str(scan_duration) + "s | Devices found: " + str(device_count))
            
            if scan_duration == 30 and device_count == 0:
                print("🔍 Still scanning... Make sure your BT510 is nearby and advertising!")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping scanner...")
        scanner.stop()
        scanner.filter_reset()
        
        if led0: led0.off()
        if led1: led1.off()
        
        print("✅ Scanner stopped! Total devices found: " + str(device_count))

if __name__ == "__main__":
    main()

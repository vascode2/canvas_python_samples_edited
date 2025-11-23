# Condensed MQTT Client Demo
import network, time, socket, struct
from machine import Pin

class MQTTClient:
    def __init__(self, client_id, server, port=1883):
        self.client_id = client_id.encode() if isinstance(client_id, str) else client_id
        self.server = server
        self.port = port
        self.sock = None
        self.pid = 0
        self.cb = None

    def _encode_remaining_length(self, length):
        result = bytearray()
        while True:
            byte = length % 128
            length = length // 128
            if length > 0:
                byte = byte | 0x80
            result.append(byte)
            if length == 0:
                break
        return result

    def _send_str(self, s):
        if isinstance(s, str):
            s = s.encode()
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def set_callback(self, f):
        self.cb = f

    def connect(self):
        try:
            self.sock = socket.socket()
            print("Socket created successfully")
            
            # Try to resolve the address
            addr_info = socket.getaddrinfo(self.server, self.port)
            addr = addr_info[0][-1]
            print("DNS resolved:", self.server, "->", addr)
            
            # Set socket timeout
            self.sock.settimeout(10)  # 10 second timeout
            print("Connecting to MQTT:", addr)
            
            self.sock.connect(addr)
            print("Socket connected successfully")
            
        except Exception as e:
            print("Connection failed:", str(e))
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            raise e
        
        try:
            # MQTT CONNECT packet
            # Variable header: Protocol Name + Level + Connect Flags + Keep Alive
            protocol_name = b"MQTT"
            protocol_level = 4
            connect_flags = 0x02  # Clean session
            keep_alive = 60
            
            # Payload: Client ID
            payload = struct.pack("!H", len(self.client_id)) + self.client_id
            
            # Calculate remaining length
            variable_header_len = 2 + len(protocol_name) + 1 + 1 + 2  # 10 bytes
            remaining_length = variable_header_len + len(payload)
            
            # Build packet
            packet = bytearray([0x10])  # CONNECT packet type
            packet.extend(self._encode_remaining_length(remaining_length))
            
            # Variable header
            packet.extend(struct.pack("!H", len(protocol_name)))
            packet.extend(protocol_name)
            packet.append(protocol_level)
            packet.append(connect_flags)
            packet.extend(struct.pack("!H", keep_alive))
            
            # Payload
            packet.extend(payload)
            
            print("Sending CONNECT packet, length:", len(packet))
            self.sock.write(packet)
            print("CONNECT packet sent")
            
            # Read CONNACK
            print("Reading CONNACK response...")
            self.sock.settimeout(5)  # 5 second timeout for response
            resp = self.sock.read(4)
            print("Received CONNACK:", [hex(b) for b in resp] if resp else "None")
            
            if not resp or len(resp) != 4:
                raise Exception("Invalid CONNACK response length: " + str(len(resp) if resp else 0))
            if resp[0] != 0x20:
                raise Exception("Invalid CONNACK packet type: " + hex(resp[0]))
            if resp[3] != 0:
                error_codes = {
                    1: "Unacceptable protocol version",
                    2: "Identifier rejected", 
                    3: "Server unavailable",
                    4: "Bad username or password",
                    5: "Not authorized"
                }
                error_msg = error_codes.get(resp[3], "Unknown error code: " + str(resp[3]))
                raise Exception("MQTT connect failed: " + error_msg)
            
            print("✓ MQTT connected!")
            
        except Exception as e:
            print("MQTT protocol error:", str(e))
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            raise e

    def publish(self, topic, msg):
        if isinstance(topic, str):
            topic = topic.encode()
        if isinstance(msg, str):
            msg = msg.encode()
            
        # Calculate remaining length
        remaining_length = 2 + len(topic) + len(msg)
        
        # Build packet
        packet = bytearray([0x30])  # PUBLISH packet type
        packet.extend(self._encode_remaining_length(remaining_length))
        
        # Variable header (topic)
        packet.extend(struct.pack("!H", len(topic)))
        packet.extend(topic)
        
        # Payload
        packet.extend(msg)
        
        self.sock.write(packet)
        print("Published:", topic.decode(), "->", msg.decode())

    def subscribe(self, topic):
        if isinstance(topic, str):
            topic = topic.encode()
            
        self.pid += 1
        
        # Calculate remaining length
        remaining_length = 2 + 2 + len(topic) + 1  # packet id + topic + qos
        
        # Build packet
        packet = bytearray([0x82])  # SUBSCRIBE packet type
        packet.extend(self._encode_remaining_length(remaining_length))
        
        # Variable header (packet identifier)
        packet.extend(struct.pack("!H", self.pid))
        
        # Payload (topic + QoS)
        packet.extend(struct.pack("!H", len(topic)))
        packet.extend(topic)
        packet.append(0x00)  # QoS 0
        
        self.sock.write(packet)
        
        # Wait for SUBACK
        resp = self.sock.read(5)
        if len(resp) >= 4 and resp[0] == 0x90:  # SUBACK
            print("✓ Subscribed to:", topic.decode())
        else:
            print("⚠ Subscription may have failed")

    def check_msg(self):
        try:
            self.sock.settimeout(0.1)  # Short timeout for non-blocking
            res = self.sock.read(1)
            if res and len(res) > 0:
                msg_type = res[0] & 0xF0
                if msg_type == 0x30:  # PUBLISH message
                    # Read remaining length
                    remaining_length = 0
                    multiplier = 1
                    while True:
                        byte = self.sock.read(1)[0]
                        remaining_length += (byte & 0x7F) * multiplier
                        if (byte & 0x80) == 0:
                            break
                        multiplier *= 128
                    
                    # Read topic length and topic
                    topic_len = struct.unpack("!H", self.sock.read(2))[0]
                    topic = self.sock.read(topic_len)
                    
                    # Read message payload
                    msg_len = remaining_length - 2 - topic_len
                    msg = self.sock.read(msg_len)
                    
                    if self.cb:
                        self.cb(topic, msg)
        except Exception as e:
            pass  # Timeout or no message available

    def disconnect(self):
        try:
            # Send DISCONNECT packet
            self.sock.write(b"\xe0\x00")
            self.sock.close()
        except:
            pass

# LED callback
def on_message(topic, msg):
    print("📨", topic.decode(), "->", msg.decode())
    try:
        if msg == b"red": led0.on(); led1.off()
        elif msg == b"green": led0.off(); led1.on()
        elif msg == b"off": led0.off(); led1.off()
    except: pass

# Test network connectivity first
def test_connectivity():
    try:
        print("🌐 Testing network connectivity...")
        test_sock = socket.socket()
        test_sock.settimeout(5)
        # Test connection to Google DNS
        test_sock.connect(('8.8.8.8', 53))
        test_sock.close()
        print("✅ Internet connectivity OK")
        return True
    except Exception as e:
        print("❌ No internet connectivity:", str(e))
        return False

# WiFi setup
print("🚀 MQTT Demo Starting...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("syi", "arkansas")
while not wlan.isconnected(): time.sleep(0.5)
print("✅ WiFi:", wlan.ifconfig()[0])

# Test connectivity before MQTT
if not test_connectivity():
    print("❌ Cannot proceed without internet connection")
    print("✅ Demo complete! (No network)")
else:
    # LED setup
    try:
        led0 = Pin("LED0", Pin.OUT)
        led1 = Pin("LED1", Pin.OUT)
        led0.off(); led1.off()
    except: led0 = led1 = None

    # MQTT setup with fallback brokers
    brokers = [
        "test.mosquitto.org",  # Eclipse test broker
        "broker.hivemq.com",   # HiveMQ public broker  
        "mqtt.eclipseprojects.io"  # Eclipse IoT broker
    ]

    mqtt_connected = False
    client = None

    for broker in brokers:
        try:
            print("🔌 Trying broker:", broker)
            client = MQTTClient("canvas_" + str(time.ticks_ms()), broker)
            client.set_callback(on_message)
            client.connect()
            mqtt_connected = True
            print("✅ Connected to", broker)
            break
        except Exception as e:
            print("❌ Failed to connect to", broker, ":", str(e))
            if client and client.sock:
                try:
                    client.sock.close()
                except:
                    pass
            client = None
            time.sleep(1)  # Brief delay before trying next broker

    if mqtt_connected and client:
        try:
            client.subscribe("canvas/led")
            client.publish("canvas/status", "Device online!")
            
            print("📡 Running for 60 seconds...")
            print("💡 Send 'red', 'green', or 'off' to canvas/led")
            
            # Run for 60 seconds only
            start_time = time.ticks_ms()
            last_publish = 0
            
            while time.ticks_diff(time.ticks_ms(), start_time) < 60000:
                client.check_msg()
                
                # Publish status every 15 seconds
                current_time = time.ticks_diff(time.ticks_ms(), start_time)
                if current_time - last_publish >= 15000:
                    uptime = str(current_time // 1000)
                    client.publish("canvas/status", "Uptime: " + uptime + "s")
                    last_publish = current_time
                
                time.sleep(0.1)  # Small delay to prevent busy loop
            
            # Cleanup
            client.publish("canvas/status", "Device offline")
            client.disconnect()
            
        except Exception as e:
            print("❌ MQTT Runtime Error:", str(e))

    else:
        print("❌ Could not connect to any MQTT broker")
        print("Check your internet connection and firewall settings")

# Final cleanup
if led0: led0.off()
if led1: led1.off()
print("✅ Demo complete! (60s)")
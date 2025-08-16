import threading
import time
import pygame
from scapy.all import sniff, TCP, ICMP, ARP, UDP
from settings import ENEMY_SPAWN_EVENT, PACKET_TO_ENEMY_MAP, NETWORK_SPAWN_COOLDOWN

class NetworkMonitor(threading.Thread):
    """
    Network packet monitor that captures packets and triggers enemy spawns in the game.
    
    Packet types mapped to enemies:
    - TCP -> Basic Enemy
    - ICMP -> Fast Enemy  
    - ARP -> Zigzag Enemy
    - UDP -> Tank Enemy
    """
    
    def __init__(self, interface=None, spawn_cooldown=NETWORK_SPAWN_COOLDOWN):
        super().__init__(daemon=True)
        self.stop_event = threading.Event()
        self.spawn_cooldown = spawn_cooldown
        self.last_spawn_time = {}  # Track last spawn time per enemy type
        self.interface = interface
        self.packet_count = {'tcp': 0, 'icmp': 0, 'arp': 0, 'udp': 0}
        
        # Initialize last spawn times
        for packet_type in PACKET_TO_ENEMY_MAP.keys():
            self.last_spawn_time[packet_type] = 0
    
    def process_packet(self, packet):
        """Process captured packet and determine if enemy should be spawned."""
        enemy_type = None
        packet_type = None
        
        # Determine packet type and corresponding enemy
        if packet.haslayer(TCP):
            packet_type = 'tcp'
            enemy_type = PACKET_TO_ENEMY_MAP['tcp']
        elif packet.haslayer(ICMP):
            packet_type = 'icmp'
            enemy_type = PACKET_TO_ENEMY_MAP['icmp']
        elif packet.haslayer(ARP):
            packet_type = 'arp'
            enemy_type = PACKET_TO_ENEMY_MAP['arp']
        elif packet.haslayer(UDP):
            packet_type = 'udp'
            enemy_type = PACKET_TO_ENEMY_MAP['udp']
        
        if enemy_type and packet_type:
            self.packet_count[packet_type] += 1
            current_time = time.time()
            last_time = self.last_spawn_time.get(packet_type, 0)
            
            # Rate limiting: only spawn if cooldown has passed
            if current_time - last_time > self.spawn_cooldown:
                self.last_spawn_time[packet_type] = current_time
                
                # Create and post the custom event to pygame
                try:
                    spawn_event = pygame.event.Event(
                        ENEMY_SPAWN_EVENT, 
                        {
                            'enemy_type': enemy_type,
                            'packet_type': packet_type,
                            'source': 'network'
                        }
                    )
                    pygame.event.post(spawn_event)
                    print(f"Network spawn: {packet_type.upper()} -> {enemy_type} enemy")
                except:
                    # If pygame isn't initialized yet, just skip
                    pass
    
    def run(self):
        """Main thread execution - start packet sniffing."""
        print(f"🌐 Network Monitor started (interface: {self.interface or 'auto'})")
        print("📡 Listening for packets: TCP→Basic, ICMP→Fast, ARP→Zigzag, UDP→Tank")
        
        try:
            # Start packet capture with BPF filter for efficiency
            sniff(
                iface=self.interface,
                filter="tcp or icmp or arp or udp",
                prn=self.process_packet,
                stop_filter=lambda p: self.stop_event.is_set(),
                store=False  # Don't store packets in memory
            )
        except PermissionError:
            print("❌ Permission denied! Try:")
            print("   sudo python main.py")
            print("   OR (Linux): sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)")
        except Exception as e:
            print(f"❌ Network monitor error: {e}")
        
        print("🌐 Network Monitor stopped")
    
    def stop(self):
        """Signal the network monitor to stop."""
        self.stop_event.set()
    
    def get_stats(self):
        """Get packet capture statistics."""
        return self.packet_count.copy()
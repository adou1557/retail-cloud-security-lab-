import ipaddress

"""
RetailLab Network Validator

This module analyzes an IPv4 network and displays its main
addressing properties, including the network address, subnet mask,
broadcast address, host range, and network capacity.
"""

def network_analyse(chaine_cidr):
    try:
        network = ipaddress.ip_network(chaine_cidr)

        # IPv4 uniquement
        if network.version != 4:
            print("Error: IPv6 is not supported.")
            return

        first_host = network.network_address + 1
        last_host = network.broadcast_address - 1

        message = f"""
Network information
-------------------

Network : {network.network_address}
CIDR : /{network.prefixlen}
Netmask : {network.netmask}
Broadcast : {network.broadcast_address}
First host : {first_host}
Last host : {last_host}
"""

        print(message)

    except ValueError:
        print("Error: invalid IPv4 network.")


d = input("Enter an IPv4 network: \n")
network_analyse(d)
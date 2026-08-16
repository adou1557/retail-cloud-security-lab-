import ipaddress

"""
RetailLab Network Overlap Detector

This module compares two IP networks and determines whether
their address spaces overlap.

Overlapping networks can cause routing, VPN, peering, and
hybrid connectivity issues.
"""

def parse_network(network_input):
    """
    Convert a string into an IPv4 or IPv6 network object.

    Args:
        network_input: Network entered by the user.

    Returns:
        An IPv4Network or IPv6Network object.

    Raises:
        ValueError: If the network is invalid.
    """
    return ipaddress.ip_network(network_input.strip(), strict=True)


def check_overlap(first_network, second_network):
    """
    Check whether two IP networks overlap.

    Args:
        first_network: First IP network.
        second_network: Second IP network.

    Returns:
        True if the networks overlap, otherwise False.

    Raises:
        TypeError: If the networks use different IP versions.
    """
    if first_network.version != second_network.version:
        raise TypeError(
            "The networks must use the same IP version."
        )

    return first_network.overlaps(second_network)


def display_result(first_network, second_network, has_overlap):
    """
    Display the network overlap analysis result.
    """
    print("\nNetwork Overlap Analysis")
    print("=" * 50)
    print(f"First network  : {first_network}")
    print(f"Second network : {second_network}")
    print(f"IP version     : IPv{first_network.version}")

    if has_overlap:
        print("\nStatus         : OVERLAP DETECTED")
        print(
            f"Result         : {first_network} overlaps "
            f"with {second_network}."
        )
    else:
        print("\nStatus         : NO OVERLAP")
        print(
            f"Result         : {first_network} and "
            f"{second_network} are separate."
        )


def main():
    """
    Run the interactive network overlap detector.
    """
    print("RetailLab - Network Overlap Detector")
    print("=" * 50)

    first_network_input = input(
        "First network (example 10.20.0.0/16): "
    )

    second_network_input = input(
        "Second network (example 10.20.10.0/24): "
    )

    try:
        first_network = parse_network(first_network_input)
        second_network = parse_network(second_network_input)

        has_overlap = check_overlap(
            first_network,
            second_network
        )

        display_result(
            first_network,
            second_network,
            has_overlap
        )

    except ValueError as error:
        print("\nStatus : INVALID INPUT")
        print(f"Error  : {error}")

    except TypeError as error:
        print("\nStatus : INCOMPATIBLE NETWORKS")
        print(f"Error  : {error}")


if __name__ == "__main__":
    main()

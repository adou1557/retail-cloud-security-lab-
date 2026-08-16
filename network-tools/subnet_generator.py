import ipaddress


def generate_store_subnets(parent_network, number_of_stores, subnet_prefix):
    """
    Generate one subnet per retail store from a parent IPv4 network.
    """

    try:
        # Convert the string into an IPv4Network object.
        network = ipaddress.ip_network(parent_network, strict=True)

    except ValueError:
        print("Error: Invalid network.")
        return

    # This project currently supports IPv4 only.
    if network.version != 4:
        print("Error: IPv4 networks only.")
        return

    # Example:
    # Parent = /24
    # New prefix cannot be /16.
    if subnet_prefix <= network.prefixlen:
        print(
            "Error: The subnet prefix must be greater "
            "than the parent prefix."
        )
        return

    # IPv4 cannot have a prefix greater than /32.
    if subnet_prefix > 32:
        print("Error: Invalid IPv4 subnet prefix.")
        return

    if number_of_stores <= 0:
        print("Error: Number of stores must be greater than zero.")
        return

    # Example:
    # Parent /16 -> Child /24
    # 2^(24 - 16) = 256 possible subnets
    available_subnets = 2 ** (subnet_prefix - network.prefixlen)

    # Verify capacity before generating all subnets.
    if number_of_stores > available_subnets:
        print("Error: Not enough subnets.")
        print(f"Required: {number_of_stores}")
        print(f"Available: {available_subnets}")
        return

    print("\nRetailLab Store Addressing Plan")
    print("=" * 45)

    # ipaddress.subnets() generates child networks.
    subnets = network.subnets(new_prefix=subnet_prefix)

    # Allocate one subnet per store.
    for store_number in range(1, number_of_stores + 1):
        subnet = next(subnets)

        print(
            f"Store-{store_number:03d} : {subnet}"
        )

    remaining_subnets = available_subnets - number_of_stores

    print("\nSummary")
    print("=" * 45)
    print(f"Parent network     : {network}")
    print(f"Subnet prefix      : /{subnet_prefix}")
    print(f"Available subnets  : {available_subnets}")
    print(f"Allocated subnets  : {number_of_stores}")
    print(f"Remaining subnets  : {remaining_subnets}")


def main():
    print("RetailLab - Store Subnet Generator")
    print("=" * 45)

    parent_network = input(
        "Parent network (example 10.20.0.0/16): "
    ).strip()

    try:
        number_of_stores = int(
            input("Number of stores: ")
        )

        subnet_prefix = int(
            input("Subnet prefix (example 24): ")
        )

    except ValueError:
        print("Error: Stores and prefix must be integers.")
        return

    generate_store_subnets(
        parent_network,
        number_of_stores,
        subnet_prefix
    )


if __name__ == "__main__":
    main()
import pandas as pd
import ipaddress
import sys


def read_csv_list_site(file):
    """Read and validate the CSV file."""

    try:
        data = pd.read_csv(file)

        required_columns = {"SITE", "NETWORK", "ROLE"}

        if not required_columns.issubset(data.columns):
            print("ERROR: Invalid CSV header")
            print("Required columns: SITE, NETWORK, ROLE")
            return None

        return data

    except FileNotFoundError:
        print(f"ERROR: File '{file}' not found")
        return None

    except pd.errors.EmptyDataError:
        print("ERROR: CSV file is empty")
        return None


def validate_network(network):
    """Return an IPv4 network or None if invalid."""

    try:
        return ipaddress.ip_network(network, strict=True)
    except ValueError:
        return None


def main():

    data = read_csv_list_site("sites.csv")

    if data is None:
        sys.exit(1)

    conflicts = []
    invalid_networks = []

    # Validate networks
    for i, row in data.iterrows():

        network = validate_network(str(row["NETWORK"]))

        if network is None:
            invalid_networks.append(
                f"{row['SITE']} - {row['NETWORK']}"
            )
            continue

        # Compare with following networks
        for j in range(i + 1, len(data)):

            network2 = validate_network(
                str(data.iloc[j]["NETWORK"])
            )

            if network2 is None:
                continue

            if network.overlaps(network2):
                conflicts.append(
                    (
                        row["SITE"],
                        network,
                        data.iloc[j]["SITE"],
                        network2
                    )
                )

    # Report
    print("\nRetailLab Network Validation Report")
    print("===================================")
    print(f"\nNetworks analyzed : {len(data)}")

    if invalid_networks:
        print("\nINVALID NETWORKS")

        for network in invalid_networks:
            print(network)

    if conflicts:
        print("\nCONFLICTS")

        for site1, net1, site2, net2 in conflicts:
            print(f"\n{site1} - {net1}")
            print(f"{site2} - {net2}")

    if invalid_networks or conflicts:
        print("\nSTATUS : FAILED")
        sys.exit(1)

    print("\nSTATUS : PASSED")


if __name__ == "__main__":
    main()
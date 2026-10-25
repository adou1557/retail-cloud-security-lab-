import logging
import socket
import sys
import time
from typing import Optional, Tuple

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def read_csv_list_site(file: str):
    """Read and validate the CSV file."""
    try:
        data = pd.read_csv(file)

        required_columns = {"SITE", "HOST", "PORT"}

        if not required_columns.issubset(data.columns):
            logger.error("Invalid CSV header")
            logger.error("Required columns: SITE, HOST, PORT")
            return None

        return data

    except FileNotFoundError:
        logger.error("File '%s' not found", file)
        return None

    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty")
        return None


def connectivity_tester(
        host: str,
        port: int,
        timeout: float = 2.0,
) -> Tuple[bool, Optional[float]]:
    """Test a TCP connection and return its status and connection time."""
    start_time = time.perf_counter()

    try:
        with socket.create_connection(
                (host, port),
                timeout=timeout,
        ):
            tcp_connection_time = (
                                          time.perf_counter() - start_time
                                  ) * 1000

            return True, round(tcp_connection_time, 2)

    except socket.gaierror as e:
        logger.error(
            "Résolution DNS échouée pour %s: %s",
            host,
            e,
        )

    except socket.timeout:
        logger.warning(
            "Connexion expirée vers %s:%d (timeout=%.1fs)",
            host,
            port,
            timeout,
        )

    except ConnectionRefusedError as e:
        logger.warning(
            "Connexion refusée sur %s:%d : %s",
            host,
            port,
            e,
        )

    except OSError as e:
        logger.error(
            "Erreur réseau/socket sur %s:%d : %s",
            host,
            port,
            e,
        )

    return False, None


if __name__ == "__main__":
    data = read_csv_list_site("sites_magasins_reseau.csv")

    if data is None:
        sys.exit(1)

    for _, row in data.iterrows():
        site = row["SITE"]
        host = row["HOST"]
        port = int(row["PORT"])

        is_open, tcp_connection_time = connectivity_tester(
            host,
            port,
        )

        if is_open:
            print(
                f"[+] {site} - {host}:{port} "
                f"est OUVERT - Temps connexion TCP : "
                f"{tcp_connection_time} ms"
            )
        else:
            print(
                f"[-] {site} - {host}:{port} "
                f"est FERME ou INACCESSIBLE"
            )
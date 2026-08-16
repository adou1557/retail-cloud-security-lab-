# Retail Network Engineering Toolkit

## Overview

The Retail Network Engineering Toolkit is a Python project developed
for RetailLab, a fictional multi-site retail company.

The project automates IP addressing validation and basic network
troubleshooting operations.

## Current Features

### Network Validator

Analyzes an IPv4 CIDR network and displays its addressing properties.

### Store Subnet Generator

Allocates one non-overlapping subnet to each retail store from a
parent IPv4 network.

### Network Overlap Detector

Compares two IP networks and identifies overlapping address spaces.

## Planned Features

- CSV addressing plan validation
- DNS resolution testing
- TCP port connectivity testing
- Automated report generation

## Project Structure

- `network_tools/`: Python network utilities
- `data/`: Sample network addressing plans
- `reports/`: Generated and example reports
- `tests/`: Automated tests
- `docs/`: Technical documentation and incident reports

## Requirements

- Python 3.10 or later
- No external dependency is currently required

## Usage

Run the subnet generator:

```bash
python network_tools/subnet_generator.py

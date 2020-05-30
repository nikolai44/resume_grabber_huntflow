import argparse
from dataclasses import dataclass


parser = argparse.ArgumentParser(description='Huntflow upload candidates script')
parser.add_argument('-t', '--token', help='API token', required=True)
parser.add_argument('-p', '--path', help='Path to database', required=True)
args = parser.parse_args()

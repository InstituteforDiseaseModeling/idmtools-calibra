#!/usr/bin/env python
import argparse

import emodpy.bamboo_api_utils as bamboo_api

# This script requires to have VPN and run from command line prompt. It only needs run one time if succeed login

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--username', help='enter bamboo username')
    parser.add_argument('-p', '--password', help='enter bamboo password')

    args = parser.parse_args()
    print("Login to bamboo and cache the credentials.")

    succeed = bamboo_api.bamboo_connection().login(username=args.username, password=args.password)
    print(f'login status: {succeed}')

    if succeed:
        bamboo_api.save_credentials(username=args.username, password=args.password)
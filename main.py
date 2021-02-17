import argparse
import os
import sqlite3
import csv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive a message convo into some format")

    parser.add_argument('backup_dir', type=str, help='Path to iphone backup')
    parser.add_argument('contact_name', type=str,
                        help='Name of contact whose conversation should be archived')
    parser.add_argument(
        '--time_range', type=str, help='Date range in the form 01/01/2001-01/01/2002')
    parser.add_argument(
        '--save_all', help='Save all conversations', action='store_true')

    args = parser.parse_args()
    return args.backup_dir, args.contact_name, args.time_range, args.save_all


def main():
    backup_dir, contact_name, time_range, save_all = parse_args()
    print(backup_dir, contact_name, time_range, save_all)


if __name__ == "__main__":
    main()

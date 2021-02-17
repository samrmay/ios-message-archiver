import argparse
import os
import sqlite3
import csv


def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive a message convo into some format")

    parser.add_argument('backup_path', type=str, help='Path to iphone backup')
    parser.add_argument('contact_name', type=str,
                        help='Name of contact whose conversation should be archived')
    parser.add_argument(
        '--time_range', type=str, help='Date range in the form 01/01/2001-01/01/2002')
    parser.add_argument(
        '--save_all', help='Save all conversations', action='store_true')

    args = parser.parse_args()
    return args.backup_path, args.contact_name, args.time_range, args.save_all


class Message_archiver:
    def __init__(self, backup_dir, contact_name, time_range, save_all):
        self.backup_dir = backup_dir
        if save_all:
            self.contact_name = '__all__'
        else:
            self.contact_name = contact_name

        if time_range:
            self.time_range = time_range
        else:
            self.time_range = '__all__'


def main():
    backup_path, contact_name, time_range, save_all = parse_args()
    print(backup_path, contact_name, time_range, save_all)


if __name__ == "__main__":
    main()

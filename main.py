import argparse
import os
import sqlite3
import csv
import time
import getpass

DATA_DICT = {'sms': ('Library/SMS/sms.db', 'message')}
MESSAGE_DICT = {'is_from_me': 21, 'handle_id': 5,
                'cache_roomnames': 35, 'text': 2}
BOS_TOKEN = '<BOS>'
EOS_TOKEN = '<EOS>'


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


class MessageArchiver:
    def __init__(self, backup_path, contact_name, time_range, save_all):
        self.backup_path = backup_path
        if save_all:
            self.contact_name = '__all__'
        else:
            self.contact_name = contact_name

        if time_range:
            self.time_range = time_range
        else:
            self.time_range = '__all__'

    def get_backup(self):
        backups_arr = []
        for backup in os.listdir(self.backup_path):
            path = self.backup_path + backup
            new_dict = {'path': path,
                        'mtime': os.path.getmtime(path)}
            backups_arr.append(new_dict)
        if (len(backups_arr) == 0):
            print('No backups found.')
            return False
        if (len(backups_arr) == 1):
            print('One backup found.')
            return backups_arr[0]

        print('Select a backup from which to retrieve data:')
        i = 0
        for backup in backups_arr:
            i += 1
            print(f'{i}. {backup.get("path")}')
            mtime = time.localtime(backup.get("mtime"))
            print(f'    Last modified on {mtime[1]}/{mtime[2]}/{mtime[0]}')
        target_index = int(input()) - 1
        while len(backups_arr) < target_index < 0:
            print(f'Error, pick an integer between 0-{len(backups_arr)}')
            target_index = int(input()) - 1
        return backups_arr[target_index]


def main():
    backup_path, contact_name, time_range, save_all = parse_args()
    archiver = MessageArchiver(backup_path, contact_name, time_range, save_all)

    archiver.get_backup()


if __name__ == "__main__":
    main()

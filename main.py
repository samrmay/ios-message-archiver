import argparse
import os
import sqlite3
import csv
import time
import getpass

DEFAULT_BACKUP_DIR = f'C:/users/{getpass.getuser()}/Apple/MobileSync/Backup/'
DATA_DICT = {'sms': ('Library/SMS/sms.db', 'message')}
MESSAGE_DICT = {'is_from_me': 21, 'handle_id': 5,
                'cache_roomnames': 35, 'text': 2}
BOS_TOKEN = '<BOS>'
EOS_TOKEN = '<EOS>'


def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive a message convo into some format")

    parser.add_argument('-b', '--backup_dir', type=str,
                        help='Path to iphone backup directory. Defaults to default directory on Windows.', default=DEFAULT_BACKUP_DIR)
    parser.add_argument('-t', '--time_range', type=str,
                        help='Date range in the form 01/01/2001-01/01/2002', default='__all__')
    parser.add_argument('-c', '--contact', type=str,
                        help='Select which conversation to save. Defaults to all convos', default='__all__')
    parser.add_argument('-f', '--filetype',
                        help='File format to save as', default='.csv')

    args = parser.parse_args()
    return args.backup_dir, args.contact, args.time_range, args.filetype


class MessageArchiver:
    def __init__(self, backup_dir, contact, time_range, filetype):
        self.backup_dir = backup_dir
        self.filetype = filetype
        # __all__ for contact/time_range will archive all conversations/time periods respectively
        self.contact = contact
        self.time_range = time_range

        self.backup_path = None
        self.db_path = None

    def get_backup(self):
        backups_arr = []
        for backup in os.listdir(self.backup_dir):
            path = self.backup_dir + backup
            new_dict = {'path': path,
                        'mtime': os.path.getmtime(path)}
            backups_arr.append(new_dict)
        if (len(backups_arr) == 0):
            raise FileNotFoundError('No backups found in directory')
        if (len(backups_arr) == 1):
            print('One backup found.')
            self.backup_path = backups_arr[0].get('path')
            return

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
        self.backup_path = backups_arr[target_index].get('path')

    def retrieve_db_path(self, target_db):
        manifest = f'{self.backup_path}/Manifest.db'
        try:
            with sqlite3.connect(manifest) as conn:
                cur = conn.cursor()
                cur.execute(
                    'SELECT * FROM Files WHERE relativePath=?', (target_db,))
                dbs = cur.fetchall()
                db_id = dbs[0][0]
            for dirpath, _, filearr in os.walk(self.backup_path):
                for filename in filearr:
                    if filename == db_id:
                        db_path = f"{dirpath}/{db_id}"
            self.db_path = db_path
        except:
            raise FileNotFoundError('Could not open backup (encrypted?)')


def main():
    backup_dir, contact, time_range, filetype = parse_args()
    archiver = MessageArchiver(
        backup_dir, contact, time_range, filetype)

    archiver.get_backup()
    archiver.retrieve_db_path(DATA_DICT.get('sms')[0])


if __name__ == "__main__":
    main()

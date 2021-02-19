import argparse
import os
import sqlite3
import csv
import time
import getpass
import re

DEFAULT_BACKUP_DIR = f'C:/users/{getpass.getuser()}/Apple/MobileSync/Backup/'
DATA_DICT = {'sms': ('Library/SMS/sms.db', 'message')}
CHAT_TABLE = 'chat'
MSSG_DICT = {'is_from_me': 21, 'handle_id': 5,
             'cache_roomnames': 35, 'text': 2}
NUM_PATT = re.compile(r'\+?1?(\d{10})')


def format_contact_number(raw, arg):
    if raw:
        try:
            return NUM_PATT.match(raw).group(1)
        except:
            argparse.ArgumentError(arg, 'Contact must be valid phone number')
    else:
        return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Archive a message convo into some format")

    parser.add_argument('-b', '--backup_dir', type=str,
                        help='Path to iphone backup directory. Defaults to default directory on Windows.', default=DEFAULT_BACKUP_DIR)
    parser.add_argument('-t', '--time_range', type=str,
                        help='Date range in the form 01/01/2001-01/01/2002', default='__all__')
    contact_arg = parser.add_argument('-c', '--contact', type=str,
                                      help='Number for which to save convos. Defaults to all', default='__all__')
    parser.add_argument('-f', '--filetype',
                        help='File format to save as', default='.csv')

    args = parser.parse_args()

    formatted_contact = format_contact_number(args.contact, contact_arg)
    return args.backup_dir, formatted_contact, args.time_range, args.filetype


class MessageArchiver:
    def __init__(self, backup_dir, contact, time_range, filetype):
        self.backup_dir = backup_dir
        self.filetype = filetype
        # __all__ for contact/time_range will archive all conversations/time periods respectively
        # Contact should be formatted to standard ten digit form (no +, leading 1)
        self.contact = contact
        self.time_range = time_range

        self.sms_local_db_path = DATA_DICT.get('sms')[0]
        self.sms_table_name = DATA_DICT.get('sms')[1]
        self.MSSG_DICT = MSSG_DICT
        self.CHAT_TABLE_NAME = CHAT_TABLE

        self.backup_path = None
        self.db_path = None
        self.mssgs = None
        self.chat_table = None
        # List of tuples containing (handle id, number, chat name)
        self.chat_handles = None
        # Dict of convos with phone numbers as keys. Contain lists of tuples (text_content, is_from_me)
        self.convo_dict = None

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

    def retrieve_db_path(self, local_path):
        manifest = f'{self.backup_path}/Manifest.db'
        try:
            with sqlite3.connect(manifest) as conn:
                cur = conn.cursor()
                cur.execute(
                    'SELECT * FROM Files WHERE relativePath=?', (local_path,))
                dbs = cur.fetchall()
                db_id = dbs[0][0]
            for dirpath, _, filearr in os.walk(self.backup_path):
                for filename in filearr:
                    if filename == db_id:
                        db_path = f"{dirpath}/{db_id}"
            self.db_path = db_path
        except:
            raise FileNotFoundError('Could not open backup (encrypted?)')

    def retrieve_all_data(self, table):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM {table}')
            return cur.fetchall()

    def retrieve_target_handles(self):
        """
        Retrieve handles for given contact from chat table (matches phone number with
        conversation handle id
        """
        handles = []
        if self.contact == '__all__':
            self.add_all_handles()
        else:
            for entry in self.chat_table:
                number = entry[6]
                if re.match(rf"\+1{self.contact}", number):
                    handles.append((entry[0], entry[6], entry[1]))
            if len(handles) == 0:
                raise IndexError('No chats found for that contact')
            self.chat_handles = handles

    def add_all_handles(self):
        self.chat_handles = [(x[0], x[6], x[1]) for x in self.chat_table]
        if len(self.chat_handles) == 0:
            raise IndexError('No chats found')

    def bin_messages(self):
        self.convo_dict = {}
        for tup in self.chat_handles:
            self.convo_dict[tup[0]] = []

        for mssg in self.mssgs:
            try:
                id_ = mssg[MSSG_DICT['handle_id']]
                text = mssg[MSSG_DICT['text']]
                is_from_me = mssg[MSSG_DICT['is_from_me']]
                self.convo_dict[id_].append((text, is_from_me))
            except KeyError:
                pass

    def save_messages(self):
        if self.filetype == '.csv':
            save = self.save_as_csv
        elif self.filetype == '.txt':
            save = self.save_as_txt

        for key in self.convo_dict.keys():
            outfile = str(key) + self.filetype
            mssg_arr = self.convo_dict[key]
            for tup in self.chat_handles:
                if key == tup[0]:
                    contact = tup[1]
                    break
            save(outfile, mssg_arr, contact)

    def save_as_csv(self, output, mssg_arr, contact):
        with open(output, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for mssg in mssg_arr:
                sender = 'me' if mssg[1] == 1 else contact
                writer.writerow([sender, mssg[0]])

    def save_as_txt(self, output, mssg_arr, contact):
        pass


def main():
    backup_dir, contact, time_range, filetype = parse_args()
    archiver = MessageArchiver(
        backup_dir, contact, time_range, filetype)

    archiver.get_backup()
    archiver.retrieve_db_path(archiver.sms_local_db_path)

    archiver.mssgs = archiver.retrieve_all_data(archiver.sms_table_name)
    archiver.chat_table = archiver.retrieve_all_data(archiver.CHAT_TABLE_NAME)
    archiver.retrieve_target_handles()
    archiver.bin_messages()
    archiver.save_messages()


if __name__ == "__main__":
    main()

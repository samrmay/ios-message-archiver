# ios-message-archiver
Archive messages from an iphone backup into .txt, .enex, .csv.

## Steps to run
1. Backup iphone through itunes. Do not encrypt or it will be inaccessible outside of native itunes.
2. Clone repo
3. Run `python main.py -h` for argument information.

## To do
- Implement date argument (currently a dummy arg)
- Implement other file types (filetype currently a dummy arg)
- Handle group chats
- Handle more varied contact input (eventually associate phone number with contact name)

# GoIT Python Core - Homework 08

Homework assignment #8 from the GoIT Python Core course: serialization and copying of objects. The console bot from homework 07 now saves the address book to disk with `pickle` and restores it on the next start.

## Task: Save and Load the Address Book

**File:** `bot.py`

- `save_data(book)` - saves the `AddressBook` to `addressbook.pkl` with `pickle.dump`
- `load_data()` - loads the `AddressBook` from `addressbook.pkl` with `pickle.load`; if there is no file yet, returns a new empty book
- `main()` - loads the book at start and saves it on exit

**Edge cases:**

| Situation | What happens |
|---|---|
| first start, no file | empty book, the file appears after the first exit |
| `close` / `exit`, Ctrl+C, Ctrl+D | the book is saved |
| the bot crashes on an unexpected error | the book is still saved (`try` / `finally`) |
| the bot is started from another folder | the same file is used, it lives next to `bot.py` |
| crash in the middle of saving | the previous save stays whole: data is written to a temporary file first |
| empty, cut or broken file | the file is renamed to `addressbook.pkl.bak`, the bot starts with an empty book |

`addressbook.pkl` is personal data, so it is in `.gitignore` and is not committed.

## Bot Commands

**Files:** `bot.py`, `address_book.py` (from homework 07)

| Command | What it does |
|---|---|
| `add [name] [phone]` | adds a new contact, or a phone to an existing contact |
| `change [name] [old phone] [new phone]` | changes a phone of the contact |
| `phone [name]` | shows phones of the contact |
| `all` | shows all contacts |
| `add-birthday [name] [DD.MM.YYYY]` | adds a birthday to the contact |
| `show-birthday [name]` | shows the birthday of the contact |
| `birthdays` | shows birthdays to congratulate during the next week |
| `hello` | greeting |
| `close` / `exit` | saves the book and closes the program |

**Example:**

```
$ python3 bot.py
Welcome to the assistant bot!
Enter a command: add John 1234567890
Contact added.
Enter a command: exit
Good bye!

$ python3 bot.py
Welcome to the assistant bot!
Enter a command: all
Contact name: John, phones: 1234567890
Enter a command: exit
Good bye!
```

## Grading Criteria

1. Serialization / deserialization is implemented with `pickle`.
2. All data is saved when the program closes.
3. On a new start, the address book from the previous run is restored.

## How to Run

```bash
python3 bot.py        # start the bot
python3 test_bot.py   # checks
```

No external dependencies, only the Python standard library (Python 3.10+).

## Project Structure

```
goit-pycore-hw-08/
├── address_book.py   # Address book classes
├── bot.py            # Console bot with save / load
├── test_bot.py       # Checks
├── .gitignore
└── README.md
```

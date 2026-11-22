"""
Checks for address_book.py and bot.py

Run: python3 test_bot.py
"""

import pickle
import tempfile
from datetime import date
from pathlib import Path

from address_book import AddressBook, Birthday, Record
from bot import (
    add_birthday,
    add_contact,
    load_data,
    parse_input,
    save_data,
    show_birthday,
)


def expect_error(error_type: type[Exception], func, *args) -> None:
    """Check that func(*args) raises error_type."""
    try:
        func(*args)
    except error_type:
        return
    raise AssertionError(f"{error_type.__name__} expected for {args!r}")


def make_book(birthdays: dict[str, str]) -> AddressBook:
    """Return a book with contacts {name: birthday}."""
    book = AddressBook()
    for name, birthday in birthdays.items():
        record = Record(name)
        record.add_birthday(birthday)
        book.add_record(record)
    return book


def test_birthday() -> None:
    """Only real dates in format DD.MM.YYYY are accepted."""
    for bad in ("1990-01-01", "32.01.1990", "29.02.2023", "01.13.1990",
                "abc", "", "01.01.2999"):
        expect_error(ValueError, Birthday, bad)
    Birthday("29.02.2024")


def test_add_birthday() -> None:
    """A record has one birthday, a new one replaces the old one."""
    record = Record("John")
    assert record.birthday is None
    record.add_birthday("01.01.1990")
    record.add_birthday("15.03.1995")
    assert "15.03.1995" in str(record)
    expect_error(ValueError, record.add_birthday, "1995-03-15")


def test_upcoming_birthdays() -> None:
    """Next 7 days only, weekend -> Monday. 19.11.2026 is Thursday."""
    book = make_book({
        "Today": "19.11.1990",      # Thursday, today
        "Friday": "20.11.1990",
        "Saturday": "21.11.1990",   # -> Monday 23.11
        "Sunday": "22.11.1990",     # -> Monday 23.11
        "Passed": "18.11.1990",     # yesterday
        "Later": "30.11.1990",      # in 11 days
    })
    book.add_record(Record("NoBirthday"))

    upcoming = book.get_upcoming_birthdays(today=date(2026, 11, 19))
    result = {item["name"]: item["congratulation_date"] for item in upcoming}
    assert result == {
        "Today": "19.11.2026",
        "Friday": "20.11.2026",
        "Saturday": "23.11.2026",
        "Sunday": "23.11.2026",
    }, result


def test_upcoming_birthdays_new_year() -> None:
    """A birthday in January is found at the end of December."""
    book = make_book({"Ann": "01.01.1990"})
    upcoming = book.get_upcoming_birthdays(today=date(2026, 12, 29))
    assert upcoming == [{"name": "Ann", "congratulation_date": "01.01.2027"}]


def test_parse_input() -> None:
    """Command is lowercased, arguments are kept."""
    assert parse_input("ADD-Birthday John 01.01.1990") == (
        "add-birthday", "John", "01.01.1990"
    )


def test_bot_errors() -> None:
    """Handlers return a message instead of crashing."""
    book = AddressBook()
    for result in (
        add_contact([], book),
        add_contact(["John", "123"], book),
        add_birthday(["Nobody", "01.01.1990"], book),
        show_birthday([], book),
    ):
        assert isinstance(result, str) and result, result

    assert book.find("John") is None  # invalid phone -> no empty contact
    assert add_contact(["John", "1234567890"], book) == "Contact added."
    assert add_contact(["John", "5555555555"], book) == "Contact updated."
    assert isinstance(add_birthday(["John", "1990-01-01"], book), str)
    add_birthday(["John", "01.01.1990"], book)
    assert "01.01.1990" in show_birthday(["John"], book)


def test_save_and_load() -> None:
    """Everything saved is restored: phones and birthdays."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "addressbook.pkl"
        book = AddressBook()
        add_contact(["John", "1234567890"], book)
        add_contact(["John", "5555555555"], book)
        add_birthday(["John", "01.01.1990"], book)
        add_contact(["Jane", "9876543210"], book)
        save_data(book, path)

        loaded = load_data(path)
        assert isinstance(loaded, AddressBook)
        assert str(loaded) == str(book)
        assert "01.01.1990" in show_birthday(["John"], loaded)
        assert not path.with_name(path.name + ".tmp").exists()

        # The second save replaces the first one
        add_contact(["Bob", "1112223333"], loaded)
        save_data(loaded, path)
        assert load_data(path).find("Bob") is not None


def test_load_missing_file() -> None:
    """First start: no file -> empty book, no file is created."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "addressbook.pkl"
        book = load_data(path)
        assert isinstance(book, AddressBook) and len(book) == 0
        assert not path.exists()


def test_load_broken_file() -> None:
    """Broken file -> empty book, the file is kept as *.bak."""
    broken_contents = (
        b"",                                  # empty file
        b"not a pickle at all",               # garbage
        pickle.dumps({"John": "123"})[:-5],   # cut in the middle
        pickle.dumps(["not", "a", "book"]),   # a pickle of another type
    )
    for contents in broken_contents:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "addressbook.pkl"
            path.write_bytes(contents)
            book = load_data(path)
            assert isinstance(book, AddressBook) and len(book) == 0
            assert not path.exists()
            assert path.with_name(path.name + ".bak").read_bytes() == contents


if __name__ == "__main__":
    test_birthday()
    test_add_birthday()
    test_upcoming_birthdays()
    test_upcoming_birthdays_new_year()
    test_parse_input()
    test_bot_errors()
    test_save_and_load()
    test_load_missing_file()
    test_load_broken_file()
    print("All checks passed.")

# Library Management System

A simple command-line library system I built in Python to practice object-oriented programming.

You can add books and members, borrow and return books, and check which ones are overdue. Data is saved in a JSON file, so nothing is lost when you close the program.

## What it does

- Add books (with more than one copy) and search by title, author or ISBN
- Two types of members:
  - Student: up to 3 books for 14 days
  - Teacher: up to 5 books for 30 days
- Borrow and return books
- Late returns are charged a fine of 10 per day
- Shows a list of overdue books
- Saves everything to a JSON file

## Concepts used

- Classes and inheritance (`Student` and `Teacher` extend an abstract `Member` class)
- Dataclasses for `Book` and `Loan`
- Custom exceptions for errors like "book unavailable" or "borrow limit reached"
- Reading and writing JSON
- Unit tests with `unittest`

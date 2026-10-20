"""The Library class: business logic for books, members and loans."""
from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

from .exceptions import (
    BookNotFoundError, BookUnavailableError, BorrowLimitError,
    DuplicateError, LoanNotFoundError, MemberNotFoundError,
)
from .models import Book, Loan, Member

FINE_PER_DAY = 10  # currency units per overdue day


class Library:
    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.members: dict[str, Member] = {}
        self.loans: List[Loan] = []

    # ---------- catalogue ----------
    def add_book(self, book: Book) -> None:
        if book.isbn in self.books:
            raise DuplicateError(f"Book with ISBN {book.isbn} already exists.")
        self.books[book.isbn] = book

    def get_book(self, isbn: str) -> Book:
        try:
            return self.books[isbn]
        except KeyError:
            raise BookNotFoundError(f"No book with ISBN {isbn}.") from None

    def search_books(self, query: str) -> List[Book]:
        q = query.lower().strip()
        return [b for b in self.books.values()
                if q in b.title.lower() or q in b.author.lower() or q in b.isbn]

    # ---------- members ----------
    def add_member(self, member: Member) -> None:
        if member.member_id in self.members:
            raise DuplicateError(f"Member {member.member_id} already exists.")
        self.members[member.member_id] = member

    def get_member(self, member_id: str) -> Member:
        try:
            return self.members[member_id]
        except KeyError:
            raise MemberNotFoundError(f"No member with ID {member_id}.") from None

    # ---------- loans ----------
    def active_loans(self, member_id: Optional[str] = None) -> List[Loan]:
        return [l for l in self.loans if l.is_active
                and (member_id is None or l.member_id == member_id)]

    def borrow(self, isbn: str, member_id: str, today: Optional[date] = None) -> Loan:
        today = today or date.today()
        book = self.get_book(isbn)
        member = self.get_member(member_id)
        if book.available < 1:
            raise BookUnavailableError(f"'{book.title}' has no copies available.")
        if len(self.active_loans(member_id)) >= member.max_loans:
            raise BorrowLimitError(
                f"{member.name} reached the limit of {member.max_loans} books.")
        if any(l.isbn == isbn for l in self.active_loans(member_id)):
            raise BorrowLimitError(f"{member.name} already has this book.")
        loan = Loan(isbn, member_id, today, today + timedelta(days=member.loan_days))
        book.available -= 1
        self.loans.append(loan)
        return loan

    def return_book(self, isbn: str, member_id: str,
                    today: Optional[date] = None) -> int:
        """Return a book and get the fine owed (0 if on time)."""
        today = today or date.today()
        for loan in self.active_loans(member_id):
            if loan.isbn == isbn:
                loan.return_date = today
                self.get_book(isbn).available += 1
                return loan.days_overdue(today) * FINE_PER_DAY
        raise LoanNotFoundError("No active loan found for this book and member.")

    def overdue_loans(self, today: Optional[date] = None) -> List[Loan]:
        today = today or date.today()
        return [l for l in self.active_loans() if l.days_overdue(today) > 0]

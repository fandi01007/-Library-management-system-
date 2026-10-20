import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from library import Book, FINE_PER_DAY, Library, Student, Teacher
from library import storage
from library.exceptions import (
    BookNotFoundError, BookUnavailableError, BorrowLimitError,
    DuplicateError, LoanNotFoundError,
)

TODAY = date(2025, 1, 1)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.lib = Library()
        for i in range(5):
            self.lib.add_book(Book(f"isbn{i}", f"Title {i}", "Author", 2020, copies=1))
        self.lib.add_book(Book("multi", "Popular", "Someone", 2021, copies=2))
        self.lib.add_member(Student("S1", "Ali", "a@x.com"))
        self.lib.add_member(Student("S2", "Sara", "s@x.com"))
        self.lib.add_member(Teacher("T1", "Dr. Raza", "t@x.com"))

    def test_duplicate_book_rejected(self):
        with self.assertRaises(DuplicateError):
            self.lib.add_book(Book("isbn0", "Dup", "X", 2000))

    def test_search_by_title_and_author(self):
        self.assertEqual(len(self.lib.search_books("popular")), 1)
        self.assertEqual(len(self.lib.search_books("author")), 5)

    def test_borrow_reduces_availability(self):
        self.lib.borrow("isbn0", "S1", TODAY)
        self.assertEqual(self.lib.get_book("isbn0").available, 0)

    def test_unavailable_book_cannot_be_borrowed(self):
        self.lib.borrow("isbn0", "S1", TODAY)
        with self.assertRaises(BookUnavailableError):
            self.lib.borrow("isbn0", "S2", TODAY)

    def test_student_limit_is_three(self):
        for i in range(3):
            self.lib.borrow(f"isbn{i}", "S1", TODAY)
        with self.assertRaises(BorrowLimitError):
            self.lib.borrow("isbn3", "S1", TODAY)

    def test_teacher_gets_higher_limit_and_longer_loan(self):
        loan = self.lib.borrow("isbn0", "T1", TODAY)
        self.assertEqual(loan.due_date, TODAY + timedelta(days=30))
        for i in range(1, 5):
            self.lib.borrow(f"isbn{i}", "T1", TODAY)
        self.assertEqual(len(self.lib.active_loans("T1")), 5)

    def test_cannot_borrow_same_book_twice(self):
        self.lib.borrow("multi", "S1", TODAY)
        with self.assertRaises(BorrowLimitError):
            self.lib.borrow("multi", "S1", TODAY)

    def test_return_on_time_has_no_fine(self):
        self.lib.borrow("isbn0", "S1", TODAY)
        fine = self.lib.return_book("isbn0", "S1", TODAY + timedelta(days=14))
        self.assertEqual(fine, 0)
        self.assertEqual(self.lib.get_book("isbn0").available, 1)

    def test_late_return_fine(self):
        self.lib.borrow("isbn0", "S1", TODAY)
        fine = self.lib.return_book("isbn0", "S1", TODAY + timedelta(days=19))
        self.assertEqual(fine, 5 * FINE_PER_DAY)

    def test_return_without_loan_fails(self):
        with self.assertRaises(LoanNotFoundError):
            self.lib.return_book("isbn0", "S1", TODAY)

    def test_overdue_detection(self):
        self.lib.borrow("isbn0", "S1", TODAY)
        self.assertEqual(self.lib.overdue_loans(TODAY + timedelta(days=10)), [])
        self.assertEqual(len(self.lib.overdue_loans(TODAY + timedelta(days=20))), 1)

    def test_unknown_book(self):
        with self.assertRaises(BookNotFoundError):
            self.lib.borrow("nope", "S1", TODAY)

    def test_save_and_load_roundtrip(self):
        self.lib.borrow("isbn0", "S1", TODAY)
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "lib.json")
            storage.save(self.lib, path)
            restored = storage.load(path)
        self.assertEqual(len(restored.books), len(self.lib.books))
        self.assertEqual(len(restored.members), 3)
        self.assertEqual(len(restored.active_loans("S1")), 1)
        self.assertEqual(restored.get_book("isbn0").available, 0)


if __name__ == "__main__":
    unittest.main()

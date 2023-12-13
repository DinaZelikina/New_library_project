from datetime import datetime
import pytest
from book import Book
from library import Library

def test_book_get_available_info():
    book1 = Book(
        book_id="123",
        title="book 1",
        author="author 1",
        year="1900",
        max_loan_time=2
    )
    book2 = Book(
        book_id="456",
        title="book 2",
        author="author 2",
        year="2000",
        max_loan_time=5
    )
    
    library = Library(
        name="new library",
        address="city",
        books=[book1, book2],
        customers=["customer"],
        history={
            1: {"book": "123", "loan_date": datetime.now()},
            2: {"book": "456", "loan_date": datetime.now(), "return_date": datetime.now()}
        }
    )
    
    book1.get_available_info(library)
    assert not book1.is_available

    book2.get_available_info(library)
    assert book2.is_available
import pytest
from library import Library, Book

@pytest.fixture
def library_fixture_1():
    library = Library(name="My_library", address="City")
    
    book1 = Book(book_id="1", title="Harry Potter 1", author="J. Rowling", year="1997", max_loan_time=5)
    book2 = Book(book_id="2", title="Harry Potter 2", author="J. Rowling", year="2000", max_loan_time=5)
    book3 = Book(book_id="3", title="Harry Potter 3", author="J. Rowling", year="2005", max_loan_time=5)
    
    library.books = [book1, book2, book3]
    
    return library

@pytest.mark.parametrize("index, expected", [
    (0, [Book(book_id="2", title="Harry Potter 2", author="J. Rowling", year="2000", max_loan_time=5),
         Book(book_id="3", title="Harry Potter 3", author="J. Rowling", year="2005", max_loan_time=5)]),
         
    (1, [Book(book_id="1", title="Harry Potter 1", author="J. Rowling", year="1997", max_loan_time=5),
         Book(book_id="3", title="Harry Potter 3", author="J. Rowling", year="2005", max_loan_time=5)]),

    (2, [Book(book_id="1", title="Harry Potter 1", author="J. Rowling", year="1997", max_loan_time=5),
         Book(book_id="2", title="Harry Potter 2", author="J. Rowling", year="2000", max_loan_time=5)])
])

def test_display_all_books(library_fixture_1, index, expected):
    library_fixture_1.books[index].is_removed = True
    result = library_fixture_1.display_all_books()
    assert result == expected

@pytest.fixture
def library_fixture_2():
    library = Library(name="My_library", address="City")
    
    book1 = Book(book_id="1", title="Harry Potter 1", author="J. Rowling", year="1997", max_loan_time=5, is_available=True, is_removed=False)
    book2 = Book(book_id="2", title="Harry Potter 2", author="J. Rowling", year="2000", max_loan_time=5, is_available=False, is_removed=False)
    book3 = Book(book_id="3", title="Harry Potter 3", author="J. Rowling", year="2005", max_loan_time=5, is_available=True, is_removed=True)
    
    library.books = [book1, book2, book3]
    
    return library

@pytest.mark.parametrize("book_title, expected", [
    ("Harry Potter 1", Book(book_id='1', title='Harry Potter 1', author='J. Rowling', year='1997', max_loan_time=5, is_available=True, is_removed=False)),
    ("Harry Potter 2", "not available"),
    ("Harry Potter 3", "not in stock"),
    ("Harry Potter 4", "not in stock")
])

def test_check_ability_by_title(library_fixture_2, book_title, expected):
    result = library_fixture_2.check_availability_by_title(book_title)
    assert result == expected
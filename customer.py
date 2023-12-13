from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Customer:
    customer_id: str
    name: str
    city: str
    birth_date: str   
    loaned_books: list = field(default_factory=list)
    late_loans: list = field(default_factory=list)
    is_removed: bool = field(default=False)

    def __str__(self):
        return(f"{self.name}")
    
# Shows on display main information about a customer       
    def display_customer(self):
        print(f"\nId: {self.customer_id}")
        print(f"Name: {self.name}")
        print(f"City: {self.city}")
        print(f"Date of birth: {self.birth_date}")
        birth_date = datetime.strptime(self.birth_date, "%d.%m.%Y")
        now = datetime.now()
        age = now.year - birth_date.year
        if birth_date.month > now.month:
            age -= 1
        if birth_date.month == now.month and birth_date.day > now.day:
            age -= 1
        print(f"Age: {age}")
    
# Gets information about books currently loaned to the сustomer from the history of all loans and returns
    def get_loaned_books(self, library):
        for key, value in library.history.items():
            if key.split("_")[0] == self.customer_id:
                for book in library.books:
                    if value["book"] == book.book_id and "return_date" not in value.keys() and not book.is_removed:
                        if book not in self.loaned_books:
                            self.loaned_books.append(book)

# Gets information about books late loanes of a сustomer. Saves book and delay duration                       
    def get_late_loans(self, library):
        self.get_loaned_books(library)
        for book in self.loaned_books:
            for value in library.history.values():
                if value["book"] == book.book_id and "return_date" not in value.keys() and not book.is_removed:
                    loan_date = datetime.strptime(value['loan_date'], "%d.%m.%Y")
                    now = datetime.now()
                    delay = (now - loan_date).days - int(book.max_loan_time)
                    if delay > 0:
                        late_loan = {"book": book, "delay": delay}
                        if late_loan not in self.late_loans:
                            self.late_loans.append(late_loan)

# Displays books currently loaned to the сustomer with the date of loan
    def display_loaned_books(self, library):
        self.get_loaned_books(library)
        for book in self.loaned_books:
            for value in library.history.values():
                if value["book"] == book.book_id and "return_date" not in value.keys() and not book.is_removed:
                    print(f"{book} loaned on {value['loan_date']}")
   
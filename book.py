from dataclasses import dataclass, field

@dataclass
class Book:
    book_id: str
    title: str
    author: str
    year: str
    max_loan_time: int
    is_available: bool = field(default=True)
    is_removed: bool = field(default=False)
       
    def __str__(self):
        return(f"\"{self.title}\", {self.author}")

# Shows on display main information about a book   
    def display_book(self):
        print(f"\nId: {self.book_id}")
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Year of publication: {self.year}")
    
# Gets information from the history of all loans and returns and change argumet "is_available" if book was already loaned
    def get_available_info(self, library):
        for record in library.history.values():        
            if record["book"] == self.book_id and "return_date" not in record.keys():
                self.is_available = False

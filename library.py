from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import json
from collections import Counter
import time
from book import *
from customer import *

@dataclass
class Library:
    name: str
    address: str
    books: list = field(default_factory=list)
    customers: list = field(default_factory=list)
    history: dict = field(default_factory=dict)

    def __str__(self):
        return f"\"{self.name}\", {self.address}"

# Gives user oportunity to end his session in every moment
    def user_input(self, message):
        user_answer = input(message)
        exit_words = ["exit", "quit", "q", "x"]
        if user_answer.lower() in exit_words:
            print("Session ended. New session started")
            self.display_actions()
        return user_answer
    
# Finds object book if we know its id number            
    def find_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                return book
            
# Finds object book if we know its title            
    def find_book_by_title(self, title):
        same_books = []
        for book in self.books:
            if book.title.lower() == title and not book.is_removed:
                same_books.append(book)
        return same_books
    
# Finds object customer if we know his id number
    def find_customer(self, customer_id):
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer
            
# Finds object customer if we know his name
    def find_customer_by_name(self, name):
        same_names = []
        for customer in self.customers:
            if customer.name.lower() == name and not customer.is_removed:
                same_names.append(customer)
        return same_names

# Makes a list of all books of the library
    def display_all_books(self):
        all_books = []
        for book in self.books:
            if not book.is_removed:
                all_books.append(book)
        return all_books

# Makes a list of all customers of the library
    def display_all_customers(self):
        all_customers = []
        for customer in self.customers:
            if not customer.is_removed:
                all_customers.append(customer)
        return all_customers

# Makes a list of all loans 
    def display_all_loans(self):
        all_loans = []
        for customer in self.customers:
            customer.loaned_books = []
            customer.get_loaned_books(self)
            for book in customer.loaned_books:
                all_loans.append({"book": book, "customer": customer})
        return all_loans

# Makes a list of all late loans    
    def display_late_loans(self):
        list_of_lates = []
        for customer in self.customers:
            customer.late_loans = []
            customer.get_late_loans(self)
            number_of_lates = len(customer.late_loans)
            if number_of_lates == 0:
                continue
            else:
                for record in customer.late_loans:
                    list_of_lates.append(f"Customer id {customer.customer_id} {customer} delayed book {record['book']} for {record['delay']} days")
        return list_of_lates

# Reads all books of the library from file if there ara books in the library
    def add_books_from_file(self, books_file):
        try:
            books_file = open("books.json", "r")
            all_books = json.load(books_file)
            books_file.close()
            self.books = [Book(**d) for d in all_books]
        except FileNotFoundError:
            pass

# Adds new book from keybord
    def add_book_from_keyboard(self):
        title = self.user_input("\nEnter the book title: ")
        author = self.user_input("Enter the book author: ")
        year = self.user_input("Enter the year of publication: ")
        if not year.isnumeric():
            print("Incorrect year of publication. Please, try again")
            self.new_session("1")
        max_loan_time = None
        for book in self.books:        
            if title.lower() == book.title.lower() and author.split()[-1].lower() == book.author.split()[-1].lower() and year == book.year:
                max_loan_time = book.max_loan_time
                break
        if max_loan_time is None:
            max_loan_time = self.user_input("Enter the maximum number of days for loan: ")
        if max_loan_time in ["10", "5", "2"]:
            try:
                id = int(self.books[-1].book_id) + 1
            except IndexError:
                id = 1
            new_book = Book(str(id), title, author, year, max_loan_time) 
            self.books.append(new_book)
            self.save_books_file(books_file="books.json")
            print(f"Adding a book {new_book} to the library was successful")
            user_answer = self.user_input('\nDo you whant to add one more book? Type "Y" for continue, "N" for end this session: ')
            if user_answer.lower() in ["y", "yes"]:
                self.new_session("1")
            elif user_answer.lower() in ["n", "no"]:
                print("Session ended")
                self.display_actions()              
            else:
                print("Unacceptable answer. Session ended")
                self.display_actions()
        else:
            print("Wrong number of days. The maximum number of days can only be 10, 5 or 2. Try again")
            self.new_session("1")

# Removes book from the library
    def remove_book(self):
        id = self.user_input('\nEnter book id (Type "F" for find book by title): ')
        if id.lower() in ["f", "find"]:
            self.new_session("3")
            self.remove_book()
        elif not id.isnumeric():
            print("Incorrect book id. Please, try again")
            self.remove_book()
        else:
            book = self.find_book(id)
            if not book:
                print("Book not found. Please, try again")
                self.remove_book()
            elif book.is_removed:
                print("This book was already removed from the library")
            else:
                print("This book was found:")
                book.display_book()
                print("\nDo you want to remove this book from the library?")
                user_answer = self.user_input('Type "Y" for remove a book, "N" for choose another book: ')
                if user_answer.lower() in ["y", "yes"]:
                    book.is_removed = True
                    for customer in self.customers:
                        if book in customer.loaned_books:
                            customer.loaned_books.remove(book)
                    self.save_books_file(books_file="books.json")
                    print(f"Removing book {book} from the library was successful")
                elif user_answer.lower() in ["n", "no"]:
                    self.remove_book()              
                else:
                    print("Unacceptable answer. Session ended")
                    self.display_actions()

# Adds customers from the file if library already has customers
    def add_customers_from_file(self, customers_file):
        try:
            customers_file = open("customers.json", "r")
            all_customers = json.load(customers_file)
            customers_file.close()
            self.customers = [Customer(**d) for d in all_customers]
        except FileNotFoundError:
            pass

# Adds customer from keybord
    def add_customer_from_keyboard(self):
        name = self.user_input("\nEnter customer full name: ")
        city = self.user_input("Enter customer city: ")
        birth_date = self.user_input("Enter customer date of birth in the format dd.mm.yyyy: ")
        try:
            datetime.strptime(birth_date, "%d.%m.%Y")
            for customer in self.customers:
                if customer.name == name.title() and customer.city == city.title() and customer.birth_date == birth_date:
                    print(f"We have a registered customer with this data. Customer id is {customer.customer_id}")
                    return
            try:
                id = int(self.customers[-1].customer_id) + 1
            except IndexError:
                id = 1
            new_customer = Customer(str(id), name.title(), city.title(), birth_date) 
            self.customers.append(new_customer)
            self.save_customers_file(customers_file="customers.json")
            print(f"New customer registration was successful\nId number of customer {new_customer} is {id}")
            return new_customer
        except ValueError:
            print("Invalid date of birth format. Try again")
            self.new_session("5")

# Removes customer
    def remove_customer(self):
        id = self.user_input('\nEnter customer id: ')
        if not id.isnumeric():
            print("Incorrect customer id. Please, try again")
            self.remove_customer()
        else:
            customer = self.find_customer(id)
            if not customer:
                print("Customer not found. Please, try again")
                self.remove_customer()
            elif customer.is_removed:
                print("This customer was already removed")
            else:
                print("This customer was found:")
                customer.display_customer()
                print("\nDo you want to remove this customer?")
                user_answer = self.user_input('Type "Y" for remove a customer, "N" for choose another customer: ')
                if user_answer.lower() in ["y", "yes"]:
                    count_books = len(customer.loaned_books)
                    if count_books > 0:
                        print(f"\nWarning: {customer} has {count_books} loaned book(s). If you remove a customer, these books\nwill be automatically removed from the library. If you do not want to remove books,\nyou need to return them to the library before removing the customer.")
                        user_answer = self.user_input('\nAre you sure you want remove a customer? (Type "Y" for continue, "N" for cancel): ')
                        if user_answer.lower() in ["y", "yes"]:
                            customer.is_removed = True
                            print(f"\nRemoving customer {customer} from the library was successful")
                            for book in customer.loaned_books:
                                book.is_removed = True
                                print(f"Book {book} is removed from the library")
                                # customer.loaned_books.remove(book)
                            self.save_customers_file(customers_file="customers.json")
                        else:
                            print("Session ended")
                            self.display_actions()
                    else:
                        customer.is_removed = True
                        print(f"Removing customer {customer} from the library was successful")
                elif user_answer.lower() in ["n", "no"]:
                    self.remove_customer()              
                else:
                    print("Unacceptable answer. Session ended")
                    self.display_actions()

# Finds out 3 most popular book from from the history of all loans and returns and shows them on display
    def display_popular_books(self):
        popular_books = Counter(record["title"] for record in self.history.values())
        most_popular_books = popular_books.most_common(3)
        if most_popular_books:
            print("\nYou can recommend the most popular books from our library to the customer:")
            for item in most_popular_books:
                for book in self.books:
                    if item[0] == book.title and not book.is_removed:
                        print(book)
                        break            

# Loads history of all loans and returns from the file if it already exists                            
    def load_history(self, history_file):
        try:
            history_file = open("history.json", "r")
            history = json.load(history_file)
            history_file.close()
            self.history.update(history)
        except FileNotFoundError:
            pass

# Gets all information about loans, retuns and availablty of the books
    def load_all_data(self):
        self.add_books_from_file(books_file="books.json")
        self.add_customers_from_file(customers_file="customers.json")
        self.load_history(history_file="history.json")
        for book in self.books:
            book.get_available_info(self)
        for customer in self.customers:
            customer.get_loaned_books(self)

# Saves history of loans and returns to the file
    def save_history(self, history_file):
        history_file = open("history.json", "w")
        json.dump(self.history, history_file, indent=2)
        history_file.close()

# Saves new books to the file
    def save_books_file(self, books_file):
        books_file = open("books.json", "w")
        books_dict = []
        for book in self.books:
            book_dict = asdict(book)
            del book_dict["is_available"]
            books_dict.append(book_dict)
        json.dump(books_dict, books_file, indent=2)
        books_file.close()

# Saves new customers to the file
    def save_customers_file(self, customers_file):
        customers_file = open("customers.json", "w")
        customers_dict = []
        for customer in self.customers:
            customer_dict = asdict(customer)
            del customer_dict["loaned_books"]
            del customer_dict["late_loans"]
            customers_dict.append(customer_dict)
        json.dump(customers_dict, customers_file, indent=2)
        customers_file.close()

# Saves all information about loans, returns and customers to the files
    def save_all_data(self):
        self.save_books_file(books_file="books.json")
        self.save_history(history_file="history.json")
        self.save_customers_file(customers_file="customers.json")

# Checks if we have a book in the library and if it is available for loan
# (there may be several identical books in the library)
    def check_availability_by_title(self, book_title):
        result = "not in stock"
        for book in self.books:
            if book_title.lower() == book.title.lower():
                result = "not available"
                if book.is_available and not book.is_removed:
                    result = book
                    break
                else:
                    if book.is_removed:
                        result = "not in stock"
                    continue
        return result
    
# Loans book for a customer if it is available and adds information about loan to history
# Counts return dedline 
    def loan_book(self, customer, book_title):
        check = self.check_availability_by_title(book_title)
        if check == "not in stock":
            print(f"Sorry, \"{book_title}\" is out of stock")
        elif check == "not available":
            print(f"Sorry, \"{book_title}\" is not available now\nYou can borrow another book from our library")
        else:
            book = check
            book.is_available = False                
            date = datetime.now().strftime("%d.%m.%Y")
            return_date = datetime.now() + timedelta(days=int(book.max_loan_time))
            customer.loaned_books.append(book)
            new_loan = {"customer": customer.customer_id, "book": book.book_id, "title": book.title, "loan_date": date}
            all_record_numbers = [record_id.split("_") for record_id in self.history.keys()]
            new_record_number = (max((int(record_number[1]) for record_number in all_record_numbers if record_number[0] == customer.customer_id), default=0)) + 1
            new_record_id = f"{customer.customer_id}_{new_record_number}"
            self.history.update({new_record_id: new_loan})
            self.save_history(history_file="history.json")
            print(f"\"{book.title}\" loaned to customer {customer}. Return deadline is {return_date.strftime('%d.%m.%Y')}") 
        
# Checks if customer has borrowed the book and return it to the library 
# Adds information about return to history
    def return_book(self, customer, book_title):
        for book in customer.loaned_books:
            if book_title.lower() == book.title.lower() and not book.is_available:
                book.is_available = True
                customer.loaned_books.remove(book)
                date = datetime.now().strftime("%d.%m.%Y")
                for record in self.history.values():
                    if "return_date" not in record.keys() and record["book"] == book.book_id:
                        record["return_date"] = date
                        print(f"{book} returned to the library") 
                        # self.continue_customer_session(customer_id) 
                        return
        print(f"Sorry,\"{book_title}\" is wrong book title")

# Check if customer id input was correct
    def wrong_customer_id(self, customer_id, action):
        if customer_id.isnumeric():
            print("Customer not found")
            print("Do you want to add a new customer?")
            user_answer = self.user_input('Type "Y" for add a customer, "N" for end this session: ')
            if user_answer.lower() in ["y", "yes"]:
                self.new_session("5")
            elif user_answer.lower() in ["n", "no"]:
                print("Session ended")
                self.new_session(action)                
            else:
                print("Unacceptable answer. Session ended")
                self.new_session(action)
        else:
            print("Incorrect customer id number. Please try again")
            self.new_session(action)

# Invites user to continue working with the program whis the same customer
    def continue_customer_session(self, customer):
        print("\nDo you want to continue session with current customer?")
        user_answer = self.user_input('Type "Y" for continue, "N" for end session: ')
        if user_answer.lower() in ["y", "yes"]:
            print("\nDo you want to loan or return a book")
            user_answer = self.user_input('Type "L" for loan, "R" for end return: ')
            if user_answer.lower() in ["l", "loan"]:
                self.new_session("9", customer_id=customer.customer_id)
                self.continue_customer_session(customer)
            elif user_answer.lower() in ["r", "return"]:
                self.new_session("10", customer_id=customer.customer_id)
                self.continue_customer_session(customer)
            else:
                print("Unacceptable answer. Session ended")
                self.display_actions()
        elif user_answer.lower() in ["n", "no"]:
            print("Session ended")
            self.display_actions()
        else:
            print("Unacceptable answer. Session ended")
            self.display_actions()

# Executes the program depending on the action selected by user
    def new_session(self, action, customer_id = None):
        if action == "1":
            self.add_book_from_keyboard()
            print("\nDo you want to add another book?")
            user_answer = self.user_input('Type "Y" for add another book, "N" for end this session: ')
            if user_answer.lower() in ["y", "yes"]:
                self.new_session("1")
            elif user_answer.lower() in ["n", "no"]:
                print("Session ended")
                self.display_actions()                
            else:
                print("Unacceptable answer. Session ended")
                self.display_actions()

        elif action == "2":
            self.remove_book()
            print("\nDo you want to remove another book?")
            user_answer = self.user_input('Type "Y" for remove another book, "N" for end this session: ')
            if user_answer.lower() in ["y", "yes"]:
                self.new_session("2")
            elif user_answer.lower() in ["n", "no"]:
                print("Session ended")
                self.display_actions()                
            else:
                print("Unacceptable answer. Session ended")
                self.display_actions()

        elif action == "3":
            title = self.user_input("\nEnter a book title: ")
            books = self.find_book_by_title(title)
            if len(books) > 0:
                print(f"\nThere are {len(books)} book(s) with this title in the library: ")
                for book in books:
                    book.display_book()
            else:
                print(f'Book with title "{title}" not found. Please, try again')
                self.new_session("3")

        elif action == "4":
            all_books = self.display_all_books()
            if len(all_books) > 0:
                print(f"\nThere are {len(all_books)} books in the library")
                for book in all_books:
                    time.sleep(0.2)
                    book.display_book()
            else:
                print("\nThere are no books in the library")

        elif action == "5":
            current_customer = self.add_customer_from_keyboard()
            self.continue_customer_session(current_customer)

        elif action == "6":
            self.remove_customer()

        elif action == "7":
            name = self.user_input("\nEnter a customer name: ")
            customers = self.find_customer_by_name(name)
            if len(customers) > 0:
                print(f"\nThere are {len(customers)} customer(s) with name {name}: ")
                for customer in customers:
                    customer.display_customer()
            else:
                print("\nCustomer not found. Do you want to add a new customer?")
                user_answer = self.user_input('Type "Y" for add a customer, "N" for end this session: ')
                if user_answer.lower() in ["y", "yes"]:
                    self.new_session("5")
                elif user_answer.lower() in ["n", "no"]:
                    print("Session ended")
                    self.display_actions()              
                else:
                    print("Unacceptable answer. Session ended")
                    self.display_actions()

        elif action == "8":
            all_customers = self.display_all_customers()
            if len(all_customers) > 0:
                print(f"\nThere are {len(all_customers)} customers in the library")
                for customer in all_customers:
                    time.sleep(0.2)
                    customer.display_customer()
            else:
                print("\nThere are no customers in the library")

        elif action == "9":
            if customer_id is not None:
                current_customer = self.find_customer(customer_id)
            else:
                customer_id = self.user_input("\nEnter customer id number: ")
                current_customer = self.find_customer(customer_id)
            if current_customer and not current_customer.is_removed:
                print(f"Current customer is {current_customer}")
                current_customer.get_late_loans(self)
                if len(current_customer.late_loans) > 0:
                    print(f'\nWarning: current customer already delayed {len(current_customer.late_loans)} book(s): {", ".join(str(late_loan["book"]) for late_loan in current_customer.late_loans)}')
                self.display_popular_books()
                print("\nWhat book does customer want to borrow?")
                book_title = self.user_input("Please, enter a title: ")
                self.loan_book(current_customer, book_title)
                self.continue_customer_session(current_customer)
            else:
                self.wrong_customer_id(customer_id, action)

        elif action == "10":
            if customer_id is not None:
                current_customer = self.find_customer(customer_id)
            else:
                customer_id = self.user_input("\nEnter customer id number: ")
                current_customer = self.find_customer(customer_id)
                print(f"Current customer is {current_customer}")
            if current_customer and not current_customer.is_removed:
                count_books = len(current_customer.loaned_books)
                if count_books > 0:
                    print(f"\n{current_customer} has {count_books} loaned book(s) now:")
                    current_customer.display_loaned_books(self)
                    print("\nWhat book does customer want to return?")
                    book_title = self.user_input("Please, enter a title: ")
                    self.return_book(current_customer, book_title)
                else:
                    print(f"\n{current_customer} has no books for return")
                self.continue_customer_session(current_customer)
            else:
                self.wrong_customer_id(customer_id, action)

        elif action == "11":
            all_loans = self.display_all_loans()
            if len(all_loans) > 0:
                print(f"\nThere are {len(all_loans)} loans now:")
                for item in all_loans:
                    time.sleep(0.2)
                    print(f"Book id {item['book'].book_id} {item['book']} is loaned to customer id {item['customer'].customer_id} {item['customer']}")
            else:
                print("\nThere are no loans now")
        
        elif action == "12":
            all_lates = self.display_late_loans()
            if len(all_lates) > 0:
                print(f"\nThere are {len(all_lates)} late loans now:")
                for record in all_lates:
                    time.sleep(0.2)
                    print(record)
            else:
                print("\nThere are no late loans now")

# Starts a new session, shows on dysplay a list of actions available to the user
    def display_actions(self):
        possible_actions = ["1. Add a new book", "2. Remove book", "3. Find book by title", "4. Display all books", 
                            "5. Add a new customer", "6. Remove customer", "7. Find customer by name", "8. Display all customers", 
                            "9. Loan a book to a customer", "10. Return a book from a customer", "11. Display all loans", "12. Display late loans"]
        print("\nYour possible actions are:")
        for action in possible_actions:
            time.sleep(0.2)
            print(action)
        while True:
            answer = input("Choose the action by number: ")
            if answer.lower() in ["exit", "quit", "q", "x"]:
                print("Library Managemet System finished. See you next time")
                self.save_all_data()
                exit()
            elif answer.isnumeric() and int(answer) in range(1, 13):
                self.new_session(answer)
                input("\nPress any key to start a new session ")
                self.display_actions()
            else:
                print("Impossible action. Pleace try again")

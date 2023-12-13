from library import *

my_library = Library("BestBooks", "Haifa")

my_library.load_all_data()
print(f"\nLibrary Managemet System started\nWelcome to the library {my_library}")
while True:
    try:
        my_library.display_actions()
    except KeyboardInterrupt:
        my_library.save_all_data()
        exit()
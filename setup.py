from backend.services import AdminPasswordHashService
from pony import orm

def main():
    if AdminPasswordHashService.exists():
    	print("Password is already set!")
    	return

    password = input("Enter website auth password (cannot be changed): ")

    AdminPasswordHashService.create(password)

if __name__ == '__main__':
    main()
from backend.services import AdminPasswordHashService
from pony import orm
import os

if not os.path.exists('demos'):
    os.makedirs('demos')

if not os.path.exists('demos/temp'):
    os.makedirs('demos/temp')

def main():
    if AdminPasswordHashService.exists():
    	print("Password is already set!")
    	return

    password = input("Enter website auth password (cannot be changed): ")

    AdminPasswordHashService.create(password)

if __name__ == '__main__':
    main()
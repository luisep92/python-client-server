import user



def main():
	u = user.User(name="Pepe", age=19, previous_years=[1999, 2000, 2001])
	print(repr(__name__))
    
if __name__ == "__main__":
    main()

def test():
	try:
		import tabletools
	except ImportError:
		tabletools = None
		print("Could not import tabletools")

	try:
		import numbertools
	except ImportError:
		numbertools = None
		print("Could not import numbertools")

	try:
		import timetools
	except ImportError:
		timetools = None
		print("Could not import timetools")

	try:
		import plottools
	except ImportError:
		plottools = None
		print("Could not import plottools")
	
	print("Current Namespace Contains: ")
	for i in dir():
		print("\t{}".format(i))

if __name__ == "__main__":
	test()
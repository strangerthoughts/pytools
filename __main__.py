
def test():
	try:
		import tabletools
	except ImportError:
		print("Could not import tabletools")

	try:
		import numbertools
	except ImportError:
		print("Could not import numbertools")

	try:
		import timetools
	except ImportError:
		print("Could not import timetools")

	try:
		import plottools
	except ImportError:
		print("Could not import plottools")
	
	print("Current Namespace Contains: ")
	for i in dir():
		print("\t{}".format(i))

if __name__ == "__main__":
	test()
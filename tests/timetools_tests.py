
from package import timetools

# list of timestamps formatted as (test_value, answer)
example_timestamps = [
	('2017-09-13', '2017-09-13'),
	('20170913', '2017-09-13'),
	('Sep 13, 2017', '2017-09-13'),
	('1997-07-16T19:20:30+01:00', '1997-07-16T19:20:30')
]

example_durations = [
	('P1Y2DT7H4S'),
	()
]

for test_value, answer_value in example_timestamps:
	timestamp = timetools.Timestamp(test_value)
	iso_string = timestamp.toIso()

	result = iso_string == answer_value

	print(result, test_value, '\t', iso_string, '\t', answer_value)


print("Finished!")



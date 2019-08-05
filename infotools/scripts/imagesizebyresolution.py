from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
from typing import List,Tuple
from tqdm import tqdm

def get_filesize(filename)->int:
	return filename.stat().st_size

def plot(x, y):
	plt.scatter(x, y)
	plt.show()

def main(folder:Path):
	files = list(folder.glob("**/*"))
	output = Path.home() / "Documents" / "sandbox" / "cache.txt"
	rows = list()
	for filename in tqdm(files):

		size= get_filesize(filename)
		try:
			image = Image.open(filename)
		except:
			continue

		height, width = image.size
		resolution = height * width

		data = {
			'filename': filename,
			'resolution': resolution,
			'filesize': size,
			'mode': image.mode,
			'format': image.format,
			'suffix': filename.suffix
		}
		rows.append(data)

	df = pandas.DataFrame(rows)

	df.to_csv(output, sep= '\t')

def main2():
	filename = Path.home() / "Documents" / "sandbox" / "cache.tsv"
	df = pandas.read_csv(filename, sep = '\t')

	filtered_df = df[df['format'] == 'JPEG']
	filtered_df = filtered_df[filtered_df['mode'] == 'RGB']

	plot(filtered_df['resolution'], filtered_df['filesise'])

if __name__ == "__main__":
	folder = Path.home() / "archive" / "Images"
	import pandas
	main2()




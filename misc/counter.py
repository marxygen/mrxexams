import json

if __name__ != '__main__':
	print('This script is to be called explicitly!')
	raise SystemExit

print('Initialized')
stats = dict()

filled = 0
total = 0

print('Counting...')

with open('words.json', 'r') as file:
	data = json.load(file)

	for (word, translation) in list(data.items()):
		stats[word.upper()[0]] = (stats[word.upper()[0]] + 1) if word.upper()[0] in list(stats.keys()) else 1
		if not (translation in ['', ' ', None, '1', 1]):
			filled += 1
		total += 1

print('Counting done\n\n')

print(f'Total numof words: {total}\nFilled entries: {filled}\n')
for (letter, number) in list(stats.items()):
	print(f'{letter} - {number} words. ~ {(number*2)//3600} hours')

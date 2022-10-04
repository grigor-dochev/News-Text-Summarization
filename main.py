from DataItem import DataItem
from DatasetLoader import DatasetLoader
from TextRank import TextRank
from rouge import Rouge

dataset_loader = DatasetLoader()
# dataset returns a dictionary mapping categories (strings) to lists of DataItem objects, where each DataItem has an article and summary property
dataset = dataset_loader.load_dataset()

data_item: DataItem = dataset['tech'][10]
example_article = data_item.get_article()
example_summary = data_item.get_summary()

textrank = TextRank()
textrank_summary = textrank.extract_sentences(example_article)

print('---------------------- TextRank Summary ----------------------')
print(textrank_summary)

print('\n')

print('----------------------- Actual Summary -----------------------')
print(example_summary)

rouge = Rouge()
scores = rouge.get_scores(textrank_summary, example_summary)
print(scores)

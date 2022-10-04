import os

from DataItem import DataItem


class DatasetLoader:
    def __init__(self):
        self._categories = ['business', 'entertainment', 'politics',
                            'tech']  # FIXME: there is a problem with one of the files in the 'sport' category
        self._dataset_directories = {
            'articles': '/Users/grigordochev/PycharmProjects/News-Text-Summarization/BBC News Summary Dataset/News Articles/',
            'summaries': '/Users/grigordochev/PycharmProjects/News-Text-Summarization/BBC News Summary Dataset/Summaries/'}

    def __load_category(self, category) -> [DataItem]:
        data_items: [DataItem] = []
        articles = {}
        summaries = {}

        for filename in os.listdir(self._dataset_directories['articles'] + category):
            file_path = os.path.join(self._dataset_directories['articles'] + category, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path) as file:
                        data = file.read()  # .replace('\n', '')
                        articles[filename] = data
                except UnicodeDecodeError as error:
                    print(error, 'File:', file_path)

        for filename in os.listdir(self._dataset_directories['summaries'] + category):
            file_path = os.path.join(self._dataset_directories['summaries'] + category, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path) as file:
                        data = file.read()  # .replace('\n', '')
                        summaries[filename] = data
                except UnicodeDecodeError as error:
                    print(error, 'File:', file_path)

        for i in range(1, min(len(summaries), len(articles))):
            article = articles[str(i).zfill(3) + '.txt']
            summary = summaries[str(i).zfill(3) + '.txt']
            data_item = DataItem(article, summary)
            data_items.append(data_item)

        return data_items

    def load_dataset(self) -> {str: [DataItem]}:
        dataset = {}

        for category in self._categories:
            category_data_items = self.__load_category(category)
            dataset[category] = category_data_items

        return dataset

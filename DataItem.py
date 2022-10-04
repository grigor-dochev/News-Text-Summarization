class DataItem:
    def __init__(self, article, summary):
        self._article = article
        self._summary = summary

    def get_article(self):
        return self._article

    def get_summary(self):
        return self._summary
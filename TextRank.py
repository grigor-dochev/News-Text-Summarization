"""Python implementation of the TextRank algoritm.

From this paper:
    https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf

Based on:
    https://gist.github.com/voidfiles/1646117
    https://github.com/davidadamojr/TextRank
"""
import io
import itertools
import os

import editdistance
import networkx as nx
import nltk


class TextRank:
    def __init__(self):
        self.setup_environment()

    def setup_environment(self):
        """Download required resources."""
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)

    def filter_for_tags(self, tagged, tags=['NN', 'JJ', 'NNP']):
        """Apply syntactic filters based on POS tags."""
        return [item for item in tagged if item[1] in tags]

    def normalize(self, tagged):
        """Return a list of tuples with the first item's periods removed."""
        return [(item[0].replace('.', ''), item[1]) for item in tagged]

    def unique_everseen(self, iterable, key=None):
        """List unique elements in order of appearance.

        Examples:
            unique_everseen('AAAABBBCCDAABBB') --> A B C D
            unique_everseen('ABBCcAD', str.lower) --> A B C D
        """
        seen = set()
        seen_add = seen.add
        if key is None:
            def key(x): return x
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

    def build_graph(self, nodes):
        """Return a networkx graph instance.

        :param nodes: List of hashables that represent the nodes of a graph.
        """
        gr = nx.Graph()  # initialize an undirected graph
        gr.add_nodes_from(nodes)
        nodePairs = list(itertools.combinations(nodes, 2))

        # add edges to the graph (weighted by Levenshtein distance)
        for pair in nodePairs:
            firstString = pair[0]
            secondString = pair[1]
            levDistance = editdistance.eval(firstString, secondString)
            gr.add_edge(firstString, secondString, weight=levDistance)

        return gr

    def extract_key_phrases(self, text):
        """Return a set of key phrases.

        :param text: A string.
        """
        # tokenize the text using nltk
        word_tokens = nltk.word_tokenize(text)

        # assign POS tags to the words in the text
        tagged = nltk.pos_tag(word_tokens)
        textlist = [x[0] for x in tagged]

        tagged = self.filter_for_tags(tagged)
        tagged = self.normalize(tagged)

        unique_word_set = self.unique_everseen([x[0] for x in tagged])
        word_set_list = list(unique_word_set)

        # this will be used to determine adjacent words in order to construct
        # keyphrases with two words

        graph = self.build_graph(word_set_list)

        # pageRank - initial value of 1.0, error tolerance of 0,0001,
        calculated_page_rank = nx.pagerank(graph, weight='weight')

        # most important words in ascending order of importance
        keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get,
                            reverse=True)

        # the number of keyphrases returned will be relative to the size of the
        # text (a third of the number of vertices)
        one_third = len(word_set_list) // 3
        keyphrases = keyphrases[0:one_third + 1]

        # take keyphrases with multiple words into consideration as done in the
        # paper - if two words are adjacent in the text and are selected as
        # keywords, join them together
        modified_key_phrases = set([])

        i = 0
        while i < len(textlist):
            w = textlist[i]
            if w in keyphrases:
                phrase_ws = [w]
                i += 1
                while i < len(textlist) and textlist[i] in keyphrases:
                    phrase_ws.append(textlist[i])
                    i += 1

                phrase = ' '.join(phrase_ws)
                if phrase not in modified_key_phrases:
                    modified_key_phrases.add(phrase)
            else:
                i += 1

        return modified_key_phrases

    def extract_sentences(self, text, summary_length=100, clean_sentences=False, language='english'):
        """Return a paragraph formatted summary of the source text.

        :param text: A string.
        """
        sent_detector = nltk.data.load('tokenizers/punkt/' + language + '.pickle')
        sentence_tokens = sent_detector.tokenize(text.strip())
        graph = self.build_graph(sentence_tokens)

        calculated_page_rank = nx.pagerank(graph, weight='weight')

        # most important sentences in ascending order of importance
        sentences = sorted(calculated_page_rank, key=calculated_page_rank.get,
                           reverse=True)

        # return a 100 word summary
        summary = ' '.join(sentences)
        summary_words = summary.split()
        summary_words = summary_words[0:summary_length]
        dot_indices = [idx for idx, word in enumerate(summary_words) if word.find('.') != -1]
        if clean_sentences and dot_indices:
            last_dot = max(dot_indices) + 1
            summary = ' '.join(summary_words[0:last_dot])
        else:
            summary = ' '.join(summary_words)

        return summary

    def write_files(self, summary, key_phrases, filename):
        """Write key phrases and summaries to a file."""
        key_phrase_file = io.open('keywords/' + filename, 'w')
        for key_phrase in key_phrases:
            key_phrase_file.write(key_phrase + '\n')
        key_phrase_file.close()

        summary_file = io.open('summaries/' + filename, 'w')
        summary_file.write(summary)
        summary_file.close()

    def summarize_all(self):
        # retrieve each of the articles
        articles = os.listdir("articles")
        for article in articles:
            article_file = io.open('articles/' + article, 'r')
            text = article_file.read()
            keyphrases = self.extract_key_phrases(text)
            summary = self.extract_sentences(text)
            self.write_files(summary, keyphrases, article)

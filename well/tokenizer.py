import logging
import spacy
import pandas as pd
import nltk
from nltk import tokenize
from string import punctuation
import unidecode
import re

def fn_stop_words(_texto):
    #try:
    #   nltk.find('stopwords')
    #except LookupError:
    #   nltk.download('stopwords')

    stop_words_pt = nltk.corpus.stopwords.words("portuguese")

    whitespace_tokenizer = nltk.WhitespaceTokenizer()
    tokens = whitespace_tokenizer.tokenize(_texto)
    novo_texto = [word for word in tokens if word not in stop_words_pt]

    return ' '.join(novo_texto)


def fn_punctuation(_texto):
    punct_tokenizer = tokenize.WordPunctTokenizer()
    tokens = punct_tokenizer.tokenize(_texto)
    novo_texto = [word for word in tokens if word not in list(punctuation)]

    return ' '.join(novo_texto)


def fn_lemmatizer(_texto):
    pt_news = spacy.load('pt_core_news_sm')
    doc = pt_news(_texto)
    novo_texto = [token.lemma_ for token in doc if token.pos_ != 'PUNCT']

    return ' '.join(novo_texto)


def fn_stemmer(_texto):
    # nltk.download('rslp')
    stemmer = nltk.RSLPStemmer()

    whitespace_tokenizer = tokenize.WhitespaceTokenizer()
    tokens = whitespace_tokenizer.tokenize(_texto)
    nova_frase = [stemmer.stem(word) for word in tokens]

    return ' '.join(nova_frase)


def tokenizer(text, to_lower=True, unicode=True, stop_words=True, lemmatizer=True, stemmer=True):
    clean_pattern = re.compile('\r|\n|\t|\s+')
    new_text = ''
    if not pd.isnull(text) and not text.isspace():
        new_text = re.sub(clean_pattern, ' ', text)

        if (to_lower and not stemmer):
            new_text = new_text.lower()

        if (unicode):
            new_text = unidecode.unidecode(new_text)

        if (stop_words):
            new_text = fn_stop_words(new_text)

        if (lemmatizer):
            new_text = fn_lemmatizer(new_text)

        if (stemmer):
            new_text = fn_stemmer(new_text)

    return new_text
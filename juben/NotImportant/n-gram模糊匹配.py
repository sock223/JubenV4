test_str1 = "I need to get most popular ngrams from text. Ngrams length must be from 1 to 5 words."
test_str2 = "I know how to exclude bigrams from trigrams, but i need better solutions."

from sklearn.feature_extraction.text import CountVectorizer

#1-5个词
c_vec = CountVectorizer(ngram_range=(1, 5))


# input to fit_transform() should be an iterable with strings
ngrams = c_vec.fit_transform([test_str1, test_str2])

# needs to happen after fit_transform()
vocab = c_vec.vocabulary_

count_values = ngrams.toarray().sum(axis=0)

# output n-grams
for ng_count, ng_text in sorted([(count_values[i],k) for k,i in vocab.items()], reverse=True):
    print(ng_count, ng_text)


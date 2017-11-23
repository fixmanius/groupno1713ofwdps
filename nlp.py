import nltk

texts="Hello Mr. Smith, how are you doing today? The weather is great, and Python is awesome. The sky is pinkish-blue. You shouldn't eat cardboard."

sentences = nltk.sent_tokenize(texts)
for sentence in sentences:
	words = nltk.word_tokenize(sentence)
	tagged_words = nltk.pos_tag(words)
	ne_tagged_words = nltk.ne_chunk(tagged_words)
	print ne_tagged_words
	
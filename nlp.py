import nltk
from nltk.corpus import stopwords

texts="Hello Mr. Trump, how are you doing today? The weather is great, and Python is awesome. The sky is pinkish-blue. You shouldn't eat cardboard."


#Tokenize
words = nltk.word_tokenize(texts)

#Stopwords Removal
stopset = set(stopwords.words('english'))
words = [w for w in words if not w in stopset]

sno = nltk.stem.SnowballStemmer('english')

for word in words:
	#Stemming
	stem_word = sno.stem(word)
	print stem_word
	
#POS-TAG
tagged_words = nltk.pos_tag(words)

#named entities
ne_tagged_words = nltk.ne_chunk(tagged_words)
print ne_tagged_words

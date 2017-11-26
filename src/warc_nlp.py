import warc
import nltk
from nltk.corpus import stopwords

#NLP function
def nlp(text):

	#text="Hello Mr. Trump, how are you doing today? The weather is great, and Python is awesome. The sky is pinkish-blue. You shouldn't eat cardboard."

	#Tokenize
	words = nltk.word_tokenize(text)

	#Stopwords Removal
	stopset = set(stopwords.words('english'))
	words = [w for w in words if not w in stopset]

	sno = nltk.stem.SnowballStemmer('english')

	for word in words:
		#Snowball stemming
		stem_word = sno.stem(word)
		print stem_word
		
	#POS-TAG
	#tagged_words = nltk.pos_tag(words)

	#named entities
	#ne_tagged_words = nltk.ne_chunk(tagged_words)
	#print ne_tagged_words
	
	return


#main program
f = warc.open("CommonCrawl-sample.warc") #filepath

from bs4 import BeautifulSoup

c=1

for num, record in enumerate(f):
	if record['WARC-Type'] == 'response':
		# print record['WARC-Record-ID']
		# print record['WARC-Target-URI']
		# print record['Content-Length']
		html_doc = record.payload.read()
		print '=-=-' * 10
		
		soup = BeautifulSoup(html_doc, 'lxml')

		body=(soup.get_text().encode('utf-8'))
		
		nlp(unicode(body,errors='ignore'))
		
		c=c+1
	
	if num > 1:
		print 'TERMINATED '+str(num-1)+" - "+str(c)
		break
		
import warc
import nltk
from nltk.corpus import stopwords
from nltk.chunk import conlltags2tree, tree2conlltags

#NLP function
def nlp(text):
	text="Hello Mr. Trump, how are you doing today? The weather in Amsterdam is great. Are you using an iPhone?"

	sentences = nltk.sent_tokenize(text)
	for sentence in sentences:
		
		#Tokenize
		words = nltk.word_tokenize(sentence)

		#Stopwords Removal
		stopset = set(stopwords.words('english'))
		words = [w for w in words if not w in stopset]		
		
		#Snowball stemming
		sno = nltk.stem.SnowballStemmer('english')
		for num, word in enumerate(words):
			stem_word = sno.stem(word)
			#print stem_word	
			
			# if num > 1:
				# print 'TERMINATEDz '+str(num-1)
				# break	
			
		#POS-TAG
		tagged_words = nltk.pos_tag(words)

		#NER
		ne_tagged_words = nltk.ne_chunk(tagged_words)
				
		iob_tagged = tree2conlltags(ne_tagged_words)
		print iob_tagged		
		
		'''
		for rel in nltk.sem.extract_rels('ORG', 'LOC', doc, corpus='ieer', pattern = IN):
			print(relextract.rtuple(rel))
		'''
		
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
		
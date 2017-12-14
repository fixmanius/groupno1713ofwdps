import sys
import nltk
import cosinesim
from nltk.corpus import stopwords
from nltk.chunk import conlltags2tree, tree2conlltags

#entity_recognition function
def entity_recognition_s(text):
	#text="It's 75 years since Casablanca was released in America. Nicholas Barber looks at how the classic romantic melodrama was really about the plight of the displaced."

	#prepare list of results
	results_list=[]
	sentence_list=[]
	sentences = nltk.sent_tokenize(text)
	for num, sentence in enumerate(sentences):
		sentence_list.append(sentence)
		#Tokenize
		words = nltk.word_tokenize(sentence)		

		#Stopwords Removal
		#stopset = set(stopwords.words('english'))
		#words = [w for w in words if not w in stopset]		
		
		#Snowball stemming
		# sno = nltk.stem.SnowballStemmer('english')
		# for num, word in enumerate(words):
			# stem_word = sno.stem(word)
			#print stem_word	
			
			# if num > 1:
				# print 'TERMINATEDz '+str(num-1)
				# break	
			
		#POS-TAG
		tagged_words = nltk.pos_tag(words)
		
		#NER
		'''ne_tagged_words = nltk.ne_chunk(tagged_words, True)
		for enum, x in enumerate(ne_tagged_words):
			print x," WAWAW ",x.node
		exit()'''
		
		#iob_tagged = tree2conlltags(ne_tagged_words)
		
		propernouns = [word for word,pos in tagged_words if (pos == 'NNP' or pos == 'NNPS')]
		
		results_list.append(propernouns)
		
		'''
		for rel in nltk.sem.extract_rels('ORG', 'LOC', doc, corpus='ieer', pattern = IN):
			print(relextract.rtuple(rel))
		'''
	
	return results_list,sentence_list

def hamming_dist(str1, str2):
	diffs = 0
	for ch1, ch2 in zip(str1, str2):
		if ch1 != ch2:
			diffs += 1
	return diffs

def char_dice_coefficient(a, b):
    a_bigrams = set(a)
    b_bigrams = set(b)
    overlap = len(a_bigrams & b_bigrams)
    return overlap * 2.0/(len(a_bigrams) + len(b_bigrams))

def bigram_dice_coefficient(a, b):
    """dice coefficient 2nt/na + nb."""
    if not len(a) or not len(b): return 0.0
    if len(a) == 1:  a=a+u'.'
    if len(b) == 1:  b=b+u'.'
    
    a_bigram_list=[]
    for i in range(len(a)-1):
      a_bigram_list.append(a[i:i+2])
    b_bigram_list=[]
    for i in range(len(b)-1):
      b_bigram_list.append(b[i:i+2])
      
    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0/(len(a_bigrams) + len(b_bigrams))
    return dice_coeff

def getBestDBO(entity,sentence):
	import requests
	import json, re
	import collections, math

	#TRIDENT_URL = 'http://10.141.0.11:8082/sparql'
	TRIDENT_URL = 'http://10.141.0.127:9001/sparql'

	prefixes = """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX owl: <http://www.w3.org/2002/07/owl#>
	PREFIX fbase: <http://rdf.freebase.com/ns/>
	PREFIX dbo:    <http://dbpedia.org/ontology/>
	PREFIX foaf: <http://xmlns.com/foaf/0.1/>
	"""
	
	po_template = prefixes + """
	SELECT DISTINCT * WHERE {
		%s ?p ?o.
	}
	"""

	#entity="Jakarta"
	#print('Counting KB facts...')
	po_template = prefixes + """
	SELECT * WHERE {
		?s foaf:name ?name.
		?s dbo:abstract ?abs.
		FILTER contains(str(?name),"%s")
	} LIMIT 100"""
	#print po_template % entity
	
	response = requests.post(TRIDENT_URL, data={'print': False, 'query': po_template %entity })

	uris = {}
	text   = {}
	if response:
		response = response.json()
		n = int(response.get('stats',{}).get('nresults',0))
		for enum, abstract in enumerate(response['results']['bindings']):
			uris[enum]=abstract['s']['value']
			text[enum]=abstract['abs']['value']
		sys.stdout.flush()

	best=None
	bestScore=0
	
	#cosine
	for i in uris:
		#print text[i]
		#print sentence
		x=cosinesim.test_cosine(text[i],sentence)
		if x>bestScore:
			best=uris[i]
			bestScore=x
	
	return best
	
# ------ main program ------

f = open("CommonCrawl-sample.warc",'r')
warc_content = f.read()

from bs4 import BeautifulSoup


if len(sys.argv) > 1:
	record_attribute = sys.argv[1]
else:
	print "provide keyname!"
	exit()

#split per warc file
d = "WARC/1.0"
s=warc_content.split(d)

for x in range(len(s)):
	warc_resp=s[x].lstrip()
	#process warc response only
	if warc_resp.startswith("WARC-Type: response"):
		
		#get key first
		payload = warc_resp
		key = None
		for line in payload.splitlines():
			if line.startswith(record_attribute):
				key = line.split(': ')[1]
				break
		
		if key:
			#parse HTML		
			soup = BeautifulSoup(warc_resp, 'lxml')
			body=(soup.get_text().encode('utf-8'))

			sent_entities,full_sents = entity_recognition_s(unicode(body,errors='ignore'))

			for enum, entities in enumerate(sent_entities):
				#print entities
				#print full_sents[enum]
				for entity in entities:
					dboURI=getBestDBO(entity,full_sents[enum])
					if dboURI!=None:
						print key+'\t'+entity+'\tm/'+dboURI
				#exit()

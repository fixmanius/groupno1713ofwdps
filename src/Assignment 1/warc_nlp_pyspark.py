from pyspark import SparkContext
import sys
import collections

sc = SparkContext("yarn", "wdps17XX")

if len(sys.argv) > 2:
	record_attribute = sys.argv[1]
	in_file = sys.argv[2]
else:
	print "provide arguments!"
	exit()
	
rdd_text=""
rdd = sc.textFile(in_file)
for line in rdd.collect():
	rdd_text += line.encode("utf-8")+"\n"

import sys
import nltk
from nltk.corpus import stopwords
from nltk.chunk import conlltags2tree, tree2conlltags

#entity_recognition function
def entity_recognition(text):
	#text="It's 75 years since Casablanca was released in America. Nicholas Barber looks at how the classic romantic melodrama was really about the plight of the displaced."

	#prepare list of results
	results_list=[]
	sentences = nltk.sent_tokenize(text)
	for num, sentence in enumerate(sentences):
		
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
		ne_tagged_words = nltk.ne_chunk(tagged_words)				
		#iob_tagged = tree2conlltags(ne_tagged_words)
		
		propernouns = [word for word,pos in tagged_words if pos == 'NNP']
		
		results_list.append(propernouns)
		
		'''
		for rel in nltk.sem.extract_rels('ORG', 'LOC', doc, corpus='ieer', pattern = IN):
			print(relextract.rtuple(rel))
		'''
	
	return results_list


def do_query(query):
	import requests
	import json, re
	import collections, math

	ELASTICSEARCH_URL = 'http://10.149.0.127:9200/freebase/label/_search'
	#TRIDENT_URL = 'http://10.141.0.11:8082/sparql'
	TRIDENT_URL = 'http://10.141.0.127:9001/sparql'

	#print('Searching for "%s"...' % query)
	response = requests.get(ELASTICSEARCH_URL, params={'q': query, 'size':100})
	ids = set()
	labels = {}
	scores = {}

	if response:
		response = response.json()
		for hit in response.get('hits', {}).get('hits', []):
			freebase_id = hit.get('_source', {}).get('resource')
			label = hit.get('_source', {}).get('label')
			score = hit.get('_score', 0)

			ids.add( freebase_id )
			scores[freebase_id] = max(scores.get(freebase_id, 0), score)
			labels.setdefault(freebase_id, set()).add( label )

	#print('Found %s results.' % len(labels))


	prefixes = """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
	PREFIX owl: <http://www.w3.org/2002/07/owl#>
	PREFIX fbase: <http://rdf.freebase.com/ns/>
	"""
	same_as_template = prefixes + """
	SELECT DISTINCT ?same WHERE {
		?s owl:sameAs %s .
		{ ?s owl:sameAs ?same .} UNION { ?same owl:sameAs ?s .}
	}
	"""
	po_template = prefixes + """
	SELECT DISTINCT * WHERE {
		%s ?p ?o.
	}
	"""

	#print('Counting KB facts...')
	facts  = {}
	for i in ids:
		response = requests.post(TRIDENT_URL, data={'print': False, 'query': po_template % i})
		if response:
			response = response.json()
			n = int(response.get('stats',{}).get('nresults',0))
			#print(i, ':', n)
			sys.stdout.flush()
			facts[i] = n

	def get_best(i):
		return math.log(facts[i]) * scores[i]

	#print('Best matches:')
	best=None
	for enum, i in enumerate(sorted(ids, key=get_best, reverse=True)[:3]):
		
		#getbest
		if enum==0:
			best=i[8:]			
	
		#print('No '+str(enum+1))
		#print(i, ':', labels[i], '(facts: %s, score: %.2f)' % (facts[i], scores[i]) )
		# sys.stdout.flush()
		# response = requests.post(TRIDENT_URL, data={'print': True, 'query': same_as_template % i})
		# if response:
			# response = response.json()
			# for binding in response.get('results', {}).get('bindings', []):
				# print(' =', binding.get('same', {}).get('value', None))
	
	return best
	
# ------ main program ------

from bs4 import BeautifulSoup

#split per warc file
d = "WARC/1.0"
s=rdd_text.split(d)

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

			sent_entities = entity_recognition(unicode(body,errors='ignore'))

			for entities in sent_entities:
				for entity in entities:
					entityID=do_query(entity)
					if entityID!=None:
						print key+'\t'+entity+'\tm/'+entityID

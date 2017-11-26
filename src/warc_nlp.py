import warc
f = warc.open("CommonCrawl-sample.warc")

for num, record in enumerate(f):
	if record['WARC-Type'] == 'response':
		# print record['WARC-Record-ID']
		# print record['WARC-Target-URI']
		# print record['Content-Length']
		html_doc = record.payload.read()
		print '=-=-' * 10
	if num > 1:
		break

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc, 'lxml')

print(soup.prettify())
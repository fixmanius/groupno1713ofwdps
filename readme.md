Running example:

run_wdps1713.sh WARC-Record-ID hdfs:///user/bbkruit/CommonCrawl-sample.warc.gz

This runs on ELASTICSEARCH and TRIDENT at node093

1. The script opens the HDFS file based on the path provided in the argument (argv 2) and collects the content as text.
2. The text (HDFS file content) is then split with "WARC/1.0" as the delimiter, this results in a list of text where each element roughly represents one warc file.
3. Iterate through each element, and only further process ones that are of WARC type response.
4. For each of the element in step 3, get the key as provided in the argument (argv 1).
5. Use beautiful soup to extract only text content in <body>.
6. Go through entity_recognition function which performs NLP. The output of the function is a list of proper nouns (NNP).
7. For each noun in step 6, go to do_query function which runs the query of the noun in elastic search.
8. Filter the candidates from the elastic search by comparing the label against the noun using hamming distance (<=2), characater dice coefficient (>0.9), and bigram dice coefficient (0.6).
9. Out of the filtered candidates, query each in trident and then return entity ID of the one with most popular one (freebase score * SPARQL hit).
9. Stream the result (key, noun, entity ID) to output.

from bs4 import BeautifulSoup
import csv
import string
soup = BeautifulSoup(open("vote_record.html"))
writer = csv.writer(open("vote_record.csv", "w"))

punc_translator = str.maketrans('', '', string.punctuation)
space_translator = str.maketrans('', '', string.whitespace)


writer.writerow(["clean_name", "vote"])
results = list(soup.find_all("ul"))
for yes in results[0].find_all("li"):
    name_processed = yes.text.translate(punc_translator)
    name_processed = name_processed.translate(space_translator)
    writer.writerow([name_processed, "yes"])
for no in results[1].find_all("li"):
    name_processed = no.text.translate(punc_translator)
    name_processed = name_processed.translate(space_translator)
    writer.writerow([name_processed, "no"])
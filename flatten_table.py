from bs4 import BeautifulSoup
soup = BeautifulSoup(open("problem_table.html"))
output = ""
for i in range(4):
    for row in soup.find("tbody").find_all("tr", recursive=False):
        for column_children in row.find_all("td", recursive=False)[i].find_all(recursive=False):
            output += str(column_children)
print(output)

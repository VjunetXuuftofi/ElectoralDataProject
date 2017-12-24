import pandas as pd
import string
data = pd.read_csv("output.csv")
incumbents = {}
adding_now = {}
output = []
punc_translator = str.maketrans('', '', string.punctuation)
space_translator = str.maketrans('', '', string.whitespace)

for i in range(1, 40):
    for index, row in data[data["congress"] == i].iterrows():
        name_processed = str(row["name"]).translate(punc_translator)
        name_processed = name_processed.translate(space_translator)
        data_tuple = (
            row["state"],
            row["district"],
            name_processed,
        )

        if data_tuple in incumbents:
            row["incumbent"] = True
            row["old_vote_share"] = incumbents[data_tuple]
            row["clean_name"] = name_processed
        else:
            row["incumbent"] = False
            row["old_vote_share"] = None
            row["clean_name"] = name_processed

        if row["result"] == "won":
            adding_now[data_tuple] = row["percentage"]
        output.append(row)
    incumbents = adding_now
    adding_now = {}
output = pd.DataFrame(output)
output.to_csv("output_with_incumbency.csv")

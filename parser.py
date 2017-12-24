from bs4 import BeautifulSoup
import re
import warnings
import csv
import string
soup = BeautifulSoup(open("1-150.html"), "lxml")
for e in soup.findAll('br'): # removing pesky linebreaks
    e.extract()


congress_re = re.compile("([0-9]+)(th|st|rd|nd)\s+Congress")
state_regex = re.compile("'?([A-z\s]+)\((.+)\)")
trial_regex = re.compile("([0-9]+)[a-z]+Trial\((.+),(1[7-9][0-9][0-9])\)")
district_regex = re.compile("([A-z|0-9\s—-]+)(\s+\(([A-z|\s]+)\))?")

only_numbers = re.compile("[0-9]+")

party_i_regex = re.compile("\(([A-z\-\s,/]+)\)")


candidate_completeness_regex_1 = re.compile("[0-9\"']?\"?\*")
candidate_completeness_regex_2 = re.compile("[0-9\"']?(\*)?[A-z]+")
candidate_completeness_regex_3 = re.compile("[0-9\"']?(\*)?([A-z\s.]+)\s*\(([A-z\-\s,/]+)\)")
candidate_completeness_regex_4 = re.compile("[0-9\"']?(\*)?([A-z\s.]+)(\s*\(([A-z\-\s,/]+)\))?\s+[\(\[]?([0-9,]+)[\)\]]?")
candidate_completeness_regex_5 = re.compile(
    "[0-9\"']?(\*)?([A-z\s.]+)(\s+\(([A-z\-\s,/]+)\))?\s+\(?([0-9,]+)\)?\s+[\(\[]([0-9.]+)[\)|\]]")

letters = re.compile("[A-z]")

candidate_completeness_regex_2_everything = re.compile("(\*)?([A-z|\s|.]+)")

punc_translator = str.maketrans('', '', string.punctuation)
space_translator = str.maketrans('', '', string.whitespace)

word_to_num = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20
}

states = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
    "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia",
    "Washington", "WestVirginia", "Wisconsin", "Wyoming"
}


writer = csv.DictWriter(open("output.csv", "w"), ["congress", "type", "year", "election_dates", "state", "district",
                                                  "runoff", "trial", "num_elected", "name", "party", "votes",
                                                  "percentage", "result"])
writer.writeheader()

def is_valid_span(span):
    if span.name == "span":
        valid = True
        for tag in span.find_all():
            if tag.name != "b" and tag.name != "i" and tag.name != "img":
                valid = False
                break
        return valid
    return False


def is_congress(span):
    try:
        return span.parent.parent["size"] == "6"
    except KeyError:
        try:
            return span.parent["size"] == "6"
        except KeyError:
            return False


def is_subheader(span):
    try:
        return span.parent.parent["size"] == "5"
    except KeyError:
        try:
            return span.parent["size"] == "5"
        except KeyError:
            return False


def is_year(span):
    try:
        return span.parent.parent["size"] == "3" or span.parent.parent["size"] == "4"
    except KeyError:
        try:
            return span.parent["size"] == "3" or span.parent["size"] == "4"
        except KeyError:
            return False


def does_not_have_i_children(span):
    for tag in span.find_all():
        if tag.name == "i":
            if not party_i_regex.match(tag.text.strip()):
                return False
            else:
                print("Detected: ", tag.text)
    return True


def contains_state_name(span):
    text = get_state_text(span)
    for state in states:
        if state in text:
            return True
    return False

def get_state_text(span):
    info = " ".join(span.text.split()).strip(" ")
    return info

def is_state(span):
    try:
        parent = span.parent.parent
        size = parent["size"]
    except KeyError:
        try:
            parent = span.parent
            size = parent["size"]
        except KeyError:
            return False
    if size == "2":
        return does_not_have_i_children(span) and contains_state_name(span)
    elif size == "1":
        try:
            style = parent["style"]
        except KeyError:
            return False
        if style == "font-size: 8pt" or style== "font-size: 9pt":
            return does_not_have_i_children(span) and contains_state_name(span)
        else:
            return False
    else:
        return False


def is_trial(span):
    try:
        parent = span.parent.parent
        size = parent["size"]
    except KeyError:
        try:
            parent = span.parent
            size = parent["size"]
        except KeyError:
            return False
    if size == "2":
        return does_not_have_i_children(span) and "Trial" in span.text
    elif size == "1":
        try:
            style = parent["style"]
        except KeyError:
            return False
        if style == "font-size: 8pt":
            return does_not_have_i_children(span) and "Trial" in span.text
        else:
            return False
    else:
        return False


def is_district(span):
    for tag in span.find_all():
        if tag.name == "i":
            return True
    return False


def parse_congress(congress_span):
    try:
        name = congress_span.find("b").text
        result = congress_re.search(name)
        if result:
            return result.group(1)
        else:
            warnings.warn("Congress not successfully parsed." + "\n" + name)
    except AttributeError:
        warnings.warn("Congress not successfully parsed." + "\n" + str(congress_span))


def parse_out_congress(soup):
    all_spans = soup.find_all(is_valid_span)
    index = -1
    current_congress = ""
    for i, span in enumerate(all_spans):
        if is_congress(span):
            result = parse_congress(span)
            if result:
                if index != -1:
                    parse_subheadings(all_spans[index + 1:i], {"congress": current_congress})
                current_congress = result
                index = i
    parse_subheadings(all_spans[index:], {"congress": current_congress})


def parse_subheadings(congress, data_so_far):
    current_heading = "StandardElections"
    index = -1
    for i, span in enumerate(congress):
        if is_subheader(span):
            subheader = parse_out_subheadings(span)
            if subheader:
                new_data = {**data_so_far, **{"type": current_heading}}
                if current_heading == "StandardElections":
                    parse_ordinary_years(congress[index + 1:i], {**new_data, **{"trial": 1}})
                if current_heading == "RunoffElections":
                    parse_runoff_states(congress[index + 1:i], new_data)
                index = i
                current_heading = subheader
                # do some parsing
            else:
                continue
    if current_heading == "StandardElections":
        parse_ordinary_years(congress[index + 1:], {**data_so_far, **{"type": current_heading, "trial": 1}})
    if current_heading == "RunoffElections":
        parse_runoff_states(congress[index + 1:], {**data_so_far, **{"type": current_heading}})


def parse_out_subheadings(subheading):
    name = subheading.find("b").text
    name = "".join(name.split())
    if name in ["RunoffElections", "SpecialElections", "StatisticalSummary", "IncompleteReturns",
                "ElectionsinRestoredAreas", "RejectedandUndeterminedElections"]:
        return name
    else:
        warnings.warn("Subheader not successfully parsed." + "\n" + name)


def parse_ordinary_years(all_ordinary, data_so_far):
    index = -1
    current_year = -1
    for i, span in enumerate(all_ordinary):
        if is_year(span):
            if index != -1:
                new_data = {**data_so_far, **{"year": current_year}}
                parse_ordinary_states(all_ordinary[index+1: i], new_data)
            index = i
            current_year = parse_out_ordinary_years(span)
    parse_ordinary_states(all_ordinary[index:], {**data_so_far, **{"year": current_year}})


def parse_out_ordinary_years(span):
    if letters.match(span.text):
        warnings.warn("Year contains letters \n" + str(span.parent.parent))
    return "".join(span.text.split())


def parse_runoff_states(all_runoff, data_so_far):
    index = -1
    current_state_info = {"state": ""}
    i = 0
    while i < len(all_runoff):
        span = all_runoff[i]
        if is_state(span):
            name = get_state_text(span)
            if index != -1:
                new_data = {**data_so_far, **current_state_info}
                parse_runoff_trials(all_runoff[index + 1: i], new_data)
            index = i
            current_state_info = {"state": name}
        i += 1
    parse_runoff_trials(all_runoff[index + 1: i], {**current_state_info, **data_so_far})


def parse_runoff_trials(runoff_state, data_so_far):
    index = -1
    current_trial_info = {"trial": 2, "election_dates": ""}
    i = 0
    while i < len(runoff_state):
        span = runoff_state[i]
        if is_trial(span):
            temp_name = get_flat_text(span)
            original_i = i
            valid = True
            while not trial_regex.match(temp_name):
                try:
                    temp_name += get_flat_text(runoff_state[i + 1])
                    i += 1
                except IndexError:
                    i = original_i
                    warnings.warn("Trial not parsed." + "\n" + temp_name + str(data_so_far))
                    valid = False
                    break
            if valid:
                if index != -1:
                    new_data = {**data_so_far, **current_trial_info}
                    parse_ordinary_districts(runoff_state[index + 1: original_i], new_data)
                index = i
                current_trial_info = parse_out_trial(temp_name)
        i += 1
    parse_ordinary_districts(runoff_state[index + 1:], {**data_so_far, **current_trial_info})


def parse_ordinary_states(ordinary_year, data_so_far):
    index = -1
    current_state_info = {"state": "", "election_dates": ""}

    i = 0
    while i < len(ordinary_year):
        span = ordinary_year[i]
        if is_state(span):
            temp_name = get_state_text(span)
            original_i = i
            valid = True
            while not state_regex.match(temp_name):
                try:
                    temp_name += get_state_text(ordinary_year[i + 1])
                    i += 1
                except IndexError:
                    i = original_i
                    warnings.warn("State not parsed." + "\n" + temp_name + str(data_so_far))
                    valid = False
                    break
            if valid:
                if index != -1:
                    new_data = {**data_so_far, **current_state_info}
                    parse_ordinary_districts(ordinary_year[index + 1: original_i], new_data)
                index = i
                current_state_info = parse_out_state(temp_name)
        i += 1
    parse_ordinary_districts(ordinary_year[index + 1:], {**data_so_far, **current_state_info})


def get_flat_text(span):
    info = "".join(span.text.split())
    return info


def parse_out_state(info):
    search = state_regex.search(info)
    state_name = search.group(1)
    dates = search.group(2)
    return {"state": state_name.strip(" "), "election_dates": dates}


def parse_out_trial(info):
    search = trial_regex.search(info)
    trial_name = search.group(1)
    dates = search.group(2)
    year = search.group(3)
    return {"trial": trial_name, "election_dates": dates, "year": int(year)}


def parse_ordinary_districts(state, data_so_far):
    index = -1
    current_district = {"district": "", "num_elected": 0}
    i = 0
    while i < len(state):
        span = state[i]
        if is_district(span):
            original_i = i
            district_so_far = span.find("i").text
            if "District" not in district_so_far and "At-Large" not in district_so_far and \
                            len(district_so_far) > 1 and not only_numbers.match(district_so_far):
                try:
                    district_so_far += " " + state[i+1].find("i").text
                    i += 1
                except AttributeError:
                    pass
                except IndexError:
                    pass
            if not letters.search(district_so_far):
                warnings.warn("Started to find a district, but did not complete \n" + district_so_far + str(data_so_far))
                i = original_i + 1
                continue
            valid = True
            while " ".join(district_so_far.split())[-1] == "-" and letters.search(district_so_far):
                try:
                    district_so_far += " " + state[i+1].find("i").text
                    i += 1
                except AttributeError:
                    warnings.warn("Started to find a district, but did not complete \n" + district_so_far + str(data_so_far))
                    i = original_i + 1
                    valid = False
                    break
            if not valid:
                continue
            if "(" in district_so_far and ")" not in district_so_far:
                try:
                    district_so_far += " " + state[i+1].find("i").text
                    i += 1
                except AttributeError:
                    warnings.warn("Started to find a district, but did not complete \n" + district_so_far + str(data_so_far))
                    i = original_i + 1
                    continue
            if index != -1:
                new_data = {**data_so_far, **current_district}
                parse_candidates(state[index + 1: original_i], new_data)
            index = i
            result = parse_out_district(district_so_far)
            if result:
                current_district = result
        i += 1
    if current_district["district"] == "":
        current_district = {"district": "Single", "num_elected": 1}
    parse_candidates(state[index+1:], {**data_so_far, **current_district})


def parse_out_district(district_info):
    result = district_regex.search(district_info)
    if result:
        district = "".join(result.group(1).split()).translate(punc_translator).translate(space_translator).replace("—", "")
        if district in ["Majorityvoterequired", "ofanotherparty", "Replacedmemberofanotherparty", "unop",
                        "unopposeddataincomplete"]:
            return None
        num_elected = 1
        if "(" in district_info and ("elected" in district_info or "members" in district_info):
            num_elected = word_to_number(district_info.split("(")[-1].strip(")").split()[0])
        return {"district": district, "num_elected": num_elected}
    else:
        warnings.warn("District not parsed" + "\n" + district_info )

def word_to_number(string):
    try:
        return int(string)
    except ValueError:
        return word_to_num[string]

def parse_candidates(district, data_so_far):
    i = 0
    text_list = []
    while i < len(district):

        span = district[i]
        text = span.text
        score = candidate_completeness_score(text)
        if score == 5:
            parse_candidate(text)
        elif score > 0:
            j = 1
            if i + j < len(district):
                new_text = text + " " + district[i+j].text
                new_score = candidate_completeness_score(new_text)
                if new_score == 5:
                    score = new_score
                    text = new_text
                    j += 1
                else:
                    while score < new_score:
                        if i+j >= len(district) - 1:
                            score = new_score
                            text = new_text
                            j += 1
                            break
                        j += 1
                        score = new_score
                        text = new_text
                        new_text = text + " " + district[i+j].text
                        new_score = candidate_completeness_score(new_text)
                        if new_score == 5:
                            score = new_score
                            text = new_text
                            j += 1
                            break
            i = i + j - 1
        if score == 1:
            warnings.warn("Only found the star.")
        if score == 2:
            if "Congress" not in text:
                warnings.warn("Please investigate.\n" + text + str(data_so_far))
                text_list.append(text)
        elif score != 0:
            create_candidate_list_from_string(text, text_list, score)
        # else:
        #     print(text)
        i += 1
    runoff = False
    final_candidate_list = []
    for candidate in text_list:
        result = parse_candidate(candidate)
        if result:
            if result["runoff"]:
                runoff = True
            final_candidate_list.append(result)
    final_candidate_list = sorted(final_candidate_list, key=candidate_sort, reverse=True)
    for i, candidate in enumerate(final_candidate_list):
        if i < data_so_far["num_elected"] and not candidate["runoff"]:
            candidate["result"] = "won"
        elif runoff:
            candidate["result"] = "runoff"
        else:
            candidate["result"] = "lost"
        candidate["runoff"] = runoff
        final_writing = {**candidate, **data_so_far}
        writer.writerow(final_writing)



def candidate_sort(x):
    try:
        return int(x["votes"])
    except TypeError:
        return 0


def create_candidate_list_from_string(text, text_list, score):
    if score == 3:
        regex = candidate_completeness_regex_3
    elif score == 4:
        regex = candidate_completeness_regex_4
    elif score == 5:
        regex = candidate_completeness_regex_5
    pos = 0
    while pos < len(text):
        match = regex.search(text, pos)
        if match:
            new_pos = match.end()
            if new_pos == pos:
                break
            text_list.append(text[pos:new_pos])
            pos = new_pos
        else:
            break


def candidate_completeness_score(string):
    if candidate_completeness_regex_5.search(string):
        return 5
    if candidate_completeness_regex_4.search(string):
        return 4
    if candidate_completeness_regex_3.search(string):
        return 3
    if candidate_completeness_regex_2.search(string):
        return 2
    if candidate_completeness_regex_1.search(string):
        return 1
    return 0


def parse_candidate(string):
    match = candidate_completeness_regex_5.match(string)
    if match:
        if match.group(4):
            party = "".join(match.group(4).split()).split(",")[0].split("/")[0]
        else:
            party = None
        return {
            "name": " ".join(match.group(2).split()),
            "party": party,
            "votes": int(" ".join(match.group(5).split()).replace(",", "")),
            "percentage": float(" ".join(match.group(6).split())),
            "runoff": bool(match.group(1))
        }
    match = candidate_completeness_regex_4.match(string)
    if match:
        if match.group(4):
            party = "".join(match.group(4).split()).split(",")[0].split("/")[0]
        else:
            party = None
        return {
            "name": " ".join(match.group(2).split()),
            "party": party,
            "votes": int(" ".join(match.group(5).split()).replace(",", "")),
            "runoff": bool(match.group(1)),
            "percentage": None
        }
    match = candidate_completeness_regex_3.match(string)
    if match:
        return {
            "name": " ".join(match.group(2).split()),
            "party": match.group(3).split(",")[0].split("/")[0],
            "votes": None,
            "runoff": bool(match.group(1)),
            "percentage": None
        }
    match = candidate_completeness_regex_2_everything.match(string)
    if match:
        return {
            "name": " ".join(match.group(2).split()),
            "party": None,
            "votes": None,
            "runoff": bool(match.group(1)),
            "percentage": None
        }

print(parse_out_congress(soup))
# Early American Electoral Data Projects

**Thomas Woodside**

This repository contains analysis of electoral results from 1788-1860.
It is divided into two main analyses: one of gerrymandering, and the
other of the shift from at-large to single-member districts.

Parsing and data wrangling is done in Python, heavily utilizing
the Beautiful Soup library. Analysis is mostly done in R.

## About the data
The data was digitized from _United States Congressional Elections, 1788-1997: The Official Results_ by Michael J. Dubin (McFarland & Company).
The book was scanned and then converted to text through onlineocr.net.
I then wrote code contained in [parser.py](parser.py) to convert the HTML
output to csv.

Substantial effort was put in to ensure that the data from the book was digitized as accurately as possible; however, it is likely that there remain some errors from the OCR used to recognize the text or the program used to convert the text to csv.

The data contains at least partial data for 6,619 elections.

The data contains:

1. The number of votes received by each candidate in regular congressional elections held for the 1st to the 39th congresses.

2. The results of any runoff elections, if applicable.

The data does not contain the results of special elections, as their formatting in the book was simply not regular enough to be parsed programmatically and would probably need to be done by hand.

## Gerrymandering

An analysis of gerrymandering was the original motivation to digitize
the data, and is contained in this repository. Please consult
[gerrymandering.pdf](gerrymandering.pdf) to see the analysis.

## Single-Member District Mandate

The Apportionment Act of 1842 mandated single-member districts for
the U.S. House. See [multi_member_districts.pdf](multi_member_districts.pdf)
for possible reasons the mandate was passed.

## Auxiliary Files

- [example.html](example.html) is an example of the HTML generated from onlineocr.net.
- [filtered.csv](filtered.csv) contains an extract of the results for each
state for each election. You can see how it was generated in [gerrymandering.Rmd](gerrymandering.pdf)
- [incumbency_analysis.py](incumbency_analysis.py) takes the output from [parser.py](parser.py)
and attempts to create new rows determining the incumbency of candidates.
- [output_with_incumbency.csv](output_with_incumbency.csv) contains the raw data obtained
from parsing the book. It is not complete, as the book itself had many elections with missing data.
- [parse_out_votes.py](parse_out_votes.py) parses the voting record from [vote_record.html](vote_record.html)
into csv.
- [parser.py](parser.py) does the majority of the parsing work, parsing HTML
like that found in [example.html](example.html) into csv.
- [problem_table.html](problem_table.html) contains an example of a
scan that was improperly converted to HTML. It can be reformatted in
[flatten_table.html](flatten_table.html).
- [state_area.csv](state_area.csv) contains the current areas of the
50 states. It is not, of course, completely accurate for early American
history, particularly in Massachusetts and Virginia.
- [vote_record.csv](vote_record.csv) contains the voting record of all
representatives who voted on the single-member districting mandate amendment
in 1842.
- [vote_record.html](vote_record.html) contains the raw voting records, from
the Library of Congress.

## Sources

#### Electoral Data

Dubin, Michael J. _United States Congressional Elections, 1788-1997: The Official Results of the Elections of the 1st
through 105th Congresses_. Jefferson, North Carolina: McFarland & Company, 1998.

#### Vote Record Data

_House Journal_. 27th Cong., 2nd sess., 3 May 1842, 779.

#### Hypotheses for Motivations For Single-Member District Mandate
Calabrese, Stephen. “An Explanation of the Continuing Federal Government Mandate of Single-Member Congressional Districts.” _Public Choice_ 130, no. 1/2 (January 2007): 
23-40. JSTOR

Crain, W. Mark. "On the Structure and Stability of Political Markets." _Journal of Political Economy_ 85, no. 4
(Aug., 1977): 829-842. JSTOR.

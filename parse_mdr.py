import re

import matplotlib.pyplot as plt
import pandas as pd
import tqdm


def extract_titles(fulltext):
    # a title is always incapsulated in p class="stitle-article-norm">
    # use a regex pattern to extract the title
    titles_pattern = r'<p class="stitle-article-norm">(.*?)</p>'
    titles = re.findall(titles_pattern, fulltext)

    # find arcticles <p class="title-article-norm"
    articles_pattern = r'<p class="title-article-norm"(.*?)</p>'
    articles = re.findall(articles_pattern, fulltext)
    # articles now have this form
    '''
    <p class="title-article-norm" id="id-2270b606-94a1-46ff-a2db-4ecc391cdac5">Article&nbsp;17</p>
    '''
    # extract the integer after >
    articles_numbers = []
    for article in articles:
        article_number = article.split(">")[1].split("<")[0]
        # remove non numerical characters
        article_number = re.sub(r'[^\d]', '', article_number)
        # conert to integer
        article_number = int(article_number)
        articles_numbers.append(article_number)

    # find line numbers for all titles
    line_numbers = []
    for i, line in enumerate(fulltext.split("\n")):
        if "<p class=\"stitle-article-norm\">" in line:
            line_numbers.append(i)

    return titles, articles_numbers, line_numbers


def clean_text(text):
    # if text contains title of another section, remove it
    # because the corresponding title always comes
    # before the start of the text
    if "<p class=\"title-article-norm" in text:
        text_cut = text.split('<p class="title-article-norm')[1]
        text = text_cut

    # remove all tags
    text = re.sub(r'<[^>]+>', '', text)

    # replace &nbsp; with space
    text = re.sub(r'&nbsp;', ' ', text)

    # remove duplice spaces
    text = re.sub(r'\s+', ' ', text)
    # remove duplicate empty lines
    text = re.sub(r'\n\n+', '\n', text)
    return text


def match_entries(
        split_texts, text_line_numbers,
        titles, articles_numbers, title_line_numbers):
    """This function finds the corresponding
    title for each text and creates a dataframe."""

    segments = []
    for j, text in tqdm.tqdm(enumerate(split_texts)):
        # find the larest title_line_number that is
        # smaller than the text_line_number
        text_line_number = text_line_numbers[j]
        title_line_number = max(
            [i for i in title_line_numbers if i < text_line_number])

        i = title_line_numbers.index(title_line_number)

        text = clean_text(text)

        # create a dictionary
        segment = {
            "title": titles[i],
            "article_number": articles_numbers[i],
            "line_number": text_line_numbers[j],
            "text": text
        }
        segments.append(segment)
    # convert to dataframe
    segments = pd.DataFrame(segments)
    return segments


def build_df():
    filepath = "data/mdr.html"

    # strategy:
    # add line numbers from original files into the fulltext
    # split by norm.
    # for the split texts remove all tags
    # save split texts json

    # read in file
    with open(filepath, "r") as f:
        fulltext = f.read()
    # get line numbers from original file

    text_line_numbers = []
    # iterate through every line in fulltext,
    # if the line contains "<p class=\"norm\">" insert the line number
    for i, line in enumerate(fulltext.split("\n")):
        if "<p class=\"norm\">" in line:
            text_line_numbers.append(i)
    # split by '<p class="norm">'
    split_texts = fulltext.split("<p class=\"norm\">")

    # remove the first and last element
    split_texts = split_texts[1:-1]

    # extract all titles
    titles, articles_numbers, title_line_numbers = extract_titles(fulltext)

    segments = match_entries(
        split_texts, text_line_numbers,
        titles, articles_numbers, title_line_numbers)

    # for some reason article 123 contains garbabe (=texts with avg len of 3)
    # so we drop that.
    segments = segments[segments.article_number != 123]

    # # plot histogram of lenghts
    # segments.text.str.len().hist(bins=100)
    # plt.show()
    return segments


def df_to_jsonL(df):
    """Saves df to jsonl format for pyserini
    format looks as follows
    {"id": "doc1", "contents": "contents of doc one."}
    {"id": "doc2", "contents": "contents of document two."}
    """
    outpath = "data/jsonl/mdr.jsonl"
# "id": "article{row.article_number}_line{row.line_number}",\

    with open(outpath, "w") as f:
        for i, row in df.iterrows():
            f.write(f'{{\
"id": {row.line_number}",\
"contents": "{row.text}",\
"title": "{row.title}",\
"article_number": "{row.article_number}",\
"line_number": "{row.line_number}"\
}}\n')
    print(f"Saved to {outpath}")


df = build_df()
df_to_jsonL(df)

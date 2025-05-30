# -*- coding: utf-8 -*-
"""3_text-classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1q4k51fRAVC8OgWDdR4WnbZzMHk-40hmv
"""

import pandas as pd

books = pd.read_csv("/content/books_cleaned (1).csv")
books

books["categories"].value_counts().reset_index()

books[books["categories"] == "Juvenile Fiction"]

books["categories"].value_counts().reset_index().query("count > 50")

books[books["categories"] == "Juvenile Fiction"]

"""**we can observe that The categories fiction and non fiction are available in large numbers so these are of more use to us

Lets create some categories in which fiction and non fiction categories are dominant

**
"""

category_mapping = {
    "Fiction": "Fiction",
    "Juvenile Fiction": "Children's Fiction",
    "Biography & Autobiography": "Nonfiction",
    "History": "Nonfiction",
    "Literary Criticism": "Nonfiction",
    "Philosophy": "Nonfiction",
    "Religion Comics & Graphic Novels": "Nonfiction",
    "Drama": "Fiction",
    "Juvenile Nonfiction": "Children's Nonfiction",
    "Science": "Nonfiction",
    "Poetry": "Fiction"
}
books["simple_categories"] = books["categories"].map(category_mapping)
books.head()

books[~(books["simple_categories"].isna())]

#!pip uninstall transformers
!pip install transformers

from transformers import pipeline

fiction_categories = ["Fiction", "Nonfiction"]

pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)

sequence = books.loc[books["simple_categories"] == "Fiction","description"].reset_index(drop = True)[0]

pipe(sequence, fiction_categories)

"""# The above output represent the probability of a particular text belonging to these categories.

# Now lets find the index of the maximum probability of the category in accordance with the text that we have provided



"""

import numpy as np
max_index = np.argmax(pipe(sequence, fiction_categories)["scores"])
max_label = pipe(sequence, fiction_categories)["labels"][max_index]
max_label

def generate_predictions(sequence,categories):
  predictions = pipe(sequence, categories)
  max_index = np.argmax(predictions["scores"])
  max_label = predictions["labels"][max_index]
  return max_label

from tqdm import tqdm
actual_cats = []
predicted_cats = []

for i in tqdm(range(0,100)):#you can increase the iteration according to the system specification.
  sequence = books.loc[books["simple_categories"] == "Fiction","description"].reset_index(drop = True)[i]
  predicted_cats += [generate_predictions(sequence,fiction_categories)]
  actual_cats += ["Fiction"]

for i in tqdm(range(0,100)):
  sequence = books.loc[books["simple_categories"] == "Nonfiction","description"].reset_index(drop = True)[i]
  predicted_cats += [generate_predictions(sequence,fiction_categories)]
  actual_cats += ["Nonfiction"]

predictions_df = pd.DataFrame({"actual_categories":actual_cats,"predicted_categories":predicted_cats})
predictions_df

predictions_df["correct_prediction"] = (np.where(predictions_df["actual_categories"] == predictions_df["predicted_categories"],1,0))

predictions_df["correct_prediction"].sum() / len(predictions_df)

isbns = []
predicted_cats = []
missing_cats = books.loc[books["simple_categories"].isna(), ["isbn13","description"]].reset_index(drop = True)
for i in tqdm(range(0, 100)):
  sequence = missing_cats.loc[i,"description"]
  predicted_cats += [generate_predictions(sequence,fiction_categories)]
  isbns += [missing_cats["isbn13"][i]]

missing_predicted_df = pd.DataFrame({"isbn":isbns,"predicted_categories":predicted_cats})
missing_predicted_df

#merging to original dataframe
books = pd.merge(books, missing_predicted_df, left_on = "isbn13", right_on = "isbn", how = "left")
books["simple_categories"] = np.where(books["simple_categories"].isna(), books["predicted_categories"], books["simple_categories"])

books = books.drop(columns =["predicted_categories"])

books

books[books["categories"].str.lower().isin([
    # "romance",
    "science fiction",
    "scifi",
    "mystery",
    "horror",
    "thriller",
    "comedy",
    "crime",
    "historical"

])]

books.to_csv("books_with_categories.csv",index = False)
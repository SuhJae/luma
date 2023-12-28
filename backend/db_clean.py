from db import LumaDB
import re

db = LumaDB()
articles = db.palace_db.find(limit=0)


def clean_up_text(text: str) -> str:
    # remove all HTML (there may be a space in a tag)
    text = re.sub('<[^>]*>', '', text, 0).strip()
    # remove all "Wrongly applied line breaks"
    text = text.replace("\\n", "")
    # remove all 2 or more consecutive spaces
    text = re.sub(' {2,}', ' ', text)
    # remove space before and after the linebreak
    text = text.replace(" \n", "\n")
    text = text.replace("\n ", "\n")
    return text


for article in articles:
    # for all value in explanation dict, apply the following logic
    for key, value in article["explanation"].items():
        article["explanation"][key] = clean_up_text(value)
        # Update the document in MongoDB
        db.palace_db.update_one({"_id": article["_id"]}, {"$set": {"explanation": article["explanation"]}})

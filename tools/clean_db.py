from app.db import LumaDB
import re


def clean_up_text(text: str) -> str:
    # Combining multiple re.sub and replace operations into fewer steps

    # Remove all HTML tags and extra spaces
    text = re.sub('<[^>]*>', '', text).strip()

    # Replace specific HTML character entities with their respective characters
    # and unify quotation marks into ASCII, using a dictionary for mapping
    html_entity_dict = {
        "\\n": "", "&nbsp;": " ", "&lt;": "<", "&gt;": ">", "&amp;": "&",
        "&quot;": "\"", "&apos;": "'", "&euro;": "€", "&pound;": "£",
        "&yen;": "¥", "&cent;": "¢", "&reg;": "®", "&trade;": "™",
        "“": "\"", "”": "\"", "‘": "'", "’": "'"
    }
    for target, replacement in html_entity_dict.items():
        text = text.replace(target, replacement)

    # Remove multiple consecutive spaces and handle space around line breaks
    text = re.sub(' {2,}', ' ', text)
    text = text.replace(" \n", "\n").replace("\n ", "\n")

    # Add space after period or comma if not present
    text = re.sub(r'(?<=[.,])(?=\S)', r' ', text)

    return text


db = LumaDB()

# For each article in the database
articles = db.palace_db.find(limit=0)
for article in articles:
    # for all value in explanation dict, apply the following logic
    for key, value in article["explanation"].items():
        article["explanation"][key] = clean_up_text(value)
        # Update the document in MongoDB
        db.palace_db.update_one({"_id": article["_id"]}, {"$set": {"explanation": article["explanation"]}})

    print(f"Updated article {article['name']['ko']} ({article['_id']})")

# For each media meta data in the database
medias = db.media_meta_db.find(limit=0)
for media in medias:
    if "explanation" not in media:
        continue

    for key, value in media["explanation"].items():
        if value is None:
            continue
        media["explanation"][key] = clean_up_text(value)
        # Update the document in MongoDB
        db.media_meta_db.update_one({"_id": media["_id"]}, {"$set": {"explanation": media["explanation"]}})

    print(f"Updated media {media['name']['ko']} ({media['_id']})")

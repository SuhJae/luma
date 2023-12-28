from elasticsearch import Elasticsearch
from db import LumaDB
from bson.objectid import ObjectId
import re


class ElasticsearchClient:
    def __init__(self, es_client: Elasticsearch = Elasticsearch("http://localhost:9200"),
                 lumaBD: LumaDB = LumaDB()) -> None:
        self.serviced_language = ["ko", "en", "ja", "zh"]
        self.es = es_client
        self.mongo_client = lumaBD
        self.es.ping()

    def setup_index(self) -> None:
        # reset the index
        for language in self.serviced_language:
            index_name = f'articles_{language}'
            if self.es.indices.exists(index=index_name):
                self.es.indices.delete(index=index_name)

        # Define the analyzer name based on the language
        analyzer_mapping = {
            "ko": "korean",
            "en": "english",
            "ja": "japanese",
            "zh": "chinese",
        }

        for language in self.serviced_language:
            analyzer_name = analyzer_mapping[language]

            # Define the index mapping
            settings = {
                "settings": {
                    "index": {
                        "analysis": {
                            "analyzer": {
                                "korean": {
                                    "type": "custom",
                                    "tokenizer": "nori_tokenizer",
                                    "filter": ["nori_readingform"]
                                },
                                "english": {
                                    "type": "standard"
                                },
                                "japanese": {
                                    "type": "custom",
                                    "tokenizer": "kuromoji_tokenizer",
                                    "filter": [
                                        "kuromoji_baseform",
                                        "kuromoji_part_of_speech",
                                        "cjk_width",
                                        "ja_stop"
                                    ]
                                },
                                "chinese": {
                                    "type": "custom",
                                    "tokenizer": "smartcn_tokenizer",
                                    "filter": ["cjk_width", "stop"]
                                },
                            },
                            "tokenizer": {
                                "nori_tokenizer": {
                                    "type": "nori_tokenizer",
                                    "decompound_mode": "mixed",
                                },
                                "kuromoji_tokenizer": {
                                    "type": "kuromoji_tokenizer"
                                },
                            },
                            "filter": {
                                "ja_stop": {
                                    "type": "stop",
                                    "stopwords": "_japanese_"
                                }
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": analyzer_name
                        },
                        "text": {
                            "type": "text",
                            "analyzer": analyzer_name
                        },
                        "suggest": {
                            "type": "completion",
                            "analyzer": analyzer_name,
                            "search_analyzer": analyzer_name,
                            "preserve_separators": True,
                            "preserve_position_increments": True,
                            "max_input_length": 50
                        }
                    }
                }
            }
            index_name = f'articles_{language}'
            self.es.indices.create(index=index_name, body=settings)

    def index(self, title: str, body: str, palace_id: int, language: str, mongo_id) -> None:
        # Prepare the entry for Elasticsearch

        es_entry = {
            "tag": palace_id,
            "o_id": str(mongo_id),
            "title": title,
            "text": body,
            "suggest": {
                "input": title,
                "weight": 10
            },
        }
        index_name = f'articles_{language}'
        # Insert the article into Elasticsearch
        self.es.index(index=index_name, body=es_entry, id=mongo_id)

    def index_article(self, article_id: ObjectId) -> None:
        # get the document from MongoDB
        document = self.mongo_client.palace_db.find_one({"_id": article_id})
        palace_code = document["serial_number"]
        if not document:
            return

        for language in self.serviced_language:
            index_title = document["name"][language]
            index_body = document["explanation"][language]

            for image in document["detail_image"]:
                image_detail = self.mongo_client.media_meta_db.find_one({"_id": image})
                # check  image_detail["name"][language] is not None
                if image_detail["name"][language] and image_detail["explanation"][language]:
                    index_body += "\n" + image_detail["name"][language] + "\n" + image_detail["explanation"][language]
            # Using Ragex to remove HTML tags
            index_body = re.sub('<[^>]*>', '', index_body, 0).strip()
            # index the article
            self.index(index_title, index_body, palace_code, language, article_id)

    def index_all_articles(self) -> None:
        # get all articles from MongoDB
        articles = self.mongo_client.palace_db.find(limit=0)
        article_count = self.mongo_client.palace_db.count_documents({})

        for i, article in enumerate(articles):
            print(f"Indexing article {i + 1} of {article_count}")
            self.index_article(article["_id"])

    def search_article(self, query: str, language: str, limit: int = 30, cursor: int = 1,
                       palace_id: int = None) -> dict:
        index_name = f'articles_{language}'
        body = {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "text"]
                        }
                    }
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},
            ]
        }
        if cursor > 1:
            body["from"] = (cursor - 1) * limit
        if palace_id:
            body["query"]["bool"]["filter"] = {"term": {"palace_id": palace_id}}

        return self.es.search(index=index_name, body=body, size=limit)

    def autocomplete(self, query: str, language: str) -> dict:
        index_name = f'articles_{language}'
        return self.es.search(index=index_name, body={
            "suggest": {
                "suggestion": {
                    "prefix": query,
                    "completion": {
                        "field": "suggest",
                        "fuzzy": {
                            "fuzziness": "auto"
                        }
                    }
                }
            }
        })


if __name__ == "__main__":
    es = ElasticsearchClient()
    # es.setup_index()
    # es.index_all_articles()

    testing_lang = "en"
    testing_query = input("Search for: ")
    result = es.search_article(query=testing_query, language=testing_lang)

    print(f"Found {result['hits']['total']['value']} results")

    for hit in result['hits']['hits']:
        print(hit['_source']['title'])
        print(f"Score: {hit['_score']}")
        print(hit['_source']['text'][:200] + "...")
        print()

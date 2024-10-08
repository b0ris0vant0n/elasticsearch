from app.logger_service import logger
from elasticsearch import Elasticsearch, NotFoundError, RequestError
from typing import List, Dict, Any, Optional


class ElasticsearchClient:
    def __init__(self, host: str = "http://elasticsearch:9200") -> None:
        self.es = Elasticsearch(host)
        self._check_connection()

    def _check_connection(self) -> None:
        try:
            if self.es.ping():
                logger.info("Успешное подключение к Elasticsearch")
            else:
                logger.error("Не удалось подключиться к Elasticsearch")
        except Exception as e:
            logger.error(f"Ошибка подключения к Elasticsearch: {e}")

    def index_product(self, sku: Any) -> None:
        doc: Dict[str, Any] = {
            "uuid": sku.uuid,
            "title": sku.title,
            "description": sku.description,
            "brand": sku.brand,
            "category_lvl_1": sku.category_lvl_1,
            "category_lvl_2": sku.category_lvl_2,
            "category_lvl_3": sku.category_lvl_3,
            "price": sku.price_after_discounts,
        }
        try:
            self.es.index(index="products", id=sku.uuid, body=doc)
        except RequestError as e:
            logger.error(f"Ошибка при индексации товара с UUID {sku.uuid}: {e}")
        except Exception as e:
            logger.error(f"Неизвестная ошибка при индексации товара с UUID {sku.uuid}: {e}")

    def search_similar_products(self, sku: Any) -> Optional[List[Dict[str, Any]]]:
        query: Dict[str, Any] = {
            "_source": ["uuid", "title", "description", "brand"],
            "query": {
                "bool": {
                    "must": {
                        "match_phrase": {
                            "title": sku.title
                        }
                    },
                    "must_not": {
                        "term": {
                            "uuid": sku.uuid
                        }
                    }
                }
            }
        }
        try:
            response = self.es.search(index="products", body=query)
            similar_products: List[Dict[str, Any]] = [hit['_source'] for hit in response['hits']['hits'][:5]]
            logger.info(f"Найдено {len(similar_products)} похожих товаров для UUID {sku.uuid}")
            return similar_products
        except NotFoundError:
            logger.error(f"Индекс 'products' не найден при поиске похожих товаров для UUID {sku.uuid}")
            return []
        except RequestError as e:
            logger.error(f"Ошибка при поиске похожих товаров для UUID {sku.uuid}: {e}")
            return []

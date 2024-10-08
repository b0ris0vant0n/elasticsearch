from app.service import logger


class ProductProcessor:
    def __init__(self, db_manager, es_manager):
        self.db_manager = db_manager
        self.es_manager = es_manager

    def process_products(self):
        all_skus = self.db_manager.get_all_skus()

        for sku in all_skus:
            self.es_manager.index_product(sku)

        logger.info("Индексировано %d товаров в Elasticsearch", len(all_skus))

        for sku in all_skus:
            similar_products = self.es_manager.search_similar_products(sku)
            sku.similar_sku = [product['uuid'] for product in similar_products]
            self.db_manager.session.commit()

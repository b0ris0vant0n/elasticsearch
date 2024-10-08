import os
from app.logger_service import logger
from app.database import SKU, Session, create_tables
from app.elasticsearch_client import ElasticsearchClient
from app.utils import parse_offer
from app.xml_parser import XMLParser
from app.database_manager import DatabaseManager
from app.product_processor import ProductProcessor
from app.report_generator import ReportGenerator


class Service:
    def __init__(self):
        create_tables()
        self.session = Session()
        self.chunk_size = int(os.getenv('CHUNK_SIZE'))
        self.xml_file = os.getenv('XML_FILE')
        self.category_map = {}
        self.offers = []
        self.total_processed = 0

        self.xml_parser = XMLParser(self.xml_file)
        self.db_manager = DatabaseManager(self.session)
        self.es_manager = ElasticsearchClient()
        self.product_processor = ProductProcessor(self.db_manager, self.es_manager)
        self.report_generator = ReportGenerator(self.db_manager)

    def run(self):
        self.category_map = self.xml_parser.build_category_map()
        logger.info("Загружено %d категорий", len(self.category_map))

        for offer_elem in self.xml_parser.parse_offers():
            product_data = parse_offer(offer_elem, self.category_map)
            sku = SKU(**product_data)
            self.offers.append(sku)
            self.total_processed += 1

            if len(self.offers) >= self.chunk_size:
                self.db_manager.save_offers(self.offers)
                self.offers = []

        if self.offers:
            self.db_manager.save_offers(self.offers)

        self.product_processor.process_products()

        self.report_generator.generate_report()

        self.session.close()
        logger.info("Обновление завершено. Всего обработано товаров: %d", self.total_processed)

from app.database import SKU
from app.logger_service import logger


class DatabaseManager:
    def __init__(self, session):
        self.session = session

    def save_offers(self, offers):
        self.session.add_all(offers)
        self.session.commit()
        logger.info("Сохранено %d товаров в базу данных", len(offers))

    def get_all_skus(self):
        return self.session.query(SKU).all()

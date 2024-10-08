import os
import lxml.etree as ET
from database import SKU, Session, create_tables
from elasticsearch_client import index_product, search_similar_products
from utils import parse_offer
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


create_tables()
session = Session()

xml_file: str = os.getenv('XML_FILE')

CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE'))

category_map: dict = {}


for event, elem in ET.iterparse(xml_file, events=("end",), tag="category"):
    category_id: int = int(elem.get("id"))
    parent_id: int = int(elem.get("parentId")) if elem.get("parentId") else None
    category_map[category_id] = {
        "name": elem.text,
        "parent_id": parent_id
    }
    elem.clear()

logger.info("Загружено %d категорий", len(category_map))

context = ET.iterparse(xml_file, events=("end",), tag="offer")

offers: list = []
total_processed: int = 0

for event, elem in context:
    product_data = parse_offer(elem, category_map)
    sku = SKU(**product_data)
    offers.append(sku)
    total_processed += 1

    if len(offers) >= CHUNK_SIZE:
        session.add_all(offers)
        session.commit()
        logger.info("Сохранено %d товаров в базу данных", len(offers))
        offers = []

    elem.clear()

if offers:
    session.add_all(offers)
    session.commit()
    logger.info("Сохранено оставшихся %d товаров в базу данных", len(offers))

all_skus: list = session.query(SKU).all()

for sku in all_skus:
    index_product(sku)

logger.info("Индексировано %d товаров в Elasticsearch", len(all_skus))

for sku in all_skus:
    similar_products = search_similar_products(sku)
    sku.similar_sku = [product['uuid'] for product in similar_products]
    session.commit()

logger.info("Обновление завершено. Всего обработано товаров: %d", total_processed)

query_result = text("""
    SELECT
        sku.uuid AS original_uuid,
        sku.title AS original_title,
        sku.similar_sku AS similar_uuids
    FROM
        sku
    WHERE
        sku.similar_sku IS NOT NULL AND array_length(sku.similar_sku, 1) > 1
    GROUP BY
        sku.uuid, sku.title
    LIMIT 15;
""")

try:
    result = session.execute(query_result)

    readme_content = "# Примеры UUID и similar_sku после матчинга\n\n"
    readme_content += "| Original UUID | Original Title | Similar UUIDs |\n"
    readme_content += "|---------------|----------------|----------------|\n"

    for row in result:
        similar_uuids = ', '.join([str(uuid) for uuid in row[2]])
        readme_content += f"| {row[0]} | {row[1]} | {similar_uuids} |\n"

    with open('README.md', 'a') as f:
        f.write(readme_content)

    logger.info("Файл README.md успешно обновлен")

except Exception as e:
    logger.error(f"Ошибка при записи в README.md: {e}")

finally:
    session.close()

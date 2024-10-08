from sqlalchemy import text
from app.service import logger


class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def generate_report(self):
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
            result = self.db_manager.session.execute(query_result)
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

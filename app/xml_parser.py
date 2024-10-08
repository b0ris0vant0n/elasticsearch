import lxml.etree as ET


class XMLParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file

    def build_category_map(self):
        category_map = {}
        for event, elem in ET.iterparse(self.xml_file, events=("end",), tag="category"):
            category_id = int(elem.get("id"))
            parent_id = int(elem.get("parentId")) if elem.get("parentId") else None
            category_map[category_id] = {
                "name": elem.text,
                "parent_id": parent_id
            }
            elem.clear()
        return category_map

    def parse_offers(self):
        context = ET.iterparse(self.xml_file, events=("end",), tag="offer")
        for event, elem in context:
            yield elem
            elem.clear()

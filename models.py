class Product:
    @staticmethod
    def from_doc(doc):
        """Helper to format product document from MongoDB"""
        return {
            "id": str(doc["_id"]),
            "name": doc.get("name"),
            "price": doc.get("price"),
            "description": doc.get("description"),
            "image_url": doc.get("image_url")
        }

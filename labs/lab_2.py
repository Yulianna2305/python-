from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


class Report(Document):
    def render(self) -> str:
        return " Report"

class Invoice(Document):
    def render(self) -> str:
        return " Invoice"

class Contract(Document):
    def render(self) -> str:
        return " Contract"

class NullDocument(Document):
    def render(self) -> str:
        return " Unknown type"


class DocumentFactory:
    @staticmethod
    def create(doc_type: str) -> Document:
        doc_type = doc_type.lower()
        mapping = {
            "report": Report,
            "invoice": Invoice,
            "contract": Contract
        }
        return mapping.get(doc_type, NullDocument)()


if __name__ == "__main__":
    for t in ["report", "invoice", "contract", "unknown"]:
        doc = DocumentFactory.create(t) 
        print(doc.render())             























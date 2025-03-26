from dataclasses import dataclass

@dataclass
class UpdateRequest:
    method : str
    type : str   
    list : WebtoonDTO[]


@dataclass
class WebtoonDTO:
    id : long
    title: str
    link: str

    def to_dict(self):
        return {
            'id' : self.id,
            'title': self.title,
            'link': self.link
        }
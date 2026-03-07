from typing import Any, Generic, TypeVar, Type, List, Optional
from sqlmodel import Session, select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get(self, id: Any) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self) -> List[T]:
        return self.session.exec(select(self.model)).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: Any) -> bool:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
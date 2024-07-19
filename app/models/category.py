from app import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        return {"name": self.name, "id": self.id}

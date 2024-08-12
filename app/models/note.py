from datetime import datetime
from app import db

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notes', lazy=True))
    category = db.relationship('Category', backref=db.backref('notes', lazy=True))
    label = db.relationship('Label', secondary = 'note_label',back_populates = 'note')


    def __repr__(self):
        return f'<Note {self.title}>'


    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'label_id': self.label_id,
            'created_at': str(self.created_at)
        }



class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_name = db.Column(db.String(100))
    note = db.relationship('Note', secondary = 'note_label', back_populates = 'label')

    def __repr__(self):
        return f"<Note {self.label_name}>"

#join table
note_label = db.Table(
    'note_label',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'))
    )

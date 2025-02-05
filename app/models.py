from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
from sqlalchemy import select, func
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.orm as so
from sqlalchemy.sql.functions import sum as sql_sum
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    
    water_usages: so.WriteOnlyMapped['WaterUsage'] = so.relationship(
        back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def sum_water_usage(self):
        return sum(usage.amount for usage in self.water_usages)    
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
    
class WaterUsage(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    time_taken: so.Mapped[float] = so.mapped_column(sa.Float(3), index=True)
    usage_type: so.Mapped[str] = so.mapped_column(sa.String(120))
    amount: so.Mapped[float] = so.mapped_column(sa.Float(3), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    user: so.Mapped[User] = so.relationship(back_populates='water_usages')

    def __repr__(self):
        return f'<WaterUsage of {self.usage_type} for {self.time_taken} minutes>'
from sqlalchemy import Column, Integer, String, Date, Numeric
from database import db

# Order table
class Order(db.Model):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    order_date = Column(Date, nullable=False)
    # A: Active, C: Cancelled, D: Done
    order_status = Column(String(1), nullable=False)
    order_value = Column(Numeric(15,2), nullable=False)

    def to_string(self):
        return f"Order number {self.id}, customer: '{self.customer_id}', date: '{self.order_date}', status: '{self.order_status}', TOTAL: ${self.order_value}"

    def __repr__(self):
        return self.to_string()
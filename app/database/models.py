from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Boolean, ForeignKey, JSON, Enum, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import enum

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    subs_id = Column(Integer, ForeignKey('subscription.id'))
    payment_id = Column(Integer, ForeignKey('paymentdetails.id'))
    referal_to = Column(String, ForeignKey('users.id'), nullable=True)
    start_date = Column(Date)
    test_available = Column(Boolean, default=True)

    # Relationships
    subscription = relationship('Subscription', back_populates='user', uselist=False)
    payment = relationship('PaymentDetails', back_populates='user', uselist=False)
    # gifts = relationship('Gift', back_populates='user')
    transactions = relationship('Transactions', back_populates='user')
    # referals = relationship('Referrals', back_populates='user', uselist=False)
    # yookassa_payments = relationship('YookassaPayments', back_populates='user')
    # referred_users = relationship(
    #     'Users',
    #     foreign_keys='Users.referal_to',
    #     backref='referrals'
    # )


class Promocodes(Base):
    __tablename__ = 'promocodes'
    name = Column(String, primary_key=True)
    date_start = Column(Date)
    description = Column(String)
    date_stop = Column(Date)
    discount = Column(Integer, default=0)

    # Relationship to PaymentDetails
    payments = relationship("PaymentDetails", back_populates="promo_code_obj")


class Discounts(Base):
    __tablename__ = 'discounts'
    name = Column(String, primary_key=True)
    discount_default = Column(Integer)
    discount_family = Column(Integer)
    discount_traffic = Column(Integer)
    discount_gift = Column(Integer)
    discount_default_to_family = Column(Integer)
    onetime_discount = Column(Integer)
    date_start = Column(TIMESTAMP)
    date_stop = Column(TIMESTAMP)

    # Relationships to PaymentDetails
    personal_payments = relationship('PaymentDetails', foreign_keys='PaymentDetails.personal_discount_name',
                                     back_populates='personal_discount')
    general_payments = relationship('PaymentDetails', foreign_keys='PaymentDetails.general_discount_name',
                                    back_populates='general_discount')


class PaymentDetails(Base):
    __tablename__ = 'paymentdetails'
    id = Column(Integer, primary_key=True)
    personal_discount_name = Column(String, ForeignKey('discounts.name'))
    general_discount_name = Column(String, ForeignKey('discounts.name'))
    promo_code = Column(String, ForeignKey('promocodes.name'))

    # Relationships
    personal_discount = relationship('Discounts', foreign_keys=[personal_discount_name],
                                     back_populates='personal_payments')
    general_discount = relationship('Discounts', foreign_keys=[general_discount_name], back_populates='general_payments')
    promo_code_obj = relationship('Promocodes', back_populates='payments')
    user = relationship('Users', back_populates='payment', uselist=False)


class SubsDefault(Base):
    __tablename__ = 'subsdefault'
    id = Column(Integer, primary_key=True)
    owner_id = Column(String, ForeignKey('users.id'), nullable=True)

    # Relationship to SubsType
    subs_types = relationship('SubsType', back_populates='default_subscription')


class SubsFamily(Base):
    __tablename__ = 'subsfamily'
    id = Column(Integer, primary_key=True)
    family_data = Column(JSON)

    # Relationship to SubsType
    subs_types = relationship('SubsType', back_populates='family_subscription')


class SubsType(Base):
    __tablename__ = 'substype'
    id = Column(Integer, primary_key=True)
    default_subs = Column(Integer, ForeignKey('subsdefault.id'))
    family_subs = Column(Integer, ForeignKey('subsfamily.id'))

    # Relationships
    default_subscription = relationship('SubsDefault', back_populates='subs_types')
    family_subscription = relationship('SubsFamily', back_populates='subs_types')
    subscription = relationship('Subscription', back_populates='subscription_type')



class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    date_start = Column(Date)
    date_stop = Column(Date)
    type = Column(Integer, ForeignKey('substype.id'))
    is_test = Column(Boolean)

    # Relationships
    subscription_type = relationship('SubsType', back_populates='subscription')
    user = relationship('Users', back_populates='subscription', uselist=False)


class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)
    amount = Column(Float)
    user_id = Column(String, ForeignKey('users.id'))
    create_date = Column(TIMESTAMP)
    pay_date = Column(TIMESTAMP)
    currency = Column(String)
    pay_system = Column(String)
    method = Column(String)
    quantity = Column(Integer)
    purchase_type = Column(String)
    bought_for = Column(String)

    # Relationship to User
    user = relationship('Users', back_populates='transactions')
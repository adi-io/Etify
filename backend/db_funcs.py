from sqlalchemy import Column, BigInteger, DateTime, String, Numeric, text, desc, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import aliased, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists, not_
from sqlalchemy.sql.expression import TextualSelect
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    host=os.getenv('HOST'),
    port=os.getenv('PORT'),
    database=os.getenv('DBNAME')
)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    __table_args__ = {'schema': 'public'}

    id = Column(BigInteger, primary_key=True,
                server_default=text("nextval('events_id_seq'::regclass)"))
    created_at = Column(DateTime(timezone=True), nullable=False,
                        server_default=text("now()"))
    user_id = Column(String, nullable=False)
    event = Column(String, nullable=False)
    user_usdc_wallet_address = Column(String, nullable=False)
    user_dspy_wallet_address = Column(String, nullable=False)
    frontend_hash = Column(UUID(as_uuid=True), nullable=False)

    smart_contract_one_transaction_hash = Column(String)  # Nullable
    smart_contract_two_transaction_hash = Column(String)  # Nullable

    buy_order_alpaca_uuid = Column(UUID(as_uuid=True))
    sell_order_alpaca_uuid = Column(UUID(as_uuid=True))

    order_amount_from_frontend = Column(Numeric())  # Nullable
    usdc_received_from_user = Column(Numeric())  # Nullable
    user_spy_net_buy_order_value = Column(Numeric())  # Nullable
    user_spy_buy_order_fee = Column(Numeric())  # Nullable

    dspy_received_from_user = Column(Numeric())  # Nullable
    user_spy_sell_order_value_usd = Column(Numeric())  # Nullable
    user_spy_sell_net_order_value_usd = Column(Numeric())  # Nullable
    user_spy_sell_order_fee_usd = Column(Numeric())  # Nullable
    redemption_usdc_sent_to_user = Column(Numeric())  # Nullable

    gas_paid_for_sending_usdc = Column(Numeric())  # Nullable
    gas_paid_for_sending_dspy_to_user = Column(Numeric())  # Nullable
    gas_paid_for_sending_dspy_to_smart_contract = Column(Numeric())  # Nullable

    dspy_average_minting_price = Column(Numeric())  # Nullable
    dspy_average_burning_price = Column(Numeric())  # Nullable
    dspy_mint_filled_quantity = Column(Numeric())  # Nullable
    dspy_burning_filled_quantity = Column(Numeric())  # Nullable

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class RegisteredWallet(Base):
    __tablename__ = 'registered_wallets'
    __table_args__ = {'schema': 'public'}

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('registered_wallets_id_seq'::regclass)"))
    usdc_wallet = Column(String)
    dspy_wallet = Column(String)
    user_id = Column(String, nullable=False, unique=True)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def run_db_query(query_func, *args, **kwargs):
    #Function not currently used
    try:
        with engine.connect():
            with Session() as session:
                result = query_func(session, *args, **kwargs)
                return result
    except Exception as e:
        print(f"Failed to connect or run query: {e}")
        return None

def insert_event(**kwargs):
    with Session() as session:
        try:
            new_event = Event(**kwargs)
            session.add(new_event)
            session.commit()
            session.refresh(new_event)
            return new_event.as_dict
        except Exception as e:
            session.rollback()
            print(f"Failed to insert event: {e}")
            return None

def get_qualified_bids():
    with Session() as session:
        e2 = aliased(Event)

        subquery = exists().where(
            (e2.frontend_hash == Event.frontend_hash) &
            ((e2.event == 'SPY_BUY_ORDER_CREATED') |
             (e2.dspy_average_minting_price.isnot(None)))
        )

        events = session.query(Event).filter(
            Event.event == "USDC_RECEIVED",
            not_(subquery)
        ).all()
        events = [e.as_dict for e in events]
        return (events)

def get_qualified_asks():
    with Session() as session:
        e2 = aliased(Event)

        subquery = exists().where(
            (e2.frontend_hash == Event.frontend_hash) &
            ((e2.event == 'SPY_SELL_ORDER_CREATED') |
             (e2.dspy_average_burning_price.isnot(None)))
        )

        events = session.query(Event).filter(
            Event.event == "DSPY_RECEIVED",
            not_(subquery)
        ).all()
        events = [e.as_dict for e in events]
        return (events)

def get_qualified_mints():
    with Session() as session:
        e2 = aliased(Event)

        subquery = exists().where(
            (e2.frontend_hash == Event.frontend_hash) &
            (e2.event == 'DSPY_TOKEN_MINTING_INITIATED')
        )

        events = session.query(Event).filter(
            Event.event == "SPY_ETF_PURCHASED",
            not_(subquery)
        ).all()
        events = [e.as_dict for e in events]
        return (events)

def get_qualified_burns():
    with Session() as session:
        e2 = aliased(Event)

        subquery = exists().where(
            (e2.frontend_hash == Event.frontend_hash) &
            (e2.event == 'DSPY_TOKEN_BURNING_INITIATED')
        )

        events = session.query(Event).filter(
            Event.event == "SPY_ETF_SOLD",
            not_(subquery)
        ).all()
        events = [e.as_dict for e in events]
        return (events)

def get_qualified_redemptions():
    with Session() as session:
        e2 = aliased(Event)

        subquery = exists().where(
            (e2.frontend_hash == Event.frontend_hash) &
            (e2.event == 'REDEMPTION_USDC_TRANSFER_INITIATED')
        )

        events = session.query(Event).filter(
            Event.event == "DSPY_TOKEN_BURNED",
            not_(subquery)
        ).all()
        events = [e.as_dict for e in events]
        return (events)

def find_buy_order(frontend_hash, user_usdc_wallet_address):
    with Session() as session:
        event = session.query(Event).filter(
            Event.event == "BUY_ORDER_CREATED",
            Event.frontend_hash == frontend_hash,
            Event.user_usdc_wallet_address == user_usdc_wallet_address
        ).first()
        event = event.as_dict if event else None
        return (event)

def find_bought_order(frontend_hash, user_dspy_wallet_address):
    with Session() as session:
        event = session.query(Event).filter(
            Event.event == "SPY_ETF_PURCHASED",
            Event.frontend_hash == frontend_hash,
            Event.user_dspy_wallet_address == user_dspy_wallet_address
        ).first()
        event = event.as_dict if event else None
        return (event)

def find_sold_order(frontend_hash):
    with Session() as session:
        event = session.query(Event).filter(
            Event.event == "SPY_ETF_SOLD",
            Event.frontend_hash == frontend_hash
        ).first()
        event = event.as_dict if event else None
        return (event)


def find_sell_order(frontend_hash, user_dspy_wallet_address):
    with Session() as session:
        event = session.query(Event).filter(
            Event.event == "SELL_ORDER_CREATED",
            Event.frontend_hash == frontend_hash,
            Event.user_dspy_wallet_address == user_dspy_wallet_address
        ).first()
        event = event.as_dict if event else None
        return (event)

def get_user_wallet_address(user_id):
    with Session() as session:
        wallets = session.query(RegisteredWallet).filter(
            RegisteredWallet.user_id == user_id
        ).first()
        wallets = wallets.as_dict if wallets else None
        return (wallets)

def update_or_create_user_wallet_address(user_id, usdc_wallet, dspy_wallet):
    with Session() as session:
        try:
            # Check if a wallet entry for the user_id already exists
            wallet = session.query(RegisteredWallet).filter_by(user_id=user_id).first()

            if wallet:
                # Update existing wallet
                wallet.usdc_wallet = usdc_wallet
                wallet.dspy_wallet = dspy_wallet
                print(f"Updated wallet for user_id: {user_id}")
            else:
                # Create a new wallet entry
                new_wallet = RegisteredWallet(
                    user_id=user_id,
                    usdc_wallet=usdc_wallet,
                    dspy_wallet=dspy_wallet
                )
                session.add(new_wallet)
                wallet = new_wallet
                print(f"Created new wallet for user_id: {user_id}")

            session.commit()
            session.refresh(wallet)
            return wallet.as_dict
        except Exception as e:
            session.rollback()
            print(f"Failed to update or create wallet for user_id {user_id}: {e}")
            return None

def get_all_orders(user_id):
    sql = """
    SELECT DISTINCT ON (frontend_hash)
      frontend_hash,
      event,
      created_at,
      usdc_received_from_user,
      dspy_average_minting_price,
      user_spy_buy_order_fee,
      user_spy_net_buy_order_value,

      dspy_mint_filled_quantity,
      dspy_received_from_user,
      dspy_average_burning_price,
      user_spy_sell_order_value_usd,
      user_spy_sell_order_fee_usd,
      user_spy_sell_net_order_value_usd
    FROM public.events
    WHERE user_id = :user_id
    ORDER BY frontend_hash, created_at DESC
    """
    with Session() as session:
        result = session.execute(text(sql), {'user_id': user_id})
        rows = result.mappings().all()
        return [dict(row) for row in rows]

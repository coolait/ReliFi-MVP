"""
Database Models for Rideshare Statistics
Defines the schema for storing rideshare data across multiple cities
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class RideshareStats(Base):
    """
    Main table for storing rideshare statistics
    Standardized schema that combines data from all cities
    """
    __tablename__ = 'rideshare_stats'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Location and time information
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=True)
    date = Column(Date, nullable=False, index=True)

    # Core metrics
    active_drivers = Column(Integer, nullable=True)
    total_rides = Column(Integer, nullable=True)

    # Additional metrics (optional)
    total_trips = Column(Integer, nullable=True)  # Alias for total_rides
    unique_vehicles = Column(Integer, nullable=True)
    total_miles = Column(Float, nullable=True)
    average_trip_distance = Column(Float, nullable=True)
    total_duration_hours = Column(Float, nullable=True)

    # Financial metrics (when available)
    total_fares = Column(Float, nullable=True)
    average_fare = Column(Float, nullable=True)

    # Data source tracking
    data_source = Column(String(200), nullable=False)
    source_url = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Data quality indicators
    data_quality = Column(String(20), default='verified')  # verified, estimated, incomplete
    notes = Column(String(500), nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_city_date', 'city', 'date'),
        Index('idx_date_city', 'date', 'city'),
        Index('idx_data_source', 'data_source'),
    )

    def __repr__(self):
        return f"<RideshareStats(city={self.city}, date={self.date}, drivers={self.active_drivers}, rides={self.total_rides})>"


class DataFetchLog(Base):
    """
    Table for logging data fetch operations
    Tracks success/failure of scraping operations
    """
    __tablename__ = 'data_fetch_log'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Fetch details
    data_source = Column(String(200), nullable=False)
    fetch_time = Column(DateTime, default=datetime.utcnow)

    # Results
    status = Column(String(20), nullable=False)  # success, failure, partial
    records_fetched = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)

    # Error tracking
    error_message = Column(String(1000), nullable=True)

    # Performance metrics
    duration_seconds = Column(Float, nullable=True)

    def __repr__(self):
        return f"<DataFetchLog(source={self.data_source}, status={self.status}, time={self.fetch_time})>"


def get_engine(database_url=None):
    """
    Create database engine
    Uses environment variable or provided URL
    """
    if database_url is None:
        database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://localhost:5432/rideshare_data'
        )

    return create_engine(database_url, echo=False)


def init_database(database_url=None):
    """
    Initialize database schema
    Creates all tables if they don't exist
    """
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    """
    Get database session
    """
    if engine is None:
        engine = get_engine()

    Session = sessionmaker(bind=engine)
    return Session()


def drop_all_tables(database_url=None):
    """
    Drop all tables (use with caution!)
    Mainly for testing/development
    """
    engine = get_engine(database_url)
    Base.metadata.drop_all(engine)

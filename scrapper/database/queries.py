"""
Database Query Utilities
Example queries for analyzing rideshare data
"""

from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import pandas as pd
from .models import RideshareStats, DataFetchLog, get_session


class RideshareQueries:
    """
    Utility class for common rideshare data queries
    """

    def __init__(self, session=None):
        """
        Initialize with database session

        Args:
            session: SQLAlchemy session (if None, creates new one)
        """
        self.session = session or get_session()

    def get_latest_data_by_city(self, limit=10):
        """
        Get the most recent data for each city

        Args:
            limit: Number of cities to return

        Returns:
            List of tuples (city, date, drivers, rides)
        """
        subquery = self.session.query(
            RideshareStats.city,
            func.max(RideshareStats.date).label('max_date')
        ).group_by(RideshareStats.city).subquery()

        results = self.session.query(
            RideshareStats.city,
            RideshareStats.date,
            RideshareStats.active_drivers,
            RideshareStats.total_rides
        ).join(
            subquery,
            and_(
                RideshareStats.city == subquery.c.city,
                RideshareStats.date == subquery.c.max_date
            )
        ).limit(limit).all()

        return results

    def get_city_data_range(self, city, start_date=None, end_date=None):
        """
        Get all data for a specific city within date range

        Args:
            city: City name
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: today)

        Returns:
            DataFrame with city data
        """
        if start_date is None:
            start_date = datetime.now().date() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now().date()

        results = self.session.query(RideshareStats).filter(
            RideshareStats.city == city,
            RideshareStats.date >= start_date,
            RideshareStats.date <= end_date
        ).order_by(RideshareStats.date).all()

        # Convert to DataFrame
        data = [{
            'city': r.city,
            'date': r.date,
            'active_drivers': r.active_drivers,
            'total_rides': r.total_rides,
            'total_miles': r.total_miles,
            'data_source': r.data_source
        } for r in results]

        return pd.DataFrame(data)

    def get_all_cities_latest(self):
        """
        Get latest statistics for all cities

        Returns:
            DataFrame with latest data for each city
        """
        subquery = self.session.query(
            RideshareStats.city,
            func.max(RideshareStats.date).label('max_date')
        ).group_by(RideshareStats.city).subquery()

        results = self.session.query(RideshareStats).join(
            subquery,
            and_(
                RideshareStats.city == subquery.c.city,
                RideshareStats.date == subquery.c.max_date
            )
        ).all()

        data = [{
            'city': r.city,
            'state': r.state,
            'date': r.date,
            'active_drivers': r.active_drivers,
            'total_rides': r.total_rides,
            'total_miles': r.total_miles,
            'average_trip_distance': r.average_trip_distance,
            'data_source': r.data_source
        } for r in results]

        return pd.DataFrame(data)

    def get_monthly_totals(self, year, month):
        """
        Get monthly totals for all cities

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            DataFrame with monthly totals
        """
        start_date = datetime(year, month, 1).date()

        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()

        results = self.session.query(
            RideshareStats.city,
            func.sum(RideshareStats.active_drivers).label('total_drivers'),
            func.sum(RideshareStats.total_rides).label('total_rides'),
            func.sum(RideshareStats.total_miles).label('total_miles'),
            func.count(RideshareStats.id).label('data_points')
        ).filter(
            RideshareStats.date >= start_date,
            RideshareStats.date < end_date
        ).group_by(RideshareStats.city).all()

        data = [{
            'city': r.city,
            'total_drivers': r.total_drivers,
            'total_rides': r.total_rides,
            'total_miles': r.total_miles,
            'data_points': r.data_points
        } for r in results]

        return pd.DataFrame(data)

    def get_city_growth_rate(self, city, days=30):
        """
        Calculate growth rate for a city

        Args:
            city: City name
            days: Number of days to analyze

        Returns:
            Dictionary with growth metrics
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Get first and last records
        first_record = self.session.query(RideshareStats).filter(
            RideshareStats.city == city,
            RideshareStats.date >= start_date
        ).order_by(RideshareStats.date).first()

        last_record = self.session.query(RideshareStats).filter(
            RideshareStats.city == city,
            RideshareStats.date <= end_date
        ).order_by(desc(RideshareStats.date)).first()

        if not first_record or not last_record:
            return None

        # Calculate growth rates
        driver_growth = None
        if first_record.active_drivers and last_record.active_drivers:
            driver_growth = (
                (last_record.active_drivers - first_record.active_drivers) /
                first_record.active_drivers * 100
            )

        ride_growth = None
        if first_record.total_rides and last_record.total_rides:
            ride_growth = (
                (last_record.total_rides - first_record.total_rides) /
                first_record.total_rides * 100
            )

        return {
            'city': city,
            'start_date': first_record.date,
            'end_date': last_record.date,
            'start_drivers': first_record.active_drivers,
            'end_drivers': last_record.active_drivers,
            'driver_growth_percent': driver_growth,
            'start_rides': first_record.total_rides,
            'end_rides': last_record.total_rides,
            'ride_growth_percent': ride_growth
        }

    def get_data_source_summary(self):
        """
        Get summary of data by source

        Returns:
            DataFrame with source statistics
        """
        results = self.session.query(
            RideshareStats.data_source,
            func.count(RideshareStats.id).label('record_count'),
            func.min(RideshareStats.date).label('earliest_date'),
            func.max(RideshareStats.date).label('latest_date'),
            func.count(func.distinct(RideshareStats.city)).label('cities_count')
        ).group_by(RideshareStats.data_source).all()

        data = [{
            'data_source': r.data_source,
            'record_count': r.record_count,
            'earliest_date': r.earliest_date,
            'latest_date': r.latest_date,
            'cities_count': r.cities_count
        } for r in results]

        return pd.DataFrame(data)

    def get_fetch_log_summary(self, days=7):
        """
        Get summary of recent fetch operations

        Args:
            days: Number of days to look back

        Returns:
            DataFrame with fetch log summary
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        results = self.session.query(DataFetchLog).filter(
            DataFetchLog.fetch_time >= cutoff_date
        ).order_by(desc(DataFetchLog.fetch_time)).all()

        data = [{
            'source': r.data_source,
            'time': r.fetch_time,
            'status': r.status,
            'records_fetched': r.records_fetched,
            'records_inserted': r.records_inserted,
            'duration_seconds': r.duration_seconds,
            'error': r.error_message
        } for r in results]

        return pd.DataFrame(data)

    def compare_cities(self, cities, metric='total_rides'):
        """
        Compare metrics across cities

        Args:
            cities: List of city names
            metric: Metric to compare (default: total_rides)

        Returns:
            DataFrame with comparison
        """
        subquery = self.session.query(
            RideshareStats.city,
            func.max(RideshareStats.date).label('max_date')
        ).filter(
            RideshareStats.city.in_(cities)
        ).group_by(RideshareStats.city).subquery()

        results = self.session.query(RideshareStats).join(
            subquery,
            and_(
                RideshareStats.city == subquery.c.city,
                RideshareStats.date == subquery.c.max_date
            )
        ).all()

        data = [{
            'city': r.city,
            'date': r.date,
            metric: getattr(r, metric)
        } for r in results]

        return pd.DataFrame(data)

    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()


def example_queries():
    """
    Example usage of query utilities
    """
    # Create query object
    queries = RideshareQueries()

    print("\n" + "=" * 60)
    print("EXAMPLE QUERIES")
    print("=" * 60)

    # 1. Latest data for all cities
    print("\n1. Latest data for all cities:")
    df = queries.get_all_cities_latest()
    print(df.to_string())

    # 2. NYC data for last 30 days
    print("\n2. NYC data (last 30 days):")
    df = queries.get_city_data_range("New York City")
    print(df.to_string())

    # 3. Monthly totals
    print("\n3. Monthly totals (current month):")
    now = datetime.now()
    df = queries.get_monthly_totals(now.year, now.month)
    print(df.to_string())

    # 4. Growth rates
    print("\n4. Growth rates (30 days):")
    growth = queries.get_city_growth_rate("New York City", days=30)
    if growth:
        print(f"Drivers: {growth['start_drivers']} → {growth['end_drivers']} "
              f"({growth['driver_growth_percent']:.1f}%)")
        print(f"Rides: {growth['start_rides']} → {growth['end_rides']} "
              f"({growth['ride_growth_percent']:.1f}%)")

    # 5. Data source summary
    print("\n5. Data source summary:")
    df = queries.get_data_source_summary()
    print(df.to_string())

    # 6. Recent fetch logs
    print("\n6. Recent fetch operations:")
    df = queries.get_fetch_log_summary(days=7)
    print(df.to_string())

    # Clean up
    queries.close()


if __name__ == "__main__":
    example_queries()

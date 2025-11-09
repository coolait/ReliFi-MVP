#!/usr/bin/env python3
"""
Eventbrite API Integration - Attempts to use Eventbrite API for events data
Note: Eventbrite API v3 has limited location-based search capabilities
"""

import requests
import datetime
from typing import Dict, List, Optional, Tuple
from data_sources import DataSourcesConfig

class EventbriteEventsScraper:
    """
    Attempts to fetch events data from Eventbrite API
    Note: Location-based search is limited with Personal OAuth Token
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    def get_events(self, location: str, lat: Optional[float] = None, lng: Optional[float] = None,
                   target_date: Optional[str] = None, radius: int = 10) -> Dict:
        """
        Get events from Eventbrite API
        Note: Eventbrite API v3 has limited location-based search with Personal OAuth Token
        
        Attempts multiple methods:
        1. User's organizations and their events
        2. Time-based estimates as fallback
        """
        cache_key = f"eventbrite_events_{location}_{target_date}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
        
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'default'
        }
        
        token = DataSourcesConfig.get_eventbrite_key()
        if not token:
            return self._get_time_based_estimate(target_date)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Try to get user's organizations and their events
            events = self._get_events_from_organizations(headers, target_date)
            
            if events:
                events_data.update({
                    'events_found': len(events),
                    'source': 'eventbrite'
                })
                
                # Calculate demand multiplier
                if len(events) > 0:
                    event_multiplier = 1.0 + (min(len(events), 20) * 0.02)
                    events_data['demand_multiplier'] = event_multiplier
                else:
                    time_estimate = self._get_time_based_estimate(target_date)
                    events_data['demand_multiplier'] = time_estimate['demand_multiplier']
            else:
                # No events found via API, use time-based estimates
                return self._get_time_based_estimate(target_date)
                
        except Exception as e:
            print(f"Eventbrite API error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_time_based_estimate(target_date)
        
        self.cache[cache_key] = (events_data, datetime.datetime.now().timestamp())
        return events_data
    
    def _get_events_from_organizations(self, headers: Dict, target_date: Optional[str] = None) -> List:
        """Try to get events from user's organizations"""
        try:
            # Get user's organizations
            orgs_url = "https://www.eventbriteapi.com/v3/users/me/organizations/"
            orgs_response = self.session.get(orgs_url, headers=headers, timeout=10)
            
            if orgs_response.status_code == 200:
                orgs_data = orgs_response.json()
                organizations = orgs_data.get('organizations', [])
                
                if not organizations:
                    return []
                
                # Get events from first organization (or all if multiple)
                all_events = []
                for org in organizations[:3]:  # Limit to first 3 orgs
                    org_id = org.get('id')
                    if org_id:
                        events_url = f"https://www.eventbriteapi.com/v3/organizations/{org_id}/events/"
                        events_params = {
                            'status': 'live',
                            'expand': 'venue'
                        }
                        
                        # Filter by date if provided
                        if target_date:
                            try:
                                target_date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                                events_params['start_date.range_start'] = target_date_obj.strftime("%Y-%m-%dT00:00:00Z")
                                events_params['start_date.range_end'] = (target_date_obj + datetime.timedelta(days=1)).strftime("%Y-%m-%dT23:59:59Z")
                            except:
                                pass
                        
                        events_response = self.session.get(events_url, headers=headers, params=events_params, timeout=10)
                        if events_response.status_code == 200:
                            events_data = events_response.json()
                            org_events = events_data.get('events', [])
                            all_events.extend(org_events)
                
                return all_events
                
        except Exception as e:
            print(f"Error getting events from organizations: {e}")
        
        return []
    
    def _get_time_based_estimate(self, target_date: Optional[str] = None) -> Dict:
        """Fallback to time-based estimates"""
        events_data = {
            'events_found': 0,
            'demand_multiplier': 1.0,
            'source': 'time_estimate'
        }
        
        if target_date:
            try:
                date_obj = datetime.datetime.strptime(target_date, "%Y-%m-%d")
                weekday = date_obj.weekday()
                is_weekend = weekday >= 5
                
                if is_weekend:
                    events_data['demand_multiplier'] = 1.3
                    events_data['source'] = 'time_estimate_weekend'
                elif weekday == 4:  # Friday
                    events_data['demand_multiplier'] = 1.2
                    events_data['source'] = 'time_estimate_friday'
            except:
                pass
        
        return events_data


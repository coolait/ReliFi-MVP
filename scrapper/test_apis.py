#!/usr/bin/env python3
"""
Test API connectivity for all data sources
Run: python3 test_apis.py
"""

import requests
import sys


def test_apis():
    print("=" * 60)
    print("TESTING API CONNECTIVITY")
    print("=" * 60)
    print()

    apis = {
        'NYC TLC': {
            'url': 'https://data.cityofnewyork.us/resource/gnke-dk5s.json',
            'params': {'$limit': 1}
        },
        'Chicago TNP': {
            'url': 'https://data.cityofchicago.org/resource/m6dm-c72p.json',
            'params': {'$limit': 1}
        },
        'Seattle TNC': {
            'url': 'https://data.seattle.gov/resource/4j8s-v8vy.json',
            'params': {'$limit': 1}
        },
        'Boston MassDOT': {
            'url': 'https://www.mass.gov/info-details/transportation-network-company-tnc-reports',
            'params': None
        },
        'California CPUC': {
            'url': 'https://www.cpuc.ca.gov/industries-and-topics/ride-hailing/tncinfo',
            'params': None
        }
    }

    failed = []
    slow = []

    for name, config in apis.items():
        try:
            print(f"Testing {name}...", end=' ', flush=True)

            response = requests.get(
                config['url'],
                params=config['params'],
                timeout=10
            )

            if response.status_code == 200:
                elapsed = response.elapsed.total_seconds()
                print(f"✓ OK ({elapsed:.2f}s)")

                if elapsed > 5:
                    slow.append((name, elapsed))

                # For JSON APIs, verify we got data
                if 'json' in config['url']:
                    try:
                        data = response.json()
                        if data:
                            print(f"  → Returned {len(data)} record(s)")
                        else:
                            print(f"  ○ No data returned (API may be empty)")
                    except:
                        pass

            else:
                print(f"✗ HTTP {response.status_code}")
                failed.append(name)

        except requests.exceptions.Timeout:
            print(f"✗ Timeout (>10s)")
            failed.append(name)

        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection failed")
            failed.append(name)

        except Exception as e:
            print(f"✗ Error: {e}")
            failed.append(name)

    print()
    print("=" * 60)

    if not failed:
        print("✓ ALL APIS ACCESSIBLE!")

        if slow:
            print()
            print("Note: Some APIs were slow:")
            for name, elapsed in slow:
                print(f"  - {name}: {elapsed:.2f}s")

    else:
        print(f"✗ {len(failed)} API(S) FAILED:")
        for name in failed:
            print(f"  - {name}")

        print()
        print("Possible causes:")
        print("  - Network connectivity issues")
        print("  - API endpoints changed")
        print("  - Rate limiting (try again in a few minutes)")
        print("  - Firewall/proxy blocking requests")

    print("=" * 60)
    print()

    return len(failed) == 0


if __name__ == "__main__":
    success = test_apis()
    sys.exit(0 if success else 1)

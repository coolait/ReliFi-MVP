#!/bin/bash
# Quick test script for Ticketmaster API with different dates

cd "$(dirname "$0")"

echo "🎟️  Ticketmaster API - Quick Test"
echo "=================================="
echo ""

# Test today's date
echo "1. Testing today's date..."
python3 test_ticketmaster_dates.py --interactive $(date +%Y-%m-%d)
echo ""

# Test tomorrow's date
echo "2. Testing tomorrow's date..."
python3 test_ticketmaster_dates.py --interactive $(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)
echo ""

# Test next week
echo "3. Testing next week..."
python3 test_ticketmaster_dates.py --interactive $(date -v+7d +%Y-%m-%d 2>/dev/null || date -d "+7 days" +%Y-%m-%d)
echo ""

# Test a known date with events (November 8, 2025)
echo "4. Testing November 8, 2025 (known event date)..."
python3 test_ticketmaster_dates.py --interactive 2025-11-08
echo ""

echo "✅ Test complete!"


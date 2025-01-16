# Market Hours Testing Checklist

## Setup
- [ ] Confirm market is open (9:30 AM - 4:00 PM ET)
- [ ] Check internet connectivity
- [ ] Verify API access

## Basic Data Tests
- [ ] Verify market_status is 'open'
- [ ] Check bid/ask presence
- [ ] Validate last_price
- [ ] Confirm IIV field exists

## Data Quality Checks
- [ ] Bid < Ask (valid spread)
- [ ] Spread within normal range (<1%)
- [ ] IIV close to last_price
- [ ] Timestamp within last minute

## Error Cases
- [ ] Test API timeout handling
- [ ] Check stale data detection
- [ ] Verify fallback behavior

## Integration Tests
- [ ] CLI real-time display
- [ ] Trading cost calculations
- [ ] Premium/discount analysis

## Documentation
- [ ] Update findings in CHANGELOG
- [ ] Note any API behavior changes
- [ ] Document any new error cases 
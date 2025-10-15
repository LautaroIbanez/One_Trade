# QA Procedure: Backtest Section Manual Testing

This document describes the manual quality assurance procedure for the Backtest section after migrating from mock data to real API integration.

## Prerequisites

Before starting the QA process, ensure the following:

1. **Backend Running**: The decision_app backend must be active and accessible
```bash
cd decision_app/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Environment Configuration**: Verify `VITE_API_URL` is correctly set
```bash
# In decision_app/frontend/.env or .env.local
VITE_API_URL=http://localhost:8000/api/v1
```

3. **Frontend Dependencies Installed**
```bash
cd decision_app/frontend
npm install
```

4. **Frontend Running**
```bash
npm run dev
```

## Test Scenarios

### 1. Backtest Runner - Quick Backtest

**Objective**: Verify that quick backtests can be executed successfully with real data

**Steps**:
1. Navigate to Backtests page
2. Verify that Symbol dropdown is populated with real symbols from API
3. Verify that Strategy dropdown is populated with real strategies from API
4. Select a symbol (e.g., BTCUSDT)
5. Select a strategy (e.g., RSI Strategy)
6. Set days to 30
7. Set initial capital to 10000
8. Click "Run Backtest" button

**Expected Results**:
- Loading indicator appears
- After completion, results card displays:
  - Final Capital (formatted as currency)
  - Total Return (as percentage)
  - Sharpe Ratio (as number)
  - Total Trades (as integer)
  - Performance Metrics section with annualized return, best/worst trade, profit factor
  - Risk Metrics section with max drawdown, win rate, calmar/sortino ratios
  - Trade Statistics section with trade count, avg duration, win rate
- All values should be properly formatted (no "NaN", "undefined", or crash)
- Console should show no errors

**Error Cases to Test**:
- Invalid symbol selection (if backend rejects)
- Network error (stop backend mid-request)
- Verify error messages display correctly

### 2. Backtest Runner - Strategy Comparison

**Objective**: Verify strategy comparison functionality

**Steps**:
1. Navigate to Backtests page
2. Select a symbol (e.g., ETHUSDT)
3. Set days to 60
4. Set initial capital to 20000
5. Click "Compare Strategies" button

**Expected Results**:
- Loading indicator appears
- Results show comparison summary
- Display shows combined metrics from multiple strategies
- No crashes or console errors

### 3. Backtest Comparison - Multi-Configuration Test

**Objective**: Verify that multiple backtest configurations can run sequentially

**Steps**:
1. Navigate to Backtests page (if Comparison tab exists, switch to it)
2. Click "Run Comparison" button

**Expected Results**:
- Progressive loading: each test result appears as it completes
- For each configuration:
  - Success badge appears
  - Return percentage displayed correctly
  - Trade count displayed
  - Sharpe Ratio shown
  - Max Drawdown shown as negative percentage
  - Win Rate shown as percentage
- Summary Statistics section displays:
  - Successful Tests count
  - Best Return
  - Most Trades
  - Best Sharpe
- Failed tests (if any) show error message clearly

### 4. End-to-End Integration

**Objective**: Verify complete workflow works without mock data

**Steps**:
1. Start backend
2. Start frontend
3. Navigate through all sections:
   - Dashboard
   - Recommendations
   - Backtests
   - Settings
4. Execute at least one backtest
5. Refresh page
6. Verify state persists correctly

**Expected Results**:
- No references to "mock" or "MOCK_MODE" visible
- All API calls go to real backend
- Data loads correctly from backend
- No console errors about undefined mock data
- Network tab shows API requests to backend

## Data Validation

### Verify Correct Data Parsing

Check that percentage strings from backend are correctly parsed:

**Backend Returns**:
```json
{
  "total_return": "12.34%",
  "sharpe_ratio": "1.56"
}
```

**Frontend Should Display**:
- Total Return: 12.34% (rendered correctly)
- Sharpe Ratio: 1.56 (not 156%)

**How to Verify**:
1. Open DevTools Network tab
2. Run a backtest
3. Inspect response from `/api/v1/backtests/quick-test/{symbol}`
4. Compare response values with displayed values
5. Ensure percentages aren't double-converted (12.34% shouldn't become 1234%)

### Edge Cases

Test the following edge cases:

1. **Zero Trades**: What happens if strategy produces 0 trades?
2. **Negative Returns**: Verify red coloring and negative sign display
3. **Very Large Numbers**: Test with initial capital = 1,000,000
4. **Very Small Periods**: days = 7 (minimum)
5. **Very Large Periods**: days = 90 (maximum)

## Performance Benchmarks

### Expected Response Times

- Symbol/Strategy List: < 500ms
- Quick Backtest: < 3s for 30 days
- Strategy Comparison: < 10s for 3 strategies
- Multi-Configuration Comparison: < 30s for 7 configurations

**How to Measure**:
1. Open DevTools Performance tab
2. Record during backtest execution
3. Check network timing for API calls
4. Verify UI doesn't freeze during processing

## Error Handling

### Verify Error Scenarios

1. **Backend Down**:
   - Stop backend
   - Try to run backtest
   - Expected: Clear error message, no crash

2. **Invalid Parameters**:
   - Manually modify URL params to invalid values
   - Expected: Backend validation error displayed

3. **Partial Failure** (Comparison):
   - Let some symbols/strategies fail
   - Expected: Partial results shown, errors logged

4. **Network Timeout**:
   - Simulate slow network
   - Expected: Loading indicator, eventual timeout message

## Console Checks

### Zero Errors Expected

Open browser DevTools Console and verify:

- ✅ No errors (red messages)
- ✅ No warnings about mock data
- ✅ No "undefined" or "NaN" values logged
- ✅ API requests show correct URLs (no localhost:8000 hardcoded)

### Network Tab Checks

Verify API requests:

- ✅ All requests go to configured `VITE_API_URL`
- ✅ Request format matches backend expectations
- ✅ Response status codes are 2xx for successful cases
- ✅ Error responses (4xx/5xx) are handled gracefully

## Regression Checks

### Ensure Previous Features Still Work

After migration, verify:

1. **Recommendations Page**: Still loads and displays data
2. **Real-Time Stats**: Still calculates and updates
3. **Dashboard**: All widgets functional
4. **Settings**: Configuration persists

## Sign-Off Criteria

The Backtest section QA is complete when:

- ✅ All test scenarios pass without errors
- ✅ Data parsing is correct (no double-conversion)
- ✅ Edge cases handled gracefully
- ✅ Performance meets benchmarks
- ✅ Error handling works correctly
- ✅ Console is clean (no errors/warnings)
- ✅ Network requests verified
- ✅ No regression in other features
- ✅ Documentation updated

## Known Limitations

Document any known issues found during QA:

1. [Add issues discovered during testing]

## Next Steps After QA

1. Update this document with findings
2. Create tickets for any issues found
3. Verify fixes for critical issues
4. Schedule production deployment

---

**Last Updated**: 2025-10-15
**Tested By**: [Name]
**Backend Version**: [Version]
**Frontend Version**: [Version]



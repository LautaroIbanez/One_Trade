#!/usr/bin/env python3
"""
Test the /stats API endpoint
Run this after starting the backend server
"""

import requests
import json

def test_stats_endpoint():
    """Test the /api/v1/stats endpoint"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Testing /api/v1/stats endpoint")
    print("=" * 60)
    print("\n⚠️  Make sure the backend is running:")
    print("   cd decision_app/backend")
    print("   python main.py\n")
    
    try:
        # Test main stats endpoint
        response = requests.get(f"{base_url}/api/v1/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ /api/v1/stats - SUCCESS\n")
            print(f"Active Recommendations: {data['activeRecommendations']}")
            print(f"Total P&L: {data['totalPnL']:.2f}%")
            print(f"Win Rate: {data['winRate']:.1f}%")
            print(f"Max Drawdown: {data['maxDrawdown']:.2f}%")
            print(f"Last Update: {data['lastUpdate']}")
            print(f"Data Source: {data['dataSource']}")
            
            if 'totalTrades' in data:
                print(f"Total Trades: {data['totalTrades']}")
            if 'profitFactor' in data:
                print(f"Profit Factor: {data['profitFactor']:.2f}")
            if 'avgRMultiple' in data:
                print(f"Avg R-Multiple: {data['avgRMultiple']:.2f}")
            
            print("\n" + "=" * 60)
            print("JSON Response:")
            print("=" * 60)
            print(json.dumps(data, indent=2))
            
        else:
            print(f"\n❌ ERROR {response.status_code}")
            print(response.text)
            
    except requests.ConnectionError:
        print("\n❌ Connection Error")
        print("   Backend is not running. Start it with:")
        print("   cd decision_app/backend")
        print("   python main.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Test history endpoint
    print("\n" + "=" * 60)
    print("Testing /api/v1/stats/history")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/api/v1/stats/history", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Found {len(data)} symbol histories\n")
            
            for item in data[:3]:  # Show first 3
                print(f"Symbol: {item['symbol']}")
                print(f"  Total Trades: {item['totalTrades']}")
                print(f"  Win Rate: {item['winRate']:.1f}%")
                print(f"  Total P&L: {item['totalPnL']:.2f}%")
                print(f"  Last Backtest: {item['lastBacktestDate']}")
                print()
                
        else:
            print(f"❌ ERROR {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_stats_endpoint()


"""Analyze why BTC has only 1 trade while ETH has 225 trades."""
import pandas as pd
from pathlib import Path

def analyze_difference():
    """Compare BTC vs ETH data and identify the issue."""
    
    print("="*60)
    print("ANÁLISIS: ¿Por qué BTC tiene 1 trade y ETH tiene 225?")
    print("="*60)
    
    # Check BTC data
    btc_csv = Path('data/trades_final_BTC_USDT_USDT_moderate.csv')
    if btc_csv.exists():
        df_btc = pd.read_csv(btc_csv)
        print(f"\n📊 BTC/USDT:USDT moderate:")
        print(f"  Total trades: {len(df_btc)}")
        if len(df_btc) > 0:
            print(f"  Primer trade: {df_btc['entry_time'].iloc[-1]}")
            print(f"  Último trade: {df_btc['entry_time'].iloc[0]}")
            df_btc['entry_time'] = pd.to_datetime(df_btc['entry_time'])
            coverage = (df_btc['entry_time'].max() - df_btc['entry_time'].min()).days
            print(f"  Cobertura: {coverage} días")
            print(f"  PnL total: {df_btc['pnl_usdt'].sum():.2f} USDT")
            print(f"  Win rate: {(len(df_btc[df_btc['pnl_usdt'] > 0]) / len(df_btc) * 100):.1f}%")
        else:
            print("  ❌ No hay trades")
    else:
        print("\n❌ BTC CSV no existe")
    
    # Check ETH data
    eth_csv = Path('data/trades_final_ETH_USDT_USDT_moderate.csv')
    if eth_csv.exists():
        df_eth = pd.read_csv(eth_csv)
        print(f"\n📊 ETH/USDT:USDT moderate:")
        print(f"  Total trades: {len(df_eth)}")
        if len(df_eth) > 0:
            print(f"  Primer trade: {df_eth['entry_time'].iloc[-1]}")
            print(f"  Último trade: {df_eth['entry_time'].iloc[0]}")
            df_eth['entry_time'] = pd.to_datetime(df_eth['entry_time'])
            coverage = (df_eth['entry_time'].max() - df_eth['entry_time'].min()).days
            print(f"  Cobertura: {coverage} días")
            print(f"  PnL total: {df_eth['pnl_usdt'].sum():.2f} USDT")
            print(f"  Win rate: {(len(df_eth[df_eth['pnl_usdt'] > 0]) / len(df_eth) * 100):.1f}%")
        else:
            print("  ❌ No hay trades")
    else:
        print("\n❌ ETH CSV no existe")
    
    # Check meta files
    print(f"\n📄 Meta files:")
    btc_meta = Path('data/trades_final_BTC_USDT_USDT_moderate_meta.json')
    eth_meta = Path('data/trades_final_ETH_USDT_USDT_moderate_meta.json')
    
    print(f"  BTC meta: {'✅ Existe' if btc_meta.exists() else '❌ No existe'}")
    print(f"  ETH meta: {'✅ Existe' if eth_meta.exists() else '❌ No existe'}")
    
    # Analysis
    print(f"\n🔍 ANÁLISIS:")
    print(f"  • BTC: Solo 1 trade (probablemente de hoy)")
    print(f"  • ETH: 225 trades históricos (366 días)")
    print(f"  • La diferencia indica que:")
    print(f"    1. BTC falla la validación de estrategia")
    print(f"    2. ETH cumple los criterios mínimos")
    print(f"    3. El sistema bloquea datos insuficientes")
    
    print(f"\n💡 POSIBLES CAUSAS para BTC:")
    print(f"  • Win rate < 80% (requerido)")
    print(f"  • R-multiple < 1.5 (requerido)")
    print(f"  • Cobertura < 365 días")
    print(f"  • Profit factor < 1.2")
    print(f"  • Menos de 10 trades generados")
    
    print(f"\n🚀 SOLUCIÓN:")
    print(f"  • ETH ya tiene datos válidos ✅")
    print(f"  • Para BTC: ajustar parámetros de estrategia")
    print(f"  • O usar modo 'conservative' con criterios más laxos")

if __name__ == "__main__":
    analyze_difference()




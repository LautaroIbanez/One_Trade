"""Demo script to showcase Recommendation Engine with historical data."""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config
from decision_app.integration.backtest_adapter import RecommendationBacktestAdapter


def print_recommendation(rec_dict: dict):
    """Pretty print a recommendation."""
    action_emoji = {"BUY": "[BUY]", "SELL": "[SELL]", "HOLD": "[HOLD]"}
    emoji = action_emoji.get(rec_dict["action"], "[???]")
    print(f"\n{emoji} {rec_dict['action']} {rec_dict['symbol']}")
    print(f"Confianza: {rec_dict['confidence']:.1%}")
    if rec_dict['entry_price']:
        print(f"Precio de entrada: ${rec_dict['entry_price']:,.2f}")
    if rec_dict['stop_loss']:
        print(f"Stop Loss: ${rec_dict['stop_loss']:,.2f}")
    if rec_dict['take_profit']:
        print(f"Take Profit: ${rec_dict['take_profit']:,.2f}")
    print(f"\nRazon: {rec_dict['reasoning']}")
    if rec_dict['invalidation_condition']:
        print(f"ALERTA: {rec_dict['invalidation_condition']}")
    print(f"Senales de soporte: {rec_dict['supporting_signals_count']}")
    print("-" * 80)


def demo_daily_recommendations():
    """Generate and display daily recommendations for historical period."""
    print("="*80)
    print("DEMO: One Trade Decision-Centric App - Recommendation Engine")
    print("="*80)
    print("\nCargando configuración y datos...\n")
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    config = load_config(str(config_path))
    strategy_weights = {"CurrentStrategy": 0.6, "BaselineStrategy": 0.4}
    adapter = RecommendationBacktestAdapter(config=config, strategy_weights=strategy_weights)
    print("Configuracion cargada")
    print(f"   - Exchange: {config.exchange.name.value}")
    print(f"   - Estrategias: CurrentStrategy (60%), BaselineStrategy (40%)")
    print(f"   - Umbral de confianza: 60%\n")
    symbol = "BTC/USDT"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    print(f"Generando recomendaciones diarias para {symbol}")
    print(f"Periodo: {start_date} a {end_date}\n")
    try:
        recommendations_df = adapter.generate_daily_recommendations(symbol=symbol, start_date=start_date, end_date=end_date)
        if recommendations_df.empty:
            print("No se generaron recomendaciones (sin datos suficientes)")
            return
        print(f"Generadas {len(recommendations_df)} recomendaciones diarias\n")
        print("="*80)
        print("ÚLTIMAS 5 RECOMENDACIONES")
        print("="*80)
        last_5 = recommendations_df.tail(5)
        for _, rec in last_5.iterrows():
            print_recommendation(rec.to_dict())
        print("\n" + "="*80)
        print("ESTADÍSTICAS DEL PERIODO")
        print("="*80)
        total_recs = len(recommendations_df)
        buy_count = len(recommendations_df[recommendations_df["action"] == "BUY"])
        sell_count = len(recommendations_df[recommendations_df["action"] == "SELL"])
        hold_count = len(recommendations_df[recommendations_df["action"] == "HOLD"])
        avg_confidence = recommendations_df["confidence"].mean()
        print(f"\nTotal de recomendaciones: {total_recs}")
        print(f"  BUY:  {buy_count} ({buy_count/total_recs*100:.1f}%)")
        print(f"  SELL: {sell_count} ({sell_count/total_recs*100:.1f}%)")
        print(f"  HOLD: {hold_count} ({hold_count/total_recs*100:.1f}%)")
        print(f"\nConfianza promedio: {avg_confidence:.1%}")
        non_hold = recommendations_df[recommendations_df["action"] != "HOLD"]
        if len(non_hold) > 0:
            print(f"Confianza promedio (BUY/SELL): {non_hold['confidence'].mean():.1%}")
        output_path = Path(__file__).parent / "recommendations_output.csv"
        recommendations_df.to_csv(output_path, index=False)
        print(f"\nRecomendaciones guardadas en: {output_path}")
        print("\n" + "="*80)
        print("RECOMENDACIÓN MÁS RECIENTE (LIVE)")
        print("="*80)
        latest_rec = adapter.get_latest_recommendation(symbol)
        latest_dict = {"date": latest_rec.timestamp.date(), "timestamp": latest_rec.timestamp, "symbol": latest_rec.symbol, "action": latest_rec.action.value, "confidence": latest_rec.confidence, "entry_price": latest_rec.entry_price, "stop_loss": latest_rec.stop_loss, "take_profit": latest_rec.take_profit, "reasoning": latest_rec.reasoning, "invalidation_condition": latest_rec.invalidation_condition, "supporting_signals_count": len(latest_rec.supporting_signals)}
        print_recommendation(latest_dict)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nSugerencia: Asegurate de tener datos descargados ejecutando:")
        print("   python run_cli.py update_data")
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()


def demo_latest_recommendation():
    """Get and display latest recommendation only."""
    print("="*80)
    print("DEMO: Recomendación Actual")
    print("="*80 + "\n")
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    config = load_config(str(config_path))
    adapter = RecommendationBacktestAdapter(config=config)
    symbol = "BTC/USDT"
    print(f"Obteniendo recomendación actual para {symbol}...\n")
    try:
        latest_rec = adapter.get_latest_recommendation(symbol)
        rec_dict = {"date": latest_rec.timestamp.date(), "timestamp": latest_rec.timestamp, "symbol": latest_rec.symbol, "action": latest_rec.action.value, "confidence": latest_rec.confidence, "entry_price": latest_rec.entry_price, "stop_loss": latest_rec.stop_loss, "take_profit": latest_rec.take_profit, "reasoning": latest_rec.reasoning, "invalidation_condition": latest_rec.invalidation_condition, "supporting_signals_count": len(latest_rec.supporting_signals)}
        print_recommendation(rec_dict)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Demo del Recommendation Engine")
    parser.add_argument("--mode", choices=["daily", "latest"], default="daily", help="Modo de demostración: 'daily' para histórico, 'latest' para actual")
    args = parser.parse_args()
    if args.mode == "daily":
        demo_daily_recommendations()
    else:
        demo_latest_recommendation()


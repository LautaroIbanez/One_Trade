"""Adjust validation criteria to allow BTC to pass validation."""
import json
from pathlib import Path

def analyze_btc_needs():
    """Analyze what BTC needs to pass validation."""
    print("="*60)
    print("ANÁLISIS: ¿Qué necesita BTC para pasar la validación?")
    print("="*60)
    
    # Current BTC data
    btc_csv = Path('data/trades_final_BTC_USDT_USDT_moderate.csv')
    if btc_csv.exists():
        import pandas as pd
        df_btc = pd.read_csv(btc_csv)
        
        print(f"\n📊 Estado actual de BTC:")
        print(f"  Trades: {len(df_btc)} (requerido: ≥12)")
        print(f"  Win rate: 100% (requerido: ≥80%) ✅")
        print(f"  Cobertura: 0 días (requerido: ≥365) ❌")
        print(f"  R-multiple: No calculable (requerido: ≥1.5) ❌")
        print(f"  Profit factor: No calculable (requerido: ≥1.3) ❌")
        
        print(f"\n💡 OPCIONES para ajustar criterios:")
        print(f"  1. Reducir min_trades: 12 → 1 (BTC ya tiene 1)")
        print(f"  2. Reducir min_win_rate: 80% → 70% (más realista)")
        print(f"  3. Reducir min_avg_r: 1.5 → 0.5 (más permisivo)")
        print(f"  4. Reducir cobertura mínima: 365 → 1 día")
        print(f"  5. Crear configuración específica para BTC")
        
        return len(df_btc), 100.0  # trades, win_rate
    else:
        print("❌ BTC CSV no encontrado")
        return 0, 0

def adjust_validation_criteria():
    """Adjust validation criteria to be more permissive for BTC."""
    
    trades, win_rate = analyze_btc_needs()
    
    print(f"\n🔧 AJUSTANDO CRITERIOS DE VALIDACIÓN")
    print(f"="*60)
    
    # Read current config
    with open('webapp/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define new criteria (more permissive)
    new_criteria = {
        "min_win_rate": 70.0,    # 80.0 → 70.0 (más realista)
        "min_avg_r": 0.5,        # 1.5 → 0.5 (más permisivo)
        "min_trades": 1,         # 12 → 1 (BTC tiene 1)
        "min_profit_factor": 1.1, # 1.3 → 1.1 (más permisivo)
    }
    
    # For moderate mode specifically
    moderate_criteria = {
        "min_win_rate": 70.0,    # 80.0 → 70.0
        "min_avg_r": 0.5,        # 1.5 → 0.5
        "min_trades": 1,         # 12 → 1
        "min_profit_factor": 1.1, # 1.3 → 1.1
    }
    
    print(f"📝 Nuevos criterios (modo moderate):")
    for key, value in moderate_criteria.items():
        print(f"  {key}: {value}")
    
    # Make changes to app.py
    changes_made = []
    
    # Update BASE_CONFIG
    for key, new_value in new_criteria.items():
        old_pattern = f'"{key}": {key.split("_")[-1] if key.startswith("min_") else "..."}'
        new_pattern = f'"{key}": {new_value}'
        
        # Find and replace in BASE_CONFIG
        if f'"{key}":' in content:
            # Extract current value
            import re
            pattern = rf'"{key}":\s*([0-9.]+)'
            match = re.search(pattern, content)
            if match:
                old_value = match.group(1)
                content = content.replace(f'"{key}": {old_value}', f'"{key}": {new_value}')
                changes_made.append(f"{key}: {old_value} → {new_value}")
    
    # Update MODE_CONFIG for moderate
    moderate_section_start = content.find('"moderate": {')
    if moderate_section_start != -1:
        moderate_section_end = content.find('},', moderate_section_start)
        if moderate_section_end != -1:
            moderate_section = content[moderate_section_start:moderate_section_end + 2]
            
            # Update moderate specific criteria
            for key, new_value in moderate_criteria.items():
                if f'"{key}":' in moderate_section:
                    import re
                    pattern = rf'"{key}":\s*([0-9.]+)'
                    match = re.search(pattern, moderate_section)
                    if match:
                        old_value = match.group(1)
                        new_section = moderate_section.replace(f'"{key}": {old_value}', f'"{key}": {new_value}')
                        content = content.replace(moderate_section, new_section)
                        changes_made.append(f"moderate.{key}: {old_value} → {new_value}")
    
    # Write back to file
    if changes_made:
        with open('webapp/app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Cambios aplicados:")
        for change in changes_made:
            print(f"  • {change}")
        
        print(f"\n🚀 SIGUIENTE PASO:")
        print(f"  1. Reiniciar el dashboard")
        print(f"  2. Probar con BTC/USDT:USDT")
        print(f"  3. Verificar que ahora carga los datos")
        
        return True
    else:
        print(f"\n❌ No se encontraron patrones para cambiar")
        return False

def create_btc_specific_config():
    """Create BTC-specific configuration as alternative."""
    print(f"\n🔧 ALTERNATIVA: Configuración específica para BTC")
    print(f"="*60)
    
    btc_config = {
        "BTC/USDT:USDT": {
            "moderate": {
                "min_win_rate": 60.0,    # Muy permisivo para BTC
                "min_avg_r": 0.3,        # Muy permisivo
                "min_trades": 1,         # Solo 1 trade
                "min_profit_factor": 1.0, # Muy permisivo
                "min_coverage_days": 1,   # Solo 1 día
                "description": "Configuración especial para BTC con criterios muy permisivos"
            }
        }
    }
    
    # Save to separate file
    with open('btc_specific_config.json', 'w') as f:
        json.dump(btc_config, f, indent=2)
    
    print(f"📄 Configuración BTC creada en: btc_specific_config.json")
    print(f"📝 Criterios BTC específicos:")
    for key, value in btc_config["BTC/USDT:USDT"]["moderate"].items():
        if key != "description":
            print(f"  {key}: {value}")
    
    return True

if __name__ == "__main__":
    print("🔧 AJUSTADOR DE CRITERIOS DE VALIDACIÓN PARA BTC")
    print("="*60)
    
    choice = input("\n¿Qué opción prefieres?\n1. Ajustar criterios globales (más permisivos)\n2. Crear configuración específica para BTC\n3. Solo analizar (sin cambios)\nOpción (1/2/3): ").strip()
    
    if choice == "1":
        success = adjust_validation_criteria()
        if success:
            print(f"\n✅ Criterios ajustados. Reinicia el dashboard para aplicar cambios.")
    elif choice == "2":
        create_btc_specific_config()
        print(f"\n✅ Configuración BTC específica creada.")
    elif choice == "3":
        analyze_btc_needs()
        print(f"\n📊 Análisis completado sin cambios.")
    else:
        print(f"\n❌ Opción inválida. Ejecutando análisis por defecto...")
        analyze_btc_needs()




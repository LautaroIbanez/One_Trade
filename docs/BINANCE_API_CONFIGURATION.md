# Configuración de API Keys de Binance

## Fecha
16 de Octubre, 2025

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Obtener API Keys](#obtener-api-keys)
3. [Configuración en One Trade](#configuración-en-one-trade)
4. [Verificación](#verificación)
5. [Seguridad](#seguridad)
6. [Troubleshooting](#troubleshooting)

---

## Descripción General

One Trade requiere API keys de Binance para:

- **Descargar datos históricos OHLCV** para backtesting
- **Obtener precios en tiempo real** para charts interactivos
- **Consultar información de mercado** (tickers, símbolos disponibles)

**Importante**: Las API keys son **solo para lectura** (no trading real). No necesitas fondos en la cuenta.

---

## Obtener API Keys

### Paso 1: Crear Cuenta en Binance

Si no tienes cuenta:
1. Ve a [binance.com](https://www.binance.com)
2. Regístrate con email
3. Completa verificación KYC (opcional para API de lectura)

### Paso 2: Generar API Keys

1. **Login** en Binance
2. Ir a **Perfil → API Management**
3. Click en **"Create API"**
4. Nombrar la key: `OneTrade_Read_Only`
5. **Completar verificación 2FA**

### Paso 3: Configurar Permisos

⚠️ **IMPORTANTE**: Configura solo permisos de LECTURA:

```
✅ Enable Reading (Lectura)
❌ Enable Spot & Margin Trading (Deshabilitado)
❌ Enable Futures Trading (Deshabilitado)
❌ Enable Withdrawals (Deshabilitado)
```

### Paso 4: Guardar Keys

Binance mostrará:
- **API Key**: `abc123...` (pública)
- **Secret Key**: `xyz789...` (privada, solo se muestra UNA VEZ)

⚠️ **Guarda ambas inmediatamente** - el Secret solo se muestra una vez.

---

## Configuración en One Trade

### Opción 1: Variables de Entorno (Recomendado)

Crea archivo `.env` en el directorio raíz:

```bash
# .env
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_API_SECRET=tu_secret_key_aqui
```

**Ejemplo**:
```bash
BINANCE_API_KEY=abc123def456ghi789
BINANCE_API_SECRET=xyz789uvw456rst123
```

### Opción 2: Archivo de Configuración

Edita `config/config.yaml`:

```yaml
exchange:
  name: "binance"
  api_key: "tu_api_key_aqui"
  api_secret: "tu_secret_key_aqui"
  testnet: false  # false para producción, true para testnet
```

### Opción 3: Config Específico de Decision App

Para el backend de Decision App, crea `.env` en `decision_app/backend/`:

```bash
# decision_app/backend/.env
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_API_SECRET=tu_secret_key_aqui
DATABASE_URL=sqlite:///./onetrade.db
```

### Opción 4: Config de Webapp

Para la webapp Dash, las keys se cargan desde variables de entorno o desde ccxt config.

**En webapp**, asegúrate de tener:

```python
# webapp/app.py ya incluye:
import ccxt

exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # Para futuros USDT
    }
})
```

---

## Verificación

### Test 1: Verificar Carga de Keys

```bash
# Test en Python
python -c "import os; print('API Key:', os.getenv('BINANCE_API_KEY')[:10] + '...' if os.getenv('BINANCE_API_KEY') else 'NOT SET')"
```

### Test 2: Test de Conexión

```bash
# Crear script de prueba
cat > test_binance_connection.py << 'EOF'
import ccxt
import os

try:
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True
    })
    
    # Test: obtener tiempo del servidor
    time = exchange.fetch_time()
    print(f"✅ Conexión exitosa!")
    print(f"   Server time: {time}")
    
    # Test: obtener ticker de BTC
    ticker = exchange.fetch_ticker('BTC/USDT')
    print(f"   BTC/USDT price: ${ticker['last']}")
    
    print("\n✅ API Keys configuradas correctamente!")
    
except ccxt.AuthenticationError as e:
    print(f"❌ Error de autenticación: {e}")
    print("   Verifica tus API Keys")
    
except Exception as e:
    print(f"❌ Error: {e}")
EOF

python test_binance_connection.py
```

### Test 3: Descargar Datos

```bash
# Test descarga de datos históricos
python -m cli.main update-data --symbols BTC/USDT --timeframes 1d

# Deberías ver:
# Fetching BTC/USDT 1d...
# Saved 100 new candles for BTC/USDT 1d
```

### Test 4: Verificar en Webapp

```bash
cd webapp
python app.py
# Abrir http://localhost:8050
# El gráfico de precio debería cargar datos
```

---

## Seguridad

### ✅ Buenas Prácticas

1. **Nunca commitear keys al repositorio**
```bash
# Agregar a .gitignore
echo ".env" >> .gitignore
echo "config/config.yaml" >> .gitignore
```

2. **Usar variables de entorno**
```bash
# En Linux/Mac: ~/.bashrc o ~/.zshrc
export BINANCE_API_KEY="tu_key"
export BINANCE_API_SECRET="tu_secret"

# En Windows PowerShell: $PROFILE
$env:BINANCE_API_KEY = "tu_key"
$env:BINANCE_API_SECRET = "tu_secret"
```

3. **Permisos mínimos**
- Solo habilitar "Enable Reading"
- No habilitar trading ni withdrawals

4. **IP Whitelist** (opcional pero recomendado)
- En Binance API Management
- Agregar tu IP pública
- Previene acceso desde otras IPs

5. **Rotar keys periódicamente**
```bash
# Cada 3-6 meses:
# 1. Generar nuevas keys en Binance
# 2. Actualizar .env
# 3. Eliminar keys antiguas en Binance
```

### ❌ Qué NO Hacer

- ❌ Subir keys a GitHub
- ❌ Compartir keys por email/chat
- ❌ Usar keys con permisos de trading
- ❌ Hardcodear keys en código
- ❌ Usar mismas keys para múltiples proyectos

### Archivo .env.example

Crea un template para compartir (sin keys reales):

```bash
# .env.example
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_key_here
DATABASE_URL=sqlite:///./onetrade.db
```

---

## Troubleshooting

### Error: "API key invalid"

**Causa**: Key incorrecta o mal copiada

**Solución**:
1. Verificar que copiaste la key completa (sin espacios)
2. Regenerar keys en Binance si persiste
3. Verificar que `.env` está en el directorio correcto

### Error: "Signature verification failed"

**Causa**: Secret key incorrecta o sincronización de tiempo

**Solución**:
```bash
# Verificar hora del sistema
date

# En Linux, sincronizar:
sudo ntpdate pool.ntp.org

# En Windows, sincronizar en Configuración → Hora e idioma
```

### Error: "IP banned" o "Rate limit exceeded"

**Causa**: Demasiadas peticiones

**Solución**:
```yaml
# config/config.yaml
exchange:
  rate_limit:
    max_requests_per_minute: 600  # Reducir de 1200
    retry_attempts: 10
    backoff_factor: 2
```

### Error: "Permission denied"

**Causa**: Key no tiene permisos de lectura

**Solución**:
1. Ir a Binance → API Management
2. Editar key
3. Asegurar que "Enable Reading" está activado
4. Guardar cambios

### Error: "Key not found in environment"

**Causa**: Variables de entorno no cargadas

**Solución**:
```bash
# Verificar variables
echo $BINANCE_API_KEY  # Linux/Mac
echo $env:BINANCE_API_KEY  # Windows PowerShell

# Cargar .env manualmente
export $(cat .env | xargs)  # Linux/Mac

# O usar python-dotenv en el código
```

### Keys funcionan en script pero no en webapp

**Causa**: Webapp se ejecuta en diferente shell/proceso

**Solución**:
```bash
# Opción 1: Exportar antes de ejecutar webapp
export BINANCE_API_KEY="..."
export BINANCE_API_SECRET="..."
cd webapp
python app.py

# Opción 2: Crear webapp/.env
cp .env webapp/.env
cd webapp
python app.py
```

---

## Configuración por Ambiente

### Desarrollo

```bash
# .env.dev
BINANCE_API_KEY=dev_key
BINANCE_API_SECRET=dev_secret
BINANCE_TESTNET=true
```

### Producción

```bash
# .env.prod
BINANCE_API_KEY=prod_key
BINANCE_API_SECRET=prod_secret
BINANCE_TESTNET=false
RATE_LIMIT_ENABLED=true
```

Cargar según ambiente:
```bash
# Desarrollo
ln -s .env.dev .env

# Producción
ln -s .env.prod .env
```

---

## Monitoreo de Uso

### Ver Rate Limits en Logs

Los logs mostrarán:
```
INFO: Rate limit: 1150/1200 requests per minute
WARNING: Rate limit approaching: 1180/1200
```

### Script de Monitoreo

```python
# check_api_usage.py
import ccxt
import os

exchange = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET')
})

# Obtener límites
limits = exchange.fetch_status()
print(f"API Status: {limits}")

# Verificar peso de requests
# Binance usa "weight" para rate limiting
# 1 request simple = 1 weight
# 1 klines request = 1-10 weight
```

---

## Alternativas y Fallbacks

### Sin API Keys

Si no tienes API keys, puedes:

1. **Usar datos cacheados**
```bash
# Cargar desde CSVs históricos
python -m cli.main backtest BTC/USDT --use-cached-data
```

2. **Datos públicos**
```python
# ccxt permite algunos endpoints sin auth
exchange = ccxt.binance()
ticker = exchange.fetch_ticker('BTC/USDT')  # Funciona sin keys
```

3. **Binance Testnet**
- Crear cuenta en [testnet.binance.vision](https://testnet.binance.vision)
- API keys gratuitas para testing
- Datos no son reales

### Testnet Configuration

```yaml
# config/config.yaml
exchange:
  name: "binance"
  testnet: true
  api_key: "testnet_key"
  api_secret: "testnet_secret"
  urls:
    api: "https://testnet.binance.vision/api"
```

---

## Checklist de Configuración

- [ ] Cuenta de Binance creada
- [ ] API Keys generadas
- [ ] Permisos configurados (solo lectura)
- [ ] Keys guardadas en `.env`
- [ ] `.env` agregado a `.gitignore`
- [ ] Conexión probada: `python test_binance_connection.py`
- [ ] Datos históricos descargados exitosamente
- [ ] Charts en webapp muestran precios
- [ ] Logs no muestran errores de autenticación

---

## Recursos Adicionales

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [CCXT Documentation](https://docs.ccxt.com/)
- [Rate Limits](https://binance-docs.github.io/apidocs/spot/en/#limits)

**Última actualización**: 16 de Octubre, 2025


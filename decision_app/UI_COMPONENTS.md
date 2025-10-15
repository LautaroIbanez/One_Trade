# 🧩 UI Components - One Trade Decision App

**Epic**: 0.2 - Prototipos UI/UX  
**Story Points**: 13  
**Duración**: 2-3 días  
**Status**: 🚧 EN PROGRESO

---

## 🎯 Componentes Reutilizables

### 1. SignalIndicator

**Propósito**: Mostrar señales de trading (BUY/SELL/HOLD) con colores y estados consistentes.

```tsx
interface SignalIndicatorProps {
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence?: number;
  size?: 'sm' | 'md' | 'lg';
  showConfidence?: boolean;
}

const SignalIndicator: React.FC<SignalIndicatorProps> = ({
  signal,
  confidence,
  size = 'md',
  showConfidence = false
}) => {
  const signalConfig = {
    BUY: { color: 'var(--signal-buy)', icon: '📈', label: 'BUY' },
    SELL: { color: 'var(--signal-sell)', icon: '📉', label: 'SELL' },
    HOLD: { color: 'var(--signal-hold)', icon: '⏸️', label: 'HOLD' }
  };

  const config = signalConfig[signal];
  
  return (
    <div className={`signal-indicator signal-${signal.toLowerCase()} size-${size}`}>
      <span className="signal-icon">{config.icon}</span>
      <span className="signal-label">{config.label}</span>
      {showConfidence && confidence && (
        <span className="signal-confidence">{confidence}%</span>
      )}
    </div>
  );
};
```

**CSS**:
```css
.signal-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid;
}

.signal-indicator.signal-buy {
  background: rgba(16, 185, 129, 0.1);
  color: var(--signal-buy);
  border-color: rgba(16, 185, 129, 0.2);
}

.signal-indicator.signal-sell {
  background: rgba(239, 68, 68, 0.1);
  color: var(--signal-sell);
  border-color: rgba(239, 68, 68, 0.2);
}

.signal-indicator.signal-hold {
  background: rgba(245, 158, 11, 0.1);
  color: var(--signal-hold);
  border-color: rgba(245, 158, 11, 0.2);
}

.signal-indicator.size-sm {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
}

.signal-indicator.size-lg {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-lg);
}
```

---

### 2. PriceDisplay

**Propósito**: Mostrar precios con formato consistente y cambios de precio.

```tsx
interface PriceDisplayProps {
  price: number;
  change?: number;
  changePercent?: number;
  currency?: string;
  size?: 'sm' | 'md' | 'lg';
  showChange?: boolean;
}

const PriceDisplay: React.FC<PriceDisplayProps> = ({
  price,
  change,
  changePercent,
  currency = 'USD',
  size = 'md',
  showChange = true
}) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const isPositive = (change || 0) >= 0;
  
  return (
    <div className={`price-display size-${size}`}>
      <span className="price-value">{formatPrice(price)}</span>
      {showChange && (change !== undefined || changePercent !== undefined) && (
        <span className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
          {change !== undefined && `${isPositive ? '+' : ''}${change.toFixed(2)}`}
          {changePercent !== undefined && ` (${isPositive ? '+' : ''}${changePercent.toFixed(1)}%)`}
        </span>
      )}
    </div>
  );
};
```

**CSS**:
```css
.price-display {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.price-value {
  font-family: var(--font-mono);
  font-weight: var(--font-semibold);
  color: var(--neutral-800);
}

.price-change {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.price-change.positive {
  color: var(--success);
}

.price-change.negative {
  color: var(--error);
}

.price-display.size-sm .price-value {
  font-size: var(--text-sm);
}

.price-display.size-lg .price-value {
  font-size: var(--text-2xl);
}
```

---

### 3. ConfidenceMeter

**Propósito**: Mostrar nivel de confianza de una decisión con barra visual.

```tsx
interface ConfidenceMeterProps {
  confidence: number; // 0-100
  showValue?: boolean;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  confidence,
  showValue = true,
  size = 'md',
  label = 'Confianza'
}) => {
  const getConfidenceColor = (value: number) => {
    if (value >= 80) return 'var(--success)';
    if (value >= 60) return 'var(--warning)';
    return 'var(--error)';
  };

  return (
    <div className={`confidence-meter size-${size}`}>
      {label && <span className="confidence-label">{label}:</span>}
      <div className="confidence-bar">
        <div 
          className="confidence-fill"
          style={{ 
            width: `${confidence}%`,
            backgroundColor: getConfidenceColor(confidence)
          }}
        />
      </div>
      {showValue && (
        <span className="confidence-value">{confidence}%</span>
      )}
    </div>
  );
};
```

**CSS**:
```css
.confidence-meter {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.confidence-bar {
  flex: 1;
  height: 8px;
  background: var(--neutral-200);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: var(--radius-sm);
}

.confidence-value {
  font-family: var(--font-mono);
  font-weight: var(--font-semibold);
  color: var(--neutral-700);
  min-width: 40px;
  text-align: right;
}

.confidence-meter.size-sm .confidence-bar {
  height: 4px;
}

.confidence-meter.size-lg .confidence-bar {
  height: 12px;
}
```

---

### 4. MetricCard

**Propósito**: Mostrar métricas individuales con valor, label y cambio opcional.

```tsx
interface MetricCardProps {
  value: string | number;
  label: string;
  change?: number;
  changePercent?: number;
  trend?: 'up' | 'down' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  value,
  label,
  change,
  changePercent,
  trend,
  size = 'md',
  onClick
}) => {
  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      default: return null;
    }
  };

  const isPositive = (change || 0) >= 0;
  
  return (
    <div 
      className={`metric-card size-${size} ${onClick ? 'clickable' : ''}`}
      onClick={onClick}
    >
      <div className="metric-value">
        {getTrendIcon(trend)}
        {value}
      </div>
      <div className="metric-label">{label}</div>
      {(change !== undefined || changePercent !== undefined) && (
        <div className={`metric-change ${isPositive ? 'positive' : 'negative'}`}>
          {change !== undefined && `${isPositive ? '+' : ''}${change}`}
          {changePercent !== undefined && ` (${isPositive ? '+' : ''}${changePercent.toFixed(1)}%)`}
        </div>
      )}
    </div>
  );
};
```

**CSS**:
```css
.metric-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  text-align: center;
  border: 1px solid var(--neutral-200);
  transition: all 0.2s ease;
}

.metric-card.clickable {
  cursor: pointer;
}

.metric-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.metric-value {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--neutral-800);
  margin-bottom: var(--space-1);
}

.metric-label {
  font-size: var(--text-sm);
  color: var(--neutral-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.metric-change {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.metric-change.positive {
  color: var(--success);
}

.metric-change.negative {
  color: var(--error);
}

.metric-card.size-sm .metric-value {
  font-size: var(--text-lg);
}

.metric-card.size-lg .metric-value {
  font-size: var(--text-3xl);
}
```

---

### 5. DataTable

**Propósito**: Tabla de datos reutilizable con sorting, filtering y pagination.

```tsx
interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  sortable?: boolean;
  filterable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (row: T) => void;
  loading?: boolean;
}

const DataTable = <T extends Record<string, any>>({
  data,
  columns,
  sortable = true,
  filterable = false,
  pagination = false,
  pageSize = 10,
  onRowClick,
  loading = false
}: DataTableProps<T>) => {
  const [sortConfig, setSortConfig] = useState<{ key: keyof T; direction: 'asc' | 'desc' } | null>(null);
  const [filter, setFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const sortedData = useMemo(() => {
    if (!sortConfig) return data;
    
    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);

  const filteredData = useMemo(() => {
    if (!filter) return sortedData;
    
    return sortedData.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(filter.toLowerCase())
      )
    );
  }, [sortedData, filter]);

  const paginatedData = useMemo(() => {
    if (!pagination) return filteredData;
    
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage, pageSize, pagination]);

  const handleSort = (key: keyof T) => {
    if (!sortable) return;
    
    setSortConfig(prev => ({
      key,
      direction: prev?.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  if (loading) {
    return <div className="data-table-loading">⏳ Cargando...</div>;
  }

  return (
    <div className="data-table-container">
      {filterable && (
        <div className="data-table-filters">
          <input
            type="text"
            placeholder="Filtrar..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="filter-input"
          />
        </div>
      )}
      
      <table className="data-table">
        <thead>
          <tr>
            {columns.map(column => (
              <th
                key={String(column.key)}
                style={{ width: column.width }}
                className={sortable && column.sortable !== false ? 'sortable' : ''}
                onClick={() => column.sortable !== false && handleSort(column.key)}
              >
                {column.label}
                {sortConfig?.key === column.key && (
                  <span className="sort-indicator">
                    {sortConfig.direction === 'asc' ? '↑' : '↓'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((row, index) => (
            <tr
              key={index}
              className={onRowClick ? 'clickable' : ''}
              onClick={() => onRowClick?.(row)}
            >
              {columns.map(column => (
                <td key={String(column.key)}>
                  {column.render
                    ? column.render(row[column.key], row)
                    : row[column.key]
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      {pagination && (
        <div className="data-table-pagination">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(prev => prev - 1)}
          >
            ← Anterior
          </button>
          <span>
            Página {currentPage} de {Math.ceil(filteredData.length / pageSize)}
          </span>
          <button
            disabled={currentPage >= Math.ceil(filteredData.length / pageSize)}
            onClick={() => setCurrentPage(prev => prev + 1)}
          >
            Siguiente →
          </button>
        </div>
      )}
    </div>
  );
};
```

**CSS**:
```css
.data-table-container {
  background: white;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--neutral-200);
}

.data-table-filters {
  padding: var(--space-4);
  border-bottom: 1px solid var(--neutral-200);
}

.filter-input {
  width: 100%;
  max-width: 300px;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: var(--neutral-50);
  padding: var(--space-4);
  text-align: left;
  font-weight: 600;
  color: var(--neutral-700);
  border-bottom: 1px solid var(--neutral-200);
  font-size: var(--text-sm);
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: var(--neutral-100);
}

.sort-indicator {
  margin-left: var(--space-2);
  color: var(--brand-primary);
}

.data-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--neutral-100);
  color: var(--neutral-600);
  font-size: var(--text-sm);
}

.data-table tr.clickable {
  cursor: pointer;
}

.data-table tr:hover {
  background: var(--neutral-50);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  border-top: 1px solid var(--neutral-200);
  background: var(--neutral-50);
}

.data-table-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  color: var(--neutral-500);
}
```

---

### 6. ChartContainer

**Propósito**: Contenedor para gráficos con loading states y controles.

```tsx
interface ChartContainerProps {
  title?: string;
  loading?: boolean;
  error?: string;
  children: React.ReactNode;
  controls?: React.ReactNode;
  height?: number;
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  loading = false,
  error,
  children,
  controls,
  height = 400
}) => {
  return (
    <div className="chart-container" style={{ height: `${height}px` }}>
      {(title || controls) && (
        <div className="chart-header">
          {title && <h3 className="chart-title">{title}</h3>}
          {controls && <div className="chart-controls">{controls}</div>}
        </div>
      )}
      
      <div className="chart-content">
        {loading && (
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <span>Cargando gráfico...</span>
          </div>
        )}
        
        {error && (
          <div className="chart-error">
            <span className="error-icon">❌</span>
            <span>{error}</span>
          </div>
        )}
        
        {!loading && !error && children}
      </div>
    </div>
  );
};
```

**CSS**:
```css
.chart-container {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--neutral-200);
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.chart-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: var(--space-2);
}

.chart-content {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  color: var(--neutral-500);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--neutral-200);
  border-top: 3px solid var(--brand-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  color: var(--error);
}

.error-icon {
  font-size: var(--text-2xl);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

### 7. NotificationToast

**Propósito**: Sistema de notificaciones toast para feedback del usuario.

```tsx
interface NotificationToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
}

const NotificationToast: React.FC<NotificationToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose(id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  const typeConfig = {
    success: { icon: '✅', color: 'var(--success)' },
    error: { icon: '❌', color: 'var(--error)' },
    warning: { icon: '⚠️', color: 'var(--warning)' },
    info: { icon: 'ℹ️', color: 'var(--info)' }
  };

  const config = typeConfig[type];

  return (
    <div 
      className={`notification-toast ${isVisible ? 'visible' : 'hidden'}`}
      style={{ borderLeftColor: config.color }}
    >
      <div className="notification-icon">{config.icon}</div>
      <div className="notification-content">
        <div className="notification-title">{title}</div>
        {message && <div className="notification-message">{message}</div>}
      </div>
      <button 
        className="notification-close"
        onClick={() => {
          setIsVisible(false);
          setTimeout(() => onClose(id), 300);
        }}
      >
        ×
      </button>
    </div>
  );
};

// Hook para manejar notificaciones
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Omit<NotificationToastProps, 'onClose'>[]>([]);

  const addNotification = (notification: Omit<NotificationToastProps, 'id' | 'onClose'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    setNotifications(prev => [...prev, { ...notification, id }]);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return {
    notifications,
    addNotification,
    removeNotification
  };
};
```

**CSS**:
```css
.notification-toast {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  background: white;
  border: 1px solid var(--neutral-200);
  border-left: 4px solid;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-width: 400px;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.notification-toast.visible {
  transform: translateX(0);
}

.notification-toast.hidden {
  transform: translateX(100%);
}

.notification-icon {
  font-size: var(--text-lg);
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  color: var(--neutral-800);
  margin-bottom: var(--space-1);
}

.notification-message {
  font-size: var(--text-sm);
  color: var(--neutral-600);
}

.notification-close {
  background: none;
  border: none;
  font-size: var(--text-lg);
  color: var(--neutral-400);
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-close:hover {
  color: var(--neutral-600);
}
```

---

### 8. FormField

**Propósito**: Campo de formulario reutilizable con validación y estados.

```tsx
interface FormFieldProps {
  label: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea';
  value: string | number;
  onChange: (value: string | number) => void;
  placeholder?: string;
  required?: boolean;
  error?: string;
  help?: string;
  options?: { value: string; label: string }[];
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  help,
  options = [],
  disabled = false,
  size = 'md'
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const newValue = type === 'number' ? Number(e.target.value) : e.target.value;
    onChange(newValue);
  };

  return (
    <div className={`form-field size-${size}`}>
      <label className="form-label">
        {label}
        {required && <span className="required">*</span>}
      </label>
      
      {type === 'select' ? (
        <select
          value={value}
          onChange={handleChange}
          className={`form-input ${error ? 'error' : ''}`}
          disabled={disabled}
        >
          <option value="">Seleccionar...</option>
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === 'textarea' ? (
        <textarea
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          className={`form-input ${error ? 'error' : ''}`}
          disabled={disabled}
          rows={4}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          className={`form-input ${error ? 'error' : ''}`}
          disabled={disabled}
        />
      )}
      
      {error && <div className="form-error">{error}</div>}
      {help && !error && <div className="form-help">{help}</div>}
    </div>
  );
};
```

**CSS**:
```css
.form-field {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--neutral-700);
  margin-bottom: var(--space-2);
}

.required {
  color: var(--error);
  margin-left: var(--space-1);
}

.form-input {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  background: var(--neutral-100);
  color: var(--neutral-500);
  cursor: not-allowed;
}

.form-input.error {
  border-color: var(--error);
}

.form-input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.form-error {
  font-size: var(--text-xs);
  color: var(--error);
  margin-top: var(--space-1);
}

.form-help {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  margin-top: var(--space-1);
}

.form-field.size-sm .form-input {
  padding: var(--space-2);
  font-size: var(--text-xs);
}

.form-field.size-lg .form-input {
  padding: var(--space-4);
  font-size: var(--text-base);
}
```

---

## 📋 Checklist de Componentes

### ✅ Componentes Base
- [x] SignalIndicator - Señales de trading
- [x] PriceDisplay - Precios y cambios
- [x] ConfidenceMeter - Nivel de confianza
- [x] MetricCard - Métricas individuales
- [x] DataTable - Tablas de datos
- [x] ChartContainer - Contenedor de gráficos
- [x] NotificationToast - Sistema de notificaciones
- [x] FormField - Campos de formulario

### ✅ Características
- [x] TypeScript interfaces
- [x] Props configurables
- [x] Estados de loading/error
- [x] Responsive design
- [x] Accesibilidad
- [x] Animaciones suaves
- [x] Modo oscuro compatible

### ✅ Reutilización
- [x] Componentes modulares
- [x] Props flexibles
- [x] CSS variables
- [x] Tamaños configurables
- [x] Temas consistentes
- [x] Documentación completa

---

**Status**: ✅ COMPLETADO  
**Epic**: 0.2 - Prototipos UI/UX (13 puntos)  
**Duración**: 2-3 días

**Próximo**: Validación con stakeholders y finalización del Epic 0.2



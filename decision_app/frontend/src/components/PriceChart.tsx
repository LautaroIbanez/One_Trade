import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, ReferenceDot } from 'recharts';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

interface PriceDataPoint {
  timestamp: string;
  date: string;
  price: number;
  signal?: 'BUY' | 'SELL' | null;
}

interface PriceChartProps {
  data: PriceDataPoint[];
  symbol: string;
  currentPrice?: number;
  entryLong?: { min: number; max: number };
  entryShort?: { min: number; max: number };
  takeProfitLong?: number;
  stopLossLong?: number;
  takeProfitShort?: number;
  stopLossShort?: number;
}

const PriceChart: React.FC<PriceChartProps> = ({
  data,
  symbol,
  currentPrice,
  entryLong,
  entryShort,
  takeProfitLong,
  stopLossLong,
  takeProfitShort,
  stopLossShort
}) => {
  const formatPrice = (value: number) => {
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-sm">{formatDate(label)}</p>
          <p className="text-sm">
            <span className="font-medium">Price:</span> {formatPrice(data.price)}
          </p>
          {data.signal && (
            <p className={`text-sm font-semibold ${data.signal === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
              {data.signal === 'BUY' ? '▲ BUY Signal' : '▼ SELL Signal'}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const renderSignalDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (payload.signal === 'BUY') {
      return (
        <circle cx={cx} cy={cy} r={6} fill="#10b981" stroke="#fff" strokeWidth={2} />
      );
    } else if (payload.signal === 'SELL') {
      return (
        <circle cx={cx} cy={cy} r={6} fill="#ef4444" stroke="#fff" strokeWidth={2} />
      );
    }
    return null;
  };

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold">{symbol} Price Chart</h3>
        </div>
        {currentPrice && (
          <div className="text-right">
            <div className="text-sm text-gray-600">Current Price</div>
            <div className="text-xl font-bold">{formatPrice(currentPrice)}</div>
          </div>
        )}
      </div>

      <div className="w-full h-80 bg-white rounded-lg border border-gray-200 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              tickFormatter={formatPrice}
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              domain={['dataMin - 100', 'dataMax + 100']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />
            
            {/* Current price line */}
            {currentPrice && (
              <ReferenceLine 
                y={currentPrice} 
                stroke="#3b82f6" 
                strokeDasharray="5 5"
                label={{ value: 'Current', position: 'right', fill: '#3b82f6', fontSize: 12 }}
              />
            )}

            {/* LONG entry range */}
            {entryLong && (
              <>
                <ReferenceLine 
                  y={entryLong.min} 
                  stroke="#10b981" 
                  strokeDasharray="3 3"
                  strokeOpacity={0.5}
                />
                <ReferenceLine 
                  y={entryLong.max} 
                  stroke="#10b981" 
                  strokeDasharray="3 3"
                  strokeOpacity={0.5}
                  label={{ value: 'LONG Entry', position: 'right', fill: '#10b981', fontSize: 11 }}
                />
              </>
            )}

            {/* SHORT entry range */}
            {entryShort && (
              <>
                <ReferenceLine 
                  y={entryShort.min} 
                  stroke="#ef4444" 
                  strokeDasharray="3 3"
                  strokeOpacity={0.5}
                />
                <ReferenceLine 
                  y={entryShort.max} 
                  stroke="#ef4444" 
                  strokeDasharray="3 3"
                  strokeOpacity={0.5}
                  label={{ value: 'SHORT Entry', position: 'right', fill: '#ef4444', fontSize: 11 }}
                />
              </>
            )}

            {/* Take Profit and Stop Loss */}
            {takeProfitLong && (
              <ReferenceLine 
                y={takeProfitLong} 
                stroke="#059669" 
                strokeWidth={2}
                label={{ value: 'TP Long', position: 'right', fill: '#059669', fontSize: 10 }}
              />
            )}
            {stopLossLong && (
              <ReferenceLine 
                y={stopLossLong} 
                stroke="#dc2626" 
                strokeWidth={2}
                label={{ value: 'SL Long', position: 'right', fill: '#dc2626', fontSize: 10 }}
              />
            )}

            <Line
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={renderSignalDot}
              name="Price"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Legend for entry/exit levels */}
      <div className="grid grid-cols-2 gap-4 text-xs">
        {entryLong && (
          <div className="bg-green-50 p-3 rounded border border-green-200">
            <div className="flex items-center space-x-1 mb-1">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="font-semibold text-green-800">LONG Entry Range</span>
            </div>
            <div className="text-green-700">
              {formatPrice(entryLong.min)} - {formatPrice(entryLong.max)}
            </div>
            {takeProfitLong && (
              <div className="text-green-700 mt-1">
                TP: {formatPrice(takeProfitLong)}
              </div>
            )}
            {stopLossLong && (
              <div className="text-red-700 mt-1">
                SL: {formatPrice(stopLossLong)}
              </div>
            )}
          </div>
        )}

        {entryShort && (
          <div className="bg-red-50 p-3 rounded border border-red-200">
            <div className="flex items-center space-x-1 mb-1">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="font-semibold text-red-800">SHORT Entry Range</span>
            </div>
            <div className="text-red-700">
              {formatPrice(entryShort.min)} - {formatPrice(entryShort.max)}
            </div>
            {takeProfitShort && (
              <div className="text-green-700 mt-1">
                TP: {formatPrice(takeProfitShort)}
              </div>
            )}
            {stopLossShort && (
              <div className="text-red-700 mt-1">
                SL: {formatPrice(stopLossShort)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceChart;


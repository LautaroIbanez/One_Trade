import React from 'react';
import { TradingLevels } from '../types/recommendations';
import { TrendingUp, Target, ShieldAlert, ArrowRight } from 'lucide-react';

interface TradePlanSummaryProps {
  recommendation: string;
  currentPrice: number;
  tradingLevels?: TradingLevels;
  entryPrice?: number;
  takeProfitTargets?: number[];
  stopLoss?: number;
}

const TradePlanSummary: React.FC<TradePlanSummaryProps> = ({ recommendation, currentPrice, tradingLevels, entryPrice, takeProfitTargets, stopLoss }) => {
  const isBuyRecommendation = recommendation.includes('BUY');
  const isSellRecommendation = recommendation.includes('SELL');
  const isHold = recommendation === 'HOLD';

  const getEntryPrice = () => {
    if (entryPrice) return entryPrice;
    if (tradingLevels) {
      if (isBuyRecommendation && tradingLevels.entry_long) {
        return (tradingLevels.entry_long.min + tradingLevels.entry_long.max) / 2;
      }
      if (isSellRecommendation && tradingLevels.entry_short) {
        return (tradingLevels.entry_short.min + tradingLevels.entry_short.max) / 2;
      }
    }
    return currentPrice;
  };

  const getTakeProfit = () => {
    if (takeProfitTargets && takeProfitTargets.length > 0) return takeProfitTargets;
    if (tradingLevels) {
      if (isBuyRecommendation && tradingLevels.take_profit_long) {
        return [tradingLevels.take_profit_long];
      }
      if (isSellRecommendation && tradingLevels.take_profit_short) {
        return [tradingLevels.take_profit_short];
      }
    }
    return null;
  };

  const getStopLoss = () => {
    if (stopLoss) return stopLoss;
    if (tradingLevels) {
      if (isBuyRecommendation && tradingLevels.stop_loss_long) {
        return tradingLevels.stop_loss_long;
      }
      if (isSellRecommendation && tradingLevels.stop_loss_short) {
        return tradingLevels.stop_loss_short;
      }
    }
    return null;
  };

  const entry = getEntryPrice();
  const tpTargets = getTakeProfit();
  const sl = getStopLoss();

  if (isHold || (!tpTargets && !sl)) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-gray-600" />
          Plan de Operación
        </h3>
        <div className="text-center py-8">
          <p className="text-gray-600 text-lg">Espera la mejor oportunidad</p>
          <p className="text-gray-500 text-sm mt-2">No hay una señal clara en este momento. Mantén tu capital seguro.</p>
        </div>
      </div>
    );
  }

  const calculateRiskReward = () => {
    if (!entry || !tpTargets || !sl) return null;
    const avgTP = tpTargets.reduce((sum, tp) => sum + tp, 0) / tpTargets.length;
    const risk = Math.abs(entry - sl);
    const reward = Math.abs(avgTP - entry);
    return (reward / risk).toFixed(2);
  };

  const riskReward = calculateRiskReward();

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        Tu Plan de Operación - Paso a Paso
      </h3>
      <div className="space-y-4">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">1</div>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 mb-1">Entra {isBuyRecommendation ? 'comprando' : 'vendiendo'}</h4>
            <p className="text-gray-700">Precio de entrada: <span className="font-bold text-blue-600">${entry.toFixed(2)}</span></p>
            {tradingLevels && ((isBuyRecommendation && tradingLevels.entry_long) || (isSellRecommendation && tradingLevels.entry_short)) && (
              <p className="text-sm text-gray-600 mt-1">Rango sugerido: ${((isBuyRecommendation ? tradingLevels.entry_long?.min : tradingLevels.entry_short?.min) || 0).toFixed(2)} - ${((isBuyRecommendation ? tradingLevels.entry_long?.max : tradingLevels.entry_short?.max) || 0).toFixed(2)}</p>
            )}
          </div>
        </div>
        <div className="ml-4 border-l-2 border-blue-300 pl-4 py-2">
          <ArrowRight className="w-5 h-5 text-blue-400" />
        </div>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold">2</div>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
              <Target className="w-4 h-4 text-green-600" />
              Toma ganancias (TP)
            </h4>
            {tpTargets && tpTargets.map((tp, idx) => {
              const profit = ((Math.abs(tp - entry) / entry) * 100).toFixed(2);
              return (
                <p key={idx} className="text-gray-700 mt-1">
                  {tpTargets.length > 1 ? `Objetivo ${idx + 1}: ` : ''}
                  <span className="font-bold text-green-600">${tp.toFixed(2)}</span>
                  <span className="text-sm text-green-700 ml-2">(+{profit}%)</span>
                </p>
              );
            })}
          </div>
        </div>
        <div className="ml-4 border-l-2 border-blue-300 pl-4 py-2">
          <ArrowRight className="w-5 h-5 text-blue-400" />
        </div>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center font-bold">3</div>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              Protege tu capital (SL)
            </h4>
            {sl && (
              <p className="text-gray-700">
                Stop Loss: <span className="font-bold text-red-600">${sl.toFixed(2)}</span>
                <span className="text-sm text-red-700 ml-2">(-{((Math.abs(entry - sl) / entry) * 100).toFixed(2)}%)</span>
              </p>
            )}
          </div>
        </div>
        {riskReward && (
          <div className="mt-6 p-4 bg-white rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600">Relación Riesgo/Beneficio</p>
            <p className="text-2xl font-bold text-blue-600">1:{riskReward}</p>
            <p className="text-xs text-gray-500 mt-1">Por cada $1 que arriesgas, puedes ganar ${riskReward}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradePlanSummary;


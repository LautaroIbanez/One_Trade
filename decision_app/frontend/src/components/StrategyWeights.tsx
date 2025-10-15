import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, Settings } from 'lucide-react';

interface StrategyWeights {
  [key: string]: number;
}

const StrategyWeights: React.FC = () => {
  const [weights, setWeights] = useState<StrategyWeights>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const fetchWeights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/enhanced-recommendations/strategy-weights');
      const data = await response.json();
      setWeights(data);
    } catch (err) {
      setError('Error fetching strategy weights');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateWeights = async (newWeights: StrategyWeights) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/enhanced-recommendations/strategy-weights', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ weights: newWeights }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setWeights(data.weights);
        setIsEditing(false);
      } else {
        throw new Error('Failed to update weights');
      }
    } catch (err) {
      setError('Error updating strategy weights');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleWeightChange = (strategy: string, value: number) => {
    setWeights(prev => ({
      ...prev,
      [strategy]: value
    }));
  };

  const handleSave = () => {
    // Validate that weights sum to 1.0
    const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    if (Math.abs(totalWeight - 1.0) > 0.01) {
      setError(`Weights must sum to 1.0, current sum: ${totalWeight.toFixed(3)}`);
      return;
    }
    
    updateWeights(weights);
  };

  const resetToDefaults = () => {
    const defaultWeights = {
      "RSI Strategy": 0.4,
      "MACD Strategy": 0.4,
      "Bollinger Bands Strategy": 0.2
    };
    setWeights(defaultWeights);
  };

  useEffect(() => {
    fetchWeights();
  }, []);

  if (loading && Object.keys(weights).length === 0) {
    return (
      <div className="flex items-center justify-center p-4">
        <RefreshCw className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading strategy weights...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Strategy Weights</h3>
        <div className="flex space-x-2">
          {!isEditing ? (
            <Button onClick={() => setIsEditing(true)} size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Edit
            </Button>
          ) : (
            <>
              <Button onClick={handleSave} size="sm" disabled={loading}>
                Save
              </Button>
              <Button onClick={() => setIsEditing(false)} size="sm" variant="outline">
                Cancel
              </Button>
            </>
          )}
          <Button onClick={resetToDefaults} size="sm" variant="outline">
            Reset
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-100 border border-red-300 rounded-md">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      <div className="space-y-3">
        {Object.entries(weights).map(([strategy, weight]) => (
          <div key={strategy} className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex-1">
              <label className="text-sm font-medium">{strategy}</label>
              <div className="text-xs text-gray-500">
                Current weight: {(weight * 100).toFixed(1)}%
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {isEditing ? (
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={weight}
                  onChange={(e) => handleWeightChange(strategy, parseFloat(e.target.value))}
                  className="w-24"
                />
              ) : (
                <div className="w-24 h-2 bg-gray-200 rounded-full">
                  <div 
                    className="h-2 bg-blue-500 rounded-full" 
                    style={{ width: `${weight * 100}%` }}
                  />
                </div>
              )}
              <span className="text-sm font-medium w-12 text-right">
                {(weight * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {isEditing && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-blue-700 text-sm">
            <strong>Total:</strong> {(Object.values(weights).reduce((sum, weight) => sum + weight, 0) * 100).toFixed(1)}%
            {Math.abs(Object.values(weights).reduce((sum, weight) => sum + weight, 0) - 1.0) > 0.01 && (
              <span className="text-red-600 ml-2">(Must equal 100%)</span>
            )}
          </p>
        </div>
      )}
    </div>
  );
};

export default StrategyWeights;

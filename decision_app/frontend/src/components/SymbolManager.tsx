import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, Plus, X } from 'lucide-react';

interface SymbolManagerProps {
  onSymbolsChange?: (symbols: string[]) => void;
}

const SymbolManager: React.FC<SymbolManagerProps> = ({ onSymbolsChange }) => {
  const [supportedSymbols, setSupportedSymbols] = useState<string[]>([]);
  const [newSymbol, setNewSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSupportedSymbols = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols');
      const data = await response.json();
      setSupportedSymbols(data);
      if (onSymbolsChange) {
        onSymbolsChange(data);
      }
    } catch (err) {
      setError('Error fetching supported symbols');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const addSymbol = async (symbol: string) => {
    if (!symbol.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols/${symbol.toUpperCase()}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        setNewSymbol('');
        fetchSupportedSymbols();
      } else {
        throw new Error('Failed to add symbol');
      }
    } catch (err) {
      setError(`Error adding symbol ${symbol}`);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const removeSymbol = async (symbol: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols/${symbol}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        fetchSupportedSymbols();
      } else {
        throw new Error('Failed to remove symbol');
      }
    } catch (err) {
      setError(`Error removing symbol ${symbol}`);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSymbol = () => {
    if (newSymbol.trim()) {
      addSymbol(newSymbol.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddSymbol();
    }
  };

  useEffect(() => {
    fetchSupportedSymbols();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Supported Symbols</h3>
        <Button onClick={fetchSupportedSymbols} size="sm" disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-red-100 border border-red-300 rounded-md">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Add new symbol */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter symbol (e.g., SOLUSDT)"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <Button onClick={handleAddSymbol} disabled={loading || !newSymbol.trim()}>
          <Plus className="h-4 w-4 mr-2" />
          Add
        </Button>
      </div>

      {/* Supported symbols list */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700">Current Symbols:</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {supportedSymbols.map((symbol) => (
            <div key={symbol} className="flex items-center justify-between p-2 border rounded-md bg-gray-50">
              <span className="text-sm font-medium">{symbol}</span>
              <Button
                onClick={() => removeSymbol(symbol)}
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                disabled={loading}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      </div>

      {supportedSymbols.length === 0 && !loading && (
        <div className="text-center py-4 text-gray-500">
          <p>No supported symbols found</p>
        </div>
      )}
    </div>
  );
};

export default SymbolManager;

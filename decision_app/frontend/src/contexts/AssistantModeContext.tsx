import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AssistantModeContextType {
  isAssistantMode: boolean;
  toggleAssistantMode: () => void;
  setAssistantMode: (enabled: boolean) => void;
}

const AssistantModeContext = createContext<AssistantModeContextType | undefined>(undefined);

export const AssistantModeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAssistantMode, setIsAssistantMode] = useState(false);

  const toggleAssistantMode = () => {
    setIsAssistantMode(prev => !prev);
  };

  const setAssistantMode = (enabled: boolean) => {
    setIsAssistantMode(enabled);
  };

  return (
    <AssistantModeContext.Provider value={{ isAssistantMode, toggleAssistantMode, setAssistantMode }}>
      {children}
    </AssistantModeContext.Provider>
  );
};

export const useAssistantMode = () => {
  const context = useContext(AssistantModeContext);
  if (context === undefined) {
    throw new Error('useAssistantMode must be used within an AssistantModeProvider');
  }
  return context;
};


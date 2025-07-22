import React, { createContext, useContext, Children } from "react";
import type { ReactNode } from "react";

// Context type
type ApiUrlContextType = {
  apiUrl: string;
};

// Create context
export const ApiUrlContext = createContext<ApiUrlContextType | undefined>(undefined);

// Provider props
type ApiUrlProviderProps = {
  apiUrl: string;
  children: ReactNode;
};

export const ApiUrlProvider: React.FC<ApiUrlProviderProps> = ({
  apiUrl,
  children,
}) => {
  return (
    <ApiUrlContext.Provider value={{ apiUrl }}>
      {children}
    </ApiUrlContext.Provider>
  );
};

export const useApiUrl = (): string => {
  const context = useContext(ApiUrlContext);
  if (!context) {
    throw new Error("useApiUrl must be used within an ApiUrlProvider");
  }
  return context.apiUrl;
};
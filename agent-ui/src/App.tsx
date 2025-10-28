import React from 'react';
import { AppProvider } from './context/AppContext';
import DashboardLayout from './components/layout/DashboardLayout';

function App() {
  return (
    <AppProvider>
      <DashboardLayout />
    </AppProvider>
  );
}

export default App;

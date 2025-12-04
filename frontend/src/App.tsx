import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import InputsPage from './pages/InputsPage';
import ScenariosPage from './pages/ScenariosPage';
import ReportsPage from './pages/ReportsPage';
import SalemReportPage from './pages/SalemReportPage';
import MonteCarloAnalyticsPage from './pages/MonteCarloAnalyticsPage';
import PresentationMode from './presentation/PresentationMode';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* Salem Report - Full page without layout */}
        <Route path="/salem-report" element={<SalemReportPage />} />
        <Route path="/salem-report/:planId" element={<SalemReportPage />} />
        
        {/* Presentation Mode - Full screen without layout */}
        <Route path="/presentation" element={<PresentationMode />} />
        
        {/* Regular app routes with layout */}
        <Route path="/*" element={
          <AppLayout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/inputs" element={<InputsPage />} />
              <Route path="/scenarios" element={<ScenariosPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/analytics" element={<MonteCarloAnalyticsPage />} />
            </Routes>
          </AppLayout>
        } />
      </Routes>
    </Router>
  );
}

export default App;

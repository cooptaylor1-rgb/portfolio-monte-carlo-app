import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import InputsPage from './pages/InputsPage';
import ScenariosPage from './pages/ScenariosPage';
import ReportsPage from './pages/ReportsPage';
import './index.css';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/inputs" element={<InputsPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;

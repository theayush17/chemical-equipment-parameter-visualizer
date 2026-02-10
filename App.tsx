
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, PieChart, Pie
} from 'recharts';

// Types
interface EquipmentSummary {
  id: number;
  filename: string;
  total_count: number;
  avg_flowrate: number;
  avg_pressure: number;
  avg_temperature: number;
  type_distribution: Record<string, number>;
  timestamp: string;
}

const API_BASE_URL = 'http://localhost:8000/api';

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [apiError, setApiError] = useState('');
  const [history, setHistory] = useState<EquipmentSummary[]>([]);
  const [currentData, setCurrentData] = useState<EquipmentSummary | null>(null);
  const [uploading, setUploading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  // Auth Header Generation
  const getAuthHeader = useCallback(() => {
    try {
      const token = btoa(`${username}:${password}`);
      return { Authorization: `Basic ${token}` };
    } catch (e) {
      console.error("Failed to encode credentials", e);
      return {};
    }
  }, [username, password]);

  const fetchHistory = useCallback(async () => {
    setApiError('');
    try {
      const response = await axios.get(`${API_BASE_URL}/history/`, {
        headers: getAuthHeader(),
        timeout: 5000 // 5 second timeout for better responsiveness
      });
      setHistory(response.data);
    } catch (err: any) {
      console.error('Failed to fetch history', err);
      if (err.message === 'Network Error') {
        setApiError('Network Error: Unable to connect to the backend server at ' + API_BASE_URL + '. Please ensure the Django server is running.');
      } else if (err.response?.status === 401) {
        setApiError('Session expired. Please log in again.');
        setIsLoggedIn(false);
      } else {
        setApiError(err.response?.data?.error || err.message || 'An unexpected error occurred.');
      }
    }
  }, [getAuthHeader]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setAuthError('Please enter both username and password.');
      return;
    }

    setIsValidating(true);
    setAuthError('');
    
    try {
      // Validate credentials by attempting a simple GET request
      await axios.get(`${API_BASE_URL}/history/`, {
        headers: {
          Authorization: `Basic ${btoa(`${username}:${password}`)}`
        },
        timeout: 5000
      });
      
      setIsLoggedIn(true);
      setAuthError('');
    } catch (err: any) {
      console.error('Login validation failed', err);
      if (err.message === 'Network Error') {
        setAuthError('Network Error: Cannot reach server. Is the backend running on port 8000?');
      } else if (err.response?.status === 401) {
        setAuthError('Invalid username or password.');
      } else {
        setAuthError(err.response?.data?.error || 'Connection failed.');
      }
    } finally {
      setIsValidating(false);
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      fetchHistory();
    }
  }, [isLoggedIn, fetchHistory]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setApiError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'multipart/form-data'
        }
      });
      setCurrentData(response.data);
      fetchHistory();
    } catch (err: any) {
      setApiError(err.response?.data?.error || err.message || 'Upload failed');
    } finally {
      setUploading(false);
      // Reset input
      e.target.value = '';
    }
  };

  const downloadReport = (id: number) => {
    const url = `${API_BASE_URL}/report/${id}/?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
    window.open(url, '_blank');
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
        <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md border border-gray-200">
          <h1 className="text-2xl font-bold mb-6 text-indigo-700 text-center uppercase tracking-wider">
            Chemical Visualizer
          </h1>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Username</label>
              <input
                type="text"
                disabled={isValidating}
                className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input
                type="password"
                disabled={isValidating}
                className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-indigo-500 focus:border-indigo-500"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {authError && (
              <div className="bg-red-50 border-l-4 border-red-500 p-3">
                <p className="text-red-700 text-sm">{authError}</p>
              </div>
            )}
            <button
              type="submit"
              disabled={isValidating}
              className={`w-full bg-indigo-600 text-white py-2 rounded-md transition font-semibold ${
                isValidating ? 'opacity-50 cursor-not-allowed' : 'hover:bg-indigo-700'
              }`}
            >
              {isValidating ? 'Connecting...' : 'Sign In'}
            </button>
          </form>
          <div className="mt-6 border-t pt-4">
            <p className="text-xs text-gray-500 text-center mb-2">Technical Requirements:</p>
            <ul className="text-[10px] text-gray-400 list-disc list-inside space-y-1">
              <li>Django Backend must be running at http://localhost:8000</li>
              <li>CORS must be enabled in Django settings</li>
              <li>Default credentials: admin / admin (after createsuperuser)</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  const pieData = currentData 
    ? Object.entries(currentData.type_distribution).map(([name, value]) => ({ name, value }))
    : [];

  const avgData = currentData ? [
    { name: 'Flowrate', value: currentData.avg_flowrate },
    { name: 'Pressure', value: currentData.avg_pressure },
    { name: 'Temperature', value: currentData.avg_temperature },
  ] : [];

  const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <h1 className="text-xl font-bold text-indigo-700">ChemVis Dashboard</h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600 hidden sm:inline">User: <strong>{username}</strong></span>
          <button 
            onClick={() => setIsLoggedIn(false)}
            className="text-sm bg-gray-100 px-3 py-1 rounded-md text-gray-600 hover:bg-gray-200 transition"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-8">
        {apiError && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-red-700 text-sm font-medium">{apiError}</p>
              <button 
                onClick={fetchHistory}
                className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded hover:bg-red-200"
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}

        {/* Upload Section */}
        <section className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h2 className="text-lg font-semibold mb-4 text-gray-800">New Dataset Upload</h2>
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <div className="relative flex-1 w-full">
              <input 
                type="file" 
                accept=".csv"
                onChange={handleFileUpload}
                disabled={uploading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer disabled:opacity-50"
              />
            </div>
            {uploading && (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-indigo-600 text-sm font-medium">Processing Data...</span>
              </div>
            )}
          </div>
        </section>

        {/* Dashboard Grid */}
        {currentData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in duration-500">
            <StatCard label="Total Equipment" value={currentData.total_count.toString()} icon="📦" />
            <StatCard label="Avg Flowrate" value={`${currentData.avg_flowrate.toFixed(2)} m³/h`} icon="💧" />
            <StatCard label="Avg Pressure" value={`${currentData.avg_pressure.toFixed(2)} bar`} icon="🌪️" />
            <StatCard label="Avg Temp" value={`${currentData.avg_temperature.toFixed(2)} °C`} icon="🔥" />
          </div>
        ) : (
          !apiError && (
            <div className="text-center py-10 bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl">
              <p className="text-gray-400">Upload a CSV file to see statistics and visualizations</p>
            </div>
          )
        )}

        {/* Visualizations */}
        {currentData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in slide-in-from-bottom-4 duration-700">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-md font-semibold mb-4 text-gray-700">Equipment Type Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-md font-semibold mb-4 text-gray-700">Averages Benchmark</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={avgData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip cursor={{fill: '#f3f4f6'}} />
                    <Bar dataKey="value" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* History Table */}
        <section className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-800">Recent Upload History (Max 5)</h2>
            <button 
              onClick={fetchHistory}
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center space-x-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Refresh</span>
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-gray-600 font-medium">
                <tr>
                  <th className="px-6 py-3">File Name</th>
                  <th className="px-6 py-3">Count</th>
                  <th className="px-6 py-3">Avg Flow</th>
                  <th className="px-6 py-3">Timestamp</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 font-medium text-gray-800">{item.filename}</td>
                    <td className="px-6 py-4">{item.total_count}</td>
                    <td className="px-6 py-4">{item.avg_flowrate.toFixed(2)}</td>
                    <td className="px-6 py-4 text-gray-500">
                      {new Date(item.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        onClick={() => downloadReport(item.id)}
                        className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-md text-xs font-bold hover:bg-indigo-100 transition"
                        title="Download PDF Report"
                      >
                        PDF
                      </button>
                    </td>
                  </tr>
                ))}
                {history.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-400 italic">
                      {apiError ? 'Could not load history due to network error.' : 'No upload history found.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
      
      <footer className="p-4 text-center text-xs text-gray-400 bg-white border-t border-gray-100">
        &copy; {new Date().getFullYear()} Chemical Equipment Parameter Visualizer
      </footer>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: string; icon: string }> = ({ label, value, icon }) => (
  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center space-x-4 transition hover:shadow-md">
    <div className="text-3xl bg-indigo-50 w-12 h-12 flex items-center justify-center rounded-lg">{icon}</div>
    <div>
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-xl font-bold text-gray-800">{value}</p>
    </div>
  </div>
);

export default App;

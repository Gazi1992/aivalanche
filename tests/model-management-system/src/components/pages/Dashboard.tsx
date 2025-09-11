import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, Clock, Target, AlertCircle, CheckCircle, BarChart2, LineChart,
  Database, FileText, TestTube, Calendar, XCircle, Download
} from 'lucide-react';
import Plot from 'react-plotly.js';
import dataService from '../../services/dataService';
import { useAuth } from '../../contexts/AuthContext';
import { Card, Badge } from '../ui';
import { PageHeader } from '../layout';
import { statsCardStyles } from '../../theme';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const stats = dataService.getStatistics();
  const allRequests = dataService.getModelRequests();
  const calibratedModels = dataService.getCalibratedModels();
  const [chartType, setChartType] = useState<'bar' | 'line'>('line');
  const [timeRange, setTimeRange] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [calibrationData, setCalibrationData] = useState<any[]>([]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const plotRef = useRef<any>(null);
  
  const handleSaveChart = () => {
    if (plotRef.current && plotRef.current.el) {
      // Create a temporary link element to download the image
      const plotElement = plotRef.current.el;
      
      // @ts-ignore - Plotly is available on window when react-plotly.js is loaded
      if (window.Plotly) {
        // @ts-ignore
        window.Plotly.downloadImage(plotElement, {
          format: 'png',
          filename: `calibration-trends-${timeRange}-${new Date().toISOString().split('T')[0]}`,
          height: 600,
          width: 1200
        });
      }
    }
  };
  
  // Filter requests based on user
  const requests = user ? allRequests.filter(req => 
    user.role === 'admin' || 
    req.requester === user.name ||
    user.preferences.recentProjects.includes(req.request_id)
  ) : allRequests;

  // Calculate key metrics first
  const totalCalibratedModels = stats.libraryStats.calibratedModels;
  const inProgressModels = calibratedModels.filter(model => model.status === 'in-progress').length;
  
  // User-specific metrics (when user is logged in)
  const userCalibratedModels = user ? user.statistics.modelsCreated : 0;
  const userCurrentMonthCalibrations = user ? Math.floor(user.statistics.modelsCreated * 0.4) : 0; // Simulate current month data
  const userLastMonthCalibrations = user ? Math.floor(user.statistics.modelsCreated * 0.3) : 0; // Simulate last month data
  const userInProgressModels = user ? calibratedModels.filter(model => model.status === 'in-progress' && model.calibration_info.engineer === user.name).length : 0;

  // Load and process calibration data
  useEffect(() => {
    // Load calibration data from CSV file
    fetch('/data/calibration-trends.csv')
      .then(response => response.text())
      .then(csvText => {
        // Parse CSV
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        const rawData = lines.slice(1).map(line => {
          const values = line.split(',');
          const row: any = {};
          headers.forEach((header, index) => {
            if (header === 'date') {
              row[header] = values[index];
            } else {
              row[header] = parseInt(values[index]) || 0;
            }
          });
          return row;
        });
        processCalibrationData(rawData);
      })
      .catch(error => {
        console.error('Error loading calibration data:', error);
        // Fallback to some default data if CSV fails to load
        const fallbackData = generateFallbackData();
        processCalibrationData(fallbackData);
      });
  }, [timeRange, user]);

  const generateFallbackData = () => {
    // Generate 6 months of realistic data with many zero days
    const data = [];
    const startDate = new Date('2025-03-01');
    const endDate = new Date('2025-08-20');
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      const dateStr = d.toISOString().split('T')[0];
      const dayOfWeek = d.getDay();
      
      // Weekends have 90% chance of 0 models
      // Weekdays have 60% chance of 0 models
      const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
      const zeroChance = isWeekend ? 0.9 : 0.6;
      
      if (Math.random() < zeroChance) {
        data.push({
          date: dateStr,
          total_models: 0,
          john_doe: 0,
          jane_smith: 0,
          bob_wilson: 0,
          alice_johnson: 0
        });
      } else {
        // Generate non-zero data
        const total = Math.floor(Math.random() * 8) + 1;
        const engineers = ['john_doe', 'jane_smith', 'bob_wilson', 'alice_johnson'];
        const distribution: any = { john_doe: 0, jane_smith: 0, bob_wilson: 0, alice_johnson: 0 };
        
        // Distribute models randomly among engineers
        let remaining = total;
        while (remaining > 0) {
          const engineer = engineers[Math.floor(Math.random() * engineers.length)];
          const amount = Math.min(remaining, Math.floor(Math.random() * 3) + 1);
          distribution[engineer] += amount;
          remaining -= amount;
        }
        
        data.push({
          date: dateStr,
          total_models: total,
          ...distribution
        });
      }
    }
    
    return data;
  };

  const processCalibrationData = (rawData: any[]) => {

    // Process data based on time range
    if (timeRange === 'daily') {
      // Show last 90 days of data (3 months)
      const dailyData = rawData.slice(-90).map(row => {
        const date = new Date(row.date);
        const userColumn = user?.name?.toLowerCase().replace(' ', '.').replace('.', '_') || '';
        return {
          month: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          models: row.total_models,
          userModels: user ? (row[userColumn as keyof typeof row] as number || 0) : 0
        };
      });
      setCalibrationData(dailyData);
    } else if (timeRange === 'weekly') {
      // Aggregate into weekly data
      const weeklyData: any = {};
      const userColumn = user?.name?.toLowerCase().replace(' ', '.').replace('.', '_') || '';
      
      // Group by week
      rawData.forEach(row => {
        const date = new Date(row.date);
        const weekStart = new Date(date);
        weekStart.setDate(date.getDate() - date.getDay()); // Start of week (Sunday)
        const weekKey = weekStart.toISOString().split('T')[0];
        
        if (!weeklyData[weekKey]) {
          weeklyData[weekKey] = { 
            models: 0, 
            userModels: 0,
            date: weekStart
          };
        }
        weeklyData[weekKey].models += row.total_models;
        weeklyData[weekKey].userModels += user ? ((row[userColumn as keyof typeof row] as number) || 0) : 0;
      });
      
      // Sort weeks and format for display
      const sortedWeeks = Object.entries(weeklyData)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([_, data]: [string, any]) => ({
          month: data.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          models: data.models,
          userModels: data.userModels
        }));
      
      // Show last 52 weeks (1 year) or all weeks if less than 52
      const weeksToShow = Math.min(sortedWeeks.length, 52);
      setCalibrationData(sortedWeeks.slice(-weeksToShow));
    } else {
      // Monthly aggregation
      const monthlyData: any = {};
      rawData.forEach(row => {
        const month = new Date(row.date).toLocaleDateString('en-US', { month: 'short' });
        if (!monthlyData[month]) {
          monthlyData[month] = { models: 0, userModels: 0 };
        }
        const userColumn = user?.name?.toLowerCase().replace(' ', '.').replace('.', '_') || '';
        monthlyData[month].models += row.total_models;
        monthlyData[month].userModels += user ? ((row[userColumn as keyof typeof row] as number) || 0) : 0;
      });
      
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const currentMonth = new Date().getMonth();
      const sortedMonths = [];
      for (let i = 11; i >= 0; i--) {
        const monthIndex = (currentMonth - i + 12) % 12;
        const monthName = months[monthIndex];
        if (monthlyData[monthName]) {
          sortedMonths.push({
            month: monthName,
            models: monthlyData[monthName].models,
            userModels: monthlyData[monthName].userModels
          });
        }
      }
      setCalibrationData(sortedMonths);
    }
  };

  const currentMonthCalibrations = calibrationData[calibrationData.length - 1]?.models || 0;
  const lastMonthCalibrations = calibrationData[calibrationData.length - 2]?.models || 0;
  const monthChange = currentMonthCalibrations - lastMonthCalibrations;
  const userMonthChange = userCurrentMonthCalibrations - userLastMonthCalibrations;
  
  // View state
  const [viewMode, setViewMode] = useState<'global' | 'personal'>('global');

  // Handle smooth transitions
  const handleTimeRangeChange = (newRange: 'daily' | 'weekly' | 'monthly') => {
    setIsTransitioning(true);
    setTimeout(() => {
      setTimeRange(newRange);
      setTimeout(() => setIsTransitioning(false), 100);
    }, 150);
  };


  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'accepted': return <CheckCircle className="w-4 h-4" />;
      case 'awaiting-info': return <AlertCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      case 'in-progress': return <Activity className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const mapStatusForBadge = (status: string): 'pending' | 'in-progress' | 'completed' | 'failed' => {
    switch (status) {
      case 'accepted': return 'completed';
      case 'awaiting-info': return 'pending';
      case 'rejected': return 'failed';
      case 'pending': return 'pending';
      case 'in-progress': return 'in-progress';
      case 'completed': return 'completed';
      case 'cancelled': return 'failed';
      default: return 'pending';
    }
  };

  return (
    <div className="h-full overflow-hidden">
      <div className="h-full flex flex-col p-4 gap-6">
        <div className="flex items-center justify-between flex-shrink-0">
          <div>
            <PageHeader
              title={user ? `Welcome back, ${user.name}!` : 'Dashboard'}
              description={user ? `Your personalized model management overview` : 'Model management system overview'}
            />
          </div>
          {user && (
            <div className="flex items-center gap-2 bg-white rounded-lg border border-gray-200 p-1">
              <button
                onClick={() => setViewMode('global')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'global'
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🌐 Global View
              </button>
              <button
                onClick={() => setViewMode('personal')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'personal'
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                👤 My Performance
              </button>
            </div>
          )}
        </div>
        
        {/* Top Section - Metrics and Library Overview */}
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-4 flex-shrink-0">
          
          {/* Key Metrics - 4 cards in one row */}
          <div className="xl:col-span-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            
            {/* Total Calibrated Models */}
            <div className={`${statsCardStyles.containerPurple} h-28 flex flex-col justify-between`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-gray-500 text-xs font-medium truncate">
                    {viewMode === 'global' ? 'Total Calibrated' : 'My Calibrated'}
                  </p>
                  <p className="text-2xl font-bold mt-0.5 text-gray-800">
                    {viewMode === 'global' ? totalCalibratedModels : userCalibratedModels}
                  </p>
                </div>
                <div className={statsCardStyles.iconContainerPurple}>
                  <Target className={statsCardStyles.iconPurple} />
                </div>
              </div>
              <div className="h-4">
                {viewMode === 'personal' && user && (
                  <p className="text-gray-400 text-xs truncate">
                    {((userCalibratedModels / totalCalibratedModels) * 100).toFixed(1)}% of total
                  </p>
                )}
              </div>
            </div>

            {/* Current Month Calibrations */}
            <div className={`${statsCardStyles.containerBlue} h-28 flex flex-col justify-between`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-gray-500 text-xs font-medium truncate">
                    {viewMode === 'global' ? 'Current Month' : 'My Current Month'}
                  </p>
                  <p className="text-2xl font-bold mt-0.5 text-gray-800">
                    {viewMode === 'global' ? currentMonthCalibrations : userCurrentMonthCalibrations}
                  </p>
                </div>
                <div className={statsCardStyles.iconContainerBlue}>
                  <Calendar className={statsCardStyles.iconBlue} />
                </div>
              </div>
              <div className="h-4">
                {viewMode === 'global' ? (
                  <p className={`text-xs flex items-center gap-1 truncate ${monthChange >= 0 ? 'text-gray-400' : 'text-gray-500'}`}>
                    {monthChange >= 0 ? '↗' : '↘'} {Math.abs(monthChange)} vs last month
                  </p>
                ) : (
                  <p className={`text-xs flex items-center gap-1 truncate ${userMonthChange >= 0 ? 'text-gray-400' : 'text-gray-500'}`}>
                    {userMonthChange >= 0 ? '↗' : '↘'} {Math.abs(userMonthChange)} vs last month
                  </p>
                )}
              </div>
            </div>

            {/* Models In Progress */}
            <div className={`${statsCardStyles.containerGreen} h-28 flex flex-col justify-between`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-gray-500 text-xs font-medium truncate">
                    {viewMode === 'global' ? 'In Progress' : 'My In Progress'}
                  </p>
                  <p className="text-2xl font-bold mt-0.5 text-gray-800">
                    {viewMode === 'global' ? inProgressModels : userInProgressModels}
                  </p>
                </div>
                <div className={statsCardStyles.iconContainerGreen}>
                  <Activity className={statsCardStyles.iconGreen} />
                </div>
              </div>
              <div className="h-4">
                {viewMode === 'personal' && user && inProgressModels > 0 && (
                  <p className="text-gray-400 text-xs truncate">
                    {((userInProgressModels / inProgressModels) * 100).toFixed(1)}% of total
                  </p>
                )}
              </div>
            </div>

            {/* Active Requests */}
            <div className={`${statsCardStyles.containerOrange} h-28 flex flex-col justify-between`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-gray-500 text-xs font-medium truncate">Active Requests</p>
                  <p className="text-2xl font-bold mt-0.5 text-gray-800">{stats.activeRequests}</p>
                </div>
                <div className={statsCardStyles.iconContainerOrange}>
                  <Clock className={statsCardStyles.iconOrange} />
                </div>
              </div>
              <div className="h-4">
                {/* Reserved space for consistency */}
              </div>
            </div>
          </div>

          {/* Library Overview */}
          <div className="bg-white rounded-lg border border-gray-200 p-3 h-28 flex flex-col">
            <h2 className="text-xs font-semibold text-gray-700 mb-1.5">Library Overview</h2>
            <div className="flex items-stretch justify-between gap-1.5 flex-1 min-h-0">
              {/* Model Templates */}
              <div className="flex-1 bg-gray-50 rounded border border-gray-200 px-2 py-1 flex flex-col items-center justify-center min-w-0">
                <div className="flex items-center gap-1 mb-0.5">
                  <Database className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                  <span className="text-lg font-bold text-gray-800">{stats.libraryStats.modelTemplates}</span>
                </div>
                <span className="text-xs text-gray-500">Templates</span>
              </div>

              {/* Reference Data */}
              <div className="flex-1 bg-gray-50 rounded border border-gray-200 px-2 py-1 flex flex-col items-center justify-center min-w-0">
                <div className="flex items-center gap-1 mb-0.5">
                  <FileText className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                  <span className="text-lg font-bold text-gray-800">{stats.libraryStats.referenceDatasets}</span>
                </div>
                <span className="text-xs text-gray-500">Ref Data</span>
              </div>

              {/* Testbenches */}
              <div className="flex-1 bg-gray-50 rounded border border-gray-200 px-2 py-1 flex flex-col items-center justify-center min-w-0">
                <div className="flex items-center gap-1 mb-0.5">
                  <TestTube className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                  <span className="text-lg font-bold text-gray-800">{stats.libraryStats.testbenches}</span>
                </div>
                <span className="text-xs text-gray-500">Testbenches</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section - Chart and Recent Activity Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0 mt-4">
          
          {/* Calibration Trends Chart */}
          <Card className="lg:col-span-2 h-full flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-base font-semibold text-gray-900">
                  {viewMode === 'global' ? 'Calibration Trends' : 'My Performance'}
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => handleTimeRangeChange('daily')}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      timeRange === 'daily' 
                        ? 'bg-white text-gray-900 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Daily
                  </button>
                  <button
                    onClick={() => handleTimeRangeChange('weekly')}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      timeRange === 'weekly' 
                        ? 'bg-white text-gray-900 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Weekly
                  </button>
                  <button
                    onClick={() => handleTimeRangeChange('monthly')}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      timeRange === 'monthly' 
                        ? 'bg-white text-gray-900 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Monthly
                  </button>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setChartType('bar')}
                    className={`p-1.5 rounded transition-colors ${
                      chartType === 'bar' 
                        ? 'bg-purple-100 text-purple-600' 
                        : 'text-gray-500 hover:bg-gray-100'
                    }`}
                    title="Bar Chart"
                  >
                    <BarChart2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setChartType('line')}
                    className={`p-1.5 rounded transition-colors ${
                      chartType === 'line' 
                        ? 'bg-purple-100 text-purple-600' 
                        : 'text-gray-500 hover:bg-gray-100'
                    }`}
                    title="Line Chart"
                  >
                    <LineChart className="w-4 h-4" />
                  </button>
                  <div className="w-px h-6 bg-gray-300 mx-1" />
                  <button
                    onClick={handleSaveChart}
                    className="p-1.5 rounded text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                    title="Save as Image"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className={`flex-1 min-h-0 relative transition-opacity duration-300 ${isTransitioning ? 'opacity-30' : 'opacity-100'}`}>
              <Plot
                ref={plotRef}
                key={`plot-${timeRange}-${chartType}`}
                data={(() => {
                  const xData = calibrationData.map(d => d.month);
                  const traces: any[] = [];
                  
                  if (chartType === 'bar') {
                    if (viewMode === 'personal' && user) {
                      traces.push({
                        x: xData,
                        y: calibrationData.map(d => d.models),
                        name: 'Global',
                        type: 'bar' as const,
                        marker: { color: '#60a5fa' }
                      });
                      traces.push({
                        x: xData,
                        y: calibrationData.map(d => d.userModels),
                        name: 'Mine',
                        type: 'bar' as const,
                        marker: { color: '#9333ea' }
                      });
                    } else {
                      traces.push({
                        x: xData,
                        y: calibrationData.map(d => d.models),
                        name: 'Models',
                        type: 'bar' as const,
                        marker: { color: '#9333ea' }
                      });
                    }
                  } else {
                    if (viewMode === 'personal' && user) {
                      traces.push({
                        x: xData,
                        y: calibrationData.map(d => d.models),
                        name: 'Global',
                        type: 'scatter' as const,
                        mode: 'lines+markers' as const,
                        line: { color: '#60a5fa', width: 2 },
                        marker: { color: '#60a5fa', size: 6 },
                        fill: 'tozeroy' as const,
                        fillcolor: 'rgba(96, 165, 250, 0.15)'
                      });
                      traces.push({
                        x: xData,
                        y: calibrationData.map(d => d.userModels),
                        name: 'Mine',
                        type: 'scatter' as const,
                        mode: 'lines+markers' as const,
                        line: { color: '#9333ea', width: 2 },
                        marker: { color: '#9333ea', size: 6 },
                        fill: 'tozeroy' as const,
                        fillcolor: 'rgba(147, 51, 234, 0.15)'
                      });
                    } else {
                      traces.push({
                        x: xData,
                        y: calibrationData.map(d => d.models),
                        name: 'Models',
                        type: 'scatter' as const,
                        mode: 'lines+markers' as const,
                        line: { color: '#9333ea', width: 2 },
                        marker: { color: '#9333ea', size: 6 },
                        fill: 'tozeroy' as const,
                        fillcolor: 'rgba(147, 51, 234, 0.2)'
                      });
                    }
                  }
                  
                  return traces;
                })()}
                layout={{
                  autosize: true,
                  margin: { l: 60, r: 10, t: 10, b: 60 },
                  xaxis: {
                    title: {
                      text: timeRange === 'daily' ? 'Day' : timeRange === 'weekly' ? 'Week' : 'Month',
                      font: { size: 14, color: '#6b7280' }
                    },
                    tickfont: { size: 13, color: '#6b7280' },
                    gridcolor: '#f0f0f0',
                    tickangle: calibrationData.length > 20 ? -45 : 0,
                    nticks: timeRange === 'daily' ? 10 : timeRange === 'weekly' ? 12 : 12,
                    tickmode: 'auto'
                  },
                  yaxis: {
                    title: {
                      text: 'Number of Models',
                      font: { size: 14, color: '#6b7280' }
                    },
                    tickfont: { size: 13, color: '#6b7280' },
                    gridcolor: '#f0f0f0'
                  },
                  legend: {
                    x: 0,
                    y: 1.1,
                    orientation: 'h',
                    font: { size: 13 }
                  },
                  paper_bgcolor: 'transparent',
                  plot_bgcolor: 'white',
                  hovermode: 'x unified',
                  hoverlabel: {
                    bgcolor: 'white',
                    bordercolor: '#e5e7eb',
                    font: { size: 14 }
                  },
                  dragmode: 'zoom',
                  showlegend: viewMode === 'personal' && user ? true : false
                }}
                config={{
                  displayModeBar: false,
                  displaylogo: false,
                  staticPlot: false,
                  scrollZoom: true,
                  responsive: true
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
                className="plotly-no-outline"
              />
            </div>
          </Card>

          {/* Recent Activity */}
          <Card padding="none" className="h-full flex flex-col overflow-hidden">
            <div className="px-3 py-2 border-b border-gray-200 flex-shrink-0">
              <h2 className="text-base font-semibold text-gray-900">Recent Activity</h2>
            </div>
            <div className="divide-y divide-gray-200 flex-1 overflow-y-auto">
              {(() => {
                interface Activity {
                  id: string;
                  type: 'pending' | 'accepted' | 'in-progress' | 'completed';
                  title: string;
                  technology: string;
                  date: Date;
                  status: string;
                  requester: string;
                }
                
                const activities: Activity[] = [];
                
                // Add pending requests
                const pendingRequests = (viewMode === 'personal' && user 
                  ? requests.filter(req => req.status === 'pending' && req.requester === user.name)
                  : allRequests.filter(req => req.status === 'pending')
                ).slice(0, 4);
                
                pendingRequests.forEach(request => {
                  activities.push({
                    id: `pending-${request.request_id}`,
                    type: 'pending',
                    title: request.title,
                    technology: request.technology,
                    date: new Date(request.request_date),
                    status: 'pending',
                    requester: request.requester
                  });
                });
                
                // Add accepted requests
                const acceptedRequests = (viewMode === 'personal' && user 
                  ? requests.filter(req => req.status === 'accepted' && req.requester === user.name)
                  : allRequests.filter(req => req.status === 'accepted')
                ).slice(0, 4);
                
                acceptedRequests.forEach(request => {
                  activities.push({
                    id: `accepted-${request.request_id}`,
                    type: 'accepted',
                    title: request.title,
                    technology: request.technology,
                    date: new Date(request.request_date),
                    status: 'accepted',
                    requester: request.requester
                  });
                });
                
                // Add in-progress calibrations from calibrated models
                const inProgressCalibrations = calibratedModels.filter((model: any) => 
                  model.status === 'in-progress' && 
                  (viewMode === 'global' || (user && model.calibration_info.engineer === user.name))
                ).slice(0, 4);
                
                inProgressCalibrations.forEach((model: any) => {
                  activities.push({
                    id: `calibration-${model.model_id}`,
                    type: 'in-progress',
                    title: model.name,
                    technology: model.technology?.node || model.category,
                    date: new Date(model.calibration_info.timestamp || model.calibration_info.start_date),
                    status: 'in-progress',
                    requester: model.calibration_info.engineer
                  });
                });
                
                // Sort by date (most recent first)
                activities.sort((a, b) => b.date.getTime() - a.date.getTime());
                
                return activities.slice(0, 12).map((activity) => (
                  <div key={activity.id} className="px-3 py-2 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                            activity.status === 'pending' ? 'bg-yellow-500' : 
                            activity.status === 'accepted' ? 'bg-green-500' :
                            activity.status === 'in-progress' ? 'bg-blue-500' : 'bg-gray-500'
                          }`}></div>
                          <h3 className="text-xs font-medium text-gray-900 truncate">{activity.title}</h3>
                          <Badge status={mapStatusForBadge(activity.status)} size="sm">
                            {getStatusIcon(activity.status)}
                          </Badge>
                        </div>
                        <div className="mt-0.5 flex items-center gap-2 text-xs text-gray-500 ml-4">
                          <span>{activity.technology}</span>
                          <span>•</span>
                          <span className="capitalize">{activity.type.replace('-', ' ')}</span>
                          {viewMode === 'global' && (
                            <>
                              <span>•</span>
                              <span>{activity.requester}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="text-right ml-2">
                        <p className="text-xs font-medium text-gray-900">
                          {activity.date.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ));
              })()}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
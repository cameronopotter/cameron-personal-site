import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [data, setData] = useState({
    revenue: [],
    users: [],
    performance: []
  });

  useEffect(() => {
    // Simulate data fetching
    setData({
      revenue: [
        { month: 'Jan', revenue: 4000, profit: 2400 },
        { month: 'Feb', revenue: 3000, profit: 1398 },
        { month: 'Mar', revenue: 2000, profit: 9800 },
        { month: 'Apr', revenue: 2780, profit: 3908 },
        { month: 'May', revenue: 1890, profit: 4800 },
        { month: 'Jun', revenue: 2390, profit: 3800 }
      ],
      users: [
        { name: 'Active Users', value: 400, color: '#8884d8' },
        { name: 'Inactive Users', value: 300, color: '#82ca9d' },
        { name: 'New Users', value: 200, color: '#ffc658' }
      ],
      performance: [
        { metric: 'CPU Usage', value: 65 },
        { metric: 'Memory Usage', value: 78 },
        { metric: 'Disk Usage', value: 45 },
        { metric: 'Network I/O', value: 89 }
      ]
    });
  }, []);

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Revenue Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Revenue & Profit Trends
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <LineChart data={data.revenue}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="profit" stroke="#82ca9d" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* User Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              User Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <PieChart>
                <Pie
                  data={data.users}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {data.users.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              System Performance Metrics
            </Typography>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={data.performance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
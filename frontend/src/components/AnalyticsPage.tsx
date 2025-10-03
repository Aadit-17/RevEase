import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Loader2 } from 'lucide-react';
import { getAnalytics } from '../services/api';
import { toast } from 'sonner';

interface SentimentData {
  name: string;
  value: number;
}

interface TopicData {
  topic: string;
  count: number;
}

export function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [sentimentData, setSentimentData] = useState<SentimentData[]>([]);
  const [topicData, setTopicData] = useState<TopicData[]>([]);

  const sentimentColors = {
    positive: '#22c55e',
    neutral: '#eab308',
    negative: '#ef4444',
    unknown: '#94a3b8'
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const data = await getAnalytics();

      // Process sentiment data
      const sentimentChartData = (data.sentiment_distribution || []).map((item: any) => ({
        name: item.name.charAt(0).toUpperCase() + item.name.slice(1),
        value: item.value
      }));

      // Process topic data
      const topicChartData = (data.topic_distribution || []).map((item: any) => ({
        topic: item.topic || 'Unknown',
        count: item.count
      }));

      setSentimentData(sentimentChartData);
      setTopicData(topicChartData);
    } catch (error) {
      // Failed to fetch analytics
      toast.error('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="gradient-text text-2xl">Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="gradient-text">Sentiment Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {sentimentData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={sentimentColors[entry.name.toLowerCase() as keyof typeof sentimentColors] || sentimentColors.unknown}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Reviews']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex justify-center items-center h-64 text-muted-foreground">
                No sentiment data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Topic Distribution */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="gradient-text">Topic Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {topicData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={topicData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 50 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="topic"
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    dataKey="count"
                    tickFormatter={(value) => Number.isInteger(value) ? value.toString() : ''}
                  />
                  <Tooltip formatter={(value) => [value, 'Reviews']} />
                  <Legend />
                  <Bar
                    dataKey="count"
                    name="Review Count"
                    fill="#3b82f6"
                  >
                    {topicData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill="#3b82f6"
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex justify-center items-center h-64 text-muted-foreground">
                No topic data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
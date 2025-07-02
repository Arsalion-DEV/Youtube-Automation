import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  TrendingUp, 
  Search, 
  Users, 
  Video, 
  Tag, 
  Clock, 
  Star,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface IntegrationStatus {
  initialized: boolean;
  services: {
    vidiq: { available: boolean; status: string };
    socialblade: { available: boolean; status: string };
    tubebuddy: { available: boolean; status: string };
  };
  last_check: string;
}

interface KeywordData {
  keyword: string;
  search_volume: number;
  competition: string;
  relevance_score: number;
}

interface ChannelStats {
  subscriber_count: number;
  total_views: number;
  video_count: number;
  grade: string;
  growth_trend: string;
}

interface ComprehensiveAnalysis {
  vidiq_analysis: any;
  socialblade_analysis: any;
  tubebuddy_analysis: any;
  combined_insights: any;
}

const IntegrationsDashboard: React.FC = () => {
  const [integrationStatus, setIntegrationStatus] = useState<IntegrationStatus | null>(null);
  const [analysis, setAnalysis] = useState<ComprehensiveAnalysis | null>(null);
  const [keywords, setKeywords] = useState<KeywordData[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState('');
  const [keywordTopic, setKeywordTopic] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadIntegrationStatus();
  }, []);

  const loadIntegrationStatus = async () => {
    try {
      const response = await fetch('/api/v2/integrations/status');
      if (response.ok) {
        const data = await response.json();
        setIntegrationStatus(data.data);
      }
    } catch (error) {
      console.error('Failed to load integration status:', error);
    }
  };

  const runComprehensiveAnalysis = async () => {
    if (!selectedChannel) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/v2/integrations/comprehensive-analysis/${selectedChannel}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysis(data.data);
      }
    } catch (error) {
      console.error('Failed to run comprehensive analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchKeywords = async () => {
    if (!keywordTopic) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/v2/integrations/keyword-research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: keywordTopic,
          channel_id: selectedChannel
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.data.vidiq_keywords) {
          setKeywords(data.data.vidiq_keywords);
        }
      }
    } catch (error) {
      console.error('Failed to search keywords:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'inactive':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getCompetitionColor = (competition: string) => {
    switch (competition) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Third-Party Integrations Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              VidIQ, Social Blade, and TubeBuddy analytics and optimization
            </p>
          </div>
          <Button 
            onClick={loadIntegrationStatus}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Status
          </Button>
        </div>

        {/* Integration Status */}
        {integrationStatus && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Integration Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">VidIQ</span>
                    {getStatusIcon(integrationStatus.services.vidiq.status)}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Keyword research & SEO optimization
                  </p>
                  <Badge 
                    variant={integrationStatus.services.vidiq.available ? "default" : "secondary"}
                    className="mt-2"
                  >
                    {integrationStatus.services.vidiq.status}
                  </Badge>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Social Blade</span>
                    {getStatusIcon(integrationStatus.services.socialblade.status)}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Channel analytics & growth tracking
                  </p>
                  <Badge 
                    variant={integrationStatus.services.socialblade.available ? "default" : "secondary"}
                    className="mt-2"
                  >
                    {integrationStatus.services.socialblade.status}
                  </Badge>
                </div>
                
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">TubeBuddy</span>
                    {getStatusIcon(integrationStatus.services.tubebuddy.status)}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Content optimization & best practices
                  </p>
                  <Badge 
                    variant={integrationStatus.services.tubebuddy.available ? "default" : "secondary"}
                    className="mt-2"
                  >
                    {integrationStatus.services.tubebuddy.status}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Channel Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Channel Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Label htmlFor="channel">Channel ID</Label>
                <Input
                  id="channel"
                  value={selectedChannel}
                  onChange={(e) => setSelectedChannel(e.target.value)}
                  placeholder="Enter YouTube channel ID"
                />
              </div>
              <Button 
                onClick={runComprehensiveAnalysis}
                disabled={!selectedChannel || loading}
                className="mt-6"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Analyze Channel'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Main Dashboard */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="keywords">Keywords</TabsTrigger>
            <TabsTrigger value="optimization">Optimization</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {analysis && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* VidIQ Insights */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Search className="w-5 h-5 text-blue-500" />
                      VidIQ Insights
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysis.vidiq_analysis?.growth_insights && (
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600">Growth Rate</p>
                          <p className="font-semibold">
                            {analysis.vidiq_analysis.growth_insights.growth_rate?.subscribers || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Best Content Type</p>
                          <p className="font-semibold">
                            {analysis.vidiq_analysis.growth_insights.best_performing_content?.[0]?.type || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Optimal Upload Time</p>
                          <p className="font-semibold">
                            {analysis.vidiq_analysis.growth_insights.optimal_upload_times?.[0] || 'N/A'}
                          </p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Social Blade Stats */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-green-500" />
                      Social Blade Stats
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysis.socialblade_analysis?.channel_stats && (
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600">Subscribers</p>
                          <p className="font-semibold">
                            {analysis.socialblade_analysis.channel_stats.subscriber_count?.toLocaleString() || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Total Views</p>
                          <p className="font-semibold">
                            {analysis.socialblade_analysis.channel_stats.total_views?.toLocaleString() || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Channel Grade</p>
                          <Badge variant="default">
                            {analysis.socialblade_analysis.channel_stats.grade || 'N/A'}
                          </Badge>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* TubeBuddy Health */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Star className="w-5 h-5 text-purple-500" />
                      TubeBuddy Health
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analysis.tubebuddy_analysis?.channel_health && (
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600">Overall Score</p>
                          <p className="font-semibold text-2xl">
                            {analysis.tubebuddy_analysis.channel_health.overall_score || 'N/A'}%
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Grade</p>
                          <Badge variant="default">
                            {analysis.tubebuddy_analysis.channel_health.grade || 'N/A'}
                          </Badge>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Top Strength</p>
                          <p className="font-semibold">
                            {analysis.tubebuddy_analysis.channel_health.strengths?.[0]?.replace('_', ' ') || 'N/A'}
                          </p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Combined Insights */}
            {analysis?.combined_insights && (
              <Card>
                <CardHeader>
                  <CardTitle>Combined Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Top Recommendations</h4>
                      <div className="space-y-2">
                        {analysis.combined_insights.top_recommendations?.slice(0, 5).map((rec: string, index: number) => (
                          <div key={index} className="flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm">{rec}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3">Content Strategy</h4>
                      <div className="space-y-2">
                        {analysis.combined_insights.content_strategy_suggestions?.slice(0, 5).map((suggestion: string, index: number) => (
                          <div key={index} className="flex items-start gap-2">
                            <Video className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm">{suggestion}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="keywords" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Keyword Research</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4 mb-6">
                  <div className="flex-1">
                    <Label htmlFor="keyword-topic">Topic</Label>
                    <Input
                      id="keyword-topic"
                      value={keywordTopic}
                      onChange={(e) => setKeywordTopic(e.target.value)}
                      placeholder="Enter topic for keyword research"
                    />
                  </div>
                  <Button 
                    onClick={searchKeywords}
                    disabled={!keywordTopic || loading}
                    className="mt-6"
                  >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : 'Search Keywords'}
                  </Button>
                </div>

                {keywords.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="font-semibold">Keyword Suggestions</h4>
                    <div className="grid gap-3">
                      {keywords.map((keyword, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex-1">
                            <span className="font-medium">{keyword.keyword}</span>
                            <div className="flex items-center gap-4 mt-1">
                              <span className="text-sm text-gray-600">
                                Volume: {keyword.search_volume?.toLocaleString() || 'N/A'}
                              </span>
                              <Badge 
                                className={getCompetitionColor(keyword.competition)}
                                variant="secondary"
                              >
                                {keyword.competition} competition
                              </Badge>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-semibold">
                              {Math.round(keyword.relevance_score * 100)}% relevance
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="optimization" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Content Optimization Tools</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <Button variant="outline" className="p-6 h-auto flex-col">
                    <Tag className="w-8 h-8 mb-2" />
                    <span className="font-semibold">Tag Suggestions</span>
                    <span className="text-sm text-gray-600">Get optimized tags for videos</span>
                  </Button>
                  
                  <Button variant="outline" className="p-6 h-auto flex-col">
                    <Clock className="w-8 h-8 mb-2" />
                    <span className="font-semibold">Upload Timing</span>
                    <span className="text-sm text-gray-600">Find best upload times</span>
                  </Button>
                  
                  <Button variant="outline" className="p-6 h-auto flex-col">
                    <BarChart3 className="w-8 h-8 mb-2" />
                    <span className="font-semibold">SEO Analysis</span>
                    <span className="text-sm text-gray-600">Analyze video SEO score</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Advanced Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <BarChart3 className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">
                    Advanced analytics dashboard will be available here.
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Run a comprehensive analysis to see detailed metrics.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default IntegrationsDashboard;
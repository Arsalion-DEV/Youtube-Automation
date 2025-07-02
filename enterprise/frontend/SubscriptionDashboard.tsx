"""
Subscription Management Dashboard
React component for managing subscription plans, billing, and usage
"""

import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Package, 
  TrendingUp, 
  Users, 
  Calendar, 
  Download,
  Check,
  X,
  AlertTriangle,
  Settings,
  RefreshCw,
  ExternalLink,
  Crown,
  Zap,
  Star,
  ArrowUp,
  ChevronRight
} from 'lucide-react';

interface SubscriptionPlan {
  id: string;
  tier: string;
  name: string;
  description: string;
  base_price: number;
  billing_cycles: {
    [key: string]: {
      price: number;
      discount: number;
    };
  };
  features: string[];
  limits: {
    [key: string]: number;
  };
  usage_pricing: {
    [key: string]: {
      included: number;
      overage_price: number;
    };
  };
}

interface CurrentSubscription {
  subscription_id: string;
  status: string;
  tier: string;
  plan_name: string;
  billing_cycle: string;
  current_period_start: string;
  current_period_end: string;
  trial_end?: string;
  features: string[];
  limits: {
    [key: string]: number;
  };
  current_usage: {
    [key: string]: number;
  };
}

interface UsageBilling {
  base_amount: number;
  usage_amount: number;
  total_amount: number;
  line_items: Array<{
    metric: string;
    usage: number;
    included: number;
    overage_quantity: number;
    overage_price: number;
    overage_amount: number;
  }>;
}

const SubscriptionDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'plans' | 'billing' | 'usage'>('overview');
  const [currentSubscription, setCurrentSubscription] = useState<CurrentSubscription | null>(null);
  const [availablePlans, setAvailablePlans] = useState<SubscriptionPlan[]>([]);
  const [usageBilling, setUsageBilling] = useState<UsageBilling | null>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      
      const [subscriptionResponse, plansResponse] = await Promise.all([
        fetch('/api/v3/subscriptions/sub-123'),
        fetch('/api/v3/subscriptions/plans')
      ]);

      const subscriptionData = await subscriptionResponse.json();
      const plansData = await plansResponse.json();

      setCurrentSubscription(subscriptionData.subscription);
      setAvailablePlans(plansData.plans);
    } catch (error) {
      console.error('Error loading subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'free': return <Package className="w-5 h-5 text-gray-500" />;
      case 'starter': return <Zap className="w-5 h-5 text-blue-500" />;
      case 'pro': return <Star className="w-5 h-5 text-purple-500" />;
      case 'business': return <Crown className="w-5 h-5 text-yellow-500" />;
      case 'enterprise': return <Crown className="w-5 h-5 text-red-500" />;
      default: return <Package className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'free': return 'border-gray-200 bg-gray-50';
      case 'starter': return 'border-blue-200 bg-blue-50';
      case 'pro': return 'border-purple-200 bg-purple-50';
      case 'business': return 'border-yellow-200 bg-yellow-50';
      case 'enterprise': return 'border-red-200 bg-red-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0; // Unlimited
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const PlanUpgradeModal: React.FC = () => {
    const [billingCycle, setBillingCycle] = useState('monthly');
    const [processing, setProcessing] = useState(false);

    if (!selectedPlan) return null;

    const handleUpgrade = async () => {
      try {
        setProcessing(true);
        
        const response = await fetch(`/api/v3/subscriptions/${currentSubscription?.subscription_id}/upgrade`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            new_plan_id: selectedPlan.id,
            billing_cycle: billingCycle
          })
        });

        if (response.ok) {
          setShowUpgradeModal(false);
          loadSubscriptionData();
        }
      } catch (error) {
        console.error('Error upgrading subscription:', error);
      } finally {
        setProcessing(false);
      }
    };

    const selectedPrice = selectedPlan.billing_cycles[billingCycle]?.price || selectedPlan.base_price;
    const discount = selectedPlan.billing_cycles[billingCycle]?.discount || 0;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold">Upgrade to {selectedPlan.name}</h3>
            <button
              onClick={() => setShowUpgradeModal(false)}
              className="p-2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-6">
            {/* Plan Overview */}
            <div className={`p-4 rounded-lg border-2 ${getTierColor(selectedPlan.tier)}`}>
              <div className="flex items-center gap-3 mb-2">
                {getTierIcon(selectedPlan.tier)}
                <h4 className="text-lg font-semibold">{selectedPlan.name}</h4>
              </div>
              <p className="text-gray-600 mb-4">{selectedPlan.description}</p>
              
              {/* Billing Cycle Selection */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  Billing Cycle
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {Object.entries(selectedPlan.billing_cycles).map(([cycle, config]) => (
                    <label key={cycle} className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                      <div className="flex items-center gap-3">
                        <input
                          type="radio"
                          name="billing_cycle"
                          value={cycle}
                          checked={billingCycle === cycle}
                          onChange={(e) => setBillingCycle(e.target.value)}
                          className="text-blue-600 focus:ring-blue-500"
                        />
                        <div>
                          <div className="font-medium capitalize">{cycle}</div>
                          <div className="text-sm text-gray-500">
                            {formatCurrency(config.price)} per {cycle.replace('ly', '')}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        {config.discount > 0 && (
                          <div className="text-sm font-medium text-green-600">
                            Save {config.discount}%
                          </div>
                        )}
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Price Summary */}
              <div className="mt-4 p-3 bg-white rounded border">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Total</span>
                  <div className="text-right">
                    <div className="text-xl font-bold">{formatCurrency(selectedPrice)}</div>
                    <div className="text-sm text-gray-500">per {billingCycle.replace('ly', '')}</div>
                  </div>
                </div>
                {discount > 0 && (
                  <div className="text-sm text-green-600 mt-1">
                    You save {formatCurrency(selectedPlan.base_price - selectedPrice)} with {billingCycle} billing
                  </div>
                )}
              </div>
            </div>

            {/* Features */}
            <div>
              <h5 className="font-medium mb-3">What's included:</h5>
              <div className="grid grid-cols-1 gap-2">
                {selectedPlan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-500" />
                    <span className="text-sm">{feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4 border-t">
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={processing}
              >
                Cancel
              </button>
              <button
                onClick={handleUpgrade}
                disabled={processing}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {processing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <ArrowUp className="w-4 h-4" />
                    Upgrade Now
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const OverviewTab: React.FC = () => (
    <div className="space-y-6">
      {currentSubscription && (
        <>
          {/* Current Plan */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                {getTierIcon(currentSubscription.tier)}
                <div>
                  <h3 className="text-lg font-semibold">{currentSubscription.plan_name}</h3>
                  <p className="text-sm text-gray-600 capitalize">{currentSubscription.billing_cycle} billing</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  currentSubscription.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {currentSubscription.status}
                </span>
                <button 
                  onClick={() => {
                    const currentPlan = availablePlans.find(p => p.tier !== currentSubscription.tier);
                    if (currentPlan) {
                      setSelectedPlan(currentPlan);
                      setShowUpgradeModal(true);
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                  <ArrowUp className="w-4 h-4" />
                  Upgrade Plan
                </button>
              </div>
            </div>

            {/* Billing Period */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Current Period</div>
                <div className="font-medium">
                  {new Date(currentSubscription.current_period_start).toLocaleDateString()} - {' '}
                  {new Date(currentSubscription.current_period_end).toLocaleDateString()}
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Next Billing Date</div>
                <div className="font-medium">
                  {new Date(currentSubscription.current_period_end).toLocaleDateString()}
                </div>
              </div>
            </div>

            {/* Usage Overview */}
            <div className="space-y-4">
              <h4 className="font-medium">Usage This Period</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(currentSubscription.current_usage).map(([metric, usage]) => {
                  const limit = currentSubscription.limits[metric] || 0;
                  const percentage = getUsagePercentage(usage, limit);
                  
                  return (
                    <div key={metric} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium capitalize">
                          {metric.replace(/_/g, ' ')}
                        </span>
                        <span className="text-sm text-gray-600">
                          {usage} / {limit === -1 ? '∞' : limit.toLocaleString()}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getUsageColor(percentage)}`}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        />
                      </div>
                      {percentage >= 90 && (
                        <div className="flex items-center gap-1 mt-2 text-sm text-orange-600">
                          <AlertTriangle className="w-4 h-4" />
                          Approaching limit
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );

  const PlansTab: React.FC = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Choose Your Plan</h3>
        <p className="text-gray-600">Scale your content creation with the right plan for your needs</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {availablePlans.map((plan) => {
          const isCurrentPlan = currentSubscription?.tier === plan.tier;
          const monthlyPrice = plan.billing_cycles.monthly?.price || plan.base_price;
          
          return (
            <div 
              key={plan.id} 
              className={`relative rounded-lg border-2 p-6 ${
                isCurrentPlan 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              {isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Current Plan
                  </span>
                </div>
              )}

              <div className="flex items-center gap-3 mb-4">
                {getTierIcon(plan.tier)}
                <div>
                  <h4 className="text-lg font-semibold">{plan.name}</h4>
                  <p className="text-sm text-gray-600">{plan.description}</p>
                </div>
              </div>

              <div className="mb-6">
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-bold">{formatCurrency(monthlyPrice)}</span>
                  <span className="text-gray-600">/{plan.tier === 'free' ? 'forever' : 'month'}</span>
                </div>
                {plan.billing_cycles.yearly && (
                  <div className="text-sm text-green-600 mt-1">
                    Save {plan.billing_cycles.yearly.discount}% with yearly billing
                  </div>
                )}
              </div>

              <div className="space-y-3 mb-6">
                {plan.features.slice(0, 5).map((feature, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                ))}
                {plan.features.length > 5 && (
                  <div className="text-sm text-gray-600">
                    +{plan.features.length - 5} more features
                  </div>
                )}
              </div>

              <div className="space-y-3 mb-6">
                <h5 className="font-medium text-sm">Limits:</h5>
                {Object.entries(plan.limits).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="font-medium">{value === -1 ? 'Unlimited' : value.toLocaleString()}</span>
                  </div>
                ))}
              </div>

              <button
                onClick={() => {
                  if (!isCurrentPlan) {
                    setSelectedPlan(plan);
                    setShowUpgradeModal(true);
                  }
                }}
                disabled={isCurrentPlan}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                  isCurrentPlan
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isCurrentPlan ? 'Current Plan' : 'Select Plan'}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );

  const BillingTab: React.FC = () => (
    <div className="space-y-6">
      {/* Billing Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Billing Summary</h3>
        
        {usageBilling && (
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b">
              <span>Base Subscription</span>
              <span className="font-medium">{formatCurrency(usageBilling.base_amount)}</span>
            </div>
            
            {usageBilling.line_items.map((item, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b">
                <div>
                  <div className="font-medium capitalize">{item.metric.replace(/_/g, ' ')} Overage</div>
                  <div className="text-sm text-gray-600">
                    {item.overage_quantity} × {formatCurrency(item.overage_price)}
                  </div>
                </div>
                <span className="font-medium">{formatCurrency(item.overage_amount)}</span>
              </div>
            ))}
            
            <div className="flex justify-between items-center pt-4 border-t-2 text-lg font-bold">
              <span>Total</span>
              <span>{formatCurrency(usageBilling.total_amount)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Payment Method */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Payment Method</h3>
          <button className="flex items-center gap-2 px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50">
            <CreditCard className="w-4 h-4" />
            Update
          </button>
        </div>
        
        <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
          <CreditCard className="w-8 h-8 text-gray-400" />
          <div>
            <div className="font-medium">•••• •••• •••• 4242</div>
            <div className="text-sm text-gray-600">Expires 12/25</div>
          </div>
        </div>
      </div>

      {/* Billing History */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Billing History</h3>
          <button className="flex items-center gap-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4" />
            Download All
          </button>
        </div>
        
        <div className="space-y-3">
          {[
            { date: '2024-01-01', amount: 99.00, status: 'paid', invoice: 'inv_001' },
            { date: '2023-12-01', amount: 99.00, status: 'paid', invoice: 'inv_002' },
            { date: '2023-11-01', amount: 99.00, status: 'paid', invoice: 'inv_003' },
          ].map((bill, index) => (
            <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="font-medium">{new Date(bill.date).toLocaleDateString()}</div>
                  <div className="text-sm text-gray-600">Invoice #{bill.invoice}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-medium">{formatCurrency(bill.amount)}</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                  {bill.status}
                </span>
                <button className="p-2 text-gray-400 hover:text-gray-600">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Subscription & Billing</h1>
          <p className="text-gray-600">Manage your subscription, billing, and usage</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
          <Settings className="w-4 h-4" />
          Settings
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Package },
            { id: 'plans', label: 'Plans', icon: Crown },
            { id: 'billing', label: 'Billing', icon: CreditCard },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'plans' && <PlansTab />}
      {activeTab === 'billing' && <BillingTab />}

      {/* Upgrade Modal */}
      {showUpgradeModal && <PlanUpgradeModal />}
    </div>
  );
};

export default SubscriptionDashboard;
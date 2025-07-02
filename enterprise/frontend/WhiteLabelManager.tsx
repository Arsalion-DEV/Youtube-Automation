"""
White Label Management Dashboard
React component for managing white-label branding and customization
"""

import React, { useState, useEffect } from 'react';
import { 
  Palette, 
  Upload, 
  Download, 
  Eye, 
  Settings, 
  Globe, 
  Mail, 
  Smartphone,
  Monitor,
  Copy,
  Check,
  X,
  RefreshCw,
  ExternalLink,
  Image as ImageIcon,
  Type,
  Code,
  Paintbrush,
  Save,
  RotateCcw
} from 'lucide-react';

interface WhiteLabelConfig {
  instance_id: string;
  organization_id: string;
  branding: {
    company_name: string;
    logo_url: string;
    primary_color: string;
    secondary_color: string;
    accent_color: string;
    font_family: string;
    email_domain?: string;
    support_email: string;
    support_phone?: string;
    website_url?: string;
  };
  domain?: {
    custom_domain: string;
    ssl_enabled: boolean;
    subdomain?: string;
  };
  features: {
    custom_domain: boolean;
    custom_email: boolean;
    custom_support: boolean;
    white_label_mobile_app: boolean;
  };
  status: string;
}

interface PreviewMode {
  desktop: boolean;
  tablet: boolean;
  mobile: boolean;
}

const WhiteLabelManager: React.FC = () => {
  const [config, setConfig] = useState<WhiteLabelConfig | null>(null);
  const [activeTab, setActiveTab] = useState<'branding' | 'domain' | 'features' | 'preview'>('branding');
  const [previewMode, setPreviewMode] = useState<keyof PreviewMode>('desktop');
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    loadWhiteLabelConfig();
  }, []);

  const loadWhiteLabelConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v3/white-label/instances/wl-instance-123');
      const data = await response.json();
      
      if (data.success) {
        setConfig(data.config);
      }
    } catch (error) {
      console.error('Error loading white-label config:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = (updates: Partial<WhiteLabelConfig>) => {
    if (config) {
      setConfig({ ...config, ...updates });
      setUnsavedChanges(true);
    }
  };

  const updateBranding = (updates: Partial<WhiteLabelConfig['branding']>) => {
    if (config) {
      setConfig({
        ...config,
        branding: { ...config.branding, ...updates }
      });
      setUnsavedChanges(true);
    }
  };

  const updateDomain = (updates: Partial<WhiteLabelConfig['domain']>) => {
    if (config) {
      setConfig({
        ...config,
        domain: { ...config.domain, ...updates }
      });
      setUnsavedChanges(true);
    }
  };

  const saveChanges = async () => {
    if (!config) return;

    try {
      setSaving(true);
      const response = await fetch(`/api/v3/white-label/instances/${config.instance_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });

      if (response.ok) {
        setUnsavedChanges(false);
      }
    } catch (error) {
      console.error('Error saving white-label config:', error);
    } finally {
      setSaving(false);
    }
  };

  const resetChanges = () => {
    loadWhiteLabelConfig();
    setUnsavedChanges(false);
  };

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const ColorPicker: React.FC<{
    label: string;
    value: string;
    onChange: (color: string) => void;
  }> = ({ label, value, onChange }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="flex items-center gap-3">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-12 h-12 border border-gray-300 rounded-lg cursor-pointer"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="#1f2937"
        />
      </div>
    </div>
  );

  const BrandingTab: React.FC = () => (
    <div className="space-y-6">
      {/* Company Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Type className="w-5 h-5" />
          Company Information
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Name
            </label>
            <input
              type="text"
              value={config?.branding.company_name || ''}
              onChange={(e) => updateBranding({ company_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Your Company Name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Website URL
            </label>
            <input
              type="url"
              value={config?.branding.website_url || ''}
              onChange={(e) => updateBranding({ website_url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://yourcompany.com"
            />
          </div>
        </div>
      </div>

      {/* Logo & Visual Identity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ImageIcon className="w-5 h-5" />
          Logo & Visual Identity
        </h3>
        
        <div className="space-y-6">
          {/* Logo Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Logo
            </label>
            <div className="flex items-center gap-4">
              {config?.branding.logo_url && (
                <div className="w-16 h-16 border border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                  <img 
                    src={config.branding.logo_url} 
                    alt="Logo" 
                    className="max-w-full max-h-full object-contain"
                  />
                </div>
              )}
              <div className="flex-1">
                <input
                  type="url"
                  value={config?.branding.logo_url || ''}
                  onChange={(e) => updateBranding({ logo_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://yourcompany.com/logo.png"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Recommended: PNG format, 200x60px or similar aspect ratio
                </p>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                <Upload className="w-4 h-4" />
                Upload
              </button>
            </div>
          </div>

          {/* Color Scheme */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ColorPicker
              label="Primary Color"
              value={config?.branding.primary_color || '#1f2937'}
              onChange={(color) => updateBranding({ primary_color: color })}
            />
            <ColorPicker
              label="Secondary Color"
              value={config?.branding.secondary_color || '#374151'}
              onChange={(color) => updateBranding({ secondary_color: color })}
            />
            <ColorPicker
              label="Accent Color"
              value={config?.branding.accent_color || '#3b82f6'}
              onChange={(color) => updateBranding({ accent_color: color })}
            />
          </div>

          {/* Typography */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Font Family
            </label>
            <select
              value={config?.branding.font_family || 'Inter'}
              onChange={(e) => updateBranding({ font_family: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Inter">Inter</option>
              <option value="Roboto">Roboto</option>
              <option value="Open Sans">Open Sans</option>
              <option value="Lato">Lato</option>
              <option value="Montserrat">Montserrat</option>
              <option value="Poppins">Poppins</option>
            </select>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Mail className="w-5 h-5" />
          Contact Information
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Support Email
            </label>
            <input
              type="email"
              value={config?.branding.support_email || ''}
              onChange={(e) => updateBranding({ support_email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="support@yourcompany.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Support Phone (Optional)
            </label>
            <input
              type="tel"
              value={config?.branding.support_phone || ''}
              onChange={(e) => updateBranding({ support_phone: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="+1 (555) 123-4567"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const DomainTab: React.FC = () => (
    <div className="space-y-6">
      {/* Custom Domain */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5" />
          Custom Domain
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Domain
            </label>
            <input
              type="text"
              value={config?.domain?.custom_domain || ''}
              onChange={(e) => updateDomain({ custom_domain: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="app.yourcompany.com"
            />
            <p className="text-xs text-gray-500 mt-1">
              Point your domain to our servers using CNAME record
            </p>
          </div>

          {config?.domain?.custom_domain && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-2">DNS Configuration</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-blue-800">Type: CNAME</span>
                  <button
                    onClick={() => copyToClipboard('CNAME', 'dns-type')}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {copied === 'dns-type' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-blue-800">Name: {config.domain.custom_domain}</span>
                  <button
                    onClick={() => copyToClipboard(config.domain.custom_domain, 'dns-name')}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {copied === 'dns-name' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-blue-800">Value: white-label.youtubeautomation.com</span>
                  <button
                    onClick={() => copyToClipboard('white-label.youtubeautomation.com', 'dns-value')}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {copied === 'dns-value' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="ssl_enabled"
              checked={config?.domain?.ssl_enabled || false}
              onChange={(e) => updateDomain({ ssl_enabled: e.target.checked })}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="ssl_enabled" className="text-sm font-medium text-gray-700">
              Enable SSL Certificate (Recommended)
            </label>
          </div>
        </div>
      </div>

      {/* Subdomain */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Alternative: Subdomain</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subdomain (if no custom domain)
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={config?.domain?.subdomain || ''}
                onChange={(e) => updateDomain({ subdomain: e.target.value })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="yourcompany"
              />
              <span className="text-gray-500">.youtubeautomation.com</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Available immediately, no DNS configuration required
            </p>
          </div>

          {config?.domain?.subdomain && (
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center justify-between">
                <span className="text-green-800 font-medium">
                  Your app will be available at: https://{config.domain.subdomain}.youtubeautomation.com
                </span>
                <button
                  onClick={() => copyToClipboard(`https://${config.domain.subdomain}.youtubeautomation.com`, 'subdomain-url')}
                  className="text-green-600 hover:text-green-800"
                >
                  {copied === 'subdomain-url' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const FeaturesTab: React.FC = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">White Label Features</h3>
        
        <div className="space-y-6">
          {/* Feature toggles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-blue-500" />
                  <span className="font-medium">Custom Domain</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  config?.features.custom_domain 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {config?.features.custom_domain ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Use your own domain name for the application
              </p>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-blue-500" />
                  <span className="font-medium">Custom Email</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  config?.features.custom_email 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {config?.features.custom_email ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Send emails from your domain instead of ours
              </p>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Settings className="w-5 h-5 text-blue-500" />
                  <span className="font-medium">Custom Support</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  config?.features.custom_support 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {config?.features.custom_support ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Replace our support channels with your own
              </p>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Smartphone className="w-5 h-5 text-blue-500" />
                  <span className="font-medium">Mobile App</span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  config?.features.white_label_mobile_app 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {config?.features.white_label_mobile_app ? 'Available' : 'Enterprise'}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Custom mobile app with your branding in app stores
              </p>
            </div>
          </div>

          {/* Additional customization options */}
          <div className="border-t pt-6">
            <h4 className="font-medium mb-4">Additional Customization</h4>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">Remove "Powered by" footer</div>
                  <div className="text-sm text-gray-600">Hide our branding from the footer</div>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm font-medium">
                  Included
                </span>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">Custom CSS injection</div>
                  <div className="text-sm text-gray-600">Add your own CSS for further customization</div>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm font-medium">
                  Available
                </span>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">Custom favicon</div>
                  <div className="text-sm text-gray-600">Use your own favicon for browser tabs</div>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm font-medium">
                  Auto-generated
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const PreviewTab: React.FC = () => (
    <div className="space-y-6">
      {/* Preview Controls */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Live Preview</h3>
        <div className="flex items-center gap-2">
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setPreviewMode('desktop')}
              className={`px-3 py-2 text-sm font-medium ${
                previewMode === 'desktop'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Monitor className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPreviewMode('tablet')}
              className={`px-3 py-2 text-sm font-medium ${
                previewMode === 'tablet'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <div className="w-4 h-4 border border-current rounded" />
            </button>
            <button
              onClick={() => setPreviewMode('mobile')}
              className={`px-3 py-2 text-sm font-medium ${
                previewMode === 'mobile'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Smartphone className="w-4 h-4" />
            </button>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <ExternalLink className="w-4 h-4" />
            Open in New Tab
          </button>
        </div>
      </div>

      {/* Preview Frame */}
      <div className="bg-gray-100 p-4 rounded-lg">
        <div 
          className={`mx-auto bg-white rounded-lg shadow-lg overflow-hidden ${
            previewMode === 'desktop' ? 'w-full max-w-6xl' :
            previewMode === 'tablet' ? 'w-full max-w-2xl' :
            'w-full max-w-sm'
          }`}
          style={{
            height: previewMode === 'desktop' ? '600px' : 
                   previewMode === 'tablet' ? '500px' : '400px'
          }}
        >
          {/* Mock App Preview */}
          <div 
            className="h-full flex flex-col"
            style={{
              '--primary-color': config?.branding.primary_color || '#1f2937',
              '--secondary-color': config?.branding.secondary_color || '#374151',
              '--accent-color': config?.branding.accent_color || '#3b82f6',
              fontFamily: config?.branding.font_family || 'Inter'
            } as React.CSSProperties}
          >
            {/* Header */}
            <div 
              className="p-4 text-white flex items-center justify-between"
              style={{ backgroundColor: 'var(--primary-color)' }}
            >
              <div className="flex items-center gap-3">
                {config?.branding.logo_url ? (
                  <img 
                    src={config.branding.logo_url} 
                    alt="Logo" 
                    className="h-8 w-auto"
                  />
                ) : (
                  <div className="w-8 h-8 bg-white bg-opacity-20 rounded flex items-center justify-center">
                    <span className="text-sm font-bold">
                      {config?.branding.company_name?.[0] || 'L'}
                    </span>
                  </div>
                )}
                <span className="font-semibold">
                  {config?.branding.company_name || 'Your Company'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full" />
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-4">
                {/* Dashboard Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">Total Videos</div>
                    <div className="text-2xl font-bold" style={{ color: 'var(--primary-color)' }}>
                      1,247
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">Total Views</div>
                    <div className="text-2xl font-bold" style={{ color: 'var(--primary-color)' }}>
                      8.4M
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">Revenue</div>
                    <div className="text-2xl font-bold" style={{ color: 'var(--primary-color)' }}>
                      $45.6K
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <button 
                  className="w-full py-3 text-white rounded-lg font-medium"
                  style={{ backgroundColor: 'var(--accent-color)' }}
                >
                  Create New Video
                </button>

                {/* Content List */}
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gray-200 rounded" />
                        <div className="flex-1">
                          <div className="font-medium">Video Title {i}</div>
                          <div className="text-sm text-gray-600">2 hours ago</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 text-center text-sm text-gray-600">
              © 2024 {config?.branding.company_name || 'Your Company'}. All rights reserved.
            </div>
          </div>
        </div>
      </div>

      {/* Preview Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">Preview Information</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• This preview shows how your app will look with the current branding settings</li>
          <li>• Changes are applied in real-time to help you visualize the final result</li>
          <li>• Save your changes to apply them to the live application</li>
          <li>• Use the device toggles to see how it looks on different screen sizes</li>
        </ul>
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
          <h1 className="text-2xl font-bold text-gray-900">White Label Management</h1>
          <p className="text-gray-600">Customize the application with your branding and domain</p>
        </div>
        <div className="flex items-center gap-3">
          {unsavedChanges && (
            <button
              onClick={resetChanges}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          )}
          <button
            onClick={saveChanges}
            disabled={!unsavedChanges || saving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </div>

      {/* Unsaved Changes Banner */}
      {unsavedChanges && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-yellow-800">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium">You have unsaved changes</span>
          </div>
          <p className="text-yellow-700 text-sm mt-1">
            Don't forget to save your changes to apply them to the live application.
          </p>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'branding', label: 'Branding', icon: Paintbrush },
            { id: 'domain', label: 'Domain', icon: Globe },
            { id: 'features', label: 'Features', icon: Settings },
            { id: 'preview', label: 'Preview', icon: Eye },
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
      {activeTab === 'branding' && <BrandingTab />}
      {activeTab === 'domain' && <DomainTab />}
      {activeTab === 'features' && <FeaturesTab />}
      {activeTab === 'preview' && <PreviewTab />}
    </div>
  );
};

export default WhiteLabelManager;
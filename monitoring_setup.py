"""
YouTube Automation Platform - Comprehensive Monitoring & Alerting System
Provides real-time monitoring, performance metrics, and automated alerting
"""

import asyncio
import logging
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI, BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Prometheus client not available. Install with: pip install prometheus-client")

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    active_publishing_jobs: int
    api_response_time: float
    database_response_time: float
    error_rate: float

@dataclass
class Alert:
    """Alert configuration and status"""
    name: str
    metric: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    enabled: bool = True
    cooldown_minutes: int = 15
    last_triggered: Optional[datetime] = None

class SystemMonitor:
    """Comprehensive system monitoring with alerting"""
    
    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.alerts: List[Alert] = []
        self.is_monitoring = False
        self.monitoring_interval = 30  # seconds
        self.max_history_hours = 24
        
        # Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self.registry = CollectorRegistry()
            self.setup_prometheus_metrics()
        
        self.setup_default_alerts()
    
    def setup_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prom_cpu_usage = Gauge(
            'system_cpu_usage_percent', 
            'System CPU usage percentage',
            registry=self.registry
        )
        self.prom_memory_usage = Gauge(
            'system_memory_usage_percent', 
            'System memory usage percentage',
            registry=self.registry
        )
        self.prom_disk_usage = Gauge(
            'system_disk_usage_percent', 
            'System disk usage percentage',
            registry=self.registry
        )
        self.prom_active_connections = Gauge(
            'websocket_connections_active', 
            'Active WebSocket connections',
            registry=self.registry
        )
        self.prom_publishing_jobs = Gauge(
            'publishing_jobs_active', 
            'Active publishing jobs',
            registry=self.registry
        )
        self.prom_api_response_time = Histogram(
            'api_response_time_seconds', 
            'API response time in seconds',
            registry=self.registry
        )
        self.prom_database_response_time = Gauge(
            'database_response_time_ms', 
            'Database response time in milliseconds',
            registry=self.registry
        )
        self.prom_error_rate = Gauge(
            'error_rate_percent', 
            'Error rate percentage',
            registry=self.registry
        )
    
    def setup_default_alerts(self):
        """Setup default alert configurations"""
        self.alerts = [
            Alert(
                name="High CPU Usage",
                metric="cpu_usage",
                threshold=80.0,
                comparison="gt",
                severity="high",
                message="System CPU usage is above 80%",
                cooldown_minutes=10
            ),
            Alert(
                name="High Memory Usage",
                metric="memory_usage",
                threshold=85.0,
                comparison="gt",
                severity="high",
                message="System memory usage is above 85%",
                cooldown_minutes=10
            ),
            Alert(
                name="Low Disk Space",
                metric="disk_usage",
                threshold=90.0,
                comparison="gt",
                severity="critical",
                message="Disk usage is above 90% - immediate action required",
                cooldown_minutes=5
            ),
            Alert(
                name="Slow API Response",
                metric="api_response_time",
                threshold=2.0,
                comparison="gt",
                severity="medium",
                message="API response time is above 2 seconds",
                cooldown_minutes=15
            ),
            Alert(
                name="High Error Rate",
                metric="error_rate",
                threshold=5.0,
                comparison="gt",
                severity="high",
                message="Error rate is above 5%",
                cooldown_minutes=5
            ),
            Alert(
                name="Database Slow Response",
                metric="database_response_time",
                threshold=1000.0,
                comparison="gt",
                severity="medium",
                message="Database response time is above 1000ms",
                cooldown_minutes=10
            )
        ]
    
    async def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Simulate active connections and jobs (replace with actual counters)
            active_connections = self.get_active_websocket_connections()
            active_jobs = self.get_active_publishing_jobs()
            
            # API response time (replace with actual measurement)
            api_response_time = await self.measure_api_response_time()
            
            # Database response time (replace with actual measurement)
            db_response_time = await self.measure_database_response_time()
            
            # Error rate (replace with actual calculation)
            error_rate = self.calculate_error_rate()
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                active_connections=active_connections,
                active_publishing_jobs=active_jobs,
                api_response_time=api_response_time,
                database_response_time=db_response_time,
                error_rate=error_rate
            )
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE:
                self.update_prometheus_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                active_connections=0,
                active_publishing_jobs=0,
                api_response_time=0.0,
                database_response_time=0.0,
                error_rate=0.0
            )
    
    def update_prometheus_metrics(self, metrics: SystemMetrics):
        """Update Prometheus metrics"""
        self.prom_cpu_usage.set(metrics.cpu_usage)
        self.prom_memory_usage.set(metrics.memory_usage)
        self.prom_disk_usage.set(metrics.disk_usage)
        self.prom_active_connections.set(metrics.active_connections)
        self.prom_publishing_jobs.set(metrics.active_publishing_jobs)
        self.prom_database_response_time.set(metrics.database_response_time)
        self.prom_error_rate.set(metrics.error_rate)
    
    def get_active_websocket_connections(self) -> int:
        """Get number of active WebSocket connections"""
        # This should be replaced with actual connection counter
        # from your realtime publisher
        try:
            # Simulate connection count
            connections = 0
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED' and conn.laddr.port in [8001, 3000]:
                    connections += 1
            return connections
        except:
            return 0
    
    def get_active_publishing_jobs(self) -> int:
        """Get number of active publishing jobs"""
        # This should be replaced with actual job counter
        # from your realtime publisher
        return 0  # Placeholder
    
    async def measure_api_response_time(self) -> float:
        """Measure API response time"""
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8001/health", timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                return end_time - start_time
            else:
                return 5.0  # Return high value for failed requests
        except:
            return 5.0  # Return high value for timeouts/errors
    
    async def measure_database_response_time(self) -> float:
        """Measure database response time"""
        try:
            start_time = time.time()
            # Simulate database query - replace with actual query
            await asyncio.sleep(0.01)  # Simulate 10ms response
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except:
            return 1000.0  # Return high value for errors
    
    def calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        # This should be replaced with actual error rate calculation
        # based on your logging/error tracking system
        return 0.0  # Placeholder
    
    def check_alerts(self, metrics: SystemMetrics):
        """Check metrics against alert thresholds"""
        current_time = datetime.now()
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            # Check cooldown period
            if (alert.last_triggered and 
                current_time - alert.last_triggered < timedelta(minutes=alert.cooldown_minutes)):
                continue
            
            # Get metric value
            metric_value = getattr(metrics, alert.metric, 0)
            
            # Check threshold
            should_trigger = False
            if alert.comparison == "gt" and metric_value > alert.threshold:
                should_trigger = True
            elif alert.comparison == "lt" and metric_value < alert.threshold:
                should_trigger = True
            elif alert.comparison == "eq" and metric_value == alert.threshold:
                should_trigger = True
            
            if should_trigger:
                alert.last_triggered = current_time
                asyncio.create_task(self.send_alert(alert, metrics))
    
    async def send_alert(self, alert: Alert, metrics: SystemMetrics):
        """Send alert notification"""
        try:
            # Prepare alert data
            alert_data = {
                "alert_name": alert.name,
                "severity": alert.severity,
                "message": alert.message,
                "metric_value": getattr(metrics, alert.metric, 0),
                "threshold": alert.threshold,
                "timestamp": metrics.timestamp.isoformat(),
                "system_metrics": asdict(metrics)
            }
            
            # Send email alert
            await self.send_email_alert(alert_data)
            
            # Send webhook alert (if configured)
            await self.send_webhook_alert(alert_data)
            
            # Send Slack alert (if configured)
            await self.send_slack_alert(alert_data)
            
            logger.warning(f"Alert triggered: {alert.name} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def send_email_alert(self, alert_data: Dict[str, Any]):
        """Send email alert notification"""
        try:
            import os
            
            smtp_host = os.getenv("SMTP_HOST")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            alert_email = os.getenv("ALERT_EMAIL", smtp_user)
            
            if not all([smtp_host, smtp_user, smtp_password, alert_email]):
                logger.warning("Email configuration incomplete, skipping email alert")
                return
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = alert_email
            msg['Subject'] = f"[{alert_data['severity'].upper()}] YouTube Automation Alert: {alert_data['alert_name']}"
            
            body = f"""
YouTube Automation Platform Alert

Alert: {alert_data['alert_name']}
Severity: {alert_data['severity'].upper()}
Message: {alert_data['message']}
Metric Value: {alert_data['metric_value']}
Threshold: {alert_data['threshold']}
Timestamp: {alert_data['timestamp']}

System Metrics:
- CPU Usage: {alert_data['system_metrics']['cpu_usage']:.1f}%
- Memory Usage: {alert_data['system_metrics']['memory_usage']:.1f}%
- Disk Usage: {alert_data['system_metrics']['disk_usage']:.1f}%
- Active Connections: {alert_data['system_metrics']['active_connections']}
- Active Jobs: {alert_data['system_metrics']['active_publishing_jobs']}
- API Response Time: {alert_data['system_metrics']['api_response_time']:.2f}s
- Database Response Time: {alert_data['system_metrics']['database_response_time']:.0f}ms
- Error Rate: {alert_data['system_metrics']['error_rate']:.1f}%

Please investigate and take appropriate action.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_user, alert_email, text)
            server.quit()
            
            logger.info(f"Email alert sent for: {alert_data['alert_name']}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    async def send_webhook_alert(self, alert_data: Dict[str, Any]):
        """Send webhook alert notification"""
        try:
            import os
            
            webhook_url = os.getenv("ALERT_WEBHOOK_URL")
            if not webhook_url:
                return
            
            payload = {
                "text": f"🚨 YouTube Automation Alert: {alert_data['alert_name']}",
                "attachments": [
                    {
                        "color": self.get_alert_color(alert_data['severity']),
                        "fields": [
                            {"title": "Severity", "value": alert_data['severity'].upper(), "short": True},
                            {"title": "Message", "value": alert_data['message'], "short": False},
                            {"title": "Metric Value", "value": str(alert_data['metric_value']), "short": True},
                            {"title": "Threshold", "value": str(alert_data['threshold']), "short": True},
                            {"title": "Timestamp", "value": alert_data['timestamp'], "short": False}
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent for: {alert_data['alert_name']}")
            
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
    
    async def send_slack_alert(self, alert_data: Dict[str, Any]):
        """Send Slack alert notification"""
        try:
            import os
            
            slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
            if not slack_webhook:
                return
            
            color_map = {
                "low": "#36a64f",      # Green
                "medium": "#ff9900",   # Orange
                "high": "#ff0000",     # Red
                "critical": "#8B0000"  # Dark Red
            }
            
            payload = {
                "text": f"🚨 YouTube Automation Platform Alert",
                "attachments": [
                    {
                        "color": color_map.get(alert_data['severity'], "#ff0000"),
                        "title": alert_data['alert_name'],
                        "text": alert_data['message'],
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert_data['severity'].upper(),
                                "short": True
                            },
                            {
                                "title": "Metric Value",
                                "value": f"{alert_data['metric_value']} (threshold: {alert_data['threshold']})",
                                "short": True
                            },
                            {
                                "title": "System Status",
                                "value": f"CPU: {alert_data['system_metrics']['cpu_usage']:.1f}% | Memory: {alert_data['system_metrics']['memory_usage']:.1f}% | Disk: {alert_data['system_metrics']['disk_usage']:.1f}%",
                                "short": False
                            }
                        ],
                        "footer": "YouTube Automation Monitoring",
                        "ts": int(datetime.fromisoformat(alert_data['timestamp']).timestamp())
                    }
                ]
            }
            
            response = requests.post(slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent for: {alert_data['alert_name']}")
            
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
    
    def get_alert_color(self, severity: str) -> str:
        """Get color code for alert severity"""
        color_map = {
            "low": "good",
            "medium": "warning", 
            "high": "danger",
            "critical": "#8B0000"
        }
        return color_map.get(severity, "danger")
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        logger.info("Starting system monitoring...")
        
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Clean old metrics (keep only last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Check alerts
                self.check_alerts(metrics)
                
                # Log current status
                logger.info(
                    f"System Status - CPU: {metrics.cpu_usage:.1f}%, "
                    f"Memory: {metrics.memory_usage:.1f}%, "
                    f"Disk: {metrics.disk_usage:.1f}%, "
                    f"API: {metrics.api_response_time:.2f}s"
                )
                
                # Wait for next interval
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_monitoring = False
        logger.info("Monitoring stopped")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 readings
        
        return {
            "current": asdict(self.metrics_history[-1]) if self.metrics_history else None,
            "averages": {
                "cpu_usage": sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
                "memory_usage": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                "api_response_time": sum(m.api_response_time for m in recent_metrics) / len(recent_metrics),
                "database_response_time": sum(m.database_response_time for m in recent_metrics) / len(recent_metrics),
            },
            "total_metrics": len(self.metrics_history),
            "monitoring_duration_hours": (
                (self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).total_seconds() / 3600
                if len(self.metrics_history) > 1 else 0
            )
        }
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus client not available"
        
        return generate_latest(self.registry).decode('utf-8')
    
    def add_custom_alert(self, alert: Alert):
        """Add a custom alert configuration"""
        self.alerts.append(alert)
        logger.info(f"Added custom alert: {alert.name}")
    
    def disable_alert(self, alert_name: str):
        """Disable a specific alert"""
        for alert in self.alerts:
            if alert.name == alert_name:
                alert.enabled = False
                logger.info(f"Disabled alert: {alert_name}")
                return
        logger.warning(f"Alert not found: {alert_name}")
    
    def enable_alert(self, alert_name: str):
        """Enable a specific alert"""
        for alert in self.alerts:
            if alert.name == alert_name:
                alert.enabled = True
                logger.info(f"Enabled alert: {alert_name}")
                return
        logger.warning(f"Alert not found: {alert_name}")

# Global monitor instance
system_monitor = SystemMonitor()

# FastAPI integration
def add_monitoring_endpoints(app: FastAPI):
    """Add monitoring endpoints to FastAPI app"""
    
    @app.get("/metrics")
    async def prometheus_metrics():
        """Prometheus metrics endpoint"""
        return system_monitor.get_prometheus_metrics()
    
    @app.get("/api/monitoring/status")
    async def monitoring_status():
        """Get current monitoring status"""
        return {
            "success": True,
            "data": {
                "is_monitoring": system_monitor.is_monitoring,
                "monitoring_interval": system_monitor.monitoring_interval,
                "alerts_count": len(system_monitor.alerts),
                "enabled_alerts": len([a for a in system_monitor.alerts if a.enabled]),
                "metrics_history_count": len(system_monitor.metrics_history)
            }
        }
    
    @app.get("/api/monitoring/metrics")
    async def get_metrics():
        """Get system metrics summary"""
        return {
            "success": True,
            "data": system_monitor.get_metrics_summary()
        }
    
    @app.get("/api/monitoring/alerts")
    async def get_alerts():
        """Get alert configurations"""
        return {
            "success": True,
            "data": {
                "alerts": [
                    {
                        "name": alert.name,
                        "metric": alert.metric,
                        "threshold": alert.threshold,
                        "comparison": alert.comparison,
                        "severity": alert.severity,
                        "enabled": alert.enabled,
                        "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None
                    }
                    for alert in system_monitor.alerts
                ]
            }
        }
    
    @app.post("/api/monitoring/alerts/{alert_name}/toggle")
    async def toggle_alert(alert_name: str):
        """Enable/disable an alert"""
        for alert in system_monitor.alerts:
            if alert.name == alert_name:
                alert.enabled = not alert.enabled
                action = "enabled" if alert.enabled else "disabled"
                return {
                    "success": True,
                    "message": f"Alert {action}: {alert_name}"
                }
        
        return {
            "success": False,
            "error": f"Alert not found: {alert_name}"
        }
    
    @app.post("/api/monitoring/start")
    async def start_monitoring(background_tasks: BackgroundTasks):
        """Start system monitoring"""
        if system_monitor.is_monitoring:
            return {
                "success": False,
                "message": "Monitoring is already running"
            }
        
        background_tasks.add_task(system_monitor.start_monitoring)
        return {
            "success": True,
            "message": "Monitoring started"
        }
    
    @app.post("/api/monitoring/stop")
    async def stop_monitoring():
        """Stop system monitoring"""
        system_monitor.stop_monitoring()
        return {
            "success": True,
            "message": "Monitoring stopped"
        }

# Example usage for adding to main application
def setup_monitoring(app: FastAPI):
    """Setup monitoring for the application"""
    add_monitoring_endpoints(app)
    
    # Start monitoring automatically
    @app.on_event("startup")
    async def startup_monitoring():
        asyncio.create_task(system_monitor.start_monitoring())
    
    @app.on_event("shutdown")
    async def shutdown_monitoring():
        system_monitor.stop_monitoring()

if __name__ == "__main__":
    # Test monitoring setup
    import asyncio
    
    async def test_monitoring():
        logger.info("Starting monitoring test...")
        
        # Start monitoring for 60 seconds
        monitor_task = asyncio.create_task(system_monitor.start_monitoring())
        
        # Wait a bit then check metrics
        await asyncio.sleep(10)
        
        summary = system_monitor.get_metrics_summary()
        print(f"Metrics Summary: {json.dumps(summary, indent=2, default=str)}")
        
        # Stop monitoring
        system_monitor.stop_monitoring()
        await monitor_task
    
    asyncio.run(test_monitoring())
#!/bin/bash

# Health Check Script for YouTube Automation Platform
# Comprehensive health monitoring for all system components

set -euo pipefail

# Configuration
HEALTH_LOG="/backups/logs/health_check_$(date +%Y%m%d).log"
METRICS_FILE="/backups/metrics/health_check_metrics.prom"
ALERT_THRESHOLD_CPU=85
ALERT_THRESHOLD_MEMORY=90
ALERT_THRESHOLD_DISK=95

# Service endpoints
BACKEND_URL="${BACKEND_URL:-http://backend:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://frontend:3000}"
REDIS_HOST="${REDIS_HOST:-redis}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$HEALTH_LOG"
}

# Health check results
HEALTH_STATUS=1  # 1 = healthy, 0 = unhealthy
HEALTH_DETAILS=""

# Function to check service health
check_service() {
    local service_name="$1"
    local check_command="$2"
    local timeout="${3:-10}"
    
    log "Checking $service_name..."
    
    if timeout "$timeout" bash -c "$check_command" 2>/dev/null; then
        log "✓ $service_name: HEALTHY"
        echo "service_health{service=\"$service_name\"} 1" >> "$METRICS_FILE"
        return 0
    else
        log "✗ $service_name: UNHEALTHY"
        echo "service_health{service=\"$service_name\"} 0" >> "$METRICS_FILE"
        HEALTH_STATUS=0
        HEALTH_DETAILS="${HEALTH_DETAILS}$service_name: UNHEALTHY; "
        return 1
    fi
}

# Function to check system resources
check_system_resources() {
    log "Checking system resources..."
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d% -f1)
    CPU_USAGE=${CPU_USAGE%.*}  # Remove decimal part
    
    log "CPU Usage: ${CPU_USAGE}%"
    echo "system_cpu_usage_percent $CPU_USAGE" >> "$METRICS_FILE"
    
    if [ "$CPU_USAGE" -gt "$ALERT_THRESHOLD_CPU" ]; then
        log "⚠ CPU usage is high: ${CPU_USAGE}%"
        HEALTH_DETAILS="${HEALTH_DETAILS}High CPU usage (${CPU_USAGE}%); "
    fi
    
    # Memory usage
    MEMORY_INFO=$(free | grep Mem)
    MEMORY_TOTAL=$(echo $MEMORY_INFO | awk '{print $2}')
    MEMORY_USED=$(echo $MEMORY_INFO | awk '{print $3}')
    MEMORY_USAGE=$((MEMORY_USED * 100 / MEMORY_TOTAL))
    
    log "Memory Usage: ${MEMORY_USAGE}%"
    echo "system_memory_usage_percent $MEMORY_USAGE" >> "$METRICS_FILE"
    echo "system_memory_total_bytes $((MEMORY_TOTAL * 1024))" >> "$METRICS_FILE"
    echo "system_memory_used_bytes $((MEMORY_USED * 1024))" >> "$METRICS_FILE"
    
    if [ "$MEMORY_USAGE" -gt "$ALERT_THRESHOLD_MEMORY" ]; then
        log "⚠ Memory usage is high: ${MEMORY_USAGE}%"
        HEALTH_DETAILS="${HEALTH_DETAILS}High memory usage (${MEMORY_USAGE}%); "
    fi
    
    # Disk usage
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d% -f1)
    log "Disk Usage: ${DISK_USAGE}%"
    echo "system_disk_usage_percent $DISK_USAGE" >> "$METRICS_FILE"
    
    if [ "$DISK_USAGE" -gt "$ALERT_THRESHOLD_DISK" ]; then
        log "⚠ Disk usage is critical: ${DISK_USAGE}%"
        HEALTH_DETAILS="${HEALTH_DETAILS}Critical disk usage (${DISK_USAGE}%); "
        HEALTH_STATUS=0
    fi
    
    # Load average
    LOAD_AVERAGE=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
    log "Load Average: $LOAD_AVERAGE"
    echo "system_load_average $LOAD_AVERAGE" >> "$METRICS_FILE"
    
    # Available disk space for uploads
    if [ -d "/app/uploads" ]; then
        UPLOADS_SPACE=$(df /app/uploads | tail -1 | awk '{print $4}')
        UPLOADS_SPACE_GB=$((UPLOADS_SPACE / 1024 / 1024))
        log "Available space for uploads: ${UPLOADS_SPACE_GB}GB"
        echo "uploads_available_space_gb $UPLOADS_SPACE_GB" >> "$METRICS_FILE"
        
        if [ "$UPLOADS_SPACE_GB" -lt 5 ]; then
            log "⚠ Low disk space for uploads: ${UPLOADS_SPACE_GB}GB"
            HEALTH_DETAILS="${HEALTH_DETAILS}Low upload space (${UPLOADS_SPACE_GB}GB); "
        fi
    fi
}

# Function to check network connectivity
check_network() {
    log "Checking network connectivity..."
    
    # Check internet connectivity
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log "✓ Internet connectivity: OK"
        echo "network_internet_connectivity 1" >> "$METRICS_FILE"
    else
        log "✗ Internet connectivity: FAILED"
        echo "network_internet_connectivity 0" >> "$METRICS_FILE"
        HEALTH_DETAILS="${HEALTH_DETAILS}No internet connectivity; "
    fi
    
    # Check DNS resolution
    if nslookup google.com > /dev/null 2>&1; then
        log "✓ DNS resolution: OK"
        echo "network_dns_resolution 1" >> "$METRICS_FILE"
    else
        log "✗ DNS resolution: FAILED"
        echo "network_dns_resolution 0" >> "$METRICS_FILE"
        HEALTH_DETAILS="${HEALTH_DETAILS}DNS resolution failed; "
    fi
}

# Function to check application-specific health
check_application_health() {
    log "Checking application-specific health..."
    
    # Check if AI models are accessible
    if [ -d "/app/models" ]; then
        MODEL_COUNT=$(find /app/models -name "*.safetensors" -o -name "*.bin" -o -name "*.pth" | wc -l)
        log "AI models available: $MODEL_COUNT"
        echo "ai_models_count $MODEL_COUNT" >> "$METRICS_FILE"
        
        if [ "$MODEL_COUNT" -eq 0 ]; then
            log "⚠ No AI models found"
            HEALTH_DETAILS="${HEALTH_DETAILS}No AI models found; "
        fi
    fi
    
    # Check video generation queue
    if command -v redis-cli &> /dev/null; then
        QUEUE_LENGTH=$(redis-cli -h "$REDIS_HOST" LLEN celery 2>/dev/null || echo "0")
        log "Celery queue length: $QUEUE_LENGTH"
        echo "celery_queue_length $QUEUE_LENGTH" >> "$METRICS_FILE"
        
        if [ "$QUEUE_LENGTH" -gt 1000 ]; then
            log "⚠ High queue length: $QUEUE_LENGTH"
            HEALTH_DETAILS="${HEALTH_DETAILS}High queue length ($QUEUE_LENGTH); "
        fi
    fi
    
    # Check recent video generation success rate
    if [ -f "/app/logs/video_generation.log" ]; then
        RECENT_FAILURES=$(grep -c "ERROR\|FAILED" /app/logs/video_generation.log | tail -100 || echo "0")
        log "Recent video generation failures: $RECENT_FAILURES"
        echo "recent_video_generation_failures $RECENT_FAILURES" >> "$METRICS_FILE"
        
        if [ "$RECENT_FAILURES" -gt 10 ]; then
            log "⚠ High number of recent failures: $RECENT_FAILURES"
            HEALTH_DETAILS="${HEALTH_DETAILS}High video generation failures ($RECENT_FAILURES); "
        fi
    fi
}

# Function to check backup health
check_backup_health() {
    log "Checking backup health..."
    
    # Check last successful backups
    BACKUP_DIR="/backups"
    
    # PostgreSQL backup
    if [ -f "$BACKUP_DIR/postgres/latest_backup_summary.json" ]; then
        POSTGRES_BACKUP_TIME=$(jq -r '.timestamp' "$BACKUP_DIR/postgres/latest_backup_summary.json" 2>/dev/null || echo "unknown")
        POSTGRES_BACKUP_EPOCH=$(date -d "${POSTGRES_BACKUP_TIME:0:8} ${POSTGRES_BACKUP_TIME:9:6}" +%s 2>/dev/null || echo "0")
        CURRENT_EPOCH=$(date +%s)
        POSTGRES_BACKUP_AGE=$((CURRENT_EPOCH - POSTGRES_BACKUP_EPOCH))
        
        log "Last PostgreSQL backup: $((POSTGRES_BACKUP_AGE / 3600)) hours ago"
        echo "backup_age_hours{type=\"postgres\"} $((POSTGRES_BACKUP_AGE / 3600))" >> "$METRICS_FILE"
        
        if [ "$POSTGRES_BACKUP_AGE" -gt 172800 ]; then  # 48 hours
            log "⚠ PostgreSQL backup is old: $((POSTGRES_BACKUP_AGE / 3600)) hours"
            HEALTH_DETAILS="${HEALTH_DETAILS}Old PostgreSQL backup; "
        fi
    else
        log "⚠ No PostgreSQL backup summary found"
        HEALTH_DETAILS="${HEALTH_DETAILS}No PostgreSQL backup; "
    fi
    
    # Redis backup
    if [ -f "$BACKUP_DIR/redis/latest_backup_summary.json" ]; then
        REDIS_BACKUP_TIME=$(jq -r '.timestamp' "$BACKUP_DIR/redis/latest_backup_summary.json" 2>/dev/null || echo "unknown")
        REDIS_BACKUP_EPOCH=$(date -d "${REDIS_BACKUP_TIME:0:8} ${REDIS_BACKUP_TIME:9:6}" +%s 2>/dev/null || echo "0")
        REDIS_BACKUP_AGE=$((CURRENT_EPOCH - REDIS_BACKUP_EPOCH))
        
        log "Last Redis backup: $((REDIS_BACKUP_AGE / 3600)) hours ago"
        echo "backup_age_hours{type=\"redis\"} $((REDIS_BACKUP_AGE / 3600))" >> "$METRICS_FILE"
        
        if [ "$REDIS_BACKUP_AGE" -gt 172800 ]; then  # 48 hours
            log "⚠ Redis backup is old: $((REDIS_BACKUP_AGE / 3600)) hours"
            HEALTH_DETAILS="${HEALTH_DETAILS}Old Redis backup; "
        fi
    fi
}

# Function to check SSL certificate
check_ssl_certificate() {
    local domain="${DOMAIN_NAME:-localhost}"
    
    if [ "$domain" != "localhost" ]; then
        log "Checking SSL certificate for $domain..."
        
        # Check certificate expiration
        CERT_EXPIRY=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | \
                     openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
        
        if [ -n "$CERT_EXPIRY" ]; then
            CERT_EXPIRY_EPOCH=$(date -d "$CERT_EXPIRY" +%s)
            CURRENT_EPOCH=$(date +%s)
            CERT_DAYS_LEFT=$(( (CERT_EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
            
            log "SSL certificate expires in $CERT_DAYS_LEFT days"
            echo "ssl_certificate_days_until_expiry $CERT_DAYS_LEFT" >> "$METRICS_FILE"
            
            if [ "$CERT_DAYS_LEFT" -lt 30 ]; then
                log "⚠ SSL certificate expires soon: $CERT_DAYS_LEFT days"
                HEALTH_DETAILS="${HEALTH_DETAILS}SSL cert expires in $CERT_DAYS_LEFT days; "
            fi
        else
            log "⚠ Could not check SSL certificate"
            HEALTH_DETAILS="${HEALTH_DETAILS}SSL certificate check failed; "
        fi
    fi
}

# Initialize metrics file
mkdir -p "$(dirname "$METRICS_FILE")" "$(dirname "$HEALTH_LOG")"
cat > "$METRICS_FILE" << EOF
# HELP health_check_timestamp Timestamp of last health check
# TYPE health_check_timestamp gauge
health_check_timestamp $(date +%s)

# HELP service_health Health status of services (1=healthy, 0=unhealthy)
# TYPE service_health gauge

# HELP system_cpu_usage_percent CPU usage percentage
# TYPE system_cpu_usage_percent gauge

# HELP system_memory_usage_percent Memory usage percentage
# TYPE system_memory_usage_percent gauge

# HELP system_disk_usage_percent Disk usage percentage
# TYPE system_disk_usage_percent gauge

# HELP overall_health_status Overall system health status
# TYPE overall_health_status gauge

EOF

log "=== YouTube Automation Platform Health Check ==="
log "Starting comprehensive health check..."

# Check all services
check_service "backend" "curl -f -s $BACKEND_URL/health > /dev/null"
check_service "frontend" "curl -f -s $FRONTEND_URL > /dev/null"
check_service "redis" "redis-cli -h $REDIS_HOST ping | grep -q PONG"
check_service "postgres" "pg_isready -h $POSTGRES_HOST -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-youtube_automation}"

# Check system resources
check_system_resources

# Check network connectivity
check_network

# Check application-specific health
check_application_health

# Check backup health
check_backup_health

# Check SSL certificate
check_ssl_certificate

# Overall health status
echo "overall_health_status $HEALTH_STATUS" >> "$METRICS_FILE"

if [ "$HEALTH_STATUS" -eq 1 ]; then
    log "=== OVERALL STATUS: HEALTHY ==="
else
    log "=== OVERALL STATUS: UNHEALTHY ==="
    log "Issues found: $HEALTH_DETAILS"
fi

# Create health summary
HEALTH_SUMMARY_FILE="/backups/health_summary.json"
cat > "$HEALTH_SUMMARY_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "overall_status": $([ "$HEALTH_STATUS" -eq 1 ] && echo "\"healthy\"" || echo "\"unhealthy\""),
  "details": "$HEALTH_DETAILS",
  "last_check": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

log "Health check completed. Status: $([ "$HEALTH_STATUS" -eq 1 ] && echo "HEALTHY" || echo "UNHEALTHY")"

exit $HEALTH_STATUS
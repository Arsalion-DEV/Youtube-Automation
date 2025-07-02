#!/bin/bash

# Application Data Backup Script for YouTube Automation Platform
# Backs up video uploads, models, configs, and other application data

set -euo pipefail

# Configuration
BACKUP_DIR="/backups/uploads"
UPLOADS_DIR="/app_uploads"
MODELS_DIR="/app/models"
CONFIGS_DIR="/app/configs"
PLUGINS_DIR="/app/plugins"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/backups/logs/uploads_backup_${TIMESTAMP}.log"

# AWS S3 Configuration (optional)
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Metrics for monitoring
METRICS_FILE="/backups/metrics/uploads_backup_metrics.prom"

# Exclusions
EXCLUDE_PATTERNS=(
    "*.tmp"
    "*.temp"
    "*/.cache/*"
    "*/tmp/*"
    "__pycache__"
    "*.pyc"
    "*.log"
    ".git"
    "node_modules"
)

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log "ERROR: Application data backup failed with exit code $exit_code"
        # Update metrics
        echo "uploads_backup_last_success_timestamp $(date +%s)" > "$METRICS_FILE"
        echo "uploads_backup_status 0" >> "$METRICS_FILE"
    fi
    exit $exit_code
}

trap cleanup EXIT

# Create backup directories
mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")" "$(dirname "$METRICS_FILE")"

log "Starting application data backup"

# Start timing
START_TIME=$(date +%s)

# Build exclude arguments for tar
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

# Function to backup a directory
backup_directory() {
    local source_dir="$1"
    local backup_name="$2"
    local backup_file="$BACKUP_DIR/${backup_name}_${TIMESTAMP}.tar.gz"
    
    if [ ! -d "$source_dir" ]; then
        log "WARNING: Directory $source_dir does not exist, skipping"
        return 0
    fi
    
    log "Backing up $source_dir to $backup_file"
    
    # Calculate source size
    local source_size=$(du -sb "$source_dir" | cut -f1)
    log "Source directory size: $(numfmt --to=iec $source_size)"
    
    # Create backup with compression
    if tar -czf "$backup_file" $EXCLUDE_ARGS -C "$(dirname "$source_dir")" "$(basename "$source_dir")" 2>>"$LOG_FILE"; then
        local backup_size=$(stat -c%s "$backup_file")
        local compression_ratio=$((source_size * 100 / backup_size))
        log "Backup created: $(numfmt --to=iec $backup_size) (${compression_ratio}% compression)"
        
        # Verify backup integrity
        if tar -tzf "$backup_file" >/dev/null 2>>"$LOG_FILE"; then
            log "Backup integrity verified for $backup_name"
            echo "$backup_file:$backup_size:$source_size"
        else
            log "ERROR: Backup integrity check failed for $backup_name"
            return 1
        fi
    else
        log "ERROR: Failed to create backup for $source_dir"
        return 1
    fi
}

# Function to calculate directory statistics
calculate_stats() {
    local dir="$1"
    local name="$2"
    
    if [ ! -d "$dir" ]; then
        return 0
    fi
    
    local total_size=$(du -sb "$dir" | cut -f1)
    local file_count=$(find "$dir" -type f | wc -l)
    local dir_count=$(find "$dir" -type d | wc -l)
    
    log "$name statistics: Size: $(numfmt --to=iec $total_size), Files: $file_count, Directories: $dir_count"
    
    # Store for metrics
    echo "${name}_size_bytes $total_size" >> "/tmp/backup_stats_${TIMESTAMP}"
    echo "${name}_file_count $file_count" >> "/tmp/backup_stats_${TIMESTAMP}"
    echo "${name}_directory_count $dir_count" >> "/tmp/backup_stats_${TIMESTAMP}"
}

# Initialize stats file
echo "" > "/tmp/backup_stats_${TIMESTAMP}"

# Calculate directory statistics
log "Calculating directory statistics..."
calculate_stats "$UPLOADS_DIR" "uploads"
calculate_stats "$MODELS_DIR" "models"
calculate_stats "$CONFIGS_DIR" "configs"
calculate_stats "$PLUGINS_DIR" "plugins"

# Backup video uploads (incremental backup for large files)
log "Starting video uploads backup..."
UPLOADS_BACKUP_INFO=""
if [ -d "$UPLOADS_DIR" ]; then
    # For uploads, we might want to do incremental backups to save space
    LAST_BACKUP_FILE="$BACKUP_DIR/.last_uploads_backup"
    
    if [ -f "$LAST_BACKUP_FILE" ]; then
        # Incremental backup since last backup
        log "Performing incremental backup of uploads since last backup"
        UPLOADS_BACKUP_FILE="$BACKUP_DIR/uploads_incremental_${TIMESTAMP}.tar.gz"
        
        if find "$UPLOADS_DIR" -newer "$LAST_BACKUP_FILE" -type f -print0 | \
           tar -czf "$UPLOADS_BACKUP_FILE" $EXCLUDE_ARGS --null -T - 2>>"$LOG_FILE"; then
            UPLOADS_BACKUP_SIZE=$(stat -c%s "$UPLOADS_BACKUP_FILE")
            log "Incremental uploads backup created: $(numfmt --to=iec $UPLOADS_BACKUP_SIZE)"
            UPLOADS_BACKUP_INFO="$UPLOADS_BACKUP_FILE:$UPLOADS_BACKUP_SIZE:incremental"
        else
            log "WARNING: Incremental uploads backup failed, performing full backup"
            UPLOADS_BACKUP_INFO=$(backup_directory "$UPLOADS_DIR" "uploads_full")
        fi
    else
        # Full backup
        log "Performing full backup of uploads (first time)"
        UPLOADS_BACKUP_INFO=$(backup_directory "$UPLOADS_DIR" "uploads_full")
    fi
    
    # Update last backup timestamp
    touch "$LAST_BACKUP_FILE"
else
    log "Uploads directory not found, skipping"
fi

# Backup AI models (full backup, but less frequent)
log "Starting AI models backup..."
MODELS_BACKUP_INFO=""
if [ -d "$MODELS_DIR" ]; then
    # Check if models backup is needed (models don't change often)
    MODELS_BACKUP_FLAG="$BACKUP_DIR/.last_models_backup"
    
    if [ ! -f "$MODELS_BACKUP_FLAG" ] || [ $(find "$MODELS_DIR" -newer "$MODELS_BACKUP_FLAG" -type f | wc -l) -gt 0 ]; then
        log "Models have changed since last backup, creating new backup"
        MODELS_BACKUP_INFO=$(backup_directory "$MODELS_DIR" "models")
        touch "$MODELS_BACKUP_FLAG"
    else
        log "Models haven't changed since last backup, skipping"
        MODELS_BACKUP_INFO="skipped:0:0"
    fi
else
    log "Models directory not found, skipping"
fi

# Backup configurations (always backup - small size)
log "Starting configurations backup..."
CONFIGS_BACKUP_INFO=$(backup_directory "$CONFIGS_DIR" "configs")

# Backup plugins (always backup - small size)
log "Starting plugins backup..."
PLUGINS_BACKUP_INFO=$(backup_directory "$PLUGINS_DIR" "plugins")

# Parse backup information
parse_backup_info() {
    local info="$1"
    if [ "$info" = "skipped:0:0" ]; then
        echo "0"
    else
        echo "$info" | cut -d: -f2
    fi
}

UPLOADS_SIZE=$(parse_backup_info "$UPLOADS_BACKUP_INFO")
MODELS_SIZE=$(parse_backup_info "$MODELS_BACKUP_INFO")
CONFIGS_SIZE=$(parse_backup_info "$CONFIGS_BACKUP_INFO")
PLUGINS_SIZE=$(parse_backup_info "$PLUGINS_BACKUP_INFO")

TOTAL_BACKUP_SIZE=$((UPLOADS_SIZE + MODELS_SIZE + CONFIGS_SIZE + PLUGINS_SIZE))

log "Total backup size: $(numfmt --to=iec $TOTAL_BACKUP_SIZE)"

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ]; then
    log "Uploading backups to S3 bucket: $S3_BUCKET"
    
    S3_PREFIX="application_backups/$(date +%Y/%m/%d)"
    
    for backup_file in "$BACKUP_DIR"/*_${TIMESTAMP}.tar.gz; do
        if [ -f "$backup_file" ]; then
            local filename=$(basename "$backup_file")
            local s3_key="$S3_PREFIX/$filename"
            
            if aws s3 cp "$backup_file" "s3://$S3_BUCKET/$s3_key" --region "$AWS_REGION" 2>>"$LOG_FILE"; then
                log "Uploaded $filename to S3 successfully"
            else
                log "WARNING: Failed to upload $filename to S3"
            fi
        fi
    done
fi

# Clean up old local backups
log "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>>"$LOG_FILE" || true

# Clean up old S3 backups if configured
if [ -n "$S3_BUCKET" ]; then
    log "Cleaning up old S3 backups..."
    CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
    aws s3 ls "s3://$S3_BUCKET/application_backups/" --recursive --region "$AWS_REGION" | \
    awk '$1 < "'$CUTOFF_DATE'" {print $4}' | \
    while read -r key; do
        aws s3 rm "s3://$S3_BUCKET/$key" --region "$AWS_REGION" 2>>"$LOG_FILE" || true
    done
fi

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log "Application data backup completed successfully in ${DURATION} seconds"

# Update metrics for monitoring
cat > "$METRICS_FILE" << EOF
# HELP uploads_backup_last_success_timestamp Timestamp of last successful uploads backup
# TYPE uploads_backup_last_success_timestamp gauge
uploads_backup_last_success_timestamp $END_TIME

# HELP uploads_backup_duration_seconds Duration of uploads backup in seconds
# TYPE uploads_backup_duration_seconds gauge
uploads_backup_duration_seconds $DURATION

# HELP uploads_backup_size_bytes Size of backup files in bytes
# TYPE uploads_backup_size_bytes gauge
uploads_backup_size_bytes{type="uploads"} $UPLOADS_SIZE
uploads_backup_size_bytes{type="models"} $MODELS_SIZE
uploads_backup_size_bytes{type="configs"} $CONFIGS_SIZE
uploads_backup_size_bytes{type="plugins"} $PLUGINS_SIZE
uploads_backup_size_bytes{type="total"} $TOTAL_BACKUP_SIZE

$(cat "/tmp/backup_stats_${TIMESTAMP}")

# HELP uploads_backup_status Status of backup (1=success, 0=failure)
# TYPE uploads_backup_status gauge
uploads_backup_status 1
EOF

# Clean up temporary stats file
rm -f "/tmp/backup_stats_${TIMESTAMP}"

log "Application data backup metrics updated"

# Create a backup summary
SUMMARY_FILE="$BACKUP_DIR/latest_backup_summary.json"
cat > "$SUMMARY_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "backup_files": {
    "uploads": "$(echo "$UPLOADS_BACKUP_INFO" | cut -d: -f1 | xargs basename 2>/dev/null || echo "skipped")",
    "models": "$(echo "$MODELS_BACKUP_INFO" | cut -d: -f1 | xargs basename 2>/dev/null || echo "skipped")",
    "configs": "$(echo "$CONFIGS_BACKUP_INFO" | cut -d: -f1 | xargs basename 2>/dev/null || echo "none")",
    "plugins": "$(echo "$PLUGINS_BACKUP_INFO" | cut -d: -f1 | xargs basename 2>/dev/null || echo "none")"
  },
  "sizes_bytes": {
    "uploads": $UPLOADS_SIZE,
    "models": $MODELS_SIZE,
    "configs": $CONFIGS_SIZE,
    "plugins": $PLUGINS_SIZE,
    "total": $TOTAL_BACKUP_SIZE
  },
  "duration_seconds": $DURATION,
  "s3_uploaded": $([ -n "$S3_BUCKET" ] && echo "true" || echo "false"),
  "status": "success"
}
EOF

log "Application data backup completed successfully!"
log "Summary: Total size: $(numfmt --to=iec $TOTAL_BACKUP_SIZE), Duration: ${DURATION}s"

exit 0
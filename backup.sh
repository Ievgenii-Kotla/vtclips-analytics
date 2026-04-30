#!/bin/bash
BACKUP_DIR=/home/USERNAME/vtclips-analytics/data/backups
TIMESTAMP=$(date +%Y%m%d)

# Create backup
docker compose -f /home/USERNAME/vtclips-analytics/compose.yaml exec -T postgres-db pg_dump -U POSTGRESUSERNAME -h localhost -p PORT -F c -v -f /app/data/backups/backup_$TIMESTAMP.dump vtc

# Only delete old backups if dump succeeded
if [ $? -eq 0 ]; then
    find $BACKUP_DIR -name "backup_*.dump" -mtime +100 -delete
else
    echo "Backup failed, skipping cleanup"
fi

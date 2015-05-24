. ./settings.sh

export PGPASSWORD="$DB_PASSWORD"

SQL='VACUUM;'
psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

SQL='VACUUM ANALYZE;'
psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

. ./settings.sh

export PGPASSWORD="$DB_PASSWORD"

SQL='VACUUM FULL;'
psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

SQL='REINDEX TABLE django_session;'
psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

SQL='REINDEX TABLE main_cart;'
psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

SQL='REINDEX TABLE main_cartitem;'
psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

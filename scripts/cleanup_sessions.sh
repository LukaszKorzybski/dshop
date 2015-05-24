. ./settings.sh

SQL='DELETE FROM main_cartitem WHERE owner_id IN (SELECT id FROM main_cart WHERE is_order = false AND session_key IN (SELECT session_key FROM django_session WHERE expire_date < now())); DELETE FROM main_cart WHERE is_order = false AND session_key IN (SELECT session_key FROM django_session WHERE expire_date < now()); DELETE FROM django_session WHERE expire_date < now();'

export PGPASSWORD="$DB_PASSWORD"

psql -c "$SQL" -h "$DB_HOST" -U "$DB_USER" "$DB_NAME"

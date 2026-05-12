set -e

for file in /clickhouse/migrations/*.sql; do
    echo "Applying $file"
    clickhouse-client \
        --host clickhouse \
        --user "$CLICKHOUSE_USER" \
        --password "$CLICKHOUSE_PASSWORD" \
        --multiquery < "$file"
done

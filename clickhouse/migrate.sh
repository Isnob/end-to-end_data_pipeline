set -e

for file in /clickhouse/migrations/*.sql; do
    echo "Applying $file"
    clickhouse-client --host clickhouse --multiquery < "$file"
done

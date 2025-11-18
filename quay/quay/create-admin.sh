#!/bin/bash
set -e

echo "🔧 Creating Quay admin user in PostgreSQL..."

ADMIN_USER='admin'
ADMIN_PASSWORD='admin123'

docker exec -i quay-quay-pg-db-1 psql -U quay -d quay <<SQL
CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO public.user (username, email, password_hash, verified, organization, robot, invoice_email, enabled, last_invalid_login)
VALUES ('$ADMIN_USER', '$ADMIN_USER@example.com', crypt('$ADMIN_PASSWORD', gen_salt('bf')), true, false, false, false, true, NOW())
ON CONFLICT (username) DO NOTHING;
SQL

TEST_USER='user'
TEST_PASSWORD='testt123'

docker exec -i quay-quay-pg-db-1 psql -U quay -d quay <<SQL
CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO public.user (username, email, password_hash, verified, organization, robot, invoice_email, enabled, last_invalid_login)
VALUES ('$TEST_USER', '$TEST_USER@example.com', crypt('$TEST_PASSWORD', gen_salt('bf')), true, false, false, false, true, NOW())
ON CONFLICT (username) DO NOTHING;
SQL

echo "✅ Admin user '$ADMIN_USER' (password: $ADMIN_PASSWORD) ensured."
echo "✅ Test user '$TEST_USER' (password: $TEST_PASSWORD) ensured."
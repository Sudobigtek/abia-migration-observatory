-- Create all databases for the platform
CREATE DATABASE abia_app;
CREATE DATABASE ckan;
CREATE DATABASE ckan_datastore;
CREATE DATABASE superset;
CREATE DATABASE odkc;
CREATE DATABASE camunda;

-- Create application user
CREATE USER abia_admin WITH PASSWORD 'your-postgres-app-user-password-from-bitwarden';
GRANT ALL PRIVILEGES ON DATABASE abia_migration TO abia_admin;
GRANT ALL PRIVILEGES ON DATABASE abia_app TO abia_admin;
GRANT ALL PRIVILEGES ON DATABASE ckan TO abia_admin;
GRANT ALL PRIVILEGES ON DATABASE superset TO abia_admin;
GRANT ALL PRIVILEGES ON DATABASE odkc TO abia_admin;
GRANT ALL PRIVILEGES ON DATABASE camunda TO abia_admin;

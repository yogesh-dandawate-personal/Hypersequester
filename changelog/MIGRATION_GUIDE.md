# Migration Guide - Hypersequester

This guide provides instructions for migrating between different versions of Hypersequester and upgrading existing installations.

## Table of Contents

1. [Version 0.1.0 - Initial Setup](#version-010---initial-setup)
2. [General Migration Principles](#general-migration-principles)
3. [Database Migrations](#database-migrations)
4. [Configuration Updates](#configuration-updates)
5. [Data Migration](#data-migration)
6. [Troubleshooting](#troubleshooting)

## Version 0.1.0 - Initial Setup

### New Installation

This is the initial release, so no migration is required. Follow the setup instructions:

```bash
# Clone the repository
git clone https://github.com/Instoradmin/Hypersequester.git
cd Hypersequester

# Run automated setup
./scripts/setup.sh

# Start the application
docker-compose up --build
```

### From Development Branch

If you were working with the development branch before this release:

#### 1. Backup Your Work
```bash
# Backup any custom changes
git stash push -m "Backup before v0.1.0 migration"

# Backup database (if you have data)
pg_dump hypersequester_dev > backup_pre_v0.1.0.sql
```

#### 2. Update to Latest
```bash
# Fetch latest changes
git fetch origin

# Switch to Development branch
git checkout Development

# Pull latest changes
git pull origin Development
```

#### 3. Update Dependencies
```bash
# Update Python dependencies
pip install -r requirements.txt

# Update Node.js dependencies
npm install
```

#### 4. Database Migration
```bash
# Run database migrations
python src/manage.py db upgrade

# Verify migration
python src/manage.py db current
```

#### 5. Configuration Update
```bash
# Update environment configuration
cp .env.example .env
# Edit .env with your specific settings
```

## General Migration Principles

### Before Any Migration

1. **Backup Everything**
   - Database dump
   - Configuration files
   - Custom code changes
   - Data files

2. **Test in Development**
   - Never migrate production directly
   - Test migration process in development environment
   - Verify all functionality works

3. **Plan Downtime**
   - Schedule maintenance window
   - Notify users of expected downtime
   - Prepare rollback plan

### Migration Process

1. **Pre-migration Checks**
   ```bash
   # Check current version
   git describe --tags
   
   # Check database status
   python src/manage.py db current
   
   # Check system health
   curl http://localhost:5000/health
   ```

2. **Backup Procedures**
   ```bash
   # Database backup
   pg_dump hypersequester > backup_$(date +%Y%m%d_%H%M%S).sql
   
   # Configuration backup
   cp -r config config_backup_$(date +%Y%m%d_%H%M%S)
   
   # Data backup
   tar -czf data_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/
   ```

3. **Migration Execution**
   ```bash
   # Stop services
   docker-compose down
   
   # Update code
   git pull origin Development
   
   # Update dependencies
   pip install -r requirements.txt
   npm install
   
   # Run migrations
   python src/manage.py db upgrade
   
   # Restart services
   docker-compose up -d
   ```

4. **Post-migration Verification**
   ```bash
   # Check service health
   curl http://localhost:5000/health
   
   # Verify database schema
   python src/manage.py db current
   
   # Run tests
   ./scripts/run-tests.sh
   ```

## Database Migrations

### Understanding Migrations

Hypersequester uses Flask-Migrate (Alembic) for database schema management:

- **Migration Files**: Located in `migrations/versions/`
- **Migration Commands**: Available through `python src/manage.py db`
- **Automatic Detection**: Schema changes are auto-detected

### Common Migration Commands

```bash
# Check current migration status
python src/manage.py db current

# Show migration history
python src/manage.py db history

# Upgrade to latest migration
python src/manage.py db upgrade

# Upgrade to specific migration
python src/manage.py db upgrade <revision_id>

# Downgrade to previous migration
python src/manage.py db downgrade

# Show pending migrations
python src/manage.py db show
```

### Creating New Migrations

When you modify database models:

```bash
# Generate migration automatically
python src/manage.py db migrate -m "Description of changes"

# Review generated migration file
# Edit if necessary

# Apply migration
python src/manage.py db upgrade
```

### Migration Rollback

If a migration fails:

```bash
# Rollback to previous version
python src/manage.py db downgrade

# Restore from backup if needed
psql hypersequester < backup_YYYYMMDD_HHMMSS.sql

# Fix migration issues and retry
python src/manage.py db upgrade
```

## Configuration Updates

### Environment Variables

When updating between versions, check for new environment variables:

```bash
# Compare with new template
diff .env .env.example

# Add any missing variables
# Update deprecated settings
```

### Configuration Files

Update configuration files in the `config/` directory:

```bash
# Backup current config
cp config/development.json config/development.json.backup

# Update with new settings
# Merge your customizations
```

### Docker Configuration

Update Docker configuration if needed:

```bash
# Rebuild containers with new configuration
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Data Migration

### File Structure Changes

If file organization changes between versions:

```bash
# Example: Moving files to new structure
mkdir -p data/new_structure
mv data/old_location/* data/new_structure/
```

### Data Format Updates

For changes in data formats:

```bash
# Run data conversion scripts (if provided)
python scripts/convert_data_v0.1.0.py

# Verify data integrity
python scripts/verify_data.py
```

### Large Dataset Migration

For large datasets:

```bash
# Use background processing
python scripts/migrate_large_dataset.py --batch-size 1000

# Monitor progress
tail -f logs/migration.log
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database status
systemctl status postgresql

# Verify connection settings
psql -h localhost -U hypersequester -d hypersequester_dev

# Update connection string if needed
```

#### 2. Migration Conflicts
```bash
# Check for conflicting migrations
python src/manage.py db heads

# Merge conflicts if multiple heads exist
python src/manage.py db merge -m "Merge migrations"
```

#### 3. Dependency Conflicts
```bash
# Clear Python cache
find . -type d -name __pycache__ -delete

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Clear Node.js cache
rm -rf node_modules package-lock.json
npm install
```

#### 4. Docker Issues
```bash
# Clean Docker environment
docker-compose down -v
docker system prune -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Recovery Procedures

#### Database Recovery
```bash
# Stop application
docker-compose down

# Restore database from backup
dropdb hypersequester_dev
createdb hypersequester_dev
psql hypersequester_dev < backup_YYYYMMDD_HHMMSS.sql

# Restart application
docker-compose up -d
```

#### Configuration Recovery
```bash
# Restore configuration from backup
cp config_backup_YYYYMMDD_HHMMSS/* config/

# Restart services
docker-compose restart
```

#### Complete System Recovery
```bash
# Restore from complete backup
git checkout <previous_working_commit>
docker-compose down -v
# Restore database and data
# Restart services
```

### Getting Help

If you encounter issues during migration:

1. **Check Logs**
   ```bash
   # Application logs
   docker-compose logs app
   
   # Database logs
   docker-compose logs postgres
   
   # System logs
   tail -f logs/hypersequester.log
   ```

2. **Verify System State**
   ```bash
   # Check service status
   docker-compose ps
   
   # Check database connectivity
   python -c "from src.backend.models import db; print('DB OK' if db else 'DB Error')"
   ```

3. **Contact Support**
   - Create GitHub issue with migration details
   - Include error logs and system information
   - Describe steps taken and current state

## Version-Specific Notes

### Future Versions

This section will be updated with specific migration notes for each version:

- **v0.2.0**: API implementation and file upload features
- **v0.3.0**: 3D visualization and real-time updates
- **v1.0.0**: Production-ready release with full features

### Breaking Changes

Future versions with breaking changes will include:
- Detailed migration scripts
- Compatibility matrices
- Deprecation warnings
- Upgrade paths

---

**Last Updated**: June 17, 2024  
**Version**: 0.1.0  
**Next Review**: With v0.2.0 release

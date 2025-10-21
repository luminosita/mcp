# CLAUDE.md - Database Patterns & Migrations

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

## Overview

This document covers database interaction patterns, migration strategies, and best practices for Go applications using Clean Architecture.

## Database Stack

- **Primary Database**: PostgreSQL (recommended) or MySQL
- **Migration Tool**: golang-migrate/migrate
- **ORM Options**:
  - GORM (feature-rich, recommended for complex apps)
  - sqlx (lightweight, SQL-first approach)
  - database/sql (standard library, maximum control)
- **Query Builder**: squirrel (optional, for dynamic queries)

## Database Connection Patterns

### Repository Pattern Implementation

```go
package repositories

import (
	"context"
	"database/sql"
)

type UserRepository interface {
	Create(ctx context.Context, user *domain.User) error
	FindByID(ctx context.Context, id string) (*domain.User, error)
	FindByEmail(ctx context.Context, email string) (*domain.User, error)
	Update(ctx context.Context, user *domain.User) error
	Delete(ctx context.Context, id string) error
	List(ctx context.Context, filter ListFilter) ([]*domain.User, error)
}

type postgresUserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) UserRepository {
	return &postgresUserRepository{db: db}
}

func (r *postgresUserRepository) Create(ctx context.Context, user *domain.User) error {
	query := `
		INSERT INTO users (id, email, username, password_hash, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`

	_, err := r.db.ExecContext(
		ctx,
		query,
		user.ID,
		user.Email,
		user.Username,
		user.PasswordHash,
		user.CreatedAt,
		user.UpdatedAt,
	)

	return err
}

func (r *postgresUserRepository) FindByID(ctx context.Context, id string) (*domain.User, error) {
	query := `
		SELECT id, email, username, password_hash, created_at, updated_at
		FROM users
		WHERE id = $1 AND deleted_at IS NULL
	`

	user := &domain.User{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&user.ID,
		&user.Email,
		&user.Username,
		&user.PasswordHash,
		&user.CreatedAt,
		&user.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, domain.ErrUserNotFound
	}

	return user, err
}
```

### Database Connection Pool Configuration

```go
package infrastructure

import (
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq"
)

type DatabaseConfig struct {
	Host            string
	Port            int
	User            string
	Password        string
	Name            string
	SSLMode         string
	MaxOpenConns    int
	MaxIdleConns    int
	ConnMaxLifetime time.Duration
	ConnMaxIdleTime time.Duration
}

func NewDatabase(cfg DatabaseConfig) (*sql.DB, error) {
	dsn := fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.Name, cfg.SSLMode,
	)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	db.SetMaxOpenConns(cfg.MaxOpenConns)
	db.SetMaxIdleConns(cfg.MaxIdleConns)
	db.SetConnMaxLifetime(cfg.ConnMaxLifetime)
	db.SetConnMaxIdleTime(cfg.ConnMaxIdleTime)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return db, nil
}
```

### Using GORM

```go
package infrastructure

import (
	"fmt"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func NewGORMDatabase(cfg DatabaseConfig) (*gorm.DB, error) {
	dsn := fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.Name, cfg.SSLMode,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
		NowFunc: func() time.Time {
			return time.Now().UTC()
		},
	})

	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	sqlDB.SetMaxOpenConns(cfg.MaxOpenConns)
	sqlDB.SetMaxIdleConns(cfg.MaxIdleConns)
	sqlDB.SetConnMaxLifetime(cfg.ConnMaxLifetime)

	return db, nil
}

type gormUserRepository struct {
	db *gorm.DB
}

func (r *gormUserRepository) FindByID(ctx context.Context, id string) (*domain.User, error) {
	var user domain.User

	err := r.db.WithContext(ctx).
		Where("id = ? AND deleted_at IS NULL", id).
		First(&user).Error

	if errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, domain.ErrUserNotFound
	}

	return &user, err
}
```

## Database Migration Patterns

### Migration Directory Structure

```
migrations/
├── 000001_create_users_table.up.sql
├── 000001_create_users_table.down.sql
├── 000002_create_posts_table.up.sql
├── 000002_create_posts_table.down.sql
├── 000003_add_user_indexes.up.sql
├── 000003_add_user_indexes.down.sql
└── ...
```

### Migration Files

#### 000001_create_users_table.up.sql

```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### 000001_create_users_table.down.sql

```sql
DROP TABLE IF EXISTS users;
```

#### 000002_create_posts_table.up.sql

```sql
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_status ON posts(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_posts_published_at ON posts(published_at) WHERE published_at IS NOT NULL;
```

#### 000002_create_posts_table.down.sql

```sql
DROP TABLE IF EXISTS posts;
```

### Migration Runner

```go
package main

import (
	"flag"
	"fmt"
	"log"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
)

func main() {
	var direction string
	var steps int

	flag.StringVar(&direction, "direction", "up", "Migration direction: up or down")
	flag.IntVar(&steps, "steps", 0, "Number of migration steps (0 = all)")
	flag.Parse()

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		log.Fatal("DATABASE_URL environment variable is required")
	}

	m, err := migrate.New(
		"file://migrations",
		databaseURL,
	)
	if err != nil {
		log.Fatalf("Failed to create migrate instance: %v", err)
	}
	defer m.Close()

	switch direction {
	case "up":
		if steps > 0 {
			err = m.Steps(steps)
		} else {
			err = m.Up()
		}
	case "down":
		if steps > 0 {
			err = m.Steps(-steps)
		} else {
			err = m.Down()
		}
	default:
		log.Fatalf("Invalid direction: %s", direction)
	}

	if err != nil && err != migrate.ErrNoChange {
		log.Fatalf("Migration failed: %v", err)
	}

	version, dirty, err := m.Version()
	if err != nil {
		log.Printf("Could not get version: %v", err)
	} else {
		log.Printf("Migration complete. Current version: %d, Dirty: %v", version, dirty)
	}
}
```

### Programmatic Migration

```go
package infrastructure

import (
	"embed"
	"fmt"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	"github.com/golang-migrate/migrate/v4/source/iofs"
)

//go:embed migrations/*.sql
var migrationsFS embed.FS

func RunMigrations(databaseURL string) error {
	sourceDriver, err := iofs.New(migrationsFS, "migrations")
	if err != nil {
		return fmt.Errorf("failed to create source driver: %w", err)
	}

	m, err := migrate.NewWithSourceInstance(
		"iofs",
		sourceDriver,
		databaseURL,
	)
	if err != nil {
		return fmt.Errorf("failed to create migrate instance: %w", err)
	}
	defer m.Close()

	if err := m.Up(); err != nil && err != migrate.ErrNoChange {
		return fmt.Errorf("migration failed: %w", err)
	}

	return nil
}
```

## Transaction Patterns

### Basic Transaction

```go
func (r *postgresUserRepository) CreateWithProfile(ctx context.Context, user *domain.User, profile *domain.Profile) error {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	if _, err := tx.ExecContext(ctx, `
		INSERT INTO users (id, email, username, password_hash, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`, user.ID, user.Email, user.Username, user.PasswordHash, user.CreatedAt, user.UpdatedAt); err != nil {
		return err
	}

	if _, err := tx.ExecContext(ctx, `
		INSERT INTO profiles (id, user_id, first_name, last_name, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`, profile.ID, user.ID, profile.FirstName, profile.LastName, profile.CreatedAt, profile.UpdatedAt); err != nil {
		return err
	}

	return tx.Commit()
}
```

### Transaction Helper

```go
type TxFunc func(tx *sql.Tx) error

func (r *postgresUserRepository) WithTransaction(ctx context.Context, fn TxFunc) error {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}

	defer func() {
		if p := recover(); p != nil {
			tx.Rollback()
			panic(p)
		} else if err != nil {
			tx.Rollback()
		} else {
			err = tx.Commit()
		}
	}()

	err = fn(tx)
	return err
}

func (r *postgresUserRepository) CreateWithProfile(ctx context.Context, user *domain.User, profile *domain.Profile) error {
	return r.WithTransaction(ctx, func(tx *sql.Tx) error {
		if _, err := tx.ExecContext(ctx, userInsertQuery, ...); err != nil {
			return err
		}

		if _, err := tx.ExecContext(ctx, profileInsertQuery, ...); err != nil {
			return err
		}

		return nil
	})
}
```

## Query Patterns

### Pagination

```go
type ListFilter struct {
	Page     int
	PageSize int
	SortBy   string
	SortDir  string
}

type PaginatedResult struct {
	Items      []*domain.User
	Total      int64
	Page       int
	PageSize   int
	TotalPages int
}

func (r *postgresUserRepository) List(ctx context.Context, filter ListFilter) (*PaginatedResult, error) {
	countQuery := `SELECT COUNT(*) FROM users WHERE deleted_at IS NULL`

	var total int64
	if err := r.db.QueryRowContext(ctx, countQuery).Scan(&total); err != nil {
		return nil, err
	}

	offset := (filter.Page - 1) * filter.PageSize

	query := fmt.Sprintf(`
		SELECT id, email, username, created_at, updated_at
		FROM users
		WHERE deleted_at IS NULL
		ORDER BY %s %s
		LIMIT $1 OFFSET $2
	`, filter.SortBy, filter.SortDir)

	rows, err := r.db.QueryContext(ctx, query, filter.PageSize, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var users []*domain.User
	for rows.Next() {
		user := &domain.User{}
		if err := rows.Scan(&user.ID, &user.Email, &user.Username, &user.CreatedAt, &user.UpdatedAt); err != nil {
			return nil, err
		}
		users = append(users, user)
	}

	totalPages := int(total) / filter.PageSize
	if int(total)%filter.PageSize > 0 {
		totalPages++
	}

	return &PaginatedResult{
		Items:      users,
		Total:      total,
		Page:       filter.Page,
		PageSize:   filter.PageSize,
		TotalPages: totalPages,
	}, nil
}
```

### Batch Operations

```go
func (r *postgresUserRepository) CreateBatch(ctx context.Context, users []*domain.User) error {
	if len(users) == 0 {
		return nil
	}

	query := `
		INSERT INTO users (id, email, username, password_hash, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6)
	`

	stmt, err := r.db.PrepareContext(ctx, query)
	if err != nil {
		return err
	}
	defer stmt.Close()

	for _, user := range users {
		if _, err := stmt.ExecContext(
			ctx,
			user.ID,
			user.Email,
			user.Username,
			user.PasswordHash,
			user.CreatedAt,
			user.UpdatedAt,
		); err != nil {
			return err
		}
	}

	return nil
}
```

## Database Seeding

### Seed Data Structure

```go
package seed

import (
	"context"
	"database/sql"
	"log"
)

type Seeder struct {
	db *sql.DB
}

func NewSeeder(db *sql.DB) *Seeder {
	return &Seeder{db: db}
}

func (s *Seeder) Seed(ctx context.Context) error {
	if err := s.seedUsers(ctx); err != nil {
		return err
	}

	if err := s.seedPosts(ctx); err != nil {
		return err
	}

	return nil
}

func (s *Seeder) seedUsers(ctx context.Context) error {
	users := []struct {
		email    string
		username string
		password string
	}{
		{"admin@example.com", "admin", "hashed_password_1"},
		{"user@example.com", "user", "hashed_password_2"},
	}

	for _, u := range users {
		_, err := s.db.ExecContext(ctx, `
			INSERT INTO users (email, username, password_hash)
			VALUES ($1, $2, $3)
			ON CONFLICT (email) DO NOTHING
		`, u.email, u.username, u.password)

		if err != nil {
			return err
		}
	}

	log.Println("Users seeded successfully")
	return nil
}
```

## Best Practices

### ✅ DO

- **Use context** for all database operations to support timeouts and cancellation
- **Use prepared statements** for repeated queries
- **Use transactions** for operations that must be atomic
- **Handle NULL values** properly with sql.NullString, sql.NullInt64, etc.
- **Close rows** using defer rows.Close() to prevent connection leaks
- **Use connection pooling** with appropriate limits
- **Create indexes** on frequently queried columns
- **Use migrations** for all schema changes
- **Version migrations** sequentially with timestamps or sequence numbers
- **Write both up and down** migrations
- **Test migrations** on staging before production
- **Use soft deletes** (deleted_at) for audit trail
- **Add created_at and updated_at** timestamps to all tables

### ❌ DON'T

- **Don't concatenate SQL** - use parameterized queries to prevent SQL injection
- **Don't ignore errors** from database operations
- **Don't leak connections** - always close rows and statements
- **Don't use SELECT *** in production - specify columns explicitly
- **Don't modify migrations** after they've been applied
- **Don't skip down migrations** - always provide rollback path
- **Don't hardcode database credentials** in code
- **Don't use ORM for complex queries** - write raw SQL when needed
- **Don't forget indexes** on foreign keys
- **Don't create indexes blindly** - measure query performance first

## Migration Best Practices

### Schema Versioning Strategy

1. **Sequential numbering**: `000001_`, `000002_`, etc.
2. **Timestamp prefix**: `20240101120000_`, `20240102150000_`
3. **Descriptive names**: `create_users_table`, `add_email_index`

### Migration Safety Checklist

- ✅ Does the migration have both up and down versions?
- ✅ Is the migration idempotent (can run multiple times safely)?
- ✅ Are there any breaking changes that require application updates?
- ✅ Will the migration lock tables for extended periods?
- ✅ Is there a rollback plan if the migration fails?
- ✅ Has the migration been tested on a copy of production data?

### Zero-Downtime Migration Pattern

```sql
-- Step 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- Step 2: Deploy code that writes to both columns

-- Step 3: Backfill data
UPDATE users SET new_email = email WHERE new_email IS NULL;

-- Step 4: Make column NOT NULL
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;

-- Step 5: Add index
CREATE INDEX idx_users_new_email ON users(new_email);

-- Step 6: Deploy code that only uses new column

-- Step 7: Drop old column
ALTER TABLE users DROP COLUMN email;
```

## Troubleshooting

### Connection Pool Exhaustion

```go
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)
db.SetConnMaxLifetime(5 * time.Minute)

stats := db.Stats()
log.Printf("Open connections: %d, In use: %d, Idle: %d",
	stats.OpenConnections,
	stats.InUse,
	stats.Idle,
)
```

### Slow Queries

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

rows, err := db.QueryContext(ctx, query)
if err != nil {
	log.Printf("Query timeout or error: %v", err)
}
```

### Migration Conflicts

```bash
# Check current migration version
migrate -path ./migrations -database "$DATABASE_URL" version

# Force to specific version (use with caution!)
migrate -path ./migrations -database "$DATABASE_URL" force 5

# Fix dirty state by manually correcting database and forcing version
```

## Related Files

- **[patterns-architecture]mcp://resources/patterns/go/patterns-architecture** - Repository pattern, Clean Architecture layer boundaries, dependency injection
- **[patterns-error-handling]mcp://resources/patterns/go/patterns-error-handling** - Database error handling, wrapping errors with context
- **[patterns-testing]mcp://resources/patterns/go/patterns-testing** - Database integration tests, test fixtures, transaction rollback patterns
- **[patterns-concurrency]mcp://resources/patterns/go/patterns-concurrency** - Connection pooling, goroutines with database operations
- **[patterns-validation]mcp://resources/patterns/go/patterns-validation** - SQL injection prevention, parameterized queries
- **[patterns-tooling]mcp://resources/patterns/go/patterns-tooling** - golang-migrate setup, database migration tasks in Taskfile

---

## External References

- [golang-migrate](https://github.com/golang-migrate/migrate)
- [GORM Documentation](https://gorm.io/docs/)
- [sqlx Documentation](http://jmoiron.github.io/sqlx/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Database Transaction Patterns](https://www.postgresql.org/docs/current/tutorial-transactions.html)

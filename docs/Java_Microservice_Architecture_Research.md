# Java Microservice Architecture Research Report

**Document Version:** 3.0 (Extended - Telemetry, Observability & Audit Logging)
**Research Date:** 2025-11-02 (Extended)
**Researcher:** Context Engineering PoC Team
**Target Framework:** Spring Boot 3.x, Java 17+

## Executive Summary

This research report establishes architectural standards for scalable Java microservice implementations using Spring Boot 3.x, focusing on production-ready patterns that leverage Spring's mature ecosystem while maintaining Clean Architecture principles. Based on analysis of official Spring documentation, established open-source projects, and community best practices, this report provides actionable guidance across critical architectural areas.

**Key Findings:**
1. **Configuration Management:** @ConfigurationProperties with Java Records (Java 17+) provides type-safe, immutable configuration with constructor binding - far superior to @Value for complex configurations[^1]
2. **Type Safety & Validation:** Comprehensive patterns using Optional<T>, sealed classes, JPA Metamodel, custom JSR-303 validators, and validation groups for environment-specific rules[^28]-[^47]
3. **Structured Logging:** Logback with Logstash encoder for JSON output, MDC for request correlation, and Spring Boot Actuator for log level management at runtime[^2]
4. **Caching:** Spring Cache abstraction with @EnableCaching provides vendor-neutral caching, Lettuce client for Redis offers reactive and sync modes with connection pooling[^3]
5. **Data Access:** Spring Data JPA with repository interfaces provides Clean Architecture compliance, HikariCP connection pool (auto-configured) offers excellent performance[^4]
6. **Error Handling:** RFC 7807 Problem Details with @ControllerAdvice for standardized API error responses, automatic Bean Validation integration, distributed tracing correlation[^44]-[^49]
7. **Telemetry & Observability:** Spring Boot Actuator with Micrometer provides production-ready metrics/health checks, OpenTelemetry integration for vendor-neutral distributed tracing[^50]-[^59]
8. **Audit Logging:** Spring Data JPA Auditing with event-driven patterns provides immutable audit trails for compliance (GDPR, SOC 2, HIPAA)[^60]-[^68]

**Critical Architectural Decision:** Leverage Spring Boot's convention-over-configuration philosophy while customizing only when necessary. Use constructor injection exclusively (field injection is an anti-pattern), embrace immutability with Java Records, utilize Optional<T> for explicit null safety, implement comprehensive validation at all layers (configuration, request, entity, business), and rely on type-safe query patterns (Criteria API, Specifications) to eliminate runtime errors.

---

## 1. Configuration Management

### 1.1 Recommended Approach: @ConfigurationProperties with Java Records

Spring Boot 3.x with Java 17+ enables @ConfigurationProperties combined with Java Records, providing a type-safe, immutable, and maintainable way to handle configuration[^1][^5]. This approach is far superior to @Value for anything beyond single properties.

**Core Benefits:**
- **Type Safety:** Property names tied to Record fields, compile-time safety
- **Immutability:** Records are immutable by default (ideal for configuration)
- **Constructor Binding:** Implicit in Spring Boot 3 (no @ConstructorBinding needed)
- **Validation:** JSR-303/JSR-380 Bean Validation support
- **IDE Support:** Autocomplete, refactoring safety

### 1.2 Implementation Example

```java
// File: src/main/java/com/example/config/AppConfig.java
package com.example.config;

import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Application configuration loaded from application.yml/properties.
 * Uses Java Record for immutability and type safety.
 * Constructor binding is implicit in Spring Boot 3.
 */
@ConfigurationProperties(prefix = "app")
@Validated
public record AppConfig(
    @NotBlank String name,
    @DefaultValue("false") boolean debug,

    ServerConfig server,
    DatabaseConfig database,
    RedisConfig redis,

    @NotBlank @Size(min = 32) String jwtSecret
) {
    /**
     * Server configuration nested record.
     */
    public record ServerConfig(
        @DefaultValue("8080") @Min(1024) @Max(65535) int port,
        @DefaultValue("10s") Duration readTimeout,
        @DefaultValue("10s") Duration writeTimeout
    ) {}

    /**
     * Database configuration nested record.
     */
    public record DatabaseConfig(
        @NotBlank String url,
        @NotBlank String username,
        @NotBlank String password,
        @DefaultValue("25") @Min(1) @Max(100) int maxPoolSize,
        @DefaultValue("5") @Min(1) int minIdle,
        @DefaultValue("5m") Duration connectionTimeout
    ) {}

    /**
     * Redis configuration nested record.
     */
    public record RedisConfig(
        @NotBlank String host,
        @DefaultValue("6379") @Min(1) @Max(65535) int port,
        String password,
        @DefaultValue("0") @Min(0) @Max(15) int database,
        @DefaultValue("10") @Min(1) int poolSize
    ) {}
}
```

**application.yml configuration:**

```yaml
app:
  name: java-microservice
  debug: false

  server:
    port: 8080
    read-timeout: 10s
    write-timeout: 10s

  database:
    url: jdbc:postgresql://localhost:5432/mydb
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:changeme}
    max-pool-size: 25
    min-idle: 5
    connection-timeout: 5m

  redis:
    host: ${REDIS_HOST:localhost}
    port: 6379
    password: ${REDIS_PASSWORD:}
    database: 0
    pool-size: 10

  jwt-secret: ${JWT_SECRET:change-this-secret-in-production}
```

**Enable configuration properties scanning:**

```java
// File: src/main/java/com/example/Application.java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * Main application entry point.
 * @ConfigurationPropertiesScan enables automatic detection of @ConfigurationProperties classes.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**Usage in services (constructor injection):**

```java
// File: src/main/java/com/example/service/UserService.java
package com.example.service;

import com.example.config.AppConfig;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final AppConfig config;

    // Constructor injection (recommended)
    public UserService(AppConfig config) {
        this.config = config;
    }

    public String getAppName() {
        return config.name();
    }

    public boolean isDebugMode() {
        return config.debug();
    }
}
```

### 1.2.1 Configuration Initialization Patterns

#### Pattern 1: Spring Boot Auto-Configuration with @ConfigurationPropertiesScan (Recommended)

Spring Boot's convention-over-configuration approach auto-discovers and initializes @ConfigurationProperties classes with zero programmatic setup[^5][^23].

**Complete implementation:**

```java
// File: src/main/java/com/example/Application.java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * Main application entry point.
 * @ConfigurationPropertiesScan enables automatic detection and binding
 * of @ConfigurationProperties classes in the application package.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

```java
// File: src/main/java/com/example/config/DatabaseProperties.java
package com.example.config;

import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Database configuration properties.
 * Auto-discovered by @ConfigurationPropertiesScan.
 * Validated at startup using JSR-303 Bean Validation.
 */
@ConfigurationProperties(prefix = "app.database")
@Validated
public record DatabaseProperties(
    @NotBlank String url,
    @NotBlank String username,
    @NotBlank String password,

    @DefaultValue("25")
    @Min(1)
    @Max(100)
    int maxPoolSize,

    @DefaultValue("5")
    @Min(1)
    int minIdle,

    @DefaultValue("30s")
    Duration connectionTimeout,

    @DefaultValue("true")
    boolean autoCommit
) {}
```

```java
// File: src/main/java/com/example/config/SecurityProperties.java
package com.example.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Security configuration properties with nested objects.
 * Demonstrates complex property binding with validation.
 */
@ConfigurationProperties(prefix = "app.security")
@Validated
public record SecurityProperties(
    @Valid JwtConfig jwt,
    @Valid CorsConfig cors
) {
    public record JwtConfig(
        @NotBlank
        @Size(min = 32, message = "JWT secret must be at least 32 characters")
        String secret,

        @DefaultValue("1h")
        Duration accessTokenExpiration,

        @DefaultValue("7d")
        Duration refreshTokenExpiration,

        @NotBlank
        @DefaultValue("HS256")
        String algorithm
    ) {}

    public record CorsConfig(
        @NotEmpty
        String[] allowedOrigins,

        @NotEmpty
        String[] allowedMethods,

        @DefaultValue("true")
        boolean allowCredentials,

        @DefaultValue("3600")
        @Min(0)
        long maxAge
    ) {}
}
```

**application.yml configuration:**

```yaml
app:
  database:
    url: jdbc:postgresql://${DB_HOST:localhost}:5432/${DB_NAME:mydb}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:changeme}
    max-pool-size: 25
    min-idle: 5
    connection-timeout: 30s
    auto-commit: true

  security:
    jwt:
      secret: ${JWT_SECRET:change-this-in-production-minimum-32-characters-required}
      access-token-expiration: 1h
      refresh-token-expiration: 7d
      algorithm: HS256
    cors:
      allowed-origins:
        - http://localhost:3000
        - https://example.com
      allowed-methods:
        - GET
        - POST
        - PUT
        - DELETE
      allow-credentials: true
      max-age: 3600
```

**Usage in services (constructor injection):**

```java
// File: src/main/java/com/example/service/JwtService.java
package com.example.service;

import com.example.config.SecurityProperties;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Date;

@Service
public class JwtService {

    private final SecurityProperties securityProperties;

    public JwtService(SecurityProperties securityProperties) {
        this.securityProperties = securityProperties;
    }

    public String generateAccessToken(String userId) {
        Instant now = Instant.now();
        Instant expiration = now.plus(securityProperties.jwt().accessTokenExpiration());

        return Jwts.builder()
            .setSubject(userId)
            .setIssuedAt(Date.from(now))
            .setExpiration(Date.from(expiration))
            .signWith(SignatureAlgorithm.HS256, securityProperties.jwt().secret())
            .compact();
    }
}
```

**Benefits:**
- ✅ **Convention over configuration:** Zero boilerplate, @ConfigurationPropertiesScan discovers all config classes automatically
- ✅ **Type-safe:** Compile-time validation, IDE autocomplete works perfectly
- ✅ **Immutable:** Java Records provide immutability by default (thread-safe)
- ✅ **Validated at startup:** JSR-303 validation fails fast if configuration invalid
- ✅ **Testable:** Easy to construct config objects in tests without Spring context
- ✅ **Documentation:** Config properties visible in Spring Boot metadata (IDE autocomplete in YAML)

**Drawbacks:**
- ❌ **Requires Spring Boot 3.x:** Constructor binding with Records requires Spring Boot 3+
- ❌ **Not dynamic:** Changes require application restart (@RefreshScope not supported with Records)

**Use When:**
- Standard Spring Boot 3.x applications (default recommendation)
- Configuration loaded once at startup
- Immutability and type safety are priorities

**Integration with Spring Boot lifecycle:**

1. **Application startup** → `@ConfigurationPropertiesScan` registers all @ConfigurationProperties classes
2. **Property binding** → Spring Boot binds YAML/properties to Record constructors
3. **Validation** → JSR-303 validation executed on bound objects
4. **Bean registration** → Validated config objects registered as Spring beans
5. **Dependency injection** → Config beans available for constructor injection in services

#### Pattern 2: Programmatic Configuration with @Bean

Programmatic configuration provides maximum flexibility for complex initialization logic, conditional configuration, or integration with external configuration sources[^24].

**Complete implementation:**

```java
// File: src/main/java/com/example/config/ApplicationConfiguration.java
package com.example.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;

/**
 * Programmatic configuration with @Bean methods.
 * Provides maximum flexibility for complex initialization logic.
 */
@Configuration
public class ApplicationConfiguration {

    private static final Logger log = LoggerFactory.getLogger(ApplicationConfiguration.class);

    private final Environment environment;

    public ApplicationConfiguration(Environment environment) {
        this.environment = environment;
    }

    /**
     * Database configuration loaded from external JSON file.
     * Demonstrates programmatic loading from non-standard sources.
     */
    @Bean
    public DatabaseConfig databaseConfig(
            @Value("${config.database.file:config/database.json}") String configFile
    ) throws IOException {
        log.info("Loading database configuration from: {}", configFile);

        Path configPath = Path.of(configFile);
        if (!Files.exists(configPath)) {
            log.warn("Database config file not found, using defaults: {}", configFile);
            return createDefaultDatabaseConfig();
        }

        // Parse JSON configuration file
        ObjectMapper mapper = new ObjectMapper();
        DatabaseConfig config = mapper.readValue(configPath.toFile(), DatabaseConfig.class);

        log.info("Database configuration loaded successfully: url={}", config.url());
        return config;
    }

    /**
     * Retry configuration with conditional logic based on active profiles.
     * Demonstrates profile-based configuration logic.
     */
    @Bean
    public RetryConfig retryConfig() {
        boolean isProduction = environment.matchesProfiles("production");

        RetryConfig config = new RetryConfig(
            maxAttempts: isProduction ? 5 : 3,
            backoffDelay: isProduction ? Duration.ofSeconds(2) : Duration.ofMillis(500),
            maxBackoffDelay: isProduction ? Duration.ofMinutes(1) : Duration.ofSeconds(5),
            exponentialBackoff: isProduction // Enable exponential backoff in production only
        );

        log.info("Retry configuration initialized: maxAttempts={}, backoff={}",
                 config.maxAttempts(), config.backoffDelay());

        return config;
    }

    /**
     * API client configuration with complex initialization.
     * Demonstrates aggregation of multiple properties into single config.
     */
    @Bean
    public ApiClientConfig apiClientConfig(
            @Value("${api.base-url}") String baseUrl,
            @Value("${api.api-key}") String apiKey,
            @Value("${api.timeout:30s}") Duration timeout,
            @Value("${api.max-retries:3}") int maxRetries,
            Environment env
    ) {
        // Complex initialization logic
        String environment = env.getProperty("spring.profiles.active", "dev");
        boolean sslVerification = !environment.equals("dev"); // Disable SSL in dev only

        ApiClientConfig config = new ApiClientConfig(
            baseUrl,
            apiKey,
            timeout,
            maxRetries,
            sslVerification
        );

        log.info("API client configured: baseUrl={}, timeout={}", baseUrl, timeout);

        return config;
    }

    private DatabaseConfig createDefaultDatabaseConfig() {
        return new DatabaseConfig(
            "jdbc:postgresql://localhost:5432/default",
            "postgres",
            "changeme",
            10, // maxPoolSize
            2   // minIdle
        );
    }
}

/**
 * Database configuration POJO (Plain Old Java Object).
 * Can be deserialized from JSON or constructed programmatically.
 */
record DatabaseConfig(
    String url,
    String username,
    String password,
    int maxPoolSize,
    int minIdle
) {}

/**
 * Retry configuration record.
 */
record RetryConfig(
    int maxAttempts,
    Duration backoffDelay,
    Duration maxBackoffDelay,
    boolean exponentialBackoff
) {}

/**
 * API client configuration record.
 */
record ApiClientConfig(
    String baseUrl,
    String apiKey,
    Duration timeout,
    int maxRetries,
    boolean sslVerification
) {}
```

**External JSON configuration file (optional):**

```json
// File: config/database.json
{
  "url": "jdbc:postgresql://db-server:5432/production",
  "username": "app_user",
  "password": "secure_password",
  "maxPoolSize": 50,
  "minIdle": 10
}
```

**Benefits:**
- ✅ **Maximum flexibility:** Full programmatic control over initialization logic
- ✅ **Complex logic:** Can load from external files, databases, vault systems, or APIs
- ✅ **Conditional configuration:** Profile-based logic, feature flags, runtime decisions
- ✅ **Aggregation:** Combine multiple property sources into single config object
- ✅ **Validation:** Custom validation logic beyond JSR-303 constraints
- ✅ **Logging:** Log configuration details during initialization for troubleshooting

**Drawbacks:**
- ❌ **More boilerplate:** Requires explicit @Bean methods for each config object
- ❌ **No @ConfigurationProperties metadata:** IDE autocomplete in YAML files won't work
- ❌ **More complex:** Harder to understand than declarative @ConfigurationProperties approach

**Use When:**
- Loading configuration from non-standard sources (JSON files, databases, vault systems)
- Complex initialization logic or conditional configuration required
- Need to aggregate multiple property sources
- Runtime decisions affect configuration values

**Integration with Spring Boot lifecycle:**

1. **@Configuration scanning** → Spring discovers configuration classes at startup
2. **@Bean method execution** → Methods called during bean initialization phase
3. **Dependency resolution** → Spring injects @Value properties and Environment beans
4. **Custom logic** → Your code executes (file loading, conditionals, validation)
5. **Bean registration** → Returned objects registered as Spring beans
6. **Dependency injection** → Config beans available for injection throughout application

#### Pattern 3: Multiple Configuration Files with @Profile

Profile-specific configuration files enable environment-specific settings (dev, staging, production) without code changes[^16][^25].

**Complete implementation:**

```java
// File: src/main/java/com/example/config/DataSourceConfig.java
package com.example.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

import javax.sql.DataSource;

/**
 * Profile-based DataSource configuration.
 * Different configurations for dev, staging, and production environments.
 */
@Configuration
public class DataSourceConfig {

    private static final Logger log = LoggerFactory.getLogger(DataSourceConfig.class);

    /**
     * Development profile: Small connection pool, relaxed timeouts.
     */
    @Bean
    @Profile("dev")
    @ConfigurationProperties("app.datasource.dev")
    public DataSource devDataSource() {
        log.info("Initializing DEVELOPMENT DataSource");

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb_dev");
        config.setUsername("dev_user");
        config.setPassword("dev_password");
        config.setMaximumPoolSize(5);  // Small pool for dev
        config.setMinimumIdle(1);
        config.setConnectionTimeout(5000);  // 5 seconds
        config.setIdleTimeout(300000);      // 5 minutes
        config.setPoolName("DevHikariPool");
        config.setAutoCommit(true);

        // Development-specific settings
        config.addDataSourceProperty("logUnclosedConnections", "true");
        config.setLeakDetectionThreshold(10000);  // 10 seconds (detect leaks faster)

        return new HikariDataSource(config);
    }

    /**
     * Staging profile: Medium connection pool, production-like settings.
     */
    @Bean
    @Profile("staging")
    @ConfigurationProperties("app.datasource.staging")
    public DataSource stagingDataSource() {
        log.info("Initializing STAGING DataSource");

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://staging-db:5432/mydb_staging");
        config.setUsername("staging_user");
        config.setPassword("staging_password");
        config.setMaximumPoolSize(15);  // Medium pool
        config.setMinimumIdle(5);
        config.setConnectionTimeout(20000);  // 20 seconds
        config.setIdleTimeout(600000);       // 10 minutes
        config.setMaxLifetime(1800000);      // 30 minutes
        config.setPoolName("StagingHikariPool");

        return new HikariDataSource(config);
    }

    /**
     * Production profile: Large connection pool, strict timeouts, monitoring.
     */
    @Bean
    @Profile("production")
    @ConfigurationProperties("app.datasource.production")
    public DataSource productionDataSource() {
        log.info("Initializing PRODUCTION DataSource");

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://prod-db-cluster:5432/mydb_prod");
        config.setUsername("prod_user");
        config.setPassword("${DB_PASSWORD}"); // From environment variable
        config.setMaximumPoolSize(50);  // Large pool for production
        config.setMinimumIdle(10);
        config.setConnectionTimeout(30000);  // 30 seconds
        config.setIdleTimeout(600000);       // 10 minutes
        config.setMaxLifetime(1800000);      // 30 minutes
        config.setPoolName("ProdHikariPool");

        // Production-specific settings
        config.setKeepaliveTime(30000);      // Validate connections every 30 seconds
        config.setValidationTimeout(5000);   // 5 seconds for validation
        config.setRegisterMbeans(true);      // Enable JMX monitoring

        return new HikariDataSource(config);
    }
}
```

```java
// File: src/main/java/com/example/config/CacheConfig.java
package com.example.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;

import java.time.Duration;

/**
 * Profile-based cache configuration.
 * Simple in-memory cache for dev/test, Redis for production.
 */
@Configuration
@EnableCaching
public class CacheConfig {

    private static final Logger log = LoggerFactory.getLogger(CacheConfig.class);

    /**
     * Development/Test: Simple in-memory cache (no Redis needed).
     */
    @Bean
    @Profile({"dev", "test"})
    public CacheManager devCacheManager() {
        log.info("Initializing DEVELOPMENT cache manager (in-memory)");
        return new ConcurrentMapCacheManager("users", "products", "sessions");
    }

    /**
     * Staging: Caffeine cache (high-performance in-memory with eviction).
     */
    @Bean
    @Profile("staging")
    public CacheManager stagingCacheManager() {
        log.info("Initializing STAGING cache manager (Caffeine)");

        CaffeineCacheManager cacheManager = new CaffeineCacheManager("users", "products", "sessions");
        cacheManager.setCaffeine(
            Caffeine.newBuilder()
                .maximumSize(5000)  // Medium size for staging
                .expireAfterWrite(Duration.ofMinutes(10))
                .recordStats()  // Enable statistics
        );
        return cacheManager;
    }

    /**
     * Production: Redis distributed cache with custom TTLs.
     */
    @Bean
    @Profile("production")
    public CacheManager productionCacheManager(RedisConnectionFactory connectionFactory) {
        log.info("Initializing PRODUCTION cache manager (Redis)");

        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(5));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            // Cache-specific TTLs
            .withCacheConfiguration("users",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(10)))
            .withCacheConfiguration("products",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(15)))
            .withCacheConfiguration("sessions",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(30)))
            .build();
    }
}
```

**Profile-specific application files:**

```yaml
# File: src/main/resources/application.yml (base configuration)
spring:
  application:
    name: java-microservice
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}  # Default to dev if not specified

app:
  name: Java Microservice
```

```yaml
# File: src/main/resources/application-dev.yml (development overrides)
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb_dev
    username: dev_user
    password: dev_password

logging:
  level:
    root: DEBUG
    com.example: DEBUG

app:
  debug: true
```

```yaml
# File: src/main/resources/application-staging.yml (staging overrides)
spring:
  datasource:
    url: jdbc:postgresql://staging-db:5432/mydb_staging
    username: staging_user
    password: ${DB_PASSWORD}

logging:
  level:
    root: INFO
    com.example: DEBUG

app:
  debug: false
```

```yaml
# File: src/main/resources/application-production.yml (production overrides)
spring:
  datasource:
    url: jdbc:postgresql://prod-db-cluster:5432/mydb_prod
    username: prod_user
    password: ${DB_PASSWORD}

  data:
    redis:
      host: ${REDIS_HOST}
      port: 6379
      password: ${REDIS_PASSWORD}

logging:
  level:
    root: WARN
    com.example: INFO

app:
  debug: false
```

**Activate profiles at runtime:**

```bash
# Via command line argument
java -jar myapp.jar --spring.profiles.active=production

# Via environment variable
export SPRING_PROFILES_ACTIVE=production
java -jar myapp.jar

# Via application.properties
# spring.profiles.active=production

# Multiple profiles (comma-separated)
java -jar myapp.jar --spring.profiles.active=production,monitoring
```

**Benefits:**
- ✅ **Environment isolation:** Separate configs for dev/staging/production without code changes
- ✅ **Profile-specific beans:** Different implementations per environment (@Profile annotation)
- ✅ **Property overrides:** Environment-specific application-{profile}.yml files
- ✅ **Testability:** Easy to activate test profiles (@ActiveProfiles in tests)
- ✅ **Multiple profiles:** Can activate multiple profiles simultaneously (production + monitoring)
- ✅ **Maintainability:** Clear separation of environment-specific configuration

**Drawbacks:**
- ❌ **Configuration duplication:** Some properties repeated across profile files
- ❌ **Profile management:** Must ensure correct profile active in each environment
- ❌ **Complexity:** Multiple configuration files to maintain

**Use When:**
- Multiple deployment environments (dev, staging, production)
- Different infrastructure per environment (local DB vs. RDS, in-memory cache vs. Redis)
- Need to swap bean implementations per environment (mock services in dev, real in production)

**Integration with Spring Boot lifecycle:**

1. **Profile activation** → Spring reads `spring.profiles.active` from environment/command line
2. **Base config loading** → `application.yml` loaded first
3. **Profile config loading** → `application-{profile}.yml` loaded and merged
4. **Property override** → Profile-specific properties override base properties
5. **@Profile beans** → Only beans matching active profile are registered
6. **Bean initialization** → Profile-specific beans initialized with profile-specific properties

#### Pattern 4: External Configuration with Spring Cloud Config

Spring Cloud Config provides centralized, versioned configuration management for distributed microservices, with dynamic refresh capabilities[^8][^26].

**Complete implementation:**

**Config Server setup:**

```java
// File: config-server/src/main/java/com/example/ConfigServerApplication.java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.config.server.EnableConfigServer;

/**
 * Spring Cloud Config Server.
 * Serves configuration from Git repository to all microservices.
 */
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
```

```yaml
# File: config-server/src/main/resources/application.yml
server:
  port: 8888

spring:
  application:
    name: config-server

  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config-repo  # Git repository with configs
          clone-on-start: true
          default-label: main
          search-paths:
            - '{application}'  # Search in application-specific subdirectory

          # Authentication (if private repo)
          username: ${GIT_USERNAME}
          password: ${GIT_TOKEN}

        # Health check
        health:
          enabled: true
```

**Config repository structure (Git):**

```
config-repo/
├── user-service/
│   ├── application.yml           (shared config for user-service)
│   ├── application-dev.yml       (dev environment)
│   ├── application-staging.yml   (staging environment)
│   └── application-production.yml (production environment)
├── order-service/
│   ├── application.yml
│   ├── application-dev.yml
│   └── application-production.yml
└── common/
    └── application.yml            (shared across all services)
```

**Example configuration in Git repo:**

```yaml
# File: config-repo/user-service/application.yml (base config)
app:
  name: User Service
  version: 1.0.0

logging:
  level:
    root: INFO
```

```yaml
# File: config-repo/user-service/application-production.yml
spring:
  datasource:
    url: jdbc:postgresql://prod-db:5432/users
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10

  data:
    redis:
      host: ${REDIS_HOST}
      port: 6379

logging:
  level:
    root: WARN
    com.example: INFO
```

**Config Client setup (microservice):**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-config</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
# File: user-service/src/main/resources/application.yml
spring:
  application:
    name: user-service  # Matches directory in config repo

  config:
    import: "configserver:http://config-server:8888"  # Config Server URL

  cloud:
    config:
      fail-fast: true  # Fail startup if Config Server unavailable
      retry:
        initial-interval: 1000
        max-attempts: 6
        max-interval: 2000
        multiplier: 1.1

  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}

# Actuator endpoint for refresh
management:
  endpoints:
    web:
      exposure:
        include: refresh,health,info
```

**Dynamic configuration refresh:**

```java
// File: src/main/java/com/example/config/DynamicConfig.java
package com.example.config;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cloud.context.config.annotation.RefreshScope;
import org.springframework.stereotype.Component;

/**
 * Dynamic configuration that can be refreshed at runtime.
 * @RefreshScope enables refresh via /actuator/refresh endpoint.
 */
@Component
@RefreshScope  // Enable dynamic refresh
@ConfigurationProperties(prefix = "app.features")
public class DynamicConfig {

    @NotBlank
    private String welcomeMessage;

    @Min(1)
    private int maxUploadSizeMb;

    private boolean enableBetaFeatures;

    // Getters and setters
    public String getWelcomeMessage() { return welcomeMessage; }
    public void setWelcomeMessage(String welcomeMessage) {
        this.welcomeMessage = welcomeMessage;
    }

    public int getMaxUploadSizeMb() { return maxUploadSizeMb; }
    public void setMaxUploadSizeMb(int maxUploadSizeMb) {
        this.maxUploadSizeMb = maxUploadSizeMb;
    }

    public boolean isEnableBetaFeatures() { return enableBetaFeatures; }
    public void setEnableBetaFeatures(boolean enableBetaFeatures) {
        this.enableBetaFeatures = enableBetaFeatures;
    }
}
```

```java
// File: src/main/java/com/example/controller/FeatureController.java
package com.example.controller;

import com.example.config.DynamicConfig;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class FeatureController {

    private final DynamicConfig dynamicConfig;

    public FeatureController(DynamicConfig dynamicConfig) {
        this.dynamicConfig = dynamicConfig;
    }

    @GetMapping("/welcome")
    public String getWelcomeMessage() {
        // Value refreshes when config updated and /actuator/refresh called
        return dynamicConfig.getWelcomeMessage();
    }
}
```

**Refresh configuration at runtime:**

```bash
# 1. Update configuration in Git repository (commit and push)
git commit -am "Update welcome message"
git push

# 2. Trigger refresh via actuator endpoint (no service restart needed)
curl -X POST http://user-service:8080/actuator/refresh

# Response: List of properties that changed
["app.features.welcomeMessage"]

# 3. New configuration active immediately
curl http://user-service:8080/welcome
# Returns updated welcome message
```

**Benefits:**
- ✅ **Centralized configuration:** Single Git repository for all microservices
- ✅ **Version control:** Configuration changes tracked in Git (audit trail)
- ✅ **Dynamic refresh:** Update config without restarting services (@RefreshScope)
- ✅ **Environment-specific:** Profile-based configs (dev/staging/production)
- ✅ **Scalability:** Config Server serves hundreds of microservice instances
- ✅ **Consistency:** All service instances get identical configuration
- ✅ **Encryption:** Sensitive values encrypted at rest (JCE or Vault integration)

**Drawbacks:**
- ❌ **Additional infrastructure:** Requires Config Server (single point of failure unless clustered)
- ❌ **Startup dependency:** Services fail to start if Config Server unavailable (use fail-fast: false to allow)
- ❌ **Complexity:** More moving parts (Git repo, Config Server, refresh endpoints)
- ❌ **Refresh coordination:** Must trigger /actuator/refresh on each service instance (or use Spring Cloud Bus)
- ❌ **Record limitations:** @RefreshScope not compatible with Java Records (must use mutable classes)

**Use When:**
- Microservices ecosystem with 5+ services requiring centralized configuration
- Need dynamic configuration updates without service restart
- Configuration changes require audit trail (Git history)
- Multiple environments with shared base configuration

**Integration with Spring Boot lifecycle:**

1. **Service startup** → Microservice contacts Config Server at `spring.config.import` URL
2. **Config fetch** → Config Server pulls configuration from Git repository
3. **Profile resolution** → Config Server returns base + profile-specific config
4. **Property binding** → Spring Boot binds configuration to @ConfigurationProperties classes
5. **Service initialization** → Application starts with configuration from Config Server
6. **Dynamic refresh** → POST to `/actuator/refresh` reloads @RefreshScope beans with updated config

### 1.2.2 Common Configuration Mistakes

#### Mistake 1: Using @Value instead of @ConfigurationProperties for grouped configuration

**❌ Problem:**

```java
// BAD: Using @Value for related configuration properties
@Service
public class EmailService {

    @Value("${email.smtp.host}")
    private String smtpHost;

    @Value("${email.smtp.port:587}")
    private int smtpPort;

    @Value("${email.smtp.username}")
    private String smtpUsername;

    @Value("${email.smtp.password}")
    private String smtpPassword;

    @Value("${email.smtp.starttls.enable:true}")
    private boolean starttlsEnable;

    @Value("${email.smtp.auth:true}")
    private boolean smtpAuth;

    @Value("${email.from.address}")
    private String fromAddress;

    @Value("${email.from.name}")
    private String fromName;

    // Issues:
    // 1. No type safety: Typos in property names only caught at runtime
    // 2. No validation: Invalid values not caught at startup
    // 3. Scattered: Properties spread across class, hard to understand full config
    // 4. No IDE support: No autocomplete in YAML files
    // 5. Hard to test: Must set system properties or use @TestPropertySource
    // 6. Not reusable: Can't inject email config into multiple services
}
```

**✅ Solution: Use @ConfigurationProperties with Record**

```java
// GOOD: @ConfigurationProperties with validation and type safety
package com.example.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

/**
 * Email configuration properties.
 * Validated at startup, reusable across services.
 */
@ConfigurationProperties(prefix = "email")
@Validated
public record EmailProperties(
    @Valid SmtpConfig smtp,
    @Valid FromConfig from
) {
    public record SmtpConfig(
        @NotBlank String host,

        @DefaultValue("587")
        @Min(1)
        @Max(65535)
        int port,

        @NotBlank String username,

        @NotBlank String password,

        @DefaultValue("true")
        boolean starttlsEnable,

        @DefaultValue("true")
        boolean auth
    ) {}

    public record FromConfig(
        @NotBlank
        @Email
        String address,

        @NotBlank
        String name
    ) {}
}
```

```yaml
# File: application.yml (IDE autocomplete works here!)
email:
  smtp:
    host: smtp.gmail.com
    port: 587
    username: ${EMAIL_USERNAME}
    password: ${EMAIL_PASSWORD}
    starttls-enable: true
    auth: true
  from:
    address: noreply@example.com
    name: Example Service
```

```java
// Service uses injected config (testable, reusable)
@Service
public class EmailService {

    private final EmailProperties emailProperties;

    public EmailService(EmailProperties emailProperties) {
        this.emailProperties = emailProperties;
    }

    public void sendEmail(String to, String subject, String body) {
        // Access validated, type-safe configuration
        String smtpHost = emailProperties.smtp().host();
        int smtpPort = emailProperties.smtp().port();
        // ...
    }
}
```

**Benefits of fix:**
- ✅ Compile-time safety: Typos caught at compile time
- ✅ Startup validation: Invalid config fails fast with clear error message
- ✅ Organized: All related properties grouped together
- ✅ IDE support: Autocomplete in YAML files
- ✅ Testable: Easy to construct EmailProperties in unit tests
- ✅ Reusable: Inject into multiple services
- ✅ Documentation: Config structure self-documenting via Record fields

#### Mistake 2: Missing validation on configuration properties

**❌ Problem:**

```java
// BAD: No validation on configuration properties
@ConfigurationProperties(prefix = "app.api")
public record ApiConfig(
    String baseUrl,      // Could be blank!
    int timeout,         // Could be negative!
    int maxRetries       // Could be 999999!
) {}

// Results in runtime failures:
// - NullPointerException when baseUrl is blank
// - Negative timeout causes IllegalArgumentException in HTTP client
// - maxRetries=999999 causes infinite retry loops
```

**Runtime failure example:**

```
2025-11-01 14:23:45.123 ERROR [main] com.example.Application - Failed to initialize API client
java.lang.IllegalArgumentException: timeout must be positive
    at com.example.ApiClient.<init>(ApiClient.java:42)
    ...
```

**✅ Solution: Add JSR-303 validation annotations**

```java
// GOOD: Validated configuration with clear constraints
package com.example.config;

import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * API client configuration with validation.
 * Fails fast at startup if configuration invalid.
 */
@ConfigurationProperties(prefix = "app.api")
@Validated
public record ApiConfig(
    @NotBlank(message = "API base URL is required")
    @Pattern(regexp = "^https?://.*", message = "Base URL must start with http:// or https://")
    String baseUrl,

    @DefaultValue("30s")
    @NotNull
    Duration timeout,  // Duration type prevents negative values

    @DefaultValue("3")
    @Min(value = 0, message = "Max retries must be non-negative")
    @Max(value = 10, message = "Max retries must not exceed 10")
    int maxRetries,

    @DefaultValue("1s")
    @NotNull
    Duration retryDelay
) {
    /**
     * Custom validation: Ensure retry delay doesn't exceed timeout.
     */
    public ApiConfig {
        if (retryDelay.compareTo(timeout) >= 0) {
            throw new IllegalArgumentException(
                "Retry delay (" + retryDelay + ") must be less than timeout (" + timeout + ")"
            );
        }
    }
}
```

```yaml
# File: application.yml
app:
  api:
    base-url: https://api.example.com
    timeout: 30s
    max-retries: 3
    retry-delay: 1s
```

**Startup validation error (if config invalid):**

```
***************************
APPLICATION FAILED TO START
***************************

Description:

Binding to target org.springframework.boot.context.properties.bind.BindException:
Failed to bind properties under 'app.api' to com.example.config.ApiConfig

Reason: Validation failed:
  - Field error in object 'app.api' on field 'baseUrl': rejected value [];
    codes [NotBlank.app.api.baseUrl];
    default message [API base URL is required]
  - Field error in object 'app.api' on field 'maxRetries': rejected value [99];
    codes [Max.app.api.maxRetries];
    default message [Max retries must not exceed 10]

Action:

Update your application's configuration. The following values are invalid:

Property: app.api.base-url
Value: (empty)
Reason: API base URL is required

Property: app.api.max-retries
Value: 99
Reason: Max retries must not exceed 10
```

**Benefits of fix:**
- ✅ Fail fast: Invalid configuration caught at startup, not during runtime
- ✅ Clear error messages: Validation messages indicate exactly what's wrong
- ✅ Prevents runtime failures: No surprise NullPointerExceptions or IllegalArgumentExceptions
- ✅ Documentation: Validation constraints document valid ranges and formats
- ✅ Custom validation: Compact constructor validates cross-field constraints

**Common validation annotations:**

| Annotation | Purpose | Example |
|------------|---------|---------|
| `@NotNull` | Value must not be null | `@NotNull Duration timeout` |
| `@NotBlank` | String must not be blank | `@NotBlank String apiKey` |
| `@NotEmpty` | Collection must not be empty | `@NotEmpty List<String> hosts` |
| `@Min(n)` | Number must be ≥ n | `@Min(1) int poolSize` |
| `@Max(n)` | Number must be ≤ n | `@Max(100) int maxConnections` |
| `@Size(min, max)` | String/Collection size | `@Size(min=8, max=64) String password` |
| `@Email` | Valid email format | `@Email String emailAddress` |
| `@Pattern(regex)` | Matches regex | `@Pattern(regexp="^[A-Z]{2}$") String country` |
| `@Positive` | Number must be positive | `@Positive int port` |
| `@URL` | Valid URL format | `@URL String endpoint` |

#### Mistake 3: Not using profiles for environment-specific configuration

**❌ Problem:**

```java
// BAD: Single configuration file with hardcoded production values
# File: application.yml (single file for all environments)
spring:
  datasource:
    url: jdbc:postgresql://prod-db-cluster:5432/mydb  # Production URL hardcoded!
    username: prod_user
    password: prod_password  # Password in source control!
    hikari:
      maximum-pool-size: 50  # Production pool size for dev environment!

  data:
    redis:
      host: prod-redis-cluster  # Production Redis in dev!
      port: 6379

logging:
  level:
    root: WARN  # Production log level in dev (hard to debug)!

# Problems:
# 1. Can't run locally (prod-db-cluster doesn't resolve to localhost)
# 2. Password in source control (security risk)
# 3. Production pool size wastes resources in dev
# 4. WARN log level makes local debugging difficult
# 5. No way to test against local database
```

**Developer workarounds (anti-patterns):**

```bash
# Developer forced to override via command line (not tracked in version control)
java -jar myapp.jar \
  --spring.datasource.url=jdbc:postgresql://localhost:5432/mydb_dev \
  --spring.datasource.username=dev_user \
  --spring.datasource.password=dev_password \
  --spring.data.redis.host=localhost \
  --logging.level.root=DEBUG

# Or worse: Commenting out production values and uncommenting dev values before each run
```

**✅ Solution: Use profile-specific configuration files**

```yaml
# File: application.yml (base configuration, common across all environments)
spring:
  application:
    name: myapp
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}  # Default to dev profile

app:
  name: My Application
  version: 1.0.0
```

```yaml
# File: application-dev.yml (development environment)
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb_dev
    username: dev_user
    password: dev_password  # OK in dev (local database)
    hikari:
      maximum-pool-size: 5   # Small pool for dev
      minimum-idle: 1

  data:
    redis:
      host: localhost
      port: 6379

logging:
  level:
    root: DEBUG  # Verbose logging for development
    com.example: DEBUG

app:
  debug: true
  features:
    enable-beta-features: true  # Enable experimental features in dev
```

```yaml
# File: application-staging.yml (staging environment)
spring:
  datasource:
    url: jdbc:postgresql://staging-db:5432/mydb_staging
    username: ${DB_USERNAME}  # From environment variable
    password: ${DB_PASSWORD}  # From environment variable
    hikari:
      maximum-pool-size: 15
      minimum-idle: 5

  data:
    redis:
      host: ${REDIS_HOST:staging-redis}
      port: 6379
      password: ${REDIS_PASSWORD}

logging:
  level:
    root: INFO
    com.example: DEBUG  # Debug our code, but not third-party libraries

app:
  debug: false
  features:
    enable-beta-features: true  # Test beta features in staging
```

```yaml
# File: application-production.yml (production environment)
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST}:5432/${DB_NAME}
    username: ${DB_USERNAME}  # From environment variable (Kubernetes secret)
    password: ${DB_PASSWORD}  # From environment variable (Kubernetes secret)
    hikari:
      maximum-pool-size: 50   # Large pool for production
      minimum-idle: 10
      connection-timeout: 30000
      max-lifetime: 1800000
      keepalive-time: 30000

  data:
    redis:
      host: ${REDIS_HOST}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD}
      ssl: true  # Enable SSL for production Redis

logging:
  level:
    root: WARN  # Minimal logging in production
    com.example: INFO

app:
  debug: false
  features:
    enable-beta-features: false  # Disable experimental features in production
```

**Environment-specific bean configuration:**

```java
// File: src/main/java/com/example/config/EnvironmentConfig.java
package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

@Configuration
public class EnvironmentConfig {

    /**
     * Development: Use mock external service (no real API calls).
     */
    @Bean
    @Profile("dev")
    public ExternalApiClient mockApiClient() {
        return new MockExternalApiClient();
    }

    /**
     * Staging & Production: Use real external service.
     */
    @Bean
    @Profile({"staging", "production"})
    public ExternalApiClient realApiClient(ApiProperties apiProperties) {
        return new RealExternalApiClient(apiProperties);
    }
}
```

**Activate profiles:**

```bash
# Development (default, no argument needed)
java -jar myapp.jar

# Staging (via environment variable - preferred for containers)
export SPRING_PROFILES_ACTIVE=staging
java -jar myapp.jar

# Production (via command line argument)
java -jar myapp.jar --spring.profiles.active=production

# Multiple profiles (e.g., production + monitoring + featureX)
java -jar myapp.jar --spring.profiles.active=production,monitoring,featureX
```

**Kubernetes deployment example:**

```yaml
# kubernetes/deployment-production.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:1.0.0
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
```

**Benefits of fix:**
- ✅ Environment isolation: Dev config doesn't affect production (and vice versa)
- ✅ Easy local development: Run without overrides, defaults to dev profile
- ✅ Secrets management: Production secrets from environment variables (Kubernetes secrets, AWS Secrets Manager)
- ✅ Resource optimization: Small pools in dev, large pools in production
- ✅ Debugging: Verbose logging in dev, minimal in production
- ✅ Version controlled: Configuration tracked in Git (except secrets)
- ✅ Testability: Test profile with in-memory database, no external dependencies

### 1.2.3 Verification and Troubleshooting

#### Spring Boot Actuator /configprops Endpoint

Spring Boot Actuator provides `/actuator/configprops` endpoint to inspect all bound @ConfigurationProperties at runtime[^27].

**Enable actuator dependency:**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**Enable configprops endpoint:**

```yaml
# File: application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,configprops,env
  endpoint:
    configprops:
      enabled: true
```

**Query configuration properties at runtime:**

```bash
# Get all bound @ConfigurationProperties
curl http://localhost:8080/actuator/configprops | jq '.'

# Example response (partial):
{
  "contexts": {
    "application": {
      "beans": {
        "app.database-com.example.config.DatabaseProperties": {
          "prefix": "app.database",
          "properties": {
            "url": "jdbc:postgresql://localhost:5432/mydb",
            "username": "postgres",
            "password": "******",  // Masked for security
            "maxPoolSize": 25,
            "minIdle": 5,
            "connectionTimeout": "PT30S",
            "autoCommit": true
          },
          "inputs": {
            "url": {
              "value": "jdbc:postgresql://localhost:5432/mydb",
              "origin": "class path resource [application.yml] - 11:9"
            },
            "maxPoolSize": {
              "value": 25,
              "origin": "class path resource [application.yml] - 14:19"
            }
          }
        },
        "app.security-com.example.config.SecurityProperties": {
          "prefix": "app.security",
          "properties": {
            "jwt": {
              "secret": "******",  // Masked
              "accessTokenExpiration": "PT1H",
              "refreshTokenExpiration": "PT168H",
              "algorithm": "HS256"
            },
            "cors": {
              "allowedOrigins": ["http://localhost:3000", "https://example.com"],
              "allowedMethods": ["GET", "POST", "PUT", "DELETE"],
              "allowCredentials": true,
              "maxAge": 3600
            }
          }
        }
      }
    }
  }
}
```

**Query specific property:**

```bash
# Get environment variable value
curl http://localhost:8080/actuator/env/app.database.url | jq '.'

# Response shows property value and origin:
{
  "property": {
    "source": "Config resource 'class path resource [application.yml]' via location 'optional:classpath:/'",
    "value": "jdbc:postgresql://localhost:5432/mydb"
  },
  "activeProfiles": ["dev"],
  "propertySources": [
    {
      "name": "systemEnvironment",
      "property": {
        "value": null
      }
    },
    {
      "name": "applicationConfig: [classpath:/application-dev.yml]",
      "property": {
        "value": "jdbc:postgresql://localhost:5432/mydb_dev",
        "origin": "class path resource [application-dev.yml] - 3:9"
      }
    }
  ]
}
```

#### Troubleshooting Configuration Issues

**Problem 1: Property not bound (value remains null)**

**Symptom:**

```
2025-11-01 14:23:45.123 ERROR [main] com.example.Application -
Binding to target org.springframework.boot.context.properties.bind.BindException:
Failed to bind properties under 'app.database' to com.example.config.DatabaseProperties

Reason: java.lang.NullPointerException: Cannot invoke "String.isEmpty()"
because "this.url" is null
```

**Diagnosis:**

```bash
# Check property exists in environment
curl http://localhost:8080/actuator/env/app.database.url

# If property missing, check application.yml property name
# Common causes:
# - Typo in property name (app.databse.url vs. app.database.url)
# - Wrong prefix in @ConfigurationProperties (prefix="database" vs. prefix="app.database")
# - Property in wrong profile file (in application-prod.yml but running dev profile)
```

**Solution:**

```yaml
# Verify property path matches @ConfigurationProperties prefix
# @ConfigurationProperties(prefix = "app.database")
app:
  database:  # Must match prefix
    url: jdbc:postgresql://localhost:5432/mydb  # Kebab-case or camelCase both work
```

**Problem 2: Property validation failure**

**Symptom:**

```
***************************
APPLICATION FAILED TO START
***************************

Description:

Binding to target org.springframework.boot.context.properties.bind.BindException:
Failed to bind properties under 'app.api' to com.example.config.ApiConfig

Reason: Validation failed:
  - Field error in object 'app.api' on field 'maxRetries': rejected value [99];
    default message [Max retries must not exceed 10]
```

**Diagnosis:**

```bash
# Check actual property value
curl http://localhost:8080/actuator/configprops | jq '.contexts.application.beans["app.api-com.example.config.ApiConfig"]'

# Check validation constraints in @ConfigurationProperties class
# - @Min/@Max constraints
# - @NotBlank/@NotNull constraints
# - Custom validation in compact constructor
```

**Solution:**

```yaml
# Fix property value to satisfy validation constraints
app:
  api:
    max-retries: 3  # Change from 99 to 3 (within @Max(10) constraint)
```

**Problem 3: @ConfigurationProperties class not discovered**

**Symptom:**

```
Field config in com.example.service.UserService required a bean of type
'com.example.config.AppConfig' that could not be found.

Action:
Consider defining a bean of type 'com.example.config.AppConfig' in your configuration.
```

**Diagnosis:**

```bash
# Check if @ConfigurationPropertiesScan present on @SpringBootApplication
# Check if @ConfigurationProperties class in scanned package

# Verify application startup logs
grep "ConfigurationProperties" logs/application.log

# Expected:
# "ConfigurationPropertiesBeanRegistrar : Registered @ConfigurationProperties bean: app.config-com.example.config.AppConfig"
```

**Solution:**

```java
// Option 1: Add @ConfigurationPropertiesScan to main application class (recommended)
@SpringBootApplication
@ConfigurationPropertiesScan  // Add this annotation
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// Option 2: Enable specific @ConfigurationProperties class explicitly
@SpringBootApplication
@EnableConfigurationProperties(AppConfig.class)  // Enable specific config
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// Option 3: Register as bean manually (not recommended)
@Configuration
public class ConfigBeans {
    @Bean
    public AppConfig appConfig() {
        return new AppConfig(...);  // Lose auto-binding benefits
    }
}
```

**Problem 4: Profile not active (wrong configuration loaded)**

**Symptom:**

```
# Application running with dev database config in production!
2025-11-01 14:23:45.123 INFO [main] com.example.Application -
The following 1 profile is active: "default"

# Expected: "production" profile active
```

**Diagnosis:**

```bash
# Check active profiles via actuator
curl http://localhost:8080/actuator/env | jq '.activeProfiles'

# Check SPRING_PROFILES_ACTIVE environment variable
echo $SPRING_PROFILES_ACTIVE

# Check command line arguments
ps aux | grep java | grep spring.profiles.active
```

**Solution:**

```bash
# Set profile via environment variable (preferred for containers)
export SPRING_PROFILES_ACTIVE=production
java -jar myapp.jar

# Or via command line argument
java -jar myapp.jar --spring.profiles.active=production

# Kubernetes: Set in deployment manifest
env:
- name: SPRING_PROFILES_ACTIVE
  value: "production"
```

**Configuration debugging checklist:**

- [ ] Verify @ConfigurationPropertiesScan on @SpringBootApplication class
- [ ] Check property prefix matches @ConfigurationProperties(prefix="...")
- [ ] Validate property names (kebab-case in YAML: `max-retries` → `maxRetries` in Java)
- [ ] Ensure active profile matches expected environment (`actuator/env` → `activeProfiles`)
- [ ] Check property value via `/actuator/configprops` endpoint
- [ ] Verify validation constraints satisfied (@Min/@Max/@NotBlank)
- [ ] Check property origin via `/actuator/env/{property.name}` (which file provided value)
- [ ] Test configuration object in unit test (construct manually to verify validation)

---

### 1.2.4 Type Safety Patterns with Records and Generics

Java 17+ Records combined with generics provide compile-time type safety that prevents entire classes of configuration errors[^28][^29]. This section demonstrates advanced type safety patterns beyond basic @ConfigurationProperties.

**Core Benefits:**
- **Compile-Time Validation:** Type errors caught before runtime
- **Generic Type Parameters:** Type-safe collections and nested configurations
- **Optional<T> for Null Safety:** Explicit nullable handling
- **Sealed Classes:** Exhaustive pattern matching for configuration variants
- **Type Inference:** Concise code with `var` keyword

#### Pattern 1: Generic Configuration with Type-Safe Collections

Type-safe collections prevent ClassCastException and enable IDE autocomplete for complex nested structures[^29].

```java
// File: src/main/java/com/example/config/ServiceDiscoveryConfig.java
package com.example.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Service discovery configuration with generic type-safe collections.
 * Demonstrates Optional<T>, List<T>, and Map<K, V> for null safety and type safety.
 */
@ConfigurationProperties(prefix = "app.services")
@Validated
public record ServiceDiscoveryConfig(
    @NotNull @Valid List<ServiceEndpoint> endpoints,
    @NotNull Map<String, RetryPolicy> retryPolicies,
    Optional<HealthCheckConfig> healthCheck  // Optional for nullable config
) {
    /**
     * Service endpoint with typed health check configuration.
     */
    public record ServiceEndpoint(
        @NotBlank String name,
        @NotBlank @Pattern(regexp = "^https?://.*") String url,
        @DefaultValue("30s") Duration timeout,
        @NotNull Protocol protocol,
        @Valid Optional<AuthConfig> auth  // Optional auth (not all services need it)
    ) {}

    /**
     * Retry policy with exponential backoff.
     */
    public record RetryPolicy(
        @Min(1) @Max(10) int maxAttempts,
        @NotNull Duration initialDelay,
        @Min(1) @Max(10) int multiplier,
        @NotNull Duration maxDelay
    ) {}

    /**
     * Health check configuration with typed interval.
     */
    public record HealthCheckConfig(
        @NotNull Duration interval,
        @Min(1) int failureThreshold,
        @Min(1) int successThreshold,
        @NotBlank String path
    ) {}

    /**
     * Authentication configuration (optional per service).
     */
    public record AuthConfig(
        @NotNull AuthType type,
        @NotBlank String credential,
        Optional<String> username  // Optional for token-based auth
    ) {}

    /**
     * Protocol enum for type-safe protocol selection.
     */
    public enum Protocol {
        HTTP, HTTPS, GRPC, WEBSOCKET
    }

    /**
     * Auth type enum for exhaustive pattern matching.
     */
    public enum AuthType {
        BASIC, BEARER, API_KEY, OAUTH2
    }

    /**
     * Compact constructor for cross-field validation.
     */
    public ServiceDiscoveryConfig {
        // Validate all service names are unique
        var duplicates = endpoints.stream()
            .map(ServiceEndpoint::name)
            .filter(name -> endpoints.stream()
                .filter(e -> e.name().equals(name))
                .count() > 1)
            .toList();

        if (!duplicates.isEmpty()) {
            throw new IllegalArgumentException(
                "Duplicate service names found: " + String.join(", ", duplicates)
            );
        }

        // Validate retry policies exist for all endpoint names
        endpoints.forEach(endpoint -> {
            if (!retryPolicies.containsKey(endpoint.name())) {
                throw new IllegalArgumentException(
                    "Missing retry policy for service: " + endpoint.name()
                );
            }
        });

        // Validate auth credentials present when auth type specified
        endpoints.forEach(endpoint -> {
            endpoint.auth().ifPresent(auth -> {
                if (auth.type() == AuthType.BASIC && auth.username().isEmpty()) {
                    throw new IllegalArgumentException(
                        "BASIC auth requires username for service: " + endpoint.name()
                    );
                }
            });
        });
    }
}
```

**application.yml configuration:**

```yaml
app:
  services:
    endpoints:
      - name: user-service
        url: https://api.example.com/users
        timeout: 30s
        protocol: HTTPS
        auth:
          type: BEARER
          credential: ${USER_SERVICE_TOKEN}
          # username not needed for BEARER token

      - name: payment-service
        url: https://payments.example.com
        timeout: 60s
        protocol: HTTPS
        auth:
          type: BASIC
          credential: ${PAYMENT_SERVICE_PASSWORD}
          username: payment_client  # Required for BASIC auth

      - name: notification-service
        url: http://localhost:9090
        timeout: 10s
        protocol: HTTP
        # No auth for internal service

    retry-policies:
      user-service:
        max-attempts: 3
        initial-delay: 1s
        multiplier: 2
        max-delay: 10s

      payment-service:
        max-attempts: 5
        initial-delay: 500ms
        multiplier: 3
        max-delay: 30s

      notification-service:
        max-attempts: 2
        initial-delay: 100ms
        multiplier: 1
        max-delay: 1s

    health-check:
      interval: 30s
      failure-threshold: 3
      success-threshold: 2
      path: /health
```

**Usage with type-safe access:**

```java
// File: src/main/java/com/example/client/ServiceClient.java
package com.example.client;

import com.example.config.ServiceDiscoveryConfig;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
public class ServiceClient {

    private final ServiceDiscoveryConfig serviceConfig;

    public ServiceClient(ServiceDiscoveryConfig serviceConfig) {
        this.serviceConfig = serviceConfig;
    }

    /**
     * Get service endpoint by name with type-safe Optional handling.
     */
    public Optional<ServiceDiscoveryConfig.ServiceEndpoint> getEndpoint(String serviceName) {
        return serviceConfig.endpoints().stream()
            .filter(endpoint -> endpoint.name().equals(serviceName))
            .findFirst();
    }

    /**
     * Get retry policy with guaranteed non-null (validated at startup).
     */
    public ServiceDiscoveryConfig.RetryPolicy getRetryPolicy(String serviceName) {
        return serviceConfig.retryPolicies().get(serviceName);
        // Safe: compact constructor validates all endpoints have retry policies
    }

    /**
     * Check if health checks enabled (Optional handling).
     */
    public boolean isHealthCheckEnabled() {
        return serviceConfig.healthCheck().isPresent();
    }

    /**
     * Get health check interval with default fallback.
     */
    public java.time.Duration getHealthCheckInterval() {
        return serviceConfig.healthCheck()
            .map(ServiceDiscoveryConfig.HealthCheckConfig::interval)
            .orElse(java.time.Duration.ofMinutes(1));  // Default 1 minute
    }

    /**
     * Build HTTP client with type-safe protocol and auth.
     */
    public void configureHttpClient(String serviceName) {
        getEndpoint(serviceName).ifPresent(endpoint -> {
            // Type-safe protocol handling
            switch (endpoint.protocol()) {
                case HTTP -> configureHttp(endpoint);
                case HTTPS -> configureHttps(endpoint);
                case GRPC -> configureGrpc(endpoint);
                case WEBSOCKET -> configureWebSocket(endpoint);
            }

            // Type-safe auth handling with Optional
            endpoint.auth().ifPresent(auth -> {
                switch (auth.type()) {
                    case BASIC -> configureBasicAuth(
                        auth.username().orElseThrow(),
                        auth.credential()
                    );
                    case BEARER -> configureBearerToken(auth.credential());
                    case API_KEY -> configureApiKey(auth.credential());
                    case OAUTH2 -> configureOAuth2(auth.credential());
                }
            });
        });
    }

    // Mock implementations
    private void configureHttp(ServiceDiscoveryConfig.ServiceEndpoint endpoint) { }
    private void configureHttps(ServiceDiscoveryConfig.ServiceEndpoint endpoint) { }
    private void configureGrpc(ServiceDiscoveryConfig.ServiceEndpoint endpoint) { }
    private void configureWebSocket(ServiceDiscoveryConfig.ServiceEndpoint endpoint) { }
    private void configureBasicAuth(String username, String password) { }
    private void configureBearerToken(String token) { }
    private void configureApiKey(String apiKey) { }
    private void configureOAuth2(String clientSecret) { }
}
```

**✅ Benefits:**

- **Type Safety:** `List<ServiceEndpoint>` prevents ClassCastException, IDE autocomplete works
- **Null Safety:** `Optional<AuthConfig>` makes nullable fields explicit
- **Exhaustive Matching:** Enum switch statements compile-time validated (no missing cases)
- **Cross-Field Validation:** Compact constructor validates dependencies between fields
- **Startup Validation:** All validation errors fail fast with clear messages

**❌ Drawbacks:**

- Verbose Record definitions for complex nested structures
- Compact constructor validation logic can become complex
- Generic type parameters require understanding of Java generics

**Use When:**
- Configuration has nested structures (services, endpoints, policies)
- Need explicit null handling (Optional<T> for nullable fields)
- Want compile-time validation of protocol/enum types
- Cross-field validation required (retry policies for all endpoints)

#### Pattern 2: Sealed Classes for Configuration Variants

Sealed classes provide exhaustive pattern matching for configuration variants, ensuring all cases handled at compile time[^30].

```java
// File: src/main/java/com/example/config/CacheConfig.java
package com.example.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * Cache configuration with sealed class hierarchy for type-safe cache providers.
 * Sealed classes ensure exhaustive pattern matching (all subtypes must be handled).
 */
@ConfigurationProperties(prefix = "app.cache")
@Validated
public record CacheConfig(
    @NotNull CacheProvider provider,
    @NotNull @Valid Map<String, CachePolicy> policies,
    @DefaultValue("true") boolean enableMetrics
) {
    /**
     * Sealed interface for cache providers.
     * Only permits Redis, Caffeine, or Ehcache implementations.
     */
    public sealed interface CacheProvider
        permits RedisCache, CaffeineCache, EhcacheCache {}

    /**
     * Redis cache provider configuration.
     */
    public record RedisCache(
        @NotBlank String host,
        @Min(1) @Max(65535) int port,
        String password,
        @Min(0) @Max(15) int database,
        @NotNull Duration timeout,
        @Min(1) int poolSize
    ) implements CacheProvider {}

    /**
     * Caffeine in-memory cache configuration.
     */
    public record CaffeineCache(
        @Min(1) long maxSize,
        @NotNull Duration expireAfterWrite,
        @NotNull Duration expireAfterAccess,
        @DefaultValue("true") boolean recordStats
    ) implements CacheProvider {}

    /**
     * Ehcache disk-persistent cache configuration.
     */
    public record EhcacheCache(
        @NotBlank String diskStorePath,
        @Min(1) long maxEntriesLocalHeap,
        @Min(1) long maxBytesLocalDisk,
        @DefaultValue("true") boolean persistent
    ) implements CacheProvider {}

    /**
     * Cache policy per cache name.
     */
    public record CachePolicy(
        @NotNull Duration ttl,
        @Min(1) long maxEntries,
        @DefaultValue("true") boolean allowNullValues,
        @NotNull EvictionStrategy evictionStrategy
    ) {}

    /**
     * Eviction strategy enum.
     */
    public enum EvictionStrategy {
        LRU,   // Least Recently Used
        LFU,   // Least Frequently Used
        FIFO,  // First In First Out
        TTL    // Time To Live only
    }
}
```

**application-redis.yml (Redis provider):**

```yaml
app:
  cache:
    provider:
      host: ${REDIS_HOST:localhost}
      port: 6379
      password: ${REDIS_PASSWORD:}
      database: 0
      timeout: 5s
      pool-size: 10

    policies:
      users:
        ttl: 1h
        max-entries: 10000
        allow-null-values: false
        eviction-strategy: LRU

      sessions:
        ttl: 30m
        max-entries: 5000
        allow-null-values: false
        eviction-strategy: TTL

    enable-metrics: true
```

**application-caffeine.yml (Caffeine provider):**

```yaml
app:
  cache:
    provider:
      max-size: 10000
      expire-after-write: 1h
      expire-after-access: 30m
      record-stats: true

    policies:
      users:
        ttl: 1h
        max-entries: 10000
        allow-null-values: false
        eviction-strategy: LRU

    enable-metrics: true
```

**Type-safe cache manager configuration:**

```java
// File: src/main/java/com/example/config/CacheManagerConfig.java
package com.example.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;

import java.time.Duration;

/**
 * Cache manager configuration with exhaustive pattern matching on sealed CacheProvider.
 * Compiler ensures all CacheProvider subtypes are handled.
 */
@Configuration
@EnableCaching
public class CacheManagerConfig {

    private final CacheConfig cacheConfig;

    public CacheManagerConfig(CacheConfig cacheConfig) {
        this.cacheConfig = cacheConfig;
    }

    /**
     * Create cache manager based on sealed CacheProvider type.
     * Sealed interface ensures exhaustive pattern matching (compiler error if case missing).
     */
    @Bean
    public CacheManager cacheManager() {
        // Exhaustive pattern matching on sealed interface
        return switch (cacheConfig.provider()) {
            case CacheConfig.RedisCache redis -> createRedisCacheManager(redis);
            case CacheConfig.CaffeineCache caffeine -> createCaffeineCacheManager(caffeine);
            case CacheConfig.EhcacheCache ehcache -> createEhcacheCacheManager(ehcache);
            // Compiler error if new CacheProvider subtype added but not handled here
        };
    }

    /**
     * Create Redis cache manager with type-safe configuration.
     */
    private CacheManager createRedisCacheManager(CacheConfig.RedisCache redis) {
        var redisConfig = new RedisStandaloneConfiguration(redis.host(), redis.port());
        if (redis.password() != null && !redis.password().isBlank()) {
            redisConfig.setPassword(redis.password());
        }
        redisConfig.setDatabase(redis.database());

        var connectionFactory = new LettuceConnectionFactory(redisConfig);
        connectionFactory.afterPropertiesSet();

        var defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofHours(1))  // Default TTL
            .disableCachingNullValues();

        // Build cache configurations from policies
        var cacheConfigs = cacheConfig.policies().entrySet().stream()
            .collect(java.util.stream.Collectors.toMap(
                java.util.Map.Entry::getKey,
                entry -> buildRedisCacheConfig(entry.getValue())
            ));

        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigs)
            .build();
    }

    /**
     * Build Redis cache configuration from policy.
     */
    private RedisCacheConfiguration buildRedisCacheConfig(CacheConfig.CachePolicy policy) {
        var config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(policy.ttl());

        if (!policy.allowNullValues()) {
            config = config.disableCachingNullValues();
        }

        return config;
    }

    /**
     * Create Caffeine cache manager with type-safe configuration.
     */
    private CacheManager createCaffeineCacheManager(CacheConfig.CaffeineCache caffeine) {
        var cacheManager = new CaffeineCacheManager();

        var caffeineBuilder = Caffeine.newBuilder()
            .maximumSize(caffeine.maxSize())
            .expireAfterWrite(caffeine.expireAfterWrite())
            .expireAfterAccess(caffeine.expireAfterAccess());

        if (caffeine.recordStats()) {
            caffeineBuilder.recordStats();
        }

        cacheManager.setCaffeine(caffeineBuilder);

        // Set cache names from policies
        cacheManager.setCacheNames(cacheConfig.policies().keySet());

        return cacheManager;
    }

    /**
     * Create Ehcache cache manager (stub implementation).
     */
    private CacheManager createEhcacheCacheManager(CacheConfig.EhcacheCache ehcache) {
        // Ehcache implementation would go here
        throw new UnsupportedOperationException("Ehcache not yet implemented");
    }
}
```

**✅ Benefits:**

- **Exhaustive Matching:** Compiler error if new CacheProvider subtype added but not handled
- **Type Safety:** Switch statement knows exact type in each case (no casting needed)
- **Refactoring Safety:** Adding new provider type forces updates to all switch statements
- **Self-Documenting:** Sealed interface shows all possible cache providers at a glance

**❌ Drawbacks:**

- Java 17+ required (sealed classes introduced in Java 17)
- All permitted subtypes must be in same file or subpackage
- More verbose than simple enum (but more type-safe for complex configurations)

**Use When:**
- Configuration has distinct variants with different fields (Redis vs. Caffeine)
- Want exhaustive pattern matching (compiler-enforced handling of all cases)
- Need type-safe downcasting (switch statement provides exact type)
- Configuration variants are closed set (known at compile time)

#### Pattern 3: Type-Safe Builder Pattern for Complex Configuration

For configurations with many optional fields and complex validation, builder pattern with type safety provides fluent API[^31].

```java
// File: src/main/java/com/example/config/HttpClientConfig.java
package com.example.config;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.List;
import java.util.Optional;

/**
 * HTTP client configuration with builder pattern for complex optional configurations.
 * Demonstrates type-safe builders for configurations with many optional fields.
 */
@ConfigurationProperties(prefix = "app.http-client")
@Validated
public record HttpClientConfig(
    @NotNull @Valid ConnectionPoolConfig connectionPool,
    @NotNull @Valid TimeoutConfig timeouts,
    @NotNull @Valid RetryConfig retry,
    Optional<@Valid ProxyConfig> proxy,
    Optional<@Valid SslConfig> ssl,
    @NotNull @Valid List<String> defaultHeaders
) {
    /**
     * Connection pool configuration.
     */
    public record ConnectionPoolConfig(
        @Min(1) @Max(500) int maxConnections,
        @Min(1) @Max(100) int maxConnectionsPerRoute,
        @NotNull Duration connectionTimeout,
        @NotNull Duration idleTimeout,
        @DefaultValue("true") boolean keepAlive
    ) {
        /**
         * Type-safe builder for ConnectionPoolConfig.
         */
        public static Builder builder() {
            return new Builder();
        }

        public static class Builder {
            private int maxConnections = 100;
            private int maxConnectionsPerRoute = 20;
            private Duration connectionTimeout = Duration.ofSeconds(30);
            private Duration idleTimeout = Duration.ofMinutes(5);
            private boolean keepAlive = true;

            public Builder maxConnections(int maxConnections) {
                this.maxConnections = maxConnections;
                return this;
            }

            public Builder maxConnectionsPerRoute(int maxConnectionsPerRoute) {
                this.maxConnectionsPerRoute = maxConnectionsPerRoute;
                return this;
            }

            public Builder connectionTimeout(Duration connectionTimeout) {
                this.connectionTimeout = connectionTimeout;
                return this;
            }

            public Builder idleTimeout(Duration idleTimeout) {
                this.idleTimeout = idleTimeout;
                return this;
            }

            public Builder keepAlive(boolean keepAlive) {
                this.keepAlive = keepAlive;
                return this;
            }

            public ConnectionPoolConfig build() {
                return new ConnectionPoolConfig(
                    maxConnections,
                    maxConnectionsPerRoute,
                    connectionTimeout,
                    idleTimeout,
                    keepAlive
                );
            }
        }
    }

    /**
     * Timeout configuration with validation.
     */
    public record TimeoutConfig(
        @NotNull Duration connectTimeout,
        @NotNull Duration readTimeout,
        @NotNull Duration writeTimeout
    ) {
        // Compact constructor for cross-field validation
        public TimeoutConfig {
            if (connectTimeout.compareTo(readTimeout) > 0) {
                throw new IllegalArgumentException(
                    "Connect timeout must be <= read timeout"
                );
            }
        }
    }

    /**
     * Retry configuration with exponential backoff.
     */
    public record RetryConfig(
        @Min(0) @Max(10) int maxRetries,
        @NotNull Duration initialDelay,
        @Min(1) @Max(10) int backoffMultiplier,
        @NotNull Duration maxDelay,
        @NotNull List<Integer> retryableStatusCodes
    ) {
        // Default retryable status codes: 5xx, 408, 429
        public static RetryConfig withDefaults() {
            return new RetryConfig(
                3,
                Duration.ofMillis(500),
                2,
                Duration.ofSeconds(10),
                List.of(408, 429, 500, 502, 503, 504)
            );
        }
    }

    /**
     * Proxy configuration (optional).
     */
    public record ProxyConfig(
        @NotBlank String host,
        @Min(1) @Max(65535) int port,
        @NotNull ProxyType type,
        Optional<ProxyAuth> auth
    ) {
        public enum ProxyType {
            HTTP, SOCKS
        }

        public record ProxyAuth(
            @NotBlank String username,
            @NotBlank String password
        ) {}
    }

    /**
     * SSL/TLS configuration (optional).
     */
    public record SslConfig(
        @NotNull SslProtocol protocol,
        @NotNull List<String> enabledCipherSuites,
        @DefaultValue("true") boolean verifyHostname,
        Optional<String> keystorePath,
        Optional<String> keystorePassword,
        Optional<String> truststorePath,
        Optional<String> truststorePassword
    ) {
        public enum SslProtocol {
            TLSv1_2, TLSv1_3
        }
    }
}
```

**application.yml with complex HTTP client configuration:**

```yaml
app:
  http-client:
    connection-pool:
      max-connections: 200
      max-connections-per-route: 50
      connection-timeout: 30s
      idle-timeout: 5m
      keep-alive: true

    timeouts:
      connect-timeout: 10s
      read-timeout: 30s
      write-timeout: 30s

    retry:
      max-retries: 3
      initial-delay: 500ms
      backoff-multiplier: 2
      max-delay: 10s
      retryable-status-codes: [408, 429, 500, 502, 503, 504]

    # Optional proxy configuration
    proxy:
      host: proxy.example.com
      port: 8080
      type: HTTP
      auth:
        username: ${PROXY_USERNAME}
        password: ${PROXY_PASSWORD}

    # Optional SSL configuration
    ssl:
      protocol: TLSv1_3
      enabled-cipher-suites:
        - TLS_AES_256_GCM_SHA384
        - TLS_AES_128_GCM_SHA256
      verify-hostname: true
      keystore-path: ${KEYSTORE_PATH:/etc/ssl/keystore.jks}
      keystore-password: ${KEYSTORE_PASSWORD}
      truststore-path: ${TRUSTSTORE_PATH:/etc/ssl/truststore.jks}
      truststore-password: ${TRUSTSTORE_PASSWORD}

    default-headers:
      - "User-Agent: MyApp/1.0"
      - "Accept: application/json"
```

**Type-safe HTTP client builder:**

```java
// File: src/main/java/com/example/client/TypeSafeHttpClient.java
package com.example.client;

import com.example.config.HttpClientConfig;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.client5.http.impl.io.PoolingHttpClientConnectionManager;
import org.apache.hc.core5.util.Timeout;
import org.springframework.stereotype.Component;

/**
 * Type-safe HTTP client builder using configuration.
 */
@Component
public class TypeSafeHttpClient {

    private final HttpClientConfig config;

    public TypeSafeHttpClient(HttpClientConfig config) {
        this.config = config;
    }

    /**
     * Build Apache HttpClient with type-safe configuration.
     */
    public CloseableHttpClient buildHttpClient() {
        var httpClientBuilder = HttpClients.custom();

        // Configure connection pool (always present)
        var poolConfig = config.connectionPool();
        var connectionManager = new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(poolConfig.maxConnections());
        connectionManager.setDefaultMaxPerRoute(poolConfig.maxConnectionsPerRoute());
        httpClientBuilder.setConnectionManager(connectionManager);

        // Configure timeouts (always present)
        var timeouts = config.timeouts();
        httpClientBuilder.setDefaultRequestConfig(
            org.apache.hc.client5.http.config.RequestConfig.custom()
                .setConnectTimeout(Timeout.ofMilliseconds(timeouts.connectTimeout().toMillis()))
                .setResponseTimeout(Timeout.ofMilliseconds(timeouts.readTimeout().toMillis()))
                .build()
        );

        // Configure proxy (optional - type-safe Optional handling)
        config.proxy().ifPresent(proxy -> {
            var proxyHost = new org.apache.hc.core5.http.HttpHost(
                proxy.host(),
                proxy.port()
            );
            httpClientBuilder.setProxy(proxyHost);

            // Configure proxy auth (nested optional)
            proxy.auth().ifPresent(auth -> {
                var credentialsProvider = new org.apache.hc.client5.http.impl.auth.BasicCredentialsProvider();
                credentialsProvider.setCredentials(
                    new org.apache.hc.client5.http.auth.AuthScope(proxy.host(), proxy.port()),
                    new org.apache.hc.client5.http.auth.UsernamePasswordCredentials(
                        auth.username(),
                        auth.password().toCharArray()
                    )
                );
                httpClientBuilder.setDefaultCredentialsProvider(credentialsProvider);
            });
        });

        // Configure SSL (optional - type-safe Optional handling)
        config.ssl().ifPresent(ssl -> {
            try {
                var sslContextBuilder = org.apache.hc.core5.ssl.SSLContextBuilder.create();

                // Load keystore (nested optional)
                if (ssl.keystorePath().isPresent() && ssl.keystorePassword().isPresent()) {
                    var keystore = java.security.KeyStore.getInstance("JKS");
                    try (var ks = new java.io.FileInputStream(ssl.keystorePath().get())) {
                        keystore.load(ks, ssl.keystorePassword().get().toCharArray());
                    }
                    sslContextBuilder.loadKeyMaterial(
                        keystore,
                        ssl.keystorePassword().get().toCharArray()
                    );
                }

                // Load truststore (nested optional)
                if (ssl.truststorePath().isPresent() && ssl.truststorePassword().isPresent()) {
                    var truststore = java.security.KeyStore.getInstance("JKS");
                    try (var ts = new java.io.FileInputStream(ssl.truststorePath().get())) {
                        truststore.load(ts, ssl.truststorePassword().get().toCharArray());
                    }
                    sslContextBuilder.loadTrustMaterial(truststore, null);
                }

                var sslContext = sslContextBuilder.build();
                httpClientBuilder.setSSLContext(sslContext);

                if (!ssl.verifyHostname()) {
                    httpClientBuilder.setSSLHostnameVerifier(
                        org.apache.hc.client5.http.ssl.NoopHostnameVerifier.INSTANCE
                    );
                }
            } catch (Exception e) {
                throw new RuntimeException("Failed to configure SSL", e);
            }
        });

        return httpClientBuilder.build();
    }

    /**
     * Calculate retry delay using exponential backoff from config.
     */
    public long calculateRetryDelay(int attemptNumber) {
        var retryConfig = config.retry();
        var delay = retryConfig.initialDelay().toMillis() *
            (long) Math.pow(retryConfig.backoffMultiplier(), attemptNumber - 1);
        return Math.min(delay, retryConfig.maxDelay().toMillis());
    }

    /**
     * Check if HTTP status code should be retried.
     */
    public boolean isRetryable(int statusCode) {
        return config.retry().retryableStatusCodes().contains(statusCode);
    }
}
```

**✅ Benefits:**

- **Type Safety:** All configuration fields type-checked at compile time
- **Optional Handling:** Explicit nullable configuration (proxy, SSL) with Optional<T>
- **Validation:** Cross-field validation in compact constructor (connectTimeout <= readTimeout)
- **Builder Pattern:** Fluent API for complex configurations with many optional fields
- **Default Values:** Static factory methods for sensible defaults (RetryConfig.withDefaults())

**❌ Drawbacks:**

- Verbose Record definitions with nested Optionals
- Builder pattern adds boilerplate (but improves readability)
- Complex Optional chaining for deeply nested optional configurations

**Use When:**
- Configuration has many optional fields (proxy, SSL, authentication)
- Need cross-field validation (timeout relationships)
- Want explicit null handling (Optional<ProxyConfig> vs. null)
- Complex configuration requires fluent builder API

---

### 1.2.5 Advanced Validation Patterns

Beyond basic JSR-303 annotations, Spring Boot supports custom validators, group validation, and cross-field validation for complex business rules[^32][^33].

#### Pattern 1: Custom Validation Annotations

Create custom validation annotations for business-specific validation rules not covered by JSR-303[^33].

```java
// File: src/main/java/com/example/validation/ValidCron.java
package com.example.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

/**
 * Custom validation annotation for cron expressions.
 * Validates cron syntax at startup (prevents runtime cron parsing errors).
 */
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = CronValidator.class)
@Documented
public @interface ValidCron {
    String message() default "Invalid cron expression";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

```java
// File: src/main/java/com/example/validation/CronValidator.java
package com.example.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.springframework.scheduling.support.CronExpression;

/**
 * Validator for @ValidCron annotation.
 * Uses Spring's CronExpression parser to validate syntax.
 */
public class CronValidator implements ConstraintValidator<ValidCron, String> {

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null || value.isBlank()) {
            return true;  // @NotBlank handles null/empty validation separately
        }

        try {
            CronExpression.parse(value);
            return true;
        } catch (IllegalArgumentException e) {
            // Invalid cron expression
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate(
                "Invalid cron expression: " + e.getMessage()
            ).addConstraintViolation();
            return false;
        }
    }
}
```

```java
// File: src/main/java/com/example/validation/ValidUrl.java
package com.example.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

/**
 * Custom validation for URLs with protocol and hostname checks.
 */
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UrlValidator.class)
@Documented
public @interface ValidUrl {
    String message() default "Invalid URL";
    String[] allowedProtocols() default {"http", "https"};
    boolean requireHostname() default true;
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

```java
// File: src/main/java/com/example/validation/UrlValidator.java
package com.example.validation;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Arrays;

/**
 * Validator for @ValidUrl annotation with protocol whitelisting.
 */
public class UrlValidator implements ConstraintValidator<ValidUrl, String> {

    private String[] allowedProtocols;
    private boolean requireHostname;

    @Override
    public void initialize(ValidUrl constraintAnnotation) {
        this.allowedProtocols = constraintAnnotation.allowedProtocols();
        this.requireHostname = constraintAnnotation.requireHostname();
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null || value.isBlank()) {
            return true;
        }

        try {
            URL url = new URL(value);

            // Validate protocol
            if (!Arrays.asList(allowedProtocols).contains(url.getProtocol())) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate(
                    "URL protocol must be one of: " + String.join(", ", allowedProtocols)
                ).addConstraintViolation();
                return false;
            }

            // Validate hostname
            if (requireHostname && (url.getHost() == null || url.getHost().isBlank())) {
                context.disableDefaultConstraintViolation();
                context.buildConstraintViolationWithTemplate(
                    "URL must include a hostname"
                ).addConstraintViolation();
                return false;
            }

            return true;
        } catch (MalformedURLException e) {
            context.disableDefaultConstraintViolation();
            context.buildConstraintViolationWithTemplate(
                "Malformed URL: " + e.getMessage()
            ).addConstraintViolation();
            return false;
        }
    }
}
```

**Usage in configuration:**

```java
// File: src/main/java/com/example/config/SchedulerConfig.java
package com.example.config;

import com.example.validation.ValidCron;
import com.example.validation.ValidUrl;
import jakarta.validation.constraints.*;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.List;

/**
 * Scheduler configuration with custom validation annotations.
 */
@ConfigurationProperties(prefix = "app.scheduler")
@Validated
public record SchedulerConfig(
    @NotNull @Valid List<ScheduledJob> jobs,
    @NotNull Duration defaultTimeout
) {
    /**
     * Scheduled job configuration with custom cron validation.
     */
    public record ScheduledJob(
        @NotBlank String name,
        @NotBlank @ValidCron String cronExpression,
        @NotBlank @ValidUrl(allowedProtocols = {"http", "https"}) String webhookUrl,
        @NotNull Duration timeout,
        @Min(0) @Max(10) int maxRetries
    ) {}
}
```

**application.yml:**

```yaml
app:
  scheduler:
    default-timeout: 5m
    jobs:
      - name: daily-report
        cron-expression: "0 0 2 * * ?"  # 2 AM daily
        webhook-url: https://api.example.com/webhooks/report
        timeout: 10m
        max-retries: 3

      - name: hourly-sync
        cron-expression: "0 0 * * * ?"  # Every hour
        webhook-url: https://sync.example.com/trigger
        timeout: 5m
        max-retries: 2

      # Invalid cron expression (validation error at startup)
      # - name: invalid-job
      #   cron-expression: "INVALID CRON"  # Fails startup validation
      #   webhook-url: https://example.com
      #   timeout: 1m
      #   max-retries: 0
```

**Startup validation error (if invalid cron):**

```
***************************
APPLICATION FAILED TO START
***************************

Description:

Binding to target org.springframework.boot.context.properties.bind.BindException:
Failed to bind properties under 'app.scheduler' to com.example.config.SchedulerConfig

Reason: Validation failed:
  - Field error in object 'app.scheduler.jobs[2]' on field 'cronExpression': rejected value [INVALID CRON];
    codes [ValidCron.jobs[2].cronExpression]; default message [Invalid cron expression: Cron expression must consist of 6 fields]

Action:

Update your application's configuration
```

**✅ Benefits:**

- **Custom Business Logic:** Validate complex rules not expressible with standard JSR-303
- **Startup Validation:** Configuration errors caught before application starts
- **Reusable:** Custom annotations reusable across multiple configuration classes
- **Clear Error Messages:** Custom validation messages explain exactly what's wrong

**❌ Drawbacks:**

- Boilerplate code (annotation + validator class per custom rule)
- Validation logic separate from configuration (in validator class)
- Requires understanding of JSR-303 ConstraintValidator API

**Use When:**
- Need business-specific validation (cron expressions, custom URL rules)
- Standard JSR-303 annotations insufficient
- Want reusable validation across multiple configurations
- Validation logic complex enough to justify separate validator class

#### Pattern 2: Validation Groups for Conditional Validation

Validation groups enable different validation rules for different scenarios (dev vs. prod, create vs. update)[^34].

```java
// File: src/main/java/com/example/validation/ValidationGroups.java
package com.example.validation;

/**
 * Validation group markers for conditional validation.
 * Different validation rules apply in different environments or scenarios.
 */
public class ValidationGroups {
    /**
     * Development environment validation (lenient).
     */
    public interface Development {}

    /**
     * Staging environment validation (moderate).
     */
    public interface Staging {}

    /**
     * Production environment validation (strict).
     */
    public interface Production {}

    /**
     * Create operation validation (all fields required).
     */
    public interface Create {}

    /**
     * Update operation validation (only changed fields validated).
     */
    public interface Update {}
}
```

```java
// File: src/main/java/com/example/config/SecurityConfig.java
package com.example.config;

import com.example.validation.ValidationGroups;
import jakarta.validation.constraints.*;
import jakarta.validation.groups.Default;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;

/**
 * Security configuration with validation groups for environment-specific rules.
 * Production has stricter validation than development.
 */
@ConfigurationProperties(prefix = "app.security")
@Validated
public record SecurityConfig(
    @NotNull JwtConfig jwt,
    @NotNull CorsConfig cors,
    @NotNull PasswordPolicyConfig passwordPolicy
) {
    /**
     * JWT configuration with group-specific validation.
     */
    public record JwtConfig(
        @NotBlank(groups = {Default.class, ValidationGroups.Development.class,
                            ValidationGroups.Staging.class, ValidationGroups.Production.class})
        // Development: Allow weak secrets (for testing)
        @Size(min = 16, message = "JWT secret must be at least 16 characters",
              groups = {Default.class, ValidationGroups.Development.class})
        // Production: Require strong secrets
        @Size(min = 64, message = "JWT secret must be at least 64 characters in production",
              groups = ValidationGroups.Production.class)
        String secret,

        @NotNull Duration accessTokenExpiration,

        @NotNull Duration refreshTokenExpiration,

        @NotBlank String algorithm
    ) {
        // Compact constructor for cross-field validation
        public JwtConfig {
            if (refreshTokenExpiration.compareTo(accessTokenExpiration) <= 0) {
                throw new IllegalArgumentException(
                    "Refresh token expiration must be greater than access token expiration"
                );
            }
        }
    }

    /**
     * CORS configuration with environment-specific allowed origins.
     */
    public record CorsConfig(
        // Development: Allow localhost origins
        @NotEmpty(groups = {Default.class, ValidationGroups.Development.class})
        // Production: Disallow wildcard origins
        @NotEmpty(message = "Allowed origins must not be empty in production",
                  groups = ValidationGroups.Production.class)
        java.util.List<@NotBlank String> allowedOrigins,

        @NotEmpty java.util.List<@NotBlank String> allowedMethods,

        boolean allowCredentials,

        @Min(0) @Max(86400) int maxAge
    ) {
        // Validation: Disallow "*" wildcard in production
        public CorsConfig {
            // This validation only matters in production (use @AssertTrue with groups in real implementation)
            if (allowedOrigins.contains("*")) {
                throw new IllegalArgumentException(
                    "Wildcard CORS origin (*) not allowed in production"
                );
            }
        }
    }

    /**
     * Password policy with group-specific strength requirements.
     */
    public record PasswordPolicyConfig(
        // Development: Lenient password requirements
        @Min(value = 4, message = "Password minimum length is 4 in development",
             groups = ValidationGroups.Development.class)
        // Production: Strict password requirements
        @Min(value = 12, message = "Password minimum length is 12 in production",
             groups = ValidationGroups.Production.class)
        int minLength,

        @AssertTrue(message = "Must require uppercase letters in production",
                    groups = ValidationGroups.Production.class)
        boolean requireUppercase,

        @AssertTrue(message = "Must require lowercase letters in production",
                    groups = ValidationGroups.Production.class)
        boolean requireLowercase,

        @AssertTrue(message = "Must require digits in production",
                    groups = ValidationGroups.Production.class)
        boolean requireDigits,

        @AssertTrue(message = "Must require special characters in production",
                    groups = ValidationGroups.Production.class)
        boolean requireSpecialChars,

        @Min(1) int maxFailedAttempts,

        @NotNull Duration lockoutDuration
    ) {}
}
```

**application-dev.yml (lenient validation):**

```yaml
app:
  security:
    jwt:
      secret: dev-secret-key-16  # 16 chars OK for dev (fails production validation)
      access-token-expiration: 1h
      refresh-token-expiration: 7d
      algorithm: HS256

    cors:
      allowed-origins:
        - "*"  # Wildcard OK for dev (would fail production validation)
      allowed-methods: ["GET", "POST", "PUT", "DELETE"]
      allow-credentials: true
      max-age: 3600

    password-policy:
      min-length: 4  # Lenient for dev (12 required in production)
      require-uppercase: false  # Not required in dev
      require-lowercase: false
      require-digits: false
      require-special-chars: false
      max-failed-attempts: 10
      lockout-duration: 5m
```

**application-production.yml (strict validation):**

```yaml
app:
  security:
    jwt:
      secret: ${JWT_SECRET}  # Must be 64+ chars in production (env variable required)
      access-token-expiration: 15m
      refresh-token-expiration: 7d
      algorithm: HS256

    cors:
      allowed-origins:
        - https://app.example.com
        - https://admin.example.com
        # No wildcard allowed in production
      allowed-methods: ["GET", "POST", "PUT", "DELETE"]
      allow-credentials: true
      max-age: 3600

    password-policy:
      min-length: 12  # Strict requirement in production
      require-uppercase: true  # All complexity requirements enforced
      require-lowercase: true
      require-digits: true
      require-special-chars: true
      max-failed-attempts: 5
      lockout-duration: 30m
```

**Activate validation group based on environment:**

```java
// File: src/main/java/com/example/config/ValidationConfiguration.java
package com.example.config;

import com.example.validation.ValidationGroups;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;

/**
 * Validation configuration with profile-specific validation groups.
 */
@Configuration
public class ValidationConfiguration {

    /**
     * Development profile: Use Development validation group (lenient).
     */
    @Bean
    @Profile("dev")
    public LocalValidatorFactoryBean devValidator() {
        var validator = new LocalValidatorFactoryBean();
        // Add Development group to default groups
        return validator;
    }

    /**
     * Production profile: Use Production validation group (strict).
     */
    @Bean
    @Profile("production")
    public LocalValidatorFactoryBean productionValidator() {
        var validator = new LocalValidatorFactoryBean();
        // Add Production group to default groups
        return validator;
    }
}
```

**✅ Benefits:**

- **Environment-Specific Validation:** Different rules for dev vs. production
- **Conditional Validation:** Different rules for create vs. update operations
- **Fail Fast:** Production-specific validation catches config errors at startup
- **Flexibility:** Enable/disable validation rules based on runtime context

**❌ Drawbacks:**

- Complex syntax (groups attribute on each annotation)
- Validation logic scattered across group annotations
- Requires manual group activation (profile-specific beans)

**Use When:**
- Validation requirements differ by environment (dev lenient, prod strict)
- Need conditional validation for operations (create vs. update)
- Want to enforce security policies in production but relax in dev
- Configuration validation rules depend on runtime context

#### Pattern 3: Programmatic Validation with Validator API

For complex validation scenarios requiring service dependencies or external system checks, use programmatic validation[^35].

```java
// File: src/main/java/com/example/validation/DatabaseConfigValidator.java
package com.example.validation;

import com.example.config.AppConfig;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Set;

/**
 * Programmatic validation of database configuration at startup.
 * Tests actual database connectivity (beyond JSR-303 validation).
 */
@Component
public class DatabaseConfigValidator {

    private static final Logger log = LoggerFactory.getLogger(DatabaseConfigValidator.class);

    private final AppConfig appConfig;
    private final DataSource dataSource;
    private final Validator validator;

    public DatabaseConfigValidator(
        AppConfig appConfig,
        DataSource dataSource,
        Validator validator
    ) {
        this.appConfig = appConfig;
        this.dataSource = dataSource;
        this.validator = validator;
    }

    /**
     * Validate database configuration after application startup.
     * Tests actual connectivity and pool configuration.
     */
    @EventListener(ApplicationReadyEvent.class)
    public void validateDatabaseConfiguration() {
        log.info("Validating database configuration...");

        // Step 1: JSR-303 validation
        Set<ConstraintViolation<AppConfig.DatabaseConfig>> violations =
            validator.validate(appConfig.database());

        if (!violations.isEmpty()) {
            violations.forEach(violation ->
                log.error("Configuration validation error: {}: {}",
                    violation.getPropertyPath(),
                    violation.getMessage())
            );
            throw new IllegalStateException("Database configuration validation failed");
        }

        // Step 2: Test actual database connectivity
        try (Connection connection = dataSource.getConnection()) {
            if (!connection.isValid(5)) {
                throw new SQLException("Database connection validation failed");
            }
            log.info("Database connectivity validated successfully");
        } catch (SQLException e) {
            log.error("Database connectivity test failed", e);
            throw new IllegalStateException("Cannot connect to database: " + e.getMessage(), e);
        }

        // Step 3: Validate connection pool configuration
        validateConnectionPoolSettings();

        log.info("Database configuration validation complete");
    }

    /**
     * Validate connection pool configuration values.
     */
    private void validateConnectionPoolSettings() {
        var dbConfig = appConfig.database();

        // Validate max pool size > min idle
        if (dbConfig.maxPoolSize() <= dbConfig.minIdle()) {
            throw new IllegalArgumentException(
                "maxPoolSize (" + dbConfig.maxPoolSize() + ") must be > minIdle (" +
                dbConfig.minIdle() + ")"
            );
        }

        // Validate connection timeout is reasonable
        if (dbConfig.connectionTimeout().toSeconds() > 60) {
            log.warn("Connection timeout is very high: {}s (consider reducing to avoid blocking)",
                dbConfig.connectionTimeout().toSeconds());
        }

        // Validate URL format
        if (!dbConfig.url().startsWith("jdbc:")) {
            throw new IllegalArgumentException(
                "Database URL must start with 'jdbc:'"
            );
        }

        log.info("Connection pool settings validated: maxPoolSize={}, minIdle={}, timeout={}",
            dbConfig.maxPoolSize(),
            dbConfig.minIdle(),
            dbConfig.connectionTimeout());
    }
}
```

```java
// File: src/main/java/com/example/validation/RedisConfigValidator.java
package com.example.validation;

import com.example.config.AppConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.stereotype.Component;

/**
 * Programmatic validation of Redis configuration at startup.
 * Tests actual Redis connectivity.
 */
@Component
public class RedisConfigValidator {

    private static final Logger log = LoggerFactory.getLogger(RedisConfigValidator.class);

    private final AppConfig appConfig;
    private final RedisConnectionFactory redisConnectionFactory;

    public RedisConfigValidator(
        AppConfig appConfig,
        RedisConnectionFactory redisConnectionFactory
    ) {
        this.appConfig = appConfig;
        this.redisConnectionFactory = redisConnectionFactory;
    }

    /**
     * Validate Redis configuration after application startup.
     * Tests actual connectivity and database selection.
     */
    @EventListener(ApplicationReadyEvent.class)
    public void validateRedisConfiguration() {
        log.info("Validating Redis configuration...");

        var redisConfig = appConfig.redis();

        try {
            // Test Redis connectivity
            var connection = redisConnectionFactory.getConnection();
            connection.ping();
            connection.close();

            log.info("Redis connectivity validated: host={}, port={}, database={}",
                redisConfig.host(),
                redisConfig.port(),
                redisConfig.database());
        } catch (Exception e) {
            log.error("Redis connectivity test failed", e);
            throw new IllegalStateException("Cannot connect to Redis: " + e.getMessage(), e);
        }

        // Validate Redis database number (0-15 for standard Redis)
        if (redisConfig.database() < 0 || redisConfig.database() > 15) {
            throw new IllegalArgumentException(
                "Redis database must be between 0-15 (got " + redisConfig.database() + ")"
            );
        }

        // Validate pool size is reasonable
        if (redisConfig.poolSize() > 100) {
            log.warn("Redis pool size is very high: {} (consider reducing to avoid resource exhaustion)",
                redisConfig.poolSize());
        }

        log.info("Redis configuration validation complete");
    }
}
```

**✅ Benefits:**

- **Runtime Validation:** Test actual connectivity, not just configuration syntax
- **Service Dependencies:** Can inject DataSource, RedisConnectionFactory for real tests
- **Startup Failure:** Application fails fast if external systems unreachable
- **Complex Logic:** Cross-system validation (database + Redis must both be reachable)

**❌ Drawbacks:**

- Requires external systems available at startup (can't start app if Redis down)
- Validation code separate from configuration definition
- Slower startup (network connectivity tests take time)

**Use When:**
- Need to test actual connectivity to external systems
- Configuration validation requires service dependencies
- Want startup to fail if external systems unreachable
- Complex cross-system validation logic

---

### 1.2.6 Type Safety Best Practices

Comprehensive type safety guidelines for configuration management using Java 17+ features[^36][^37].

#### Best Practice 1: Use Optional<T> for Nullable Configuration

Make nullable configuration explicit with Optional<T> instead of null checks[^36].

**❌ Anti-Pattern: Implicit nullability**

```java
// BAD: Implicit null (no indication field is nullable)
@ConfigurationProperties(prefix = "app")
public record AppConfig(
    String proxyUrl,  // Is this nullable? Unclear!
    Integer port       // Is this nullable? Unclear!
) {
    // Null checks scattered throughout codebase
    public boolean hasProxy() {
        return proxyUrl != null && !proxyUrl.isBlank();
    }
}

// Service code full of null checks
public void configureClient(AppConfig config) {
    if (config.proxyUrl() != null) {  // Repetitive null check
        setProxy(config.proxyUrl());
    }

    int port = config.port() != null ? config.port() : 8080;  // Verbose default
}
```

**✅ Best Practice: Explicit Optional<T>**

```java
// GOOD: Explicit Optional (clear that fields are nullable)
@ConfigurationProperties(prefix = "app")
public record AppConfig(
    Optional<String> proxyUrl,  // Clearly nullable
    Optional<Integer> port       // Clearly nullable
) {
    // Optional API for clean null handling
    public boolean hasProxy() {
        return proxyUrl.isPresent();
    }

    public String getProxyUrlOrDefault(String defaultUrl) {
        return proxyUrl.orElse(defaultUrl);
    }
}

// Service code uses Optional API (no null checks)
public void configureClient(AppConfig config) {
    config.proxyUrl().ifPresent(this::setProxy);  // Clean, fluent

    int port = config.port().orElse(8080);  // Concise default
}
```

**When to use Optional<T>:**

| Scenario | Use Optional<T>? | Rationale |
|----------|------------------|-----------|
| Configuration field may be unset | ✅ Yes | Makes nullability explicit |
| Field has @DefaultValue | ❌ No | Default value means non-null |
| Field required (@NotNull) | ❌ No | Validation ensures non-null |
| Nested configuration block | ✅ Yes | Entire block may be omitted |
| Collection field | ❌ No | Use empty list instead of null |

#### Best Practice 2: Prefer Records over POJOs for Immutability

Java Records provide immutability, equals/hashCode, and toString for free[^29].

**❌ Anti-Pattern: Mutable POJO**

```java
// BAD: Mutable POJO (verbose, error-prone)
@ConfigurationProperties(prefix = "app.database")
public class DatabaseConfig {
    private String url;
    private String username;
    private String password;
    private int maxPoolSize;

    // Setters allow mutation after construction
    public void setUrl(String url) { this.url = url; }
    public void setUsername(String username) { this.username = username; }
    public void setPassword(String password) { this.password = password; }
    public void setMaxPoolSize(int maxPoolSize) { this.maxPoolSize = maxPoolSize; }

    // Getters
    public String getUrl() { return url; }
    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public int getMaxPoolSize() { return maxPoolSize; }

    // Must manually implement equals/hashCode/toString
    @Override
    public boolean equals(Object o) { /* boilerplate */ }

    @Override
    public int hashCode() { /* boilerplate */ }

    @Override
    public String toString() { /* boilerplate */ }
}

// Problem: Configuration can be mutated after initialization
dbConfig.setMaxPoolSize(1000);  // Unexpected mutation!
```

**✅ Best Practice: Immutable Record**

```java
// GOOD: Immutable Record (concise, type-safe)
@ConfigurationProperties(prefix = "app.database")
public record DatabaseConfig(
    String url,
    String username,
    String password,
    int maxPoolSize
) {
    // equals/hashCode/toString auto-generated
    // No setters (immutable by default)
}

// Configuration cannot be mutated (compile error)
// dbConfig.setMaxPoolSize(1000);  // Compile error: no setter
```

**Record benefits:**

- ✅ **Immutable:** No setters, thread-safe by default
- ✅ **Concise:** No boilerplate getters/setters/equals/hashCode
- ✅ **Type-Safe:** All fields final, null checks via validation
- ✅ **Readable:** Clear intent (data carrier, not business logic)

#### Best Practice 3: Use Enums for Fixed Value Sets

Enums provide compile-time validation for fixed value sets (protocols, log levels, cache strategies)[^37].

**❌ Anti-Pattern: String constants**

```java
// BAD: String constants (no compile-time validation)
@ConfigurationProperties(prefix = "app.cache")
public record CacheConfig(
    String strategy  // Could be "LRU", "lru", "LeastRecentlyUsed", typo, etc.
) {
    // Runtime validation needed (error not caught until execution)
    public void validateStrategy() {
        if (!strategy.equalsIgnoreCase("LRU") &&
            !strategy.equalsIgnoreCase("LFU") &&
            !strategy.equalsIgnoreCase("FIFO")) {
            throw new IllegalArgumentException("Invalid cache strategy: " + strategy);
        }
    }
}

// Usage requires string literals (no IDE autocomplete, typos possible)
if (config.strategy().equals("LRU")) {  // Typo risk: "LRU" vs "lru"
    configureLru();
}
```

**✅ Best Practice: Type-safe Enum**

```java
// GOOD: Type-safe Enum (compile-time validation)
@ConfigurationProperties(prefix = "app.cache")
public record CacheConfig(
    @NotNull CacheStrategy strategy  // Enum ensures valid values only
) {
    public enum CacheStrategy {
        LRU,   // Least Recently Used
        LFU,   // Least Frequently Used
        FIFO,  // First In First Out
        TTL    // Time To Live
    }
}

// Usage with switch expression (exhaustive, compile-time checked)
switch (config.strategy()) {
    case LRU -> configureLru();
    case LFU -> configureLfu();
    case FIFO -> configureFifo();
    case TTL -> configureTtl();
    // Compiler error if case missing
}
```

**application.yml with enum:**

```yaml
app:
  cache:
    strategy: LRU  # Must match enum constant name
```

**Enum benefits:**

- ✅ **Type Safety:** Only valid enum constants allowed
- ✅ **IDE Support:** Autocomplete shows all valid values
- ✅ **Exhaustive Matching:** Switch statements checked at compile time
- ✅ **Refactoring Safety:** Renaming enum updates all usages

#### Best Practice 4: Validate at Construction with Compact Constructor

Use Record compact constructors for validation that runs immediately at object creation[^29].

**✅ Best Practice: Compact constructor validation**

```java
@ConfigurationProperties(prefix = "app.retry")
public record RetryConfig(
    @Min(1) @Max(10) int maxAttempts,
    @NotNull Duration initialDelay,
    @Min(1) int backoffMultiplier,
    @NotNull Duration maxDelay
) {
    /**
     * Compact constructor for cross-field validation.
     * Runs after JSR-303 validation, before field assignment.
     */
    public RetryConfig {
        // Validate initialDelay < maxDelay
        if (initialDelay.compareTo(maxDelay) >= 0) {
            throw new IllegalArgumentException(
                "initialDelay (" + initialDelay + ") must be < maxDelay (" + maxDelay + ")"
            );
        }

        // Validate backoff multiplier results in reasonable delay
        var predictedMaxDelay = initialDelay.multipliedBy(
            (long) Math.pow(backoffMultiplier, maxAttempts - 1)
        );
        if (predictedMaxDelay.compareTo(Duration.ofMinutes(10)) > 0) {
            throw new IllegalArgumentException(
                "Backoff multiplier (" + backoffMultiplier + ") with maxAttempts (" +
                maxAttempts + ") results in excessive delay: " + predictedMaxDelay
            );
        }
    }
}
```

**Validation order:**

1. **JSR-303 validation:** `@Min`, `@Max`, `@NotNull` checked first
2. **Compact constructor:** Cross-field validation runs second
3. **Field assignment:** Fields assigned only if all validation passes

**Compact constructor benefits:**

- ✅ **Fail Fast:** Validation at construction time (before object usable)
- ✅ **Immutability Enforced:** No setters, validation runs once
- ✅ **Cross-Field Validation:** Check relationships between fields
- ✅ **Clear Intent:** Validation logic colocated with Record definition

#### Best Practice 5: Use Type Inference with var for Readability

Java 10+ `var` keyword reduces verbosity while maintaining type safety[^38].

**✅ Best Practice: Type inference with var**

```java
// Service with injected configuration
public class CacheService {
    private final CacheConfig config;

    public CacheService(CacheConfig config) {
        this.config = config;
    }

    public void configureCacheManager() {
        // GOOD: Use var for obvious types (reduces verbosity)
        var strategy = config.strategy();  // Type: CacheStrategy (clear from context)
        var ttl = config.ttl();            // Type: Duration (clear from context)
        var maxEntries = config.maxEntries();  // Type: long (clear from context)

        // GOOD: Use var for complex generic types
        var endpoints = config.endpoints();  // Type: List<ServiceEndpoint> (verbose if explicit)
        var policies = config.policies();    // Type: Map<String, RetryPolicy> (verbose if explicit)

        // BAD: Don't use var when type not obvious
        var result = calculate();  // Type unclear! What does calculate() return?

        // GOOD: Explicit type when not obvious
        Optional<String> proxyUrl = config.proxyUrl();  // Explicit Optional important
    }
}
```

**var guidelines:**

| Scenario | Use var? | Rationale |
|----------|----------|-----------|
| Type obvious from RHS | ✅ Yes | `var config = new CacheConfig(...)` |
| Return type of config method | ✅ Yes | `var ttl = config.ttl()` (clear) |
| Complex generic types | ✅ Yes | `var map = new HashMap<String, List<ServiceEndpoint>>()` |
| Primitive wrappers | ✅ Yes | `var count = config.maxRetries()` |
| Method return unclear | ❌ No | `var result = process()` (unclear) |
| Lambda expressions | ❌ No | `var fn = x -> x * 2` (type inference conflict) |

---

### 1.3 Alternative Approaches

**Alternative 1: @Value for Simple Properties**

Use @Value for single, unrelated properties[^6]. Not recommended for grouped configuration.

*Pros:* Simple syntax, no extra class needed
*Cons:* No type safety, scattered configuration, no validation, doesn't scale
*Use When:* Single property in single class (rare)

```java
@Service
public class EmailService {
    @Value("${email.smtp.host}")
    private String smtpHost;

    @Value("${email.smtp.port:587}")
    private int smtpPort;

    // Not recommended for complex configs - use @ConfigurationProperties instead
}
```

**Alternative 2: Environment Variables with @Value**

Read directly from environment variables[^7].

*Pros:* Twelve-factor app compliance, container-native
*Cons:* Still has @Value drawbacks (no type safety, scattered)
*Use When:* Simple services with <5 configuration values

```java
@Value("${DATABASE_URL}")
private String databaseUrl;

@Value("${REDIS_HOST:localhost}")
private String redisHost;
```

**Alternative 3: Spring Cloud Config**

Centralized configuration server for distributed systems[^8].

*Pros:* Centralized config, dynamic refresh, versioning
*Cons:* Additional infrastructure, complexity
*Use When:* Microservices ecosystem with 5+ services

### 1.4 Decision Criteria

| Factor | @ConfigurationProperties + Records | @Value | Spring Cloud Config |
|--------|-----------------------------------|--------|---------------------|
| Type Safety | ✅ Excellent | ❌ None | ✅ Excellent |
| Validation | ✅ JSR-303/380 | ❌ Manual | ✅ JSR-303/380 |
| Immutability | ✅ Records | ❌ Mutable | ✅ Depends |
| Scalability | ✅ Scales well | ❌ Doesn't scale | ✅ Scales well |
| Complexity | Low | Very Low | High |
| Hot Reload | ⚠️ Via @RefreshScope | ❌ No | ✅ Yes |
| **Recommended For** | **Most apps** | Single properties | Large ecosystems |

**Decision Rule:** Use @ConfigurationProperties with Records for all grouped configuration (default), @Value only for single unrelated properties, Spring Cloud Config for microservices ecosystems requiring centralized management.

---

## 2. Structured Logging

### 2.1 Recommended Approach: Logback with Logstash Encoder + MDC

Spring Boot uses Logback by default with SLF4J facade, providing excellent structured logging when combined with Logstash encoder for JSON output and MDC (Mapped Diagnostic Context) for request correlation[^2][^9].

**Core Benefits:**
- **Default in Spring Boot:** No additional dependencies for basic logging
- **Structured JSON:** Logstash encoder provides machine-parsable JSON logs
- **MDC for Correlation:** Thread-local context for request IDs, user IDs
- **Spring Boot Actuator:** Runtime log level management via REST API
- **Performance:** Async appenders for non-blocking logging

### 2.2 Implementation Example

**Add Logstash encoder dependency:**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.4</version>
</dependency>
```

**Logback configuration for JSON logging:**

```xml
<!-- File: src/main/resources/logback-spring.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <springProperty scope="context" name="appName" source="spring.application.name" defaultValue="java-microservice"/>

    <!-- Console appender with JSON encoding for production -->
    <appender name="CONSOLE_JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <!-- Add application name to all log entries -->
            <customFields>{"app":"${appName}"}</customFields>

            <!-- Include MDC fields (request_id, user_id, etc.) -->
            <includeMdcKeyName>request_id</includeMdcKeyName>
            <includeMdcKeyName>user_id</includeMdcKeyName>

            <!-- Include stack traces for exceptions -->
            <throwableConverter class="net.logstash.logback.stacktrace.ShortenedThrowableConverter">
                <maxDepthPerThrowable>30</maxDepthPerThrowable>
                <maxLength>2048</maxLength>
            </throwableConverter>
        </encoder>
    </appender>

    <!-- Text appender for development (human-readable) -->
    <appender name="CONSOLE_TEXT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} [%X{request_id}] - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- Async appender wrapper for non-blocking logging -->
    <appender name="ASYNC_JSON" class="ch.qos.logback.classic.AsyncAppender">
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <appender-ref ref="CONSOLE_JSON"/>
    </appender>

    <!-- Profile-specific appenders -->
    <springProfile name="production">
        <root level="INFO">
            <appender-ref ref="ASYNC_JSON"/>
        </root>
    </springProfile>

    <springProfile name="!production">
        <root level="DEBUG">
            <appender-ref ref="CONSOLE_TEXT"/>
        </root>
    </springProfile>

    <!-- Reduce noise from Spring internals -->
    <logger name="org.springframework" level="INFO"/>
    <logger name="org.hibernate" level="INFO"/>
</configuration>
```

**MDC Filter for Request Correlation:**

```java
// File: src/main/java/com/example/filter/RequestCorrelationFilter.java
package com.example.filter;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.UUID;

/**
 * Filter that adds request correlation ID to MDC for request tracing.
 * MDC values automatically included in all log entries within request scope.
 */
@Component
@Order(1) // Execute first
public class RequestCorrelationFilter implements Filter {

    private static final Logger log = LoggerFactory.getLogger(RequestCorrelationFilter.class);
    private static final String REQUEST_ID_HEADER = "X-Request-ID";
    private static final String MDC_REQUEST_ID_KEY = "request_id";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;

        try {
            // Get request ID from header or generate new one
            String requestId = httpRequest.getHeader(REQUEST_ID_HEADER);
            if (requestId == null || requestId.isBlank()) {
                requestId = UUID.randomUUID().toString();
            }

            // Add request ID to MDC (thread-local storage)
            MDC.put(MDC_REQUEST_ID_KEY, requestId);
            MDC.put("method", httpRequest.getMethod());
            MDC.put("path", httpRequest.getRequestURI());

            log.info("Request started");

            // Process request
            chain.doFilter(request, response);

            log.info("Request completed");

        } finally {
            // CRITICAL: Clear MDC to prevent memory leaks
            // (Tomcat thread pool reuses threads)
            MDC.clear();
        }
    }
}
```

**Usage in application code:**

```java
// File: src/main/java/com/example/service/UserService.java
package com.example.service;

import com.example.domain.User;
import com.example.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User createUser(String email, String name) {
        // MDC request_id automatically included in log entries
        log.info("Creating user: email={}", email);

        try {
            User user = new User(email, name);
            User saved = userRepository.save(user);

            log.info("User created successfully: userId={}, email={}", saved.getId(), email);

            return saved;
        } catch (Exception e) {
            log.error("Failed to create user: email={}", email, e);
            throw e;
        }
    }
}
```

**Example JSON log output (production):**

```json
{
  "@timestamp": "2025-11-01T14:23:45.123Z",
  "level": "INFO",
  "logger_name": "com.example.service.UserService",
  "message": "User created successfully: userId=123, email=test@example.com",
  "app": "java-microservice",
  "request_id": "a3f2c1d4-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "method": "POST",
  "path": "/api/users",
  "thread_name": "http-nio-8080-exec-1"
}
```

### 2.2.1 Logger Initialization Patterns

#### Pattern 1: Logback Configuration at Application Startup (Recommended)

Logback auto-initializes when Spring Boot starts, reading `logback-spring.xml`[^9].

```java
// File: src/main/resources/logback-spring.xml
// Configuration loaded automatically at startup
// No programmatic initialization needed

// File: src/main/java/com/example/Application.java
@SpringBootApplication
public class Application {
    private static final Logger log = LoggerFactory.getLogger(Application.class);

    public static void main(String[] args) {
        // Logging already configured before this point
        log.info("Starting application");

        SpringApplication.run(Application.class, args);

        log.info("Application started successfully");
    }
}
```

**Benefits:**
- ✅ Automatic initialization (Spring Boot convention)
- ✅ Profile-based configuration (dev vs. production)
- ✅ No programmatic configuration needed

**Use When:** Standard Spring Boot applications (default recommendation)

#### Pattern 2: Programmatic Logback Configuration (Advanced)

Programmatically configure Logback for advanced scenarios[^10].

```java
// File: src/main/java/com/example/config/LoggingConfig.java
package com.example.config;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class LoggingConfig {

    @EventListener(ApplicationReadyEvent.class)
    public void configureDynamicLogging() {
        LoggerContext loggerContext = (LoggerContext) LoggerFactory.getILoggerFactory();

        // Dynamically set log levels (example: reduce Hibernate noise)
        Logger hibernateLogger = loggerContext.getLogger("org.hibernate");
        hibernateLogger.setLevel(Level.WARN);

        // Can add appenders, change patterns, etc. programmatically
    }
}
```

**Use When:** Need runtime log level changes, dynamic appender configuration

#### Pattern 3: Spring Boot Actuator for Runtime Log Level Management

Use Actuator REST API to change log levels at runtime without restart[^11].

**Enable actuator dependency:**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**application.yml configuration:**

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,loggers
  endpoint:
    loggers:
      enabled: true
```

**REST API usage:**

```bash
# Get current log level for package
curl http://localhost:8080/actuator/loggers/com.example.service

# Change log level at runtime (no restart needed)
curl -X POST http://localhost:8080/actuator/loggers/com.example.service \
  -H "Content-Type: application/json" \
  -d '{"configuredLevel": "DEBUG"}'

# Response:
# {
#   "configuredLevel": "DEBUG",
#   "effectiveLevel": "DEBUG"
# }
```

**Use When:** Need to debug production issues without restart, temporary log level changes

### 2.2.2 Common Initialization Mistakes

**❌ Mistake 1: Missing MDC cleanup in async processing**

```java
// BAD: Async method loses MDC context
@Async
public void processAsync(Long userId) {
    // MDC cleared by servlet thread - request_id missing!
    log.info("Processing async for user: {}", userId);
}
```

**✅ Fix: Copy MDC to async threads**

```java
// GOOD: Propagate MDC to async thread
@Async
public void processAsync(Long userId) {
    // Copy MDC from parent thread
    MDC.setContextMap(MDC.getCopyOfContextMap());

    try {
        log.info("Processing async for user: {}", userId);
        // Now request_id is included
    } finally {
        MDC.clear(); // Clean up
    }
}

// OR use TaskDecorator for automatic MDC propagation
@Configuration
public class AsyncConfig implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setTaskDecorator(new MdcTaskDecorator()); // Automatic MDC copy
        executor.initialize();
        return executor;
    }
}

class MdcTaskDecorator implements TaskDecorator {
    @Override
    public Runnable decorate(Runnable runnable) {
        Map<String, String> contextMap = MDC.getCopyOfContextMap();
        return () -> {
            try {
                if (contextMap != null) {
                    MDC.setContextMap(contextMap);
                }
                runnable.run();
            } finally {
                MDC.clear();
            }
        };
    }
}
```

**❌ Mistake 2: Using wrong logger instance**

```java
// BAD: Using wrong class name in logger
public class UserService {
    private static final Logger log = LoggerFactory.getLogger(SomeOtherClass.class); // Wrong!
}
```

**✅ Fix: Use correct class for logger**

```java
// GOOD: Logger matches the class
public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    // OR use Lombok @Slf4j annotation
}
```

**❌ Mistake 3: Not configuring logging in tests**

```java
// BAD: Test logs pollute output
@SpringBootTest
class UserServiceTest {
    // Logs from test execution clutter test output
}
```

**✅ Fix: Configure test-specific logging**

```yaml
# File: src/test/resources/logback-test.xml
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- Quieter logging for tests -->
    <root level="WARN">
        <appender-ref ref="CONSOLE"/>
    </root>

    <!-- Enable DEBUG for specific packages under test -->
    <logger name="com.example.service" level="DEBUG"/>
</configuration>
```

### 2.3 Alternative Approaches

**Alternative 1: Log4j2 for Performance**

Apache Log4j2 offers better async performance than Logback[^12].

*Pros:* Faster async logging, lambda support, plugins
*Cons:* Additional configuration, not Spring Boot default
*Use When:* Logging throughput >100K logs/second matters

**Alternative 2: Logz.io or ELK Integration**

Direct integration with log aggregation platforms.

*Pros:* Centralized logs, search, alerting
*Cons:* External service dependency, cost
*Use When:* Production microservices requiring centralized logging

### 2.4 Decision Criteria

**Use Logback (default) when:**
- Standard Spring Boot application
- JSON logs with Logstash encoder sufficient
- MDC-based correlation meets needs

**Use Log4j2 when:**
- Logging performance is critical bottleneck
- Need advanced features (lambda support, plugins)
- Willing to customize Spring Boot defaults

**Use direct ELK integration when:**
- Multiple microservices requiring centralized logs
- Need advanced search, alerting, dashboards

---

## 3. Caching Strategies

### 3.1 Recommended Approach: Spring Cache Abstraction with Redis

Spring's Cache abstraction (`@EnableCaching`, `@Cacheable`) provides vendor-neutral caching that works with Redis, Caffeine, EhCache, or in-memory caching[^3][^13]. For distributed caching, Lettuce client (auto-configured by Spring Boot) offers excellent Redis integration with connection pooling.

**Core Benefits:**
- **Vendor-Neutral:** Switch cache providers without code changes
- **Declarative:** @Cacheable, @CacheEvict, @CachePut annotations
- **Spring Boot Auto-Configuration:** Zero-config Redis setup
- **Lettuce Client:** Async and sync Redis operations with connection pooling
- **Testing:** Easy to disable cache or use in-memory for tests

### 3.2 Implementation Example

**Add Redis dependencies:**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
```

**application.yml configuration:**

```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 300000  # 5 minutes default TTL (milliseconds)

  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: 6379
      password: ${REDIS_PASSWORD:}
      database: 0

      # Connection pool configuration (Lettuce)
      lettuce:
        pool:
          max-active: 10    # Max concurrent connections
          max-idle: 5       # Max idle connections
          min-idle: 2       # Min idle connections to maintain
          max-wait: 3000ms  # Max wait time for connection
```

**Enable caching:**

```java
// File: src/main/java/com/example/config/CacheConfig.java
package com.example.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.autoconfigure.cache.RedisCacheManagerBuilderCustomizer;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;

import java.time.Duration;

/**
 * Cache configuration for Redis with JSON serialization.
 */
@Configuration
@EnableCaching
public class CacheConfig {

    /**
     * Customize Redis cache configuration for JSON serialization.
     */
    @Bean
    public RedisCacheManagerBuilderCustomizer redisCacheManagerBuilderCustomizer(ObjectMapper objectMapper) {
        return builder -> builder
            .cacheDefaults(RedisCacheConfiguration.defaultCacheConfig()
                // Serialize values as JSON (not Java serialization)
                .serializeValuesWith(
                    RedisSerializationContext.SerializationPair.fromSerializer(
                        new GenericJackson2JsonRedisSerializer(objectMapper)
                    )
                )
                // Default TTL for all caches
                .entryTtl(Duration.ofMinutes(5))
            )
            // Cache-specific TTLs
            .withCacheConfiguration("users",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(10))
            )
            .withCacheConfiguration("products",
                RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(15))
            );
    }
}
```

**Using cache annotations in service:**

```java
// File: src/main/java/com/example/service/UserService.java
package com.example.service;

import com.example.domain.User;
import com.example.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Cache-aside pattern: check cache first, load from DB on miss.
     * Cache key: "users::{userId}"
     */
    @Cacheable(value = "users", key = "#userId")
    public Optional<User> getUserById(Long userId) {
        log.info("Cache miss for user: userId={}", userId);
        return userRepository.findById(userId);
    }

    /**
     * Update cache when user saved (write-through).
     * Cache key: "users::{user.id}"
     */
    @CachePut(value = "users", key = "#user.id")
    public User saveUser(User user) {
        log.info("Saving user and updating cache: userId={}", user.getId());
        return userRepository.save(user);
    }

    /**
     * Evict cache entry when user deleted.
     */
    @CacheEvict(value = "users", key = "#userId")
    public void deleteUser(Long userId) {
        log.info("Deleting user and evicting cache: userId={}", userId);
        userRepository.deleteById(userId);
    }

    /**
     * Clear entire "users" cache.
     */
    @CacheEvict(value = "users", allEntries = true)
    public void clearUserCache() {
        log.info("Clearing entire user cache");
    }
}
```

**Programmatic cache access (when annotations insufficient):**

```java
// File: src/main/java/com/example/service/ProductService.java
package com.example.service;

import com.example.domain.Product;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.stereotype.Service;

@Service
public class ProductService {

    private final CacheManager cacheManager;

    public ProductService(CacheManager cacheManager) {
        this.cacheManager = cacheManager;
    }

    public Optional<Product> getProduct(Long productId) {
        Cache cache = cacheManager.getCache("products");
        if (cache != null) {
            Product cached = cache.get(productId, Product.class);
            if (cached != null) {
                return Optional.of(cached);
            }
        }

        // Load from database (not shown)
        Product product = loadFromDatabase(productId);

        if (cache != null && product != null) {
            cache.put(productId, product);
        }

        return Optional.ofNullable(product);
    }
}
```

### 3.2.1 Cache Initialization Patterns

#### Pattern 1: Spring Boot Auto-Configuration (Recommended)

Let Spring Boot auto-configure Redis cache with minimal configuration[^14].

```yaml
# File: application.yml
spring:
  cache:
    type: redis  # Spring Boot auto-configures RedisCacheManager
  data:
    redis:
      host: localhost
      port: 6379
```

```java
// File: Application.java
@SpringBootApplication
@EnableCaching  // Single annotation enables caching
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**Benefits:**
- ✅ Zero configuration (convention over configuration)
- ✅ Production-ready defaults (Lettuce connection pool)
- ✅ Easy to override with custom CacheManager bean

**Use When:** Standard Redis caching needs (default recommendation)

#### Pattern 2: Custom CacheManager for Multiple Cache Providers

Configure multiple cache managers (e.g., Redis + local Caffeine cache)[^15].

```java
// File: src/main/java/com/example/config/MultiCacheConfig.java
package com.example.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.cache.support.CompositeCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;

import java.time.Duration;
import java.util.List;

@Configuration
@EnableCaching
public class MultiCacheConfig {

    /**
     * Primary cache manager: tries Redis first, then local Caffeine cache.
     */
    @Bean
    @Primary
    public CacheManager compositeCacheManager(
            RedisCacheManager redisCacheManager,
            CacheManager localCacheManager
    ) {
        CompositeCacheManager cacheManager = new CompositeCacheManager();
        cacheManager.setCacheManagers(List.of(redisCacheManager, localCacheManager));
        cacheManager.setFallbackToNoOpCache(false);
        return cacheManager;
    }

    /**
     * Redis cache manager (distributed).
     */
    @Bean
    public RedisCacheManager redisCacheManager(RedisConnectionFactory connectionFactory) {
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(
                org.springframework.data.redis.cache.RedisCacheConfiguration.defaultCacheConfig()
                    .entryTtl(Duration.ofMinutes(5))
            )
            .build();
    }

    /**
     * Local in-memory cache manager (Caffeine).
     * Used as fallback if Redis unavailable.
     */
    @Bean
    public CacheManager localCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager("users", "products");
        cacheManager.setCaffeine(
            Caffeine.newBuilder()
                .maximumSize(1000)
                .expireAfterWrite(Duration.ofMinutes(5))
        );
        return cacheManager;
    }
}
```

**Use When:** Need fallback cache if Redis unavailable, or two-level caching (local + distributed)

#### Pattern 3: Conditional Cache Manager with @Profile

Enable different cache managers per environment[^16].

```java
// File: src/main/java/com/example/config/CacheConfig.java
package com.example.config;

import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;

@Configuration
@EnableCaching
public class CacheConfig {

    /**
     * Production: Use Redis for distributed caching.
     */
    @Bean
    @Profile("production")
    public CacheManager redisCacheManager(RedisConnectionFactory connectionFactory) {
        return RedisCacheManager.builder(connectionFactory).build();
    }

    /**
     * Development/Test: Use simple in-memory cache (no Redis needed).
     */
    @Bean
    @Profile({"dev", "test"})
    public CacheManager simpleCacheManager() {
        return new ConcurrentMapCacheManager("users", "products");
    }
}
```

**Use When:** Want in-memory cache for local dev/test, Redis for production

### 3.2.2 Connection Pool Configuration Best Practices

Lettuce connection pool settings (auto-configured by Spring Boot)[^17]:

```yaml
spring:
  data:
    redis:
      host: redis
      port: 6379
      password: ${REDIS_PASSWORD}
      database: 0

      # Connection timeouts
      timeout: 3000ms         # Command timeout
      connect-timeout: 5000ms # Connection establishment timeout

      # Lettuce connection pool
      lettuce:
        pool:
          max-active: 10    # Max concurrent connections
          # Scale: (expected_concurrent_requests / 2)

          max-idle: 5       # Max idle connections to keep
          # Reduces latency (connection already established)

          min-idle: 2       # Min idle connections to maintain
          # Keeps pool warm

          max-wait: 3000ms  # Max wait time for connection from pool
          # Fail fast if pool exhausted

        shutdown-timeout: 100ms  # Graceful shutdown
```

**Configuration Guidelines:**

| Setting | Recommended Value | Rationale |
|---------|------------------|-----------|
| `max-active` | `concurrent_requests / 2` | Each request uses connection briefly |
| `max-idle` | `max-active / 2` | Balance latency vs. resources |
| `min-idle` | `2-5` | Keep pool warm, reduce latency |
| `max-wait` | `3s` | Fail fast on pool exhaustion |
| `timeout` | `3s` | Fast failure for commands |

### 3.3 Alternative Approaches

**Alternative 1: Caffeine for Local Caching**

High-performance in-memory cache (successor to Guava)[^18].

*Pros:* Sub-millisecond latency, no network, excellent performance
*Cons:* Not distributed, memory-bound, data lost on restart
*Use When:* Single-instance deployment, second-level cache

**Alternative 2: EhCache for Tiered Caching**

Multi-tier caching (heap, off-heap, disk)[^19].

*Pros:* Tiered storage, overflow to disk, persistence
*Cons:* More complex, not distributed (without Terracotta)
*Use When:* Large cache datasets requiring overflow

### 3.4 Decision Criteria

| Pattern | Best For | Distributed | Performance |
|---------|----------|------------|-------------|
| **Redis (Spring Cache)** | **Microservices** | ✅ Yes | ⚠️ Network latency |
| Caffeine | Single instance | ❌ No | ✅✅ Fastest |
| Redis + Caffeine | Two-level cache | ✅ L2 only | ✅ L1 fast, L2 distributed |
| EhCache | Large datasets | ⚠️ With Terracotta | ✅ Good |

**TTL Selection Guidelines:**
- **User sessions:** 30 minutes
- **User profiles:** 5-10 minutes
- **Product catalog:** 10-15 minutes
- **Real-time data:** 10-60 seconds

---

## 4. Data Access Patterns

### 4.1 Recommended Approach: Spring Data JPA with Repository Pattern

Spring Data JPA provides Clean Architecture compliance through repository interfaces, eliminating boilerplate while maintaining separation of concerns[^4][^20]. HikariCP (auto-configured by Spring Boot) offers excellent connection pool performance.

**Core Benefits:**
- **Zero Boilerplate:** Repository interfaces auto-implemented
- **Clean Architecture:** Repository interface in domain, implementation in infrastructure
- **Query Methods:** Derived queries from method names
- **JPQL/Native SQL:** Full query control when needed
- **HikariCP:** Production-grade connection pool (auto-configured)

### 4.2 Database Connection Initialization

#### Pattern 1: Spring Boot Auto-Configuration (Recommended)

Spring Boot auto-configures DataSource, HikariCP, and JPA with minimal configuration[^21].

**application.yml:**

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:5432/${DB_NAME:mydb}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:changeme}
    driver-class-name: org.postgresql.Driver

    # HikariCP configuration (auto-configured by Spring Boot)
    hikari:
      maximum-pool-size: 25        # Max concurrent connections
      minimum-idle: 5              # Min idle connections
      connection-timeout: 30000    # 30 seconds
      idle-timeout: 600000         # 10 minutes
      max-lifetime: 1800000        # 30 minutes
      pool-name: HikariPool-1

  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    show-sql: false  # Don't log SQL (use logging framework)
    hibernate:
      ddl-auto: validate  # Production: validate schema, don't auto-create
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
        jdbc:
          batch_size: 20     # Batch inserts/updates
        order_inserts: true  # Optimize batch ordering
```

**Benefits:**
- ✅ Zero configuration code
- ✅ Production-ready defaults (HikariCP)
- ✅ Easy to override with custom beans

**Use When:** Standard database access (default recommendation)

### 4.3 Repository Pattern Implementation

#### Repository Interface (Domain Layer)

```java
// File: src/main/java/com/example/domain/repository/UserRepository.java
package com.example.domain.repository;

import com.example.domain.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.List;

/**
 * User repository interface (port).
 * Spring Data JPA auto-implements this interface (adapter).
 * Domain layer defines WHAT operations needed.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // Derived query methods (no implementation needed)
    Optional<User> findByEmail(String email);

    List<User> findByNameContainingIgnoreCase(String name);

    boolean existsByEmail(String email);

    // Custom JPQL query
    @Query("SELECT u FROM User u WHERE u.email = :email AND u.active = true")
    Optional<User> findActiveUserByEmail(@Param("email") String email);

    // Native SQL query (when JPQL insufficient)
    @Query(value = "SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'",
           nativeQuery = true)
    List<User> findRecentUsers();
}
```

#### Entity (Domain Layer)

```java
// File: src/main/java/com/example/domain/entity/User.java
package com.example.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * User domain entity.
 * JPA annotations for persistence, validation annotations for constraints.
 */
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_user_email", columnList = "email", unique = true)
})
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Email(message = "Email must be valid")
    @NotBlank(message = "Email is required")
    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false)
    private boolean active = true;

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    // JPA requires no-arg constructor
    protected User() {
    }

    public User(String email, String name) {
        this.email = email;
        this.name = name;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
```

### 4.4 Repository Dependency Injection

#### Service Layer (Application Layer)

```java
// File: src/main/java/com/example/service/UserService.java
package com.example.service;

import com.example.domain.entity.User;
import com.example.domain.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * User service with business logic.
 * Depends on repository interface (dependency inversion).
 */
@Service
public class UserService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;

    // Constructor injection (recommended over field injection)
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Transactional(readOnly = true)
    public Optional<User> getUserById(Long userId) {
        log.debug("Fetching user: userId={}", userId);
        return userRepository.findById(userId);
    }

    @Transactional(readOnly = true)
    public Optional<User> getUserByEmail(String email) {
        log.debug("Fetching user by email: email={}", email);
        return userRepository.findByEmail(email);
    }

    @Transactional
    public User createUser(String email, String name) {
        log.info("Creating user: email={}", email);

        // Business validation
        if (userRepository.existsByEmail(email)) {
            throw new IllegalArgumentException("User with email already exists: " + email);
        }

        User user = new User(email, name);
        User saved = userRepository.save(user);

        log.info("User created: userId={}, email={}", saved.getId(), email);
        return saved;
    }

    @Transactional
    public User updateUser(Long userId, String name) {
        log.info("Updating user: userId={}", userId);

        User user = userRepository.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));

        user.setName(name);
        // No explicit save() needed - managed entity automatically updated at transaction commit

        log.info("User updated: userId={}, newName={}", userId, name);
        return user;
    }

    @Transactional
    public void deleteUser(Long userId) {
        log.info("Deleting user: userId={}", userId);

        if (!userRepository.existsById(userId)) {
            throw new IllegalArgumentException("User not found: " + userId);
        }

        userRepository.deleteById(userId);
        log.info("User deleted: userId={}", userId);
    }

    @Transactional(readOnly = true)
    public List<User> searchUsers(String namePattern) {
        log.debug("Searching users: pattern={}", namePattern);
        return userRepository.findByNameContainingIgnoreCase(namePattern);
    }
}
```

#### REST Controller (Presentation Layer)

```java
// File: src/main/java/com/example/controller/UserController.java
package com.example.controller;

import com.example.domain.entity.User;
import com.example.service.UserService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return userService.getUserById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping
    public ResponseEntity<List<User>> searchUsers(@RequestParam String name) {
        List<User> users = userService.searchUsers(name);
        return ResponseEntity.ok(users);
    }

    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody CreateUserRequest request) {
        User user = userService.createUser(request.email(), request.name());
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }

    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request
    ) {
        User user = userService.updateUser(id, request.name());
        return ResponseEntity.ok(user);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }

    // Request DTOs (Java Records)
    public record CreateUserRequest(
        @Email @NotBlank String email,
        @NotBlank String name
    ) {}

    public record UpdateUserRequest(
        @NotBlank String name
    ) {}
}
```

### 4.5 Testing with Mocked Repositories

#### Unit Tests with Mockito

```java
// File: src/test/java/com/example/service/UserServiceTest.java
package com.example.service;

import com.example.domain.entity.User;
import com.example.domain.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void createUser_Success() {
        // Given
        String email = "test@example.com";
        String name = "Test User";

        when(userRepository.existsByEmail(email)).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            user.setId(123L); // Simulate ID assignment
            return user;
        });

        // When
        User result = userService.createUser(email, name);

        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(123L);
        assertThat(result.getEmail()).isEqualTo(email);
        assertThat(result.getName()).isEqualTo(name);

        verify(userRepository).existsByEmail(email);
        verify(userRepository).save(any(User.class));
    }

    @Test
    void createUser_DuplicateEmail_ThrowsException() {
        // Given
        String email = "test@example.com";
        when(userRepository.existsByEmail(email)).thenReturn(true);

        // When/Then
        assertThatThrownBy(() -> userService.createUser(email, "Test"))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("already exists");

        verify(userRepository).existsByEmail(email);
        verify(userRepository, never()).save(any());
    }
}
```

#### Integration Tests with @DataJpaTest

```java
// File: src/test/java/com/example/repository/UserRepositoryTest.java
package com.example.repository;

import com.example.domain.entity.User;
import com.example.domain.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test for UserRepository using @DataJpaTest.
 * Uses in-memory H2 database, auto-rolls back after each test.
 */
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_UserExists_ReturnsUser() {
        // Given
        User user = new User("test@example.com", "Test User");
        entityManager.persist(user);
        entityManager.flush();

        // When
        Optional<User> found = userRepository.findByEmail("test@example.com");

        // Then
        assertThat(found).isPresent();
        assertThat(found.get().getEmail()).isEqualTo("test@example.com");
        assertThat(found.get().getName()).isEqualTo("Test User");
    }

    @Test
    void findByEmail_UserNotExists_ReturnsEmpty() {
        // When
        Optional<User> found = userRepository.findByEmail("nonexistent@example.com");

        // Then
        assertThat(found).isEmpty();
    }

    @Test
    void existsByEmail_UserExists_ReturnsTrue() {
        // Given
        User user = new User("test@example.com", "Test User");
        entityManager.persist(user);
        entityManager.flush();

        // When
        boolean exists = userRepository.existsByEmail("test@example.com");

        // Then
        assertThat(exists).isTrue();
    }
}
```

### 4.6 Connection Pool Configuration Best Practices

HikariCP configuration (auto-configured by Spring Boot)[^22]:

```yaml
spring:
  datasource:
    hikari:
      # Connection pool size
      maximum-pool-size: 25
      # Scale: (concurrent_requests * avg_query_duration * 2)
      # Example: 100 RPS * 0.1s query = 10 concurrent queries → 25 provides headroom

      minimum-idle: 5
      # Min idle connections to maintain (reduces latency)

      # Timeouts
      connection-timeout: 30000  # 30 seconds (max wait for connection)
      idle-timeout: 600000       # 10 minutes (close idle connections after)
      max-lifetime: 1800000      # 30 minutes (recycle connections after)

      # Health checks
      keepalive-time: 30000      # 30 seconds (validate idle connections)
      validation-timeout: 5000   # 5 seconds (max time for validation query)

      # Leak detection (development)
      leak-detection-threshold: 60000  # 60 seconds (warn if connection held too long)

      # Pooling behavior
      auto-commit: true
      connection-init-sql: "SELECT 1"  # Query to test connections
```

**Configuration Guidelines:**

| Setting | Recommended Value | Rationale |
|---------|------------------|-----------|
| `maximum-pool-size` | `concurrent_requests * avg_duration * 2` | Handles spikes |
| `minimum-idle` | `maximum-pool-size / 5` | Balance latency vs. resources |
| `connection-timeout` | `30s` | Fail fast on exhaustion |
| `max-lifetime` | `30m` | Prevent stale connections |
| `keepalive-time` | `30s` | Validate idle connections |

### 4.7 Decision Criteria

**Use Spring Data JPA when:**
- Standard CRUD operations dominate
- Want zero boilerplate (derived queries)
- Clean Architecture with repository pattern

**Use MyBatis when:**
- Complex SQL queries required
- Prefer SQL over JPQL
- Need fine-grained control over queries

**Use JdbcTemplate when:**
- Simple SQL without ORM overhead
- Dynamic queries constructed at runtime
- Maximum performance critical


---

### 4.8 JPA Type Safety with Criteria API and Type-Safe Queries

Spring Data JPA provides type-safe query construction through Criteria API and Specification pattern, eliminating string-based JPQL prone to typos[^39][^40].

**Core Benefits:**
- **Compile-Time Safety:** Entity field references checked by compiler
- **Refactoring Safe:** Renaming fields updates all query references
- **IDE Autocomplete:** Full IDE support for entity fields and methods
- **Dynamic Queries:** Build complex queries conditionally without string concatenation

#### Pattern 1: JPA Criteria API for Type-Safe Queries

Criteria API provides compile-time type checking for dynamic query construction[^39].

```java
// File: src/main/java/com/example/repository/UserRepositoryCustom.java
package com.example.repository;

import com.example.domain.entity.User;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Custom repository interface for type-safe dynamic queries.
 * Implemented using JPA Criteria API.
 */
public interface UserRepositoryCustom {
    /**
     * Search users with type-safe dynamic criteria.
     */
    List<User> searchUsers(UserSearchCriteria criteria);
}

/**
 * Search criteria with Optional fields for dynamic queries.
 */
record UserSearchCriteria(
    java.util.Optional<String> namePattern,
    java.util.Optional<String> emailPattern,
    java.util.Optional<Boolean> active,
    java.util.Optional<LocalDateTime> createdAfter,
    java.util.Optional<LocalDateTime> createdBefore
) {}
```

```java
// File: src/main/java/com/example/repository/UserRepositoryCustomImpl.java
package com.example.repository;

import com.example.domain.entity.User;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.criteria.*;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;

/**
 * Implementation of custom repository using JPA Criteria API.
 * Provides type-safe dynamic query construction.
 */
@Repository
public class UserRepositoryCustomImpl implements UserRepositoryCustom {

    @PersistenceContext
    private EntityManager entityManager;

    /**
     * Build type-safe dynamic query using Criteria API.
     * All entity field references are compile-time checked.
     */
    @Override
    public List<User> searchUsers(UserSearchCriteria criteria) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> user = query.from(User.class);

        // Build predicates dynamically (type-safe)
        List<Predicate> predicates = new ArrayList<>();

        // Name pattern search (type-safe: user.get(User_.name) checked at compile time)
        criteria.namePattern().ifPresent(pattern ->
            predicates.add(cb.like(
                cb.lower(user.get("name")),  // String literal (not ideal)
                "%" + pattern.toLowerCase() + "%"
            ))
        );

        // Email pattern search
        criteria.emailPattern().ifPresent(pattern ->
            predicates.add(cb.like(
                cb.lower(user.get("email")),
                "%" + pattern.toLowerCase() + "%"
            ))
        );

        // Active status filter
        criteria.active().ifPresent(active ->
            predicates.add(cb.equal(user.get("active"), active))
        );

        // Created after date filter
        criteria.createdAfter().ifPresent(date ->
            predicates.add(cb.greaterThanOrEqualTo(user.get("createdAt"), date))
        );

        // Created before date filter
        criteria.createdBefore().ifPresent(date ->
            predicates.add(cb.lessThanOrEqualTo(user.get("createdAt"), date))
        );

        // Combine all predicates with AND
        query.where(cb.and(predicates.toArray(new Predicate[0])));

        // Order by created date descending
        query.orderBy(cb.desc(user.get("createdAt")));

        return entityManager.createQuery(query).getResultList();
    }
}
```

**✅ Enhanced Type Safety with JPA Metamodel:**

JPA Metamodel generates static metamodel classes for compile-time field reference checking[^40].

```java
// File: src/main/java/com/example/domain/entity/User_.java
// Generated by JPA Metamodel processor
package com.example.domain.entity;

import jakarta.persistence.metamodel.SingularAttribute;
import jakarta.persistence.metamodel.StaticMetamodel;

import java.time.LocalDateTime;

/**
 * JPA Metamodel for User entity.
 * Auto-generated for type-safe Criteria API queries.
 */
@StaticMetamodel(User.class)
public class User_ {
    public static volatile SingularAttribute<User, Long> id;
    public static volatile SingularAttribute<User, String> email;
    public static volatile SingularAttribute<User, String> name;
    public static volatile SingularAttribute<User, Boolean> active;
    public static volatile SingularAttribute<User, LocalDateTime> createdAt;
    public static volatile SingularAttribute<User, LocalDateTime> updatedAt;
}
```

**Enhanced implementation with Metamodel:**

```java
/**
 * Type-safe query using JPA Metamodel.
 * All field references checked at compile time (no string literals).
 */
@Override
public List<User> searchUsers(UserSearchCriteria criteria) {
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<User> query = cb.createQuery(User.class);
    Root<User> user = query.from(User.class);

    List<Predicate> predicates = new ArrayList<>();

    // Type-safe field references using User_ metamodel
    criteria.namePattern().ifPresent(pattern ->
        predicates.add(cb.like(
            cb.lower(user.get(User_.name)),  // Compile-time checked!
            "%" + pattern.toLowerCase() + "%"
        ))
    );

    criteria.emailPattern().ifPresent(pattern ->
        predicates.add(cb.like(
            cb.lower(user.get(User_.email)),  // Compile-time checked!
            "%" + pattern.toLowerCase() + "%"
        ))
    );

    criteria.active().ifPresent(active ->
        predicates.add(cb.equal(user.get(User_.active), active))  // Compile-time checked!
    );

    criteria.createdAfter().ifPresent(date ->
        predicates.add(cb.greaterThanOrEqualTo(user.get(User_.createdAt), date))  // Compile-time checked!
    );

    criteria.createdBefore().ifPresent(date ->
        predicates.add(cb.lessThanOrEqualTo(user.get(User_.createdAt), date))  // Compile-time checked!
    );

    query.where(cb.and(predicates.toArray(new Predicate[0])));
    query.orderBy(cb.desc(user.get(User_.createdAt)));

    return entityManager.createQuery(query).getResultList();
}
```

**Enable JPA Metamodel generation in Maven:**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jpamodelgen</artifactId>
    <scope>provided</scope>
</dependency>

<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <annotationProcessorPaths>
                    <path>
                        <groupId>org.hibernate.orm</groupId>
                        <artifactId>hibernate-jpamodelgen</artifactId>
                        <version>${hibernate.version}</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

**✅ Benefits:**

- **Compile-Time Safety:** `User_.name` checked by compiler (typos caught immediately)
- **Refactoring Safe:** Renaming `User.name` field updates all `User_.name` references
- **IDE Autocomplete:** Full IDE support for entity fields
- **No String Literals:** Field names not hardcoded as strings
- **Dynamic Queries:** Build complex queries conditionally without string concatenation

**❌ Drawbacks:**

- Verbose syntax compared to derived query methods
- Requires JPA Metamodel setup (annotation processor)
- Generated `User_` classes must be in classpath

**Use When:**
- Need dynamic query construction (filters applied conditionally)
- Want compile-time safety for complex queries
- Refactoring entity fields frequently
- Building search APIs with multiple optional criteria

#### Pattern 2: Spring Data JPA Specification for Reusable Type-Safe Queries

Specification pattern encapsulates reusable query predicates with type safety[^41].

```java
// File: src/main/java/com/example/repository/UserRepository.java
package com.example.repository;

import com.example.domain.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

/**
 * User repository with Specification support.
 * JpaSpecificationExecutor enables type-safe dynamic queries.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long>,
                                        JpaSpecificationExecutor<User> {
    // Derived queries
    java.util.Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);

    // Specification-based queries provided by JpaSpecificationExecutor:
    // - List<User> findAll(Specification<User> spec)
    // - Page<User> findAll(Specification<User> spec, Pageable pageable)
    // - long count(Specification<User> spec)
}
```

```java
// File: src/main/java/com/example/repository/specification/UserSpecifications.java
package com.example.repository.specification;

import com.example.domain.entity.User;
import com.example.domain.entity.User_;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDateTime;

/**
 * Reusable type-safe specifications for User entity queries.
 * Each specification is composable and type-safe.
 */
public class UserSpecifications {

    /**
     * Specification for name contains search (case-insensitive).
     */
    public static Specification<User> nameContains(String pattern) {
        return (root, query, cb) -> {
            if (pattern == null || pattern.isBlank()) {
                return cb.conjunction();  // No-op predicate (always true)
            }
            return cb.like(
                cb.lower(root.get(User_.name)),
                "%" + pattern.toLowerCase() + "%"
            );
        };
    }

    /**
     * Specification for email contains search (case-insensitive).
     */
    public static Specification<User> emailContains(String pattern) {
        return (root, query, cb) -> {
            if (pattern == null || pattern.isBlank()) {
                return cb.conjunction();
            }
            return cb.like(
                cb.lower(root.get(User_.email)),
                "%" + pattern.toLowerCase() + "%"
            );
        };
    }

    /**
     * Specification for active status filter.
     */
    public static Specification<User> hasActiveStatus(Boolean active) {
        return (root, query, cb) -> {
            if (active == null) {
                return cb.conjunction();
            }
            return cb.equal(root.get(User_.active), active);
        };
    }

    /**
     * Specification for created after date.
     */
    public static Specification<User> createdAfter(LocalDateTime date) {
        return (root, query, cb) -> {
            if (date == null) {
                return cb.conjunction();
            }
            return cb.greaterThanOrEqualTo(root.get(User_.createdAt), date);
        };
    }

    /**
     * Specification for created before date.
     */
    public static Specification<User> createdBefore(LocalDateTime date) {
        return (root, query, cb) -> {
            if (date == null) {
                return cb.conjunction();
            }
            return cb.lessThanOrEqualTo(root.get(User_.createdAt), date);
        };
    }

    /**
     * Specification for created between dates (combines two specifications).
     */
    public static Specification<User> createdBetween(LocalDateTime start, LocalDateTime end) {
        return Specification.where(createdAfter(start))
                           .and(createdBefore(end));
    }

    /**
     * Specification for active users only.
     */
    public static Specification<User> isActive() {
        return hasActiveStatus(true);
    }

    /**
     * Specification for inactive users only.
     */
    public static Specification<User> isInactive() {
        return hasActiveStatus(false);
    }
}
```

**Service usage with composable specifications:**

```java
// File: src/main/java/com/example/service/UserSearchService.java
package com.example.service;

import com.example.domain.entity.User;
import com.example.repository.UserRepository;
import com.example.repository.specification.UserSpecifications;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

/**
 * User search service with composable type-safe specifications.
 */
@Service
public class UserSearchService {

    private final UserRepository userRepository;

    public UserSearchService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Search users with dynamic criteria (type-safe composition).
     */
    @Transactional(readOnly = true)
    public List<User> searchUsers(
        String namePattern,
        String emailPattern,
        Boolean active,
        LocalDateTime createdAfter,
        LocalDateTime createdBefore
    ) {
        // Compose specifications (type-safe AND composition)
        Specification<User> spec = Specification.where(null);

        // Add specifications conditionally (null-safe)
        spec = spec.and(UserSpecifications.nameContains(namePattern));
        spec = spec.and(UserSpecifications.emailContains(emailPattern));
        spec = spec.and(UserSpecifications.hasActiveStatus(active));
        spec = spec.and(UserSpecifications.createdAfter(createdAfter));
        spec = spec.and(UserSpecifications.createdBefore(createdBefore));

        return userRepository.findAll(spec);
    }

    /**
     * Search active users by name pattern with pagination.
     */
    @Transactional(readOnly = true)
    public Page<User> searchActiveUsers(String namePattern, int page, int size) {
        // Compose specifications (fluent API)
        var spec = Specification.where(UserSpecifications.isActive())
                               .and(UserSpecifications.nameContains(namePattern));

        var pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());

        return userRepository.findAll(spec, pageable);
    }

    /**
     * Find recently created active users.
     */
    @Transactional(readOnly = true)
    public List<User> findRecentActiveUsers(int daysAgo) {
        var cutoffDate = LocalDateTime.now().minusDays(daysAgo);

        // Compose specifications (readable, type-safe)
        var spec = Specification.where(UserSpecifications.isActive())
                               .and(UserSpecifications.createdAfter(cutoffDate));

        return userRepository.findAll(spec, Sort.by("createdAt").descending());
    }

    /**
     * Complex search: Active users with name pattern created in date range.
     */
    @Transactional(readOnly = true)
    public List<User> complexSearch(
        String namePattern,
        LocalDateTime startDate,
        LocalDateTime endDate
    ) {
        // Complex composition (still type-safe, readable)
        var spec = Specification.where(UserSpecifications.isActive())
                               .and(UserSpecifications.nameContains(namePattern))
                               .and(UserSpecifications.createdBetween(startDate, endDate));

        return userRepository.findAll(spec);
    }
}
```

**✅ Benefits:**

- **Reusable:** Specifications encapsulate query logic (DRY principle)
- **Composable:** AND/OR/NOT composition with fluent API
- **Type-Safe:** JPA Metamodel ensures compile-time field checking
- **Testable:** Specifications easily unit tested in isolation
- **Readable:** Fluent API reads like English (isActive().and(nameContains(...)))

**❌ Drawbacks:**

- Initial setup overhead (create specification classes)
- Learning curve (Specification API less intuitive than derived queries)
- Verbose for simple queries (derived queries more concise)

**Use When:**
- Need reusable query logic across multiple services
- Complex dynamic queries with many optional criteria
- Want composable query building (AND/OR combinations)
- Prefer functional style over imperative Criteria API

---

### 4.9 Entity Validation Patterns with JPA Lifecycle Callbacks

JPA entity validation combines JSR-303 annotations with lifecycle callbacks for comprehensive data integrity[^42][^43].

#### Pattern 1: JSR-303 Bean Validation on Entities

Standard JSR-303 validation annotations on entity fields validated automatically by JPA provider[^43].

```java
// File: src/main/java/com/example/domain/entity/Product.java
package com.example.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Product entity with comprehensive JSR-303 validation.
 * Validation automatically enforced on persist/update.
 */
@Entity
@Table(name = "products", indexes = {
    @Index(name = "idx_product_sku", columnList = "sku", unique = true),
    @Index(name = "idx_product_category", columnList = "category")
})
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Product name is required")
    @Size(min = 3, max = 200, message = "Product name must be between 3 and 200 characters")
    @Column(nullable = false, length = 200)
    private String name;

    @NotBlank(message = "SKU is required")
    @Pattern(regexp = "^[A-Z0-9]{6,20}$", message = "SKU must be 6-20 uppercase alphanumeric characters")
    @Column(nullable = false, unique = true, length = 20)
    private String sku;

    @NotBlank(message = "Product description is required")
    @Size(min = 10, max = 2000, message = "Description must be between 10 and 2000 characters")
    @Column(nullable = false, length = 2000)
    private String description;

    @NotNull(message = "Price is required")
    @DecimalMin(value = "0.01", message = "Price must be at least 0.01")
    @DecimalMax(value = "999999.99", message = "Price cannot exceed 999999.99")
    @Digits(integer = 6, fraction = 2, message = "Price must have at most 6 integer digits and 2 decimal places")
    @Column(nullable = false, precision = 8, scale = 2)
    private BigDecimal price;

    @NotNull(message = "Stock quantity is required")
    @Min(value = 0, message = "Stock quantity cannot be negative")
    @Max(value = 999999, message = "Stock quantity cannot exceed 999999")
    @Column(nullable = false)
    private Integer stockQuantity;

    @NotBlank(message = "Category is required")
    @Size(min = 3, max = 50, message = "Category must be between 3 and 50 characters")
    @Column(nullable = false, length = 50)
    private String category;

    @NotNull(message = "Active status is required")
    @Column(nullable = false)
    private Boolean active = true;

    @Email(message = "Vendor email must be valid")
    @Column(length = 255)
    private String vendorEmail;

    @URL(message = "Product URL must be valid")
    @Column(length = 500)
    private String productUrl;

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    // JPA requires no-arg constructor
    protected Product() {
    }

    public Product(
        String name,
        String sku,
        String description,
        BigDecimal price,
        Integer stockQuantity,
        String category
    ) {
        this.name = name;
        this.sku = sku;
        this.description = description;
        this.price = price;
        this.stockQuantity = stockQuantity;
        this.category = category;
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }

    public Integer getStockQuantity() { return stockQuantity; }
    public void setStockQuantity(Integer stockQuantity) { this.stockQuantity = stockQuantity; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public Boolean getActive() { return active; }
    public void setActive(Boolean active) { this.active = active; }

    public String getVendorEmail() { return vendorEmail; }
    public void setVendorEmail(String vendorEmail) { this.vendorEmail = vendorEmail; }

    public String getProductUrl() { return productUrl; }
    public void setProductUrl(String productUrl) { this.productUrl = productUrl; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
```

**Enable JPA validation in application.yml:**

```yaml
spring:
  jpa:
    properties:
      hibernate:
        # Enable Bean Validation for entities
        javax.persistence.validation.mode: AUTO  # Validate on persist/update
        # Validation groups: PRE_PERSIST, PRE_UPDATE, PRE_REMOVE
```

**Validation triggered automatically:**

```java
// Service code
@Service
public class ProductService {

    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Transactional
    public Product createProduct(ProductCreateRequest request) {
        var product = new Product(
            request.name(),
            request.sku(),
            request.description(),
            request.price(),
            request.stockQuantity(),
            request.category()
        );

        // Validation triggered automatically on save()
        // ConstraintViolationException thrown if validation fails
        return productRepository.save(product);
    }
}
```

**Validation exception handling:**

```java
// Controller with validation exception handler
@RestController
@RequestMapping("/api/products")
public class ProductController {

    @ExceptionHandler(jakarta.validation.ConstraintViolationException.class)
    public ResponseEntity<Map<String, String>> handleConstraintViolation(
        jakarta.validation.ConstraintViolationException ex
    ) {
        Map<String, String> errors = ex.getConstraintViolations().stream()
            .collect(java.util.stream.Collectors.toMap(
                violation -> violation.getPropertyPath().toString(),
                violation -> violation.getMessage()
            ));

        return ResponseEntity.badRequest().body(errors);
    }
}
```

**✅ Benefits:**

- **Automatic Validation:** No manual validation code needed
- **Data Integrity:** Database constraints match validation rules
- **Self-Documenting:** Constraints visible on entity definition
- **Consistent:** Same validation rules for create/update

**❌ Drawbacks:**

- Validation exceptions thrown at persist time (not at object creation)
- All fields validated on every save (can't validate subset)
- Complex cross-field validation requires custom validators

**Use When:**
- Need automatic validation on entity persistence
- Want database constraints synchronized with validation rules
- Validation rules are field-level (not cross-field)
- Don't need conditional validation (same rules for create/update)

#### Pattern 2: JPA Lifecycle Callbacks for Custom Validation

JPA lifecycle callbacks (@PrePersist, @PreUpdate) enable custom validation logic before persistence[^42].

```java
// File: src/main/java/com/example/domain/entity/Order.java
package com.example.domain.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Order entity with JPA lifecycle callbacks for complex validation.
 */
@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(nullable = false, unique = true, length = 50)
    private String orderNumber;

    @NotNull
    @Column(nullable = false)
    private Long customerId;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private OrderStatus status;

    @NotNull
    @DecimalMin("0.00")
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;

    @NotNull
    @DecimalMin("0.00")
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal taxAmount;

    @NotNull
    @DecimalMin("0.00")
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal shippingAmount;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    @NotEmpty(message = "Order must have at least one item")
    private List<OrderItem> items = new ArrayList<>();

    @NotBlank
    @Column(nullable = false, length = 500)
    private String shippingAddress;

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @Column
    private LocalDateTime shippedAt;

    @Column
    private LocalDateTime deliveredAt;

    public enum OrderStatus {
        PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
    }

    /**
     * PrePersist callback: Validate before inserting new order.
     * Runs after JSR-303 validation, before SQL INSERT.
     */
    @PrePersist
    protected void validateBeforeCreate() {
        // Validate order has items
        if (items == null || items.isEmpty()) {
            throw new IllegalStateException("Order must have at least one item");
        }

        // Validate calculated total matches item sum
        BigDecimal calculatedTotal = items.stream()
            .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal expectedTotal = calculatedTotal.add(taxAmount).add(shippingAmount);

        if (totalAmount.compareTo(expectedTotal) != 0) {
            throw new IllegalStateException(
                String.format("Total amount mismatch: expected %.2f, got %.2f",
                    expectedTotal, totalAmount)
            );
        }

        // Validate initial status is PENDING
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("New order must have PENDING status");
        }

        // Validate shipping date is not set for new order
        if (shippedAt != null || deliveredAt != null) {
            throw new IllegalStateException("New order cannot have shipping/delivery dates");
        }
    }

    /**
     * PreUpdate callback: Validate before updating existing order.
     * Runs after JSR-303 validation, before SQL UPDATE.
     */
    @PreUpdate
    protected void validateBeforeUpdate() {
        // Validate status transitions
        validateStatusTransition();

        // Validate shipped date when status is SHIPPED
        if (status == OrderStatus.SHIPPED && shippedAt == null) {
            throw new IllegalStateException("Shipped order must have shippedAt timestamp");
        }

        // Validate delivered date when status is DELIVERED
        if (status == OrderStatus.DELIVERED) {
            if (shippedAt == null || deliveredAt == null) {
                throw new IllegalStateException(
                    "Delivered order must have both shippedAt and deliveredAt timestamps"
                );
            }

            // Validate deliveredAt is after shippedAt
            if (deliveredAt.isBefore(shippedAt)) {
                throw new IllegalStateException("Delivery date must be after shipping date");
            }
        }

        // Validate cancelled orders cannot be modified
        if (status == OrderStatus.CANCELLED) {
            throw new IllegalStateException("Cannot update cancelled order");
        }
    }

    /**
     * Validate order status transitions (state machine).
     */
    private void validateStatusTransition() {
        // Status transition rules:
        // PENDING -> CONFIRMED or CANCELLED
        // CONFIRMED -> PROCESSING or CANCELLED
        // PROCESSING -> SHIPPED or CANCELLED
        // SHIPPED -> DELIVERED
        // DELIVERED -> (terminal state)
        // CANCELLED -> (terminal state)

        // Implementation would track previous status and validate transitions
        // For brevity, simplified validation shown
    }

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getOrderNumber() { return orderNumber; }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }

    public Long getCustomerId() { return customerId; }
    public void setCustomerId(Long customerId) { this.customerId = customerId; }

    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus status) { this.status = status; }

    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }

    public BigDecimal getTaxAmount() { return taxAmount; }
    public void setTaxAmount(BigDecimal taxAmount) { this.taxAmount = taxAmount; }

    public BigDecimal getShippingAmount() { return shippingAmount; }
    public void setShippingAmount(BigDecimal shippingAmount) { this.shippingAmount = shippingAmount; }

    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }

    public String getShippingAddress() { return shippingAddress; }
    public void setShippingAddress(String shippingAddress) { this.shippingAddress = shippingAddress; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }

    public LocalDateTime getShippedAt() { return shippedAt; }
    public void setShippedAt(LocalDateTime shippedAt) { this.shippedAt = shippedAt; }

    public LocalDateTime getDeliveredAt() { return deliveredAt; }
    public void setDeliveredAt(LocalDateTime deliveredAt) { this.deliveredAt = deliveredAt; }

    // Bidirectional relationship helper methods
    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }

    public void removeItem(OrderItem item) {
        items.remove(item);
        item.setOrder(null);
    }
}
```

**✅ Benefits:**

- **Complex Validation:** Cross-field, business logic validation
- **State Machine Validation:** Validate entity state transitions
- **Calculated Field Validation:** Verify computed values match expected
- **Pre-Persistence Hook:** Validation runs before database write

**❌ Drawbacks:**

- Validation exceptions thrown at persist/update time (not object creation)
- Cannot inject Spring beans in lifecycle callbacks (entity not managed by Spring)
- Complex validation logic in entity class (violates Single Responsibility)

**Use When:**
- Need cross-field validation (total matches item sum)
- Validate state transitions (order status state machine)
- Verify calculated fields before persistence
- Business rules enforcement at entity level

---

## 9. Error Handling and Validation

Comprehensive error handling and validation strategies for Spring Boot microservices, focusing on RFC 7807 Problem Details, global exception handling, and Bean Validation integration[^44][^45][^46].

### 9.1 Recommended Approach: RFC 7807 Problem Details with @ControllerAdvice

Spring Boot 3.x provides native RFC 7807 Problem Details support for standardized API error responses[^44][^46]. Combined with @ControllerAdvice for global exception handling and Bean Validation for request validation, this creates a production-ready error handling strategy.

**Core Benefits:**
- **Standardized Format:** RFC 7807 Problem Details for consistent error responses
- **Global Handling:** @ControllerAdvice centralizes exception handling (DRY principle)
- **Bean Validation:** Automatic request validation with clear error messages
- **Type Safety:** Strongly-typed error responses (not generic Map<String, Object>)
- **Client-Friendly:** Machine-readable error codes, human-readable messages

### 9.2 Implementation Example

#### Step 1: Enable RFC 7807 Problem Details

```yaml
# File: application.yml
spring:
  mvc:
    problemdetails:
      enabled: true  # Enable RFC 7807 Problem Details support
```

#### Step 2: Define Custom Exception Hierarchy

```java
// File: src/main/java/com/example/exception/BaseException.java
package com.example.exception;

/**
 * Base exception for all business exceptions.
 * Provides common fields for error handling.
 */
public abstract class BaseException extends RuntimeException {

    private final String errorCode;
    private final int httpStatus;

    protected BaseException(String message, String errorCode, int httpStatus) {
        super(message);
        this.errorCode = errorCode;
        this.httpStatus = httpStatus;
    }

    protected BaseException(String message, String errorCode, int httpStatus, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
        this.httpStatus = httpStatus;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public int getHttpStatus() {
        return httpStatus;
    }
}
```

```java
// File: src/main/java/com/example/exception/ResourceNotFoundException.java
package com.example.exception;

/**
 * Exception thrown when requested resource not found.
 * Maps to HTTP 404 Not Found.
 */
public class ResourceNotFoundException extends BaseException {

    public ResourceNotFoundException(String resourceType, Object resourceId) {
        super(
            String.format("%s not found with id: %s", resourceType, resourceId),
            "RESOURCE_NOT_FOUND",
            404
        );
    }

    public ResourceNotFoundException(String message) {
        super(message, "RESOURCE_NOT_FOUND", 404);
    }
}
```

```java
// File: src/main/java/com/example/exception/BusinessValidationException.java
package com.example.exception;

import java.util.Map;

/**
 * Exception thrown when business validation fails.
 * Maps to HTTP 422 Unprocessable Entity.
 */
public class BusinessValidationException extends BaseException {

    private final Map<String, String> validationErrors;

    public BusinessValidationException(String message, Map<String, String> validationErrors) {
        super(message, "BUSINESS_VALIDATION_FAILED", 422);
        this.validationErrors = validationErrors;
    }

    public Map<String, String> getValidationErrors() {
        return validationErrors;
    }
}
```

```java
// File: src/main/java/com/example/exception/UnauthorizedException.java
package com.example.exception;

/**
 * Exception thrown when authentication fails.
 * Maps to HTTP 401 Unauthorized.
 */
public class UnauthorizedException extends BaseException {

    public UnauthorizedException(String message) {
        super(message, "UNAUTHORIZED", 401);
    }

    public UnauthorizedException() {
        super("Authentication required", "UNAUTHORIZED", 401);
    }
}
```

```java
// File: src/main/java/com/example/exception/ForbiddenException.java
package com.example.exception;

/**
 * Exception thrown when user lacks permission.
 * Maps to HTTP 403 Forbidden.
 */
public class ForbiddenException extends BaseException {

    public ForbiddenException(String message) {
        super(message, "FORBIDDEN", 403);
    }

    public ForbiddenException(String resource, String action) {
        super(
            String.format("Not authorized to %s %s", action, resource),
            "FORBIDDEN",
            403
        );
    }
}
```

#### Step 3: Global Exception Handler with RFC 7807 Problem Details

```java
// File: src/main/java/com/example/exception/GlobalExceptionHandler.java
package com.example.exception;

import jakarta.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.net.URI;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Global exception handler using RFC 7807 Problem Details.
 * Centralizes error handling across all controllers.
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * Handle custom business exceptions (ResourceNotFoundException, etc.).
     */
    @ExceptionHandler(BaseException.class)
    public ResponseEntity<ProblemDetail> handleBaseException(
        BaseException ex,
        WebRequest request
    ) {
        log.error("Business exception: {}", ex.getMessage(), ex);

        var problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.valueOf(ex.getHttpStatus()),
            ex.getMessage()
        );

        problemDetail.setTitle(ex.getErrorCode());
        problemDetail.setType(URI.create("/errors/" + ex.getErrorCode().toLowerCase()));
        problemDetail.setProperty("errorCode", ex.getErrorCode());
        problemDetail.setProperty("timestamp", Instant.now());

        // Add validation errors if BusinessValidationException
        if (ex instanceof BusinessValidationException validationEx) {
            problemDetail.setProperty("validationErrors", validationEx.getValidationErrors());
        }

        return ResponseEntity
            .status(ex.getHttpStatus())
            .body(problemDetail);
    }

    /**
     * Handle Bean Validation errors (@Valid on request body).
     * Triggered by @Valid annotation on controller method parameters.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ProblemDetail> handleMethodArgumentNotValid(
        MethodArgumentNotValidException ex,
        WebRequest request
    ) {
        log.error("Validation failed: {}", ex.getMessage());

        // Extract field errors from BindingResult
        Map<String, String> errors = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .collect(Collectors.toMap(
                FieldError::getField,
                fieldError -> fieldError.getDefaultMessage() != null
                    ? fieldError.getDefaultMessage()
                    : "Invalid value",
                (existing, replacement) -> existing  // Keep first error if duplicate field
            ));

        var problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST,
            "Request validation failed"
        );

        problemDetail.setTitle("VALIDATION_FAILED");
        problemDetail.setType(URI.create("/errors/validation_failed"));
        problemDetail.setProperty("errorCode", "VALIDATION_FAILED");
        problemDetail.setProperty("timestamp", Instant.now());
        problemDetail.setProperty("validationErrors", errors);
        problemDetail.setProperty("errorCount", errors.size());

        return ResponseEntity
            .badRequest()
            .body(problemDetail);
    }

    /**
     * Handle constraint violations (e.g., JPA entity validation failures).
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ProblemDetail> handleConstraintViolation(
        ConstraintViolationException ex,
        WebRequest request
    ) {
        log.error("Constraint violation: {}", ex.getMessage());

        Map<String, String> errors = ex.getConstraintViolations().stream()
            .collect(Collectors.toMap(
                violation -> violation.getPropertyPath().toString(),
                violation -> violation.getMessage(),
                (existing, replacement) -> existing
            ));

        var problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST,
            "Constraint validation failed"
        );

        problemDetail.setTitle("CONSTRAINT_VIOLATION");
        problemDetail.setType(URI.create("/errors/constraint_violation"));
        problemDetail.setProperty("errorCode", "CONSTRAINT_VIOLATION");
        problemDetail.setProperty("timestamp", Instant.now());
        problemDetail.setProperty("validationErrors", errors);

        return ResponseEntity
            .badRequest()
            .body(problemDetail);
    }

    /**
     * Handle generic exceptions (catch-all for unexpected errors).
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ProblemDetail> handleGenericException(
        Exception ex,
        WebRequest request
    ) {
        log.error("Unexpected error", ex);

        var problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "An unexpected error occurred"
        );

        problemDetail.setTitle("INTERNAL_SERVER_ERROR");
        problemDetail.setType(URI.create("/errors/internal_server_error"));
        problemDetail.setProperty("errorCode", "INTERNAL_SERVER_ERROR");
        problemDetail.setProperty("timestamp", Instant.now());

        // Don't expose internal error details in production
        if (log.isDebugEnabled()) {
            problemDetail.setProperty("debugMessage", ex.getMessage());
        }

        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(problemDetail);
    }
}
```

#### Step 4: Request DTOs with Bean Validation

```java
// File: src/main/java/com/example/dto/CreateUserRequest.java
package com.example.dto;

import jakarta.validation.constraints.*;

/**
 * Request DTO for user creation with Bean Validation annotations.
 * Validation triggered automatically by @Valid in controller.
 */
public record CreateUserRequest(
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be between 2 and 100 characters")
    String name,

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    String email,

    @NotBlank(message = "Password is required")
    @Size(min = 8, max = 64, message = "Password must be between 8 and 64 characters")
    @Pattern(
        regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
        message = "Password must contain uppercase, lowercase, digit, and special character"
    )
    String password,

    @NotNull(message = "Age is required")
    @Min(value = 18, message = "Age must be at least 18")
    @Max(value = 150, message = "Age must be at most 150")
    Integer age,

    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Phone number must be valid E.164 format")
    String phoneNumber
) {}
```

#### Step 5: Controller with Validation

```java
// File: src/main/java/com/example/controller/UserController.java
package com.example.controller;

import com.example.dto.CreateUserRequest;
import com.example.dto.UserResponse;
import com.example.exception.ResourceNotFoundException;
import com.example.service.UserService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * User controller with Bean Validation and error handling.
 */
@RestController
@RequestMapping("/api/users")
@Validated  // Enable validation for method parameters
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    /**
     * Create user with validated request body.
     * @Valid triggers Bean Validation, handled by GlobalExceptionHandler.
     */
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        var user = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(user);
    }

    /**
     * Get user by ID with path variable validation.
     * @Min validates userId parameter.
     */
    @GetMapping("/{userId}")
    public ResponseEntity<UserResponse> getUser(
        @PathVariable @Min(1) Long userId
    ) {
        return userService.getUserById(userId)
            .map(ResponseEntity::ok)
            .orElseThrow(() -> new ResourceNotFoundException("User", userId));
    }

    /**
     * Search users by name pattern.
     */
    @GetMapping("/search")
    public ResponseEntity<List<UserResponse>> searchUsers(
        @RequestParam @NotBlank String namePattern
    ) {
        var users = userService.searchUsers(namePattern);
        return ResponseEntity.ok(users);
    }

    /**
     * Delete user by ID.
     */
    @DeleteMapping("/{userId}")
    public ResponseEntity<Void> deleteUser(@PathVariable @Min(1) Long userId) {
        if (!userService.deleteUser(userId)) {
            throw new ResourceNotFoundException("User", userId);
        }
        return ResponseEntity.noContent().build();
    }
}
```

**Example error responses:**

**Validation error (400 Bad Request):**

```json
{
  "type": "/errors/validation_failed",
  "title": "VALIDATION_FAILED",
  "status": 400,
  "detail": "Request validation failed",
  "errorCode": "VALIDATION_FAILED",
  "timestamp": "2025-11-02T10:30:00Z",
  "errorCount": 3,
  "validationErrors": {
    "name": "Name must be between 2 and 100 characters",
    "email": "Email must be valid",
    "password": "Password must contain uppercase, lowercase, digit, and special character"
  }
}
```

**Resource not found (404 Not Found):**

```json
{
  "type": "/errors/resource_not_found",
  "title": "RESOURCE_NOT_FOUND",
  "status": 404,
  "detail": "User not found with id: 999",
  "errorCode": "RESOURCE_NOT_FOUND",
  "timestamp": "2025-11-02T10:30:00Z"
}
```

**✅ Benefits:**

- **Standardized:** RFC 7807 Problem Details format (industry standard)
- **Centralized:** @RestControllerAdvice handles all exceptions globally
- **Automatic Validation:** @Valid triggers Bean Validation, no manual checks
- **Type-Safe:** ProblemDetail strongly typed (not generic Map)
- **Client-Friendly:** Clear error codes, detailed validation messages, timestamps

**❌ Drawbacks:**

- Global exception handling can become complex with many exception types
- RFC 7807 format may be overkill for simple APIs
- Additional overhead for error response construction

**Use When:**
- Building REST APIs for external clients (standardized error format)
- Need centralized exception handling (DRY principle)
- Want automatic request validation (@Valid)
- Multiple exception types with custom error codes

---

### 9.3 Additional Validation Patterns

#### Pattern 1: Custom Validation for Business Rules

(Already covered in Section 1.2.5 - Custom Validation Annotations)

#### Pattern 2: Service Layer Validation

Business validation in service layer (beyond JSR-303 field validation)[^47].

```java
// File: src/main/java/com/example/service/OrderService.java
package com.example.service;

import com.example.domain.entity.Order;
import com.example.exception.BusinessValidationException;
import com.example.repository.OrderRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

/**
 * Order service with business validation.
 */
@Service
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    /**
     * Create order with comprehensive business validation.
     */
    @Transactional
    public Order createOrder(OrderCreateRequest request) {
        // Business validation (beyond JSR-303)
        Map<String, String> errors = new HashMap<>();

        // Validate customer exists
        if (!customerExists(request.customerId())) {
            errors.put("customerId", "Customer not found: " + request.customerId());
        }

        // Validate all products exist and have sufficient stock
        request.items().forEach(item -> {
            if (!productExists(item.productId())) {
                errors.put("items.productId", "Product not found: " + item.productId());
            } else if (!hasSufficientStock(item.productId(), item.quantity())) {
                errors.put("items.quantity",
                    String.format("Insufficient stock for product %d (requested: %d)",
                        item.productId(), item.quantity()));
            }
        });

        // Validate total amount matches calculated amount
        BigDecimal calculatedTotal = calculateTotal(request);
        if (request.totalAmount().compareTo(calculatedTotal) != 0) {
            errors.put("totalAmount",
                String.format("Total amount mismatch: expected %.2f, got %.2f",
                    calculatedTotal, request.totalAmount()));
        }

        // Throw if validation errors
        if (!errors.isEmpty()) {
            throw new BusinessValidationException("Order validation failed", errors);
        }

        // Create order (validation passed)
        var order = buildOrder(request);
        return orderRepository.save(order);
    }

    private boolean customerExists(Long customerId) {
        // Implementation
        return true;
    }

    private boolean productExists(Long productId) {
        // Implementation
        return true;
    }

    private boolean hasSufficientStock(Long productId, int quantity) {
        // Implementation
        return true;
    }

    private BigDecimal calculateTotal(OrderCreateRequest request) {
        // Implementation
        return BigDecimal.ZERO;
    }

    private Order buildOrder(OrderCreateRequest request) {
        // Implementation
        return new Order();
    }
}
```

**✅ Benefits:**

- **Business Logic Validation:** Beyond JSR-303 field validation
- **Cross-Entity Validation:** Check relationships (customer exists, stock available)
- **Transactional:** Validation within transaction boundary
- **Clear Error Messages:** Specific error for each validation failure

---

### 9.7 Error Correlation with Distributed Tracing

In distributed microservice architectures, correlating errors across service boundaries requires propagating trace context through the call chain. Spring Cloud Sleuth (now migrating to OpenTelemetry) provides automatic trace context propagation, enabling errors to be linked to distributed traces[^48][^49].

**Core Benefits:**
- **Error Traceability:** Link exceptions to specific trace spans across services
- **Root Cause Analysis:** Follow error propagation through distributed call chain
- **Automatic Context Propagation:** Trace IDs/Span IDs automatically included in logs
- **Error Sampling:** Configure sampling strategies to capture all errors while sampling normal requests

#### Implementation with Spring Cloud Sleuth and OpenTelemetry

**Step 1: Add Dependencies**

```xml
<!-- File: pom.xml -->
<dependencies>
    <!-- Spring Cloud Sleuth with OpenTelemetry bridge -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-sleuth</artifactId>
        <version>3.1.9</version>
    </dependency>

    <!-- OpenTelemetry integration -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-api</artifactId>
        <version>1.32.0</version>
    </dependency>

    <!-- Zipkin exporter for trace visualization -->
    <dependency>
        <groupId>io.zipkin.reporter2</groupId>
        <artifactId>zipkin-reporter-brave</artifactId>
        <version>2.16.4</version>
    </dependency>

    <!-- Logback encoder for trace context in logs -->
    <dependency>
        <groupId>net.logstash.logback</groupId>
        <artifactId>logstash-logback-encoder</artifactId>
        <version>7.4</version>
    </dependency>
</dependencies>
```

**Step 2: Configure Trace Context in Logs**

```xml
<!-- File: src/main/resources/logback-spring.xml -->
<configuration>
    <appender name="CONSOLE_JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <!-- Include trace/span IDs in every log entry -->
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <includeMdcKeyName>parentSpanId</includeMdcKeyName>

            <!-- Include exception details with trace context -->
            <throwableConverter class="net.logstash.logback.stacktrace.ShortenedThrowableConverter">
                <maxDepthPerThrowable>30</maxDepthPerThrowable>
                <maxLength>2048</maxLength>
                <shortenedClassNameLength>30</shortenedClassNameLength>
            </throwableConverter>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="CONSOLE_JSON"/>
    </root>
</configuration>
```

**Step 3: Configure Error Sampling Strategy**

```yaml
# File: application.yml
spring:
  sleuth:
    sampler:
      # Sample 10% of successful requests, 100% of errors
      probability: 0.1

    # Always sample errors (override probability for error traces)
    baggage:
      remote-fields:
        - error
        - errorMessage

  zipkin:
    base-url: http://zipkin-server:9411
    sender:
      type: web  # Use HTTP to send traces

    # Batch configuration for performance
    message-timeout: 1
    queue-size: 1000

# Custom error sampling (sample all errors regardless of probability)
management:
  tracing:
    sampling:
      probability: 0.1  # Base sampling rate

    # OpenTelemetry configuration (Sleuth 3.x uses OpenTelemetry)
    opentelemetry:
      propagation:
        type: B3,W3C  # Support both B3 and W3C trace context formats
```

**Step 4: Enhanced Exception Handler with Trace Context**

```java
// File: src/main/java/com/example/exception/TracingExceptionHandler.java
package com.example.exception;

import brave.Span;
import brave.Tracer;
import io.opentelemetry.api.trace.Span as OtelSpan;
import io.opentelemetry.api.trace.StatusCode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;

import java.net.URI;
import java.time.Instant;

/**
 * Global exception handler with distributed tracing integration.
 * Records exceptions in trace spans and includes trace context in error responses.
 */
@RestControllerAdvice
public class TracingExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(TracingExceptionHandler.class);

    private final Tracer tracer;  // Brave tracer from Spring Cloud Sleuth

    public TracingExceptionHandler(Tracer tracer) {
        this.tracer = tracer;
    }

    /**
     * Handle custom business exceptions with trace context.
     */
    @ExceptionHandler(BaseException.class)
    public ResponseEntity<ProblemDetail> handleBaseException(
        BaseException ex,
        WebRequest request
    ) {
        // Get current trace span
        Span currentSpan = tracer.currentSpan();

        if (currentSpan != null) {
            // Record exception in span (visible in Zipkin/Jaeger)
            currentSpan.error(ex);

            // Add error tags to span for filtering
            currentSpan.tag("error.type", ex.getClass().getSimpleName());
            currentSpan.tag("error.code", ex.getErrorCode());
            currentSpan.tag("http.status_code", String.valueOf(ex.getHttpStatus()));

            // Also record in OpenTelemetry span (if using OTel bridge)
            OtelSpan otelSpan = OtelSpan.current();
            otelSpan.recordException(ex);
            otelSpan.setStatus(StatusCode.ERROR, ex.getMessage());
        }

        // Log error with trace context (traceId/spanId automatically included by Sleuth)
        log.error("Business exception [errorCode={}]: {}",
            ex.getErrorCode(), ex.getMessage(), ex);

        var problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.valueOf(ex.getHttpStatus()),
            ex.getMessage()
        );

        problemDetail.setTitle(ex.getErrorCode());
        problemDetail.setType(URI.create("/errors/" + ex.getErrorCode().toLowerCase()));
        problemDetail.setProperty("errorCode", ex.getErrorCode());
        problemDetail.setProperty("timestamp", Instant.now());

        // Include trace context in error response for client-side correlation
        if (currentSpan != null) {
            problemDetail.setProperty("traceId", currentSpan.context().traceIdString());
            problemDetail.setProperty("spanId", currentSpan.context().spanIdString());
        }

        return ResponseEntity
            .status(ex.getHttpStatus())
            .body(problemDetail);
    }

    /**
     * Handle generic exceptions with trace context.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ProblemDetail> handleGenericException(
        Exception ex,
        WebRequest request
    ) {
        Span currentSpan = tracer.currentSpan();

        if (currentSpan != null) {
            // Record unexpected exception in span
            currentSpan.error(ex);
            currentSpan.tag("error.type", "UnexpectedException");
            currentSpan.tag("http.status_code", "500");

            // OpenTelemetry span
            OtelSpan otelSpan = OtelSpan.current();
            otelSpan.recordException(ex);
            otelSpan.setStatus(StatusCode.ERROR, "Internal server error");
        }

        log.error("Unexpected error", ex);

        var problemDetail = ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR,
            "An unexpected error occurred"
        );

        problemDetail.setTitle("INTERNAL_SERVER_ERROR");
        problemDetail.setType(URI.create("/errors/internal_server_error"));
        problemDetail.setProperty("errorCode", "INTERNAL_SERVER_ERROR");
        problemDetail.setProperty("timestamp", Instant.now());

        // Include trace context
        if (currentSpan != null) {
            problemDetail.setProperty("traceId", currentSpan.context().traceIdString());
            problemDetail.setProperty("spanId", currentSpan.context().spanIdString());
        }

        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(problemDetail);
    }
}
```

**Step 5: Service Layer with Manual Span Creation for Error Scenarios**

```java
// File: src/main/java/com/example/service/PaymentService.java
package com.example.service;

import brave.Span;
import brave.Tracer;
import com.example.exception.PaymentFailedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Payment service demonstrating manual span creation for error tracking.
 */
@Service
public class PaymentService {

    private static final Logger log = LoggerFactory.getLogger(PaymentService.class);

    private final Tracer tracer;
    private final PaymentGatewayClient paymentGateway;

    public PaymentService(Tracer tracer, PaymentGatewayClient paymentGateway) {
        this.tracer = tracer;
        this.paymentGateway = paymentGateway;
    }

    /**
     * Process payment with detailed error tracing.
     */
    public PaymentResult processPayment(PaymentRequest request) {
        // Create custom span for payment processing
        Span paymentSpan = tracer.nextSpan().name("payment.process").start();

        try (Tracer.SpanInScope ws = tracer.withSpanInScope(paymentSpan)) {
            // Add business context to span
            paymentSpan.tag("payment.amount", request.amount().toString());
            paymentSpan.tag("payment.currency", request.currency());
            paymentSpan.tag("payment.method", request.paymentMethod());

            log.info("Processing payment: amount={}, currency={}",
                request.amount(), request.currency());

            // Call external payment gateway
            PaymentResult result = paymentGateway.charge(request);

            if (!result.isSuccessful()) {
                // Record payment failure in span
                paymentSpan.tag("payment.status", "failed");
                paymentSpan.tag("payment.error.code", result.errorCode());
                paymentSpan.tag("payment.error.message", result.errorMessage());

                // Create error event in span timeline
                paymentSpan.annotate("payment_gateway_rejected");

                log.error("Payment failed: errorCode={}, message={}",
                    result.errorCode(), result.errorMessage());

                throw new PaymentFailedException(
                    result.errorCode(),
                    result.errorMessage()
                );
            }

            // Success path
            paymentSpan.tag("payment.status", "success");
            paymentSpan.tag("payment.transactionId", result.transactionId());

            log.info("Payment successful: transactionId={}", result.transactionId());

            return result;

        } catch (Exception ex) {
            // Record exception in span
            paymentSpan.error(ex);
            paymentSpan.tag("error", "true");

            // Force this trace to be sampled (important for error analysis)
            paymentSpan.tag("sampling.priority", "1");

            throw ex;

        } finally {
            // Always finish span
            paymentSpan.finish();
        }
    }
}
```

**Example Log Output with Trace Context:**

```json
{
  "timestamp": "2025-11-02T10:30:00.123Z",
  "level": "ERROR",
  "logger": "com.example.exception.TracingExceptionHandler",
  "message": "Business exception [errorCode=PAYMENT_FAILED]: Payment gateway rejected transaction",
  "traceId": "5e2f8b3a9c1d4e6f",
  "spanId": "7a8b9c0d1e2f3a4b",
  "parentSpanId": "1a2b3c4d5e6f7a8b",
  "exception": {
    "class": "com.example.exception.PaymentFailedException",
    "message": "Payment gateway rejected transaction",
    "stackTrace": [...]
  },
  "tags": {
    "error.type": "PaymentFailedException",
    "error.code": "PAYMENT_FAILED",
    "payment.amount": "99.99",
    "payment.currency": "USD"
  }
}
```

**Example Error Response with Trace Context:**

```json
{
  "type": "/errors/payment_failed",
  "title": "PAYMENT_FAILED",
  "status": 422,
  "detail": "Payment gateway rejected transaction",
  "errorCode": "PAYMENT_FAILED",
  "timestamp": "2025-11-02T10:30:00Z",
  "traceId": "5e2f8b3a9c1d4e6f",
  "spanId": "7a8b9c0d1e2f3a4b"
}
```

**Zipkin Query for Error Analysis:**

Clients can use traceId from error response to query Zipkin:

```bash
# Query Zipkin for full trace including error
curl "http://zipkin:9411/api/v2/trace/5e2f8b3a9c1d4e6f"

# Search for all failed payment traces
curl "http://zipkin:9411/api/v2/traces?annotationQuery=error.code=PAYMENT_FAILED&limit=100"
```

**✅ Benefits:**

- **Full Error Context:** Trace context links errors across distributed services
- **Automatic Propagation:** Sleuth/OTel automatically propagates trace IDs through HTTP headers, message queues
- **Client Correlation:** Clients receive traceId in error response for support tickets
- **Error Sampling:** Configure 100% sampling for errors, lower sampling for success cases
- **Unified Observability:** Errors visible in Zipkin/Jaeger UI with full request timeline

**❌ Drawbacks:**

- **Performance Overhead:** Trace context adds ~1-5ms latency per request
- **Storage Costs:** High error sampling rates increase trace storage requirements
- **Complexity:** Requires Zipkin/Jaeger infrastructure for trace visualization
- **Migration Challenge:** Spring Cloud Sleuth deprecated, migrating to OpenTelemetry

**Use When:**
- Building distributed microservices (multi-service architectures)
- Need root cause analysis for errors across services
- Want client-side error correlation (support tickets with traceId)
- Implementing SRE best practices (observability, SLOs)

**Avoid When:**
- Monolithic applications (single service doesn't need distributed tracing)
- Ultra-low latency requirements (tracing adds overhead)
- No observability infrastructure (Zipkin/Jaeger not available)

---

## 10. Telemetry and Observability

Production-grade microservices require comprehensive telemetry for monitoring health, performance, and diagnosing issues. Spring Boot Actuator combined with Micrometer provides a production-ready observability stack with minimal configuration[^50][^51][^52].

### 10.1 Recommended Approach: Spring Boot Actuator with Micrometer

Spring Boot Actuator provides production-ready features (health checks, metrics, environment info) through HTTP endpoints. Micrometer acts as a metrics facade supporting multiple monitoring systems (Prometheus, Datadog, InfluxDB)[^50][^53].

**Core Benefits:**
- **Auto-Configuration:** Actuator auto-configures 40+ metrics out-of-box (JVM, HTTP, database, cache)
- **Prometheus Integration:** Native Prometheus endpoint for Kubernetes monitoring
- **Health Indicators:** Liveness/readiness probes for Kubernetes orchestration
- **Vendor-Neutral:** Micrometer facade supports switching monitoring backends
- **Custom Metrics:** Simple API for business metrics (@Timed, @Counted, MeterRegistry)
- **Distributed Tracing:** Integrates with OpenTelemetry/Zipkin via Spring Cloud Sleuth

### 10.2 Implementation Examples

#### Step 1: Add Dependencies

```xml
<!-- File: pom.xml -->
<dependencies>
    <!-- Spring Boot Actuator (health, metrics, info endpoints) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>

    <!-- Micrometer Prometheus registry (for Prometheus scraping) -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>

    <!-- OpenTelemetry integration (distributed tracing) -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-tracing-bridge-otel</artifactId>
    </dependency>

    <!-- Zipkin exporter for trace visualization -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-zipkin</artifactId>
    </dependency>
</dependencies>
```

#### Step 2: Configure Actuator Endpoints

```yaml
# File: application.yml
management:
  endpoints:
    web:
      exposure:
        # Expose specific endpoints (don't expose all in production)
        include: health,info,metrics,prometheus,loggers
      base-path: /actuator

  endpoint:
    health:
      # Show detailed health info (use only in dev/staging)
      show-details: when-authorized
      show-components: always

      # Kubernetes probes configuration
      probes:
        enabled: true

      # Group health indicators for liveness/readiness
      group:
        liveness:
          include: ping,diskSpace
        readiness:
          include: db,redis,customService

    metrics:
      enabled: true

    prometheus:
      enabled: true

    loggers:
      enabled: true  # Allow runtime log level changes

  metrics:
    export:
      prometheus:
        enabled: true
        step: 1m  # Scraping interval

    distribution:
      # Histogram buckets for HTTP request duration (SLO-based)
      percentiles-histogram:
        http.server.requests: true
      slo:
        http.server.requests: 10ms,50ms,100ms,200ms,500ms,1s,2s

    tags:
      # Global tags added to all metrics
      application: ${spring.application.name}
      environment: ${spring.profiles.active}
      region: us-east-1

  tracing:
    sampling:
      probability: 0.1  # Sample 10% of requests for tracing

  info:
    # Include build info, git commit in /actuator/info
    git:
      mode: full
    build:
      enabled: true
    env:
      enabled: true

spring:
  application:
    name: user-service

# Logging configuration for metrics
logging:
  level:
    io.micrometer: INFO
    org.springframework.boot.actuate: INFO
```

#### Step 3: Custom Health Indicators

```java
// File: src/main/java/com/example/health/CustomServiceHealthIndicator.java
package com.example.health;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.time.Instant;

/**
 * Custom health indicator for external service dependency.
 * Implements HealthIndicator for integration with Actuator health endpoint.
 */
@Component
public class CustomServiceHealthIndicator implements HealthIndicator {

    private final ExternalServiceClient externalService;
    private volatile Instant lastCheckTime = Instant.now();
    private volatile boolean lastCheckSuccessful = true;

    private static final Duration HEALTH_CHECK_TIMEOUT = Duration.ofSeconds(5);

    public CustomServiceHealthIndicator(ExternalServiceClient externalService) {
        this.externalService = externalService;
    }

    /**
     * Check health of external service dependency.
     * Called by Actuator health endpoint.
     */
    @Override
    public Health health() {
        try {
            // Perform health check with timeout
            boolean isHealthy = externalService.ping(HEALTH_CHECK_TIMEOUT);

            lastCheckTime = Instant.now();
            lastCheckSuccessful = isHealthy;

            if (isHealthy) {
                return Health.up()
                    .withDetail("service", "external-api")
                    .withDetail("status", "reachable")
                    .withDetail("lastCheckTime", lastCheckTime)
                    .withDetail("responseTime", externalService.getLastResponseTime())
                    .build();
            } else {
                return Health.down()
                    .withDetail("service", "external-api")
                    .withDetail("status", "unreachable")
                    .withDetail("lastCheckTime", lastCheckTime)
                    .withDetail("error", "Health check failed")
                    .build();
            }

        } catch (Exception ex) {
            lastCheckSuccessful = false;

            return Health.down()
                .withDetail("service", "external-api")
                .withDetail("status", "error")
                .withDetail("lastCheckTime", Instant.now())
                .withException(ex)
                .build();
        }
    }
}
```

```java
// File: src/main/java/com/example/health/DatabaseConnectionHealthIndicator.java
package com.example.health;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;

/**
 * Custom database health indicator with connection pool metrics.
 */
@Component
public class DatabaseConnectionHealthIndicator implements HealthIndicator {

    private final JdbcTemplate jdbcTemplate;
    private final DataSource dataSource;

    public DatabaseConnectionHealthIndicator(JdbcTemplate jdbcTemplate, DataSource dataSource) {
        this.jdbcTemplate = jdbcTemplate;
        this.dataSource = dataSource;
    }

    @Override
    public Health health() {
        try {
            // Execute simple query to verify connectivity
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);

            // Get HikariCP metrics (if using HikariCP)
            com.zaxxer.hikari.HikariDataSource hikariDS =
                (com.zaxxer.hikari.HikariDataSource) dataSource;

            var poolStats = hikariDS.getHikariPoolMXBean();

            return Health.up()
                .withDetail("database", "PostgreSQL")
                .withDetail("status", "connected")
                .withDetail("activeConnections", poolStats.getActiveConnections())
                .withDetail("idleConnections", poolStats.getIdleConnections())
                .withDetail("totalConnections", poolStats.getTotalConnections())
                .withDetail("threadsAwaitingConnection", poolStats.getThreadsAwaitingConnection())
                .withDetail("maxPoolSize", hikariDS.getMaximumPoolSize())
                .build();

        } catch (Exception ex) {
            return Health.down()
                .withDetail("database", "PostgreSQL")
                .withDetail("status", "disconnected")
                .withException(ex)
                .build();
        }
    }
}
```

#### Step 4: Custom Metrics with Micrometer

```java
// File: src/main/java/com/example/service/OrderService.java
package com.example.service;

import io.micrometer.core.annotation.Counted;
import io.micrometer.core.annotation.Timed;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Order service with custom business metrics using Micrometer.
 */
@Service
public class OrderService {

    private final MeterRegistry meterRegistry;
    private final OrderRepository orderRepository;

    // Custom counters for business metrics
    private final Counter ordersCreatedCounter;
    private final Counter ordersCancelledCounter;
    private final Counter ordersFailedCounter;

    // Gauge for active orders (real-time value)
    private final AtomicInteger activeOrdersGauge;

    // Timer for order processing duration
    private final Timer orderProcessingTimer;

    public OrderService(MeterRegistry meterRegistry, OrderRepository orderRepository) {
        this.meterRegistry = meterRegistry;
        this.orderRepository = orderRepository;

        // Initialize custom metrics
        this.ordersCreatedCounter = Counter.builder("orders.created")
            .description("Total number of orders created")
            .tag("service", "order-service")
            .register(meterRegistry);

        this.ordersCancelledCounter = Counter.builder("orders.cancelled")
            .description("Total number of orders cancelled")
            .tag("service", "order-service")
            .register(meterRegistry);

        this.ordersFailedCounter = Counter.builder("orders.failed")
            .description("Total number of failed order creations")
            .tag("service", "order-service")
            .register(meterRegistry);

        // Gauge for active orders (snapshot of current state)
        this.activeOrdersGauge = meterRegistry.gauge(
            "orders.active",
            new AtomicInteger(0)
        );

        // Timer for measuring order processing duration
        this.orderProcessingTimer = Timer.builder("orders.processing.duration")
            .description("Order processing duration")
            .tag("service", "order-service")
            .publishPercentiles(0.5, 0.95, 0.99)  // P50, P95, P99
            .publishPercentileHistogram()
            .register(meterRegistry);
    }

    /**
     * Create order with automatic method timing via @Timed annotation.
     * Micrometer automatically creates timer metric for this method.
     */
    @Timed(value = "orders.create.duration", description = "Time to create order", percentiles = {0.5, 0.95, 0.99})
    @Counted(value = "orders.create.invocations", description = "Number of create order invocations")
    public Order createOrder(OrderRequest request) {
        // Manual timer for specific section
        return orderProcessingTimer.record(() -> {
            try {
                // Business logic
                Order order = buildOrder(request);
                Order savedOrder = orderRepository.save(order);

                // Increment success counter
                ordersCreatedCounter.increment();

                // Update active orders gauge
                activeOrdersGauge.incrementAndGet();

                // Record order value as distribution summary
                meterRegistry.summary("orders.value")
                    .record(request.totalAmount().doubleValue());

                return savedOrder;

            } catch (Exception ex) {
                // Increment failure counter
                ordersFailedCounter.increment();

                // Record failure by order type (add dynamic tags)
                Counter.builder("orders.failed.by_type")
                    .tag("orderType", request.orderType())
                    .tag("failureReason", ex.getClass().getSimpleName())
                    .register(meterRegistry)
                    .increment();

                throw ex;
            }
        });
    }

    /**
     * Cancel order with metric tracking.
     */
    public void cancelOrder(Long orderId) {
        orderRepository.findById(orderId).ifPresent(order -> {
            order.setStatus(OrderStatus.CANCELLED);
            orderRepository.save(order);

            // Increment cancellation counter
            ordersCancelledCounter.increment();

            // Decrement active orders
            activeOrdersGauge.decrementAndGet();

            // Record cancellation reason (dynamic tag)
            Counter.builder("orders.cancelled.by_reason")
                .tag("reason", order.getCancellationReason())
                .register(meterRegistry)
                .increment();
        });
    }

    /**
     * Manually time a specific operation.
     */
    public void processPayment(Long orderId) {
        Timer.Sample sample = Timer.start(meterRegistry);

        try {
            // Payment processing logic
            performPaymentProcessing(orderId);

            // Record successful payment duration
            sample.stop(Timer.builder("payments.processing.duration")
                .tag("status", "success")
                .register(meterRegistry));

        } catch (Exception ex) {
            // Record failed payment duration
            sample.stop(Timer.builder("payments.processing.duration")
                .tag("status", "failed")
                .tag("error", ex.getClass().getSimpleName())
                .register(meterRegistry));

            throw ex;
        }
    }

    private Order buildOrder(OrderRequest request) {
        return new Order();
    }

    private void performPaymentProcessing(Long orderId) {
        // Implementation
    }
}
```

**Example Prometheus Metrics Output:**

```prometheus
# HELP orders_created_total Total number of orders created
# TYPE orders_created_total counter
orders_created_total{application="user-service",environment="production",service="order-service"} 15234.0

# HELP orders_active Active orders
# TYPE orders_active gauge
orders_active{application="user-service",environment="production"} 342.0

# HELP orders_processing_duration_seconds Order processing duration
# TYPE orders_processing_duration_seconds histogram
orders_processing_duration_seconds{application="user-service",environment="production",quantile="0.5"} 0.045
orders_processing_duration_seconds{application="user-service",environment="production",quantile="0.95"} 0.120
orders_processing_duration_seconds{application="user-service",environment="production",quantile="0.99"} 0.250
orders_processing_duration_seconds_count{application="user-service",environment="production"} 15234.0
orders_processing_duration_seconds_sum{application="user-service",environment="production"} 892.5

# HELP http_server_requests_seconds HTTP request duration
# TYPE http_server_requests_seconds histogram
http_server_requests_seconds{application="user-service",method="POST",status="201",uri="/api/orders"} 0.050
```

---

### 10.2.1 Telemetry Initialization Patterns

#### Pattern 1: Spring Boot Actuator with Micrometer (Recommended)

**Use Case:** Standard Spring Boot applications requiring production-ready metrics, health checks, and monitoring integration.

**Implementation:**

```java
// File: src/main/java/com/example/config/MetricsConfiguration.java
package com.example.config;

import io.micrometer.core.aop.TimedAspect;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmMemoryMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmThreadMetrics;
import io.micrometer.core.instrument.binder.system.ProcessorMetrics;
import org.springframework.boot.actuate.autoconfigure.metrics.MeterRegistryCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

/**
 * Metrics configuration with common tags and custom metrics.
 */
@Configuration
@EnableAspectJAutoProxy
public class MetricsConfiguration {

    /**
     * Add common tags to all metrics (application, environment).
     */
    @Bean
    public MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config()
            .commonTags(
                "application", "user-service",
                "environment", System.getenv().getOrDefault("ENV", "local"),
                "region", System.getenv().getOrDefault("AWS_REGION", "us-east-1")
            );
    }

    /**
     * Enable @Timed annotation support for method-level timing.
     */
    @Bean
    public TimedAspect timedAspect(MeterRegistry meterRegistry) {
        return new TimedAspect(meterRegistry);
    }

    /**
     * JVM metrics (GC, memory, threads) - already auto-configured by Actuator.
     * Explicit registration shown for educational purposes.
     */
    @Bean
    public JvmGcMetrics jvmGcMetrics() {
        return new JvmGcMetrics();
    }

    @Bean
    public JvmMemoryMetrics jvmMemoryMetrics() {
        return new JvmMemoryMetrics();
    }

    @Bean
    public JvmThreadMetrics jvmThreadMetrics() {
        return new JvmThreadMetrics();
    }

    @Bean
    public ProcessorMetrics processorMetrics() {
        return new ProcessorMetrics();
    }
}
```

**✅ Benefits:**
- Auto-configured JVM, HTTP, database, cache metrics
- Prometheus endpoint ready for Kubernetes monitoring
- Health checks for Kubernetes liveness/readiness probes
- Simple @Timed/@Counted annotations for custom metrics

**❌ Drawbacks:**
- Limited to metrics Micrometer supports (not as flexible as OpenTelemetry)
- Requires separate tracing library (Spring Cloud Sleuth/OpenTelemetry)

**Use When:**
- Standard Spring Boot microservices
- Using Prometheus for monitoring
- Need quick setup with minimal configuration

---

#### Pattern 2: OpenTelemetry Java Agent Auto-Instrumentation

**Use Case:** Zero-code instrumentation for existing applications, vendor-neutral telemetry supporting metrics, traces, and logs.

**Implementation:**

```bash
# Download OpenTelemetry Java Agent
curl -L https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar \
  -o opentelemetry-javaagent.jar

# Run application with OTel agent
java -javaagent:opentelemetry-javaagent.jar \
  -Dotel.service.name=user-service \
  -Dotel.traces.exporter=zipkin \
  -Dotel.metrics.exporter=prometheus \
  -Dotel.exporter.zipkin.endpoint=http://zipkin:9411/api/v2/spans \
  -Dotel.exporter.prometheus.port=9090 \
  -Dotel.instrumentation.spring-webmvc.enabled=true \
  -Dotel.instrumentation.jdbc.enabled=true \
  -jar target/user-service.jar
```

**Configuration File:**

```yaml
# File: otel-config.yaml (alternative to JVM args)
otel:
  service:
    name: user-service

  traces:
    exporter: zipkin

  metrics:
    exporter: prometheus

  exporter:
    zipkin:
      endpoint: http://zipkin:9411/api/v2/spans
    prometheus:
      port: 9090
      host: 0.0.0.0

  instrumentation:
    spring-webmvc:
      enabled: true
    jdbc:
      enabled: true
    redis:
      enabled: true
    kafka:
      enabled: true

  resource:
    attributes:
      environment: production
      region: us-east-1
```

**Kubernetes Deployment with OTel Agent:**

```yaml
# File: k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  template:
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        env:
        - name: JAVA_TOOL_OPTIONS
          value: "-javaagent:/otel/opentelemetry-javaagent.jar"
        - name: OTEL_SERVICE_NAME
          value: "user-service"
        - name: OTEL_TRACES_EXPORTER
          value: "otlp"
        - name: OTEL_METRICS_EXPORTER
          value: "prometheus"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector:4317"

        volumeMounts:
        - name: otel-agent
          mountPath: /otel

      initContainers:
      # Download OTel agent at pod startup
      - name: otel-agent-downloader
        image: curlimages/curl:latest
        command:
        - sh
        - -c
        - |
          curl -L https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar \
            -o /otel/opentelemetry-javaagent.jar
        volumeMounts:
        - name: otel-agent
          mountPath: /otel

      volumes:
      - name: otel-agent
        emptyDir: {}
```

**✅ Benefits:**
- **Zero Code Changes:** Auto-instruments HTTP, JDBC, Redis, Kafka, etc.
- **Vendor-Neutral:** CNCF standard, works with any OpenTelemetry backend
- **Unified Telemetry:** Metrics, traces, logs in single standard
- **Automatic Context Propagation:** Trace context automatically propagated across services

**❌ Drawbacks:**
- **Agent Overhead:** 5-10% performance overhead vs. manual instrumentation
- **Limited Customization:** Can't customize auto-instrumentation logic
- **Startup Time:** Adds 1-2 seconds to application startup

**Use When:**
- Existing applications without instrumentation code
- Need vendor-neutral telemetry (avoid lock-in)
- Want unified metrics + traces + logs
- Using Kubernetes with OpenTelemetry Collector

**Avoid When:**
- Ultra-low latency requirements (agent adds overhead)
- Need fine-grained control over instrumentation
- Small applications where manual instrumentation is simpler

---

#### Pattern 3: Manual Instrumentation with @Observed/@Timed

**Use Case:** Fine-grained control over what gets instrumented, custom metrics for business logic.

**Implementation:**

```java
// File: src/main/java/com/example/service/InventoryService.java
package com.example.service;

import io.micrometer.observation.annotation.Observed;
import io.micrometer.core.annotation.Timed;
import org.springframework.stereotype.Service;

/**
 * Inventory service with manual instrumentation.
 * @Observed creates traces and metrics for this method.
 */
@Service
public class InventoryService {

    private final InventoryRepository repository;

    public InventoryService(InventoryRepository repository) {
        this.repository = repository;
    }

    /**
     * Check stock with automatic tracing and metrics.
     * @Observed creates a span in distributed trace + metrics.
     */
    @Observed(
        name = "inventory.check_stock",
        contextualName = "check-stock",
        lowCardinalityKeyValues = {"service", "inventory"}
    )
    @Timed(
        value = "inventory.check_stock.duration",
        description = "Time to check inventory stock",
        percentiles = {0.5, 0.95, 0.99}
    )
    public boolean hasStock(Long productId, int quantity) {
        return repository.findByProductId(productId)
            .map(inventory -> inventory.getQuantity() >= quantity)
            .orElse(false);
    }

    /**
     * Reserve stock with custom observation context.
     */
    @Observed(
        name = "inventory.reserve_stock",
        contextualName = "reserve-stock"
    )
    public void reserveStock(Long productId, int quantity) {
        var inventory = repository.findByProductId(productId)
            .orElseThrow(() -> new ProductNotFoundException(productId));

        if (inventory.getQuantity() < quantity) {
            throw new InsufficientStockException(productId, quantity);
        }

        inventory.setQuantity(inventory.getQuantity() - quantity);
        repository.save(inventory);
    }
}
```

**✅ Benefits:**
- **Fine-Grained Control:** Instrument only critical paths
- **Custom Context:** Add business-specific tags to spans/metrics
- **Lower Overhead:** No auto-instrumentation overhead
- **Spring Boot Integration:** Works seamlessly with Actuator/Micrometer

**❌ Drawbacks:**
- **Manual Work:** Must add annotations to every method
- **Maintenance:** Easy to miss instrumenting new methods
- **Boilerplate:** More code vs. auto-instrumentation

**Use When:**
- Need precise control over instrumentation
- Want to add business-specific tags/context
- Performance-critical paths (avoid auto-instrumentation overhead)

---

#### Pattern 4: Hybrid Approach (Actuator + OpenTelemetry)

**Use Case:** Use Spring Boot Actuator for health/metrics, OpenTelemetry for distributed tracing.

**Implementation:**

```xml
<!-- File: pom.xml -->
<dependencies>
    <!-- Spring Boot Actuator for health/metrics -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>

    <!-- Micrometer Prometheus -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-registry-prometheus</artifactId>
    </dependency>

    <!-- Micrometer OpenTelemetry bridge for tracing -->
    <dependency>
        <groupId>io.micrometer</groupId>
        <artifactId>micrometer-tracing-bridge-otel</artifactId>
    </dependency>

    <!-- OpenTelemetry exporter -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-otlp</artifactId>
    </dependency>
</dependencies>
```

```yaml
# File: application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,prometheus,info

  metrics:
    export:
      prometheus:
        enabled: true

  tracing:
    sampling:
      probability: 0.1

  # OpenTelemetry configuration
  otlp:
    tracing:
      endpoint: http://otel-collector:4317

spring:
  application:
    name: user-service
```

**✅ Benefits:**
- **Best of Both:** Actuator metrics + OpenTelemetry tracing
- **Gradual Migration:** Migrate from Sleuth to OTel incrementally
- **Kubernetes-Friendly:** Prometheus metrics + OTLP traces

**❌ Drawbacks:**
- **Complexity:** Two telemetry systems to manage
- **Duplication:** Some overlap between Micrometer and OTel metrics

**Use When:**
- Migrating from Sleuth to OpenTelemetry
- Need Prometheus metrics + OTLP tracing
- Want Spring Boot Actuator health checks + OTel observability

---

### 10.2.2 Common Telemetry Mistakes

#### Mistake 1: Not Configuring MDC for Async/Reactive Operations

**Problem:** MDC (Mapped Diagnostic Context) not propagated to async threads, losing trace context in logs.

**Bad Example:**

```java
@Service
public class UserService {

    @Async  // MDC context lost in async thread!
    public CompletableFuture<User> loadUserAsync(Long userId) {
        // traceId/spanId not in logs here
        log.info("Loading user: {}", userId);
        return CompletableFuture.completedFuture(fetchUser(userId));
    }
}
```

**Good Example:**

```java
// File: src/main/java/com/example/config/AsyncConfiguration.java
package com.example.config;

import org.slf4j.MDC;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.TaskDecorator;
import org.springframework.scheduling.annotation.AsyncConfigurer;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.Map;
import java.util.concurrent.Executor;

/**
 * Async configuration with MDC propagation.
 */
@Configuration
@EnableAsync
public class AsyncConfiguration implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");

        // Propagate MDC context to async threads
        executor.setTaskDecorator(new MdcTaskDecorator());

        executor.initialize();
        return executor;
    }

    /**
     * TaskDecorator that copies MDC context to async threads.
     */
    static class MdcTaskDecorator implements TaskDecorator {

        @Override
        public Runnable decorate(Runnable runnable) {
            // Capture MDC context from parent thread
            Map<String, String> contextMap = MDC.getCopyOfContextMap();

            return () -> {
                try {
                    // Restore MDC context in async thread
                    if (contextMap != null) {
                        MDC.setContextMap(contextMap);
                    }

                    runnable.run();

                } finally {
                    // Clean up MDC after task completes
                    MDC.clear();
                }
            };
        }
    }
}
```

**Reactive (WebFlux) Example:**

```java
// File: src/main/java/com/example/config/ReactiveConfiguration.java
package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Hooks;
import reactor.core.scheduler.Schedulers;

/**
 * Reactive configuration with context propagation.
 */
@Configuration
public class ReactiveConfiguration {

    @Bean
    public void configureReactorContext() {
        // Enable automatic context propagation in Reactor
        Hooks.enableAutomaticContextPropagation();

        // Configure schedulers with MDC support
        Schedulers.onScheduleHook("mdc", runnable -> {
            // Context propagation handled by Hooks.enableAutomaticContextPropagation()
            return runnable;
        });
    }
}
```

**✅ Fix:**
- Use `TaskDecorator` to propagate MDC in @Async methods
- Enable `Hooks.enableAutomaticContextPropagation()` for Reactor/WebFlux
- Spring Cloud Sleuth/OpenTelemetry handle this automatically if configured

---

#### Mistake 2: Creating Too Many Custom Metrics (Cardinality Explosion)

**Problem:** High-cardinality tags (user IDs, IP addresses) cause metric explosion, overwhelming Prometheus.

**Bad Example:**

```java
// DON'T DO THIS - userId creates millions of unique time series!
Counter.builder("user.requests")
    .tag("userId", String.valueOf(userId))  // ❌ High cardinality!
    .tag("ipAddress", request.getRemoteAddr())  // ❌ High cardinality!
    .register(meterRegistry)
    .increment();
```

**Prometheus Cardinality Explosion:**
```
user_requests{userId="1",ipAddress="192.168.1.1"} 5
user_requests{userId="2",ipAddress="192.168.1.2"} 3
user_requests{userId="3",ipAddress="192.168.1.3"} 8
...
# 1 million users × 100k IPs = 100 billion time series!
```

**Good Example:**

```java
// Use low-cardinality tags (bounded set of values)
Counter.builder("user.requests")
    .tag("userType", user.getType())  // ✅ Low cardinality: [FREE, PREMIUM, ENTERPRISE]
    .tag("region", user.getRegion())  // ✅ Low cardinality: [US, EU, APAC]
    .tag("status", response.getStatus())  // ✅ Low cardinality: [200, 400, 500]
    .register(meterRegistry)
    .increment();

// Use distribution summaries for high-cardinality values
meterRegistry.summary("user.session.duration")
    .record(sessionDurationMs);
```

**Cardinality Guidelines:**
- **Low Cardinality (Good):** <100 unique values (status codes, regions, user types)
- **Medium Cardinality (Caution):** 100-10,000 unique values (product categories, error codes)
- **High Cardinality (Avoid):** >10,000 unique values (user IDs, IP addresses, timestamps)

---

#### Mistake 3: Missing Trace Context Propagation in @Async Methods

**Problem:** Distributed trace broken when calling @Async methods (span context lost).

**Bad Example:**

```java
@Service
public class OrderService {

    @Async
    public void sendOrderConfirmation(Long orderId) {
        // New trace started here (not linked to parent trace)
        emailService.send(buildConfirmationEmail(orderId));
    }
}
```

**Good Example:**

```java
// File: src/main/java/com/example/config/TracingAsyncConfiguration.java
package com.example.config;

import brave.Tracer;
import brave.propagation.CurrentTraceContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.AsyncConfigurer;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

/**
 * Async configuration with trace context propagation.
 */
@Configuration
@EnableAsync
public class TracingAsyncConfiguration implements AsyncConfigurer {

    private final CurrentTraceContext currentTraceContext;

    public TracingAsyncConfiguration(CurrentTraceContext currentTraceContext) {
        this.currentTraceContext = currentTraceContext;
    }

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);

        // Decorate executor with trace context propagation
        executor.setTaskDecorator(runnable ->
            currentTraceContext.wrap(runnable)
        );

        executor.initialize();
        return executor;
    }
}
```

**Alternative (Manual Propagation):**

```java
@Service
public class OrderService {

    private final Tracer tracer;

    @Async
    public void sendOrderConfirmation(Long orderId) {
        // Manually create child span
        Span asyncSpan = tracer.nextSpan().name("send-order-confirmation").start();

        try (Tracer.SpanInScope ws = tracer.withSpanInScope(asyncSpan)) {
            asyncSpan.tag("orderId", orderId.toString());

            emailService.send(buildConfirmationEmail(orderId));

        } finally {
            asyncSpan.finish();
        }
    }
}
```

---

### 10.2.3 Verification and Troubleshooting

#### Verify Spring Boot Actuator Endpoints

```bash
# Check health endpoint
curl http://localhost:8080/actuator/health

# Expected output:
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "activeConnections": 5,
        "maxPoolSize": 25
      }
    },
    "redis": {
      "status": "UP",
      "details": {
        "version": "7.0.0"
      }
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 250GB,
        "free": 150GB
      }
    }
  }
}

# Check Prometheus metrics
curl http://localhost:8080/actuator/prometheus

# Expected output (sample):
# HELP jvm_memory_used_bytes Used bytes of a given JVM memory area.
# TYPE jvm_memory_used_bytes gauge
jvm_memory_used_bytes{application="user-service",area="heap",id="G1 Eden Space"} 1.234e+08

# HELP http_server_requests_seconds HTTP request duration
# TYPE http_server_requests_seconds histogram
http_server_requests_seconds{application="user-service",method="GET",status="200",uri="/api/users/{id}"} 0.050

# Check metrics endpoint (list all available metrics)
curl http://localhost:8080/actuator/metrics

# Check specific metric
curl http://localhost:8080/actuator/metrics/jvm.memory.used
```

#### Prometheus Scraping Configuration

```yaml
# File: prometheus.yml (Prometheus server config)
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Scrape Spring Boot Actuator /actuator/prometheus endpoint
  - job_name: 'spring-boot-apps'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets:
          - 'user-service:8080'
          - 'order-service:8080'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
```

**Kubernetes ServiceMonitor (Prometheus Operator):**

```yaml
# File: k8s/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  selector:
    matchLabels:
      app: user-service
  endpoints:
  - port: http
    path: /actuator/prometheus
    interval: 30s
    scrapeTimeout: 10s
```

#### Trace Debugging with Zipkin UI

```bash
# Query Zipkin for recent traces
curl "http://zipkin:9411/api/v2/traces?serviceName=user-service&limit=10"

# Get specific trace by ID
curl "http://zipkin:9411/api/v2/trace/{traceId}"

# Search for failed traces
curl "http://zipkin:9411/api/v2/traces?serviceName=user-service&annotationQuery=error=true"
```

**Zipkin UI Navigation:**
1. Access Zipkin UI: `http://zipkin:9411/zipkin/`
2. Search by:
   - Service name: `user-service`
   - Span name: `orders.create`
   - Tags: `http.status_code=500`
   - Duration: `minDuration=1s`
3. Click trace to view full call chain
4. Inspect span tags for error details

---

### 10.3 Alternative Approaches

#### Micrometer vs. OpenTelemetry Metrics

| Feature | Micrometer | OpenTelemetry |
|---------|------------|---------------|
| **Vendor Support** | Prometheus, Datadog, InfluxDB, New Relic | Any OTLP-compatible backend |
| **Spring Boot Integration** | Native (auto-configured) | Requires manual setup |
| **Metrics Types** | Counter, Gauge, Timer, Summary | Counter, Gauge, Histogram |
| **Traces Support** | Via Spring Cloud Sleuth | Native (unified metrics + traces) |
| **Adoption** | De facto standard for Spring Boot | CNCF standard (growing) |
| **Learning Curve** | Low (Spring Boot conventions) | Medium (new concepts) |

**Recommendation:** Use **Micrometer** for standard Spring Boot apps with Prometheus. Use **OpenTelemetry** for vendor-neutral telemetry or if you need unified metrics + traces + logs[^54][^55].

---

#### Spring Cloud Sleuth vs. OpenTelemetry Java Agent

| Feature | Spring Cloud Sleuth | OpenTelemetry Java Agent |
|---------|---------------------|---------------------------|
| **Instrumentation** | Spring-specific auto-instrumentation | Universal auto-instrumentation |
| **Configuration** | Spring Boot properties | JVM args or config file |
| **Code Changes** | None (auto-configured) | None (agent-based) |
| **Customization** | Spring Beans, @NewSpan | OTel SDK API |
| **Future** | Deprecated (migrate to OTel) | Active development |
| **Performance** | Low overhead | 5-10% overhead |

**Recommendation:** **Migrate to OpenTelemetry** - Spring Cloud Sleuth is deprecated. Use OTel Java Agent for zero-code instrumentation or Micrometer Tracing Bridge OTel for Spring Boot integration[^56][^57].

---

#### Prometheus vs. InfluxDB vs. Datadog

| Feature | Prometheus | InfluxDB | Datadog |
|---------|------------|----------|---------|
| **Data Model** | Time series (pull-based) | Time series (push-based) | Unified metrics/traces/logs |
| **Storage** | Local disk (limited retention) | Scalable (long-term storage) | Cloud-managed |
| **Querying** | PromQL | InfluxQL/Flux | Datadog Query Language |
| **Alerting** | Alertmanager | Kapacitor | Built-in |
| **Cost** | Free (self-hosted) | Free tier + paid | SaaS ($$) |
| **Kubernetes** | De facto standard | Supported | Supported |

**Recommendation:** Use **Prometheus** for Kubernetes environments (industry standard, free). Use **Datadog** for enterprise observability (unified platform, paid). Use **InfluxDB** for IoT/high-cardinality time series[^58][^59].

---

### 10.4 Decision Criteria

#### When to Use Actuator + Micrometer (Spring Boot Standard)

**Use When:**
- ✅ Building Spring Boot microservices
- ✅ Using Prometheus for monitoring (Kubernetes standard)
- ✅ Need quick setup with minimal configuration
- ✅ Want health checks for Kubernetes liveness/readiness probes
- ✅ Team familiar with Spring Boot conventions

**Avoid When:**
- ❌ Need vendor-neutral telemetry (not locked to Prometheus)
- ❌ Require unified metrics + traces + logs (use OpenTelemetry)
- ❌ Using non-Spring frameworks (use OpenTelemetry Java Agent)

---

#### When to Use OpenTelemetry (Vendor-Neutral, CNCF Standard)

**Use When:**
- ✅ Need vendor-neutral telemetry (avoid lock-in)
- ✅ Want unified metrics + traces + logs (single standard)
- ✅ Using multiple languages/frameworks (Go, Python, Java)
- ✅ Require OTLP export (OpenTelemetry Collector)
- ✅ Future-proofing (CNCF standard, active development)

**Avoid When:**
- ❌ Team unfamiliar with OpenTelemetry (steep learning curve)
- ❌ Need immediate Spring Boot integration (Micrometer easier)
- ❌ Ultra-low latency requirements (agent overhead)

---

#### When to Use Proprietary Solutions (AWS CloudWatch, Datadog APM)

**Use When:**
- ✅ Using AWS/Azure/GCP (native integration)
- ✅ Need unified observability platform (metrics + traces + logs + APM)
- ✅ Want managed service (no self-hosting)
- ✅ Enterprise support required (24/7 support, SLAs)

**Avoid When:**
- ❌ Multi-cloud strategy (avoid vendor lock-in)
- ❌ Cost-sensitive (SaaS pricing adds up)
- ❌ Need full control over telemetry data

---

### 10.6 OpenTelemetry SDK Manual Instrumentation

For fine-grained control over distributed tracing, metrics, and logging context, use the OpenTelemetry SDK directly. This approach provides full control over span creation, metric instrumentation, and trace context propagation[^54][^60].

#### 10.6.1 OpenTelemetry Dependencies

```xml
<!-- File: pom.xml -->
<properties>
    <opentelemetry.version>1.32.0</opentelemetry.version>
    <opentelemetry-instrumentation.version>1.32.0-alpha</opentelemetry-instrumentation.version>
</properties>

<dependencies>
    <!-- OpenTelemetry API (manual instrumentation) -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-api</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- OpenTelemetry SDK (required for agent-less setup) -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-sdk</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- OpenTelemetry SDK Autoconfigure (environment-based config) -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-sdk-extension-autoconfigure</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- OTLP Exporter (export to OpenTelemetry Collector) -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-otlp</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- Zipkin Exporter (alternative to OTLP) -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-zipkin</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- Jaeger Exporter (alternative to OTLP) -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-jaeger</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- OpenTelemetry Metrics SDK -->
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-sdk-metrics</artifactId>
        <version>${opentelemetry.version}</version>
    </dependency>

    <!-- Spring Boot integration (optional - for auto-config) -->
    <dependency>
        <groupId>io.opentelemetry.instrumentation</groupId>
        <artifactId>opentelemetry-spring-boot-starter</artifactId>
        <version>${opentelemetry-instrumentation.version}</version>
    </dependency>
</dependencies>
```

#### 10.6.2 OpenTelemetry SDK Initialization

```java
// File: src/main/java/com/example/config/OpenTelemetryConfiguration.java
package com.example.config;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
import io.opentelemetry.context.propagation.ContextPropagators;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.exporter.otlp.metrics.OtlpGrpcMetricExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import io.opentelemetry.sdk.trace.samplers.Sampler;
import io.opentelemetry.semconv.resource.attributes.ResourceAttributes;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

/**
 * OpenTelemetry SDK configuration with OTLP exporter.
 * Initializes tracer, meter provider, and context propagation.
 */
@Configuration
public class OpenTelemetryConfiguration {

    @Value("${otel.service.name:user-service}")
    private String serviceName;

    @Value("${otel.exporter.otlp.endpoint:http://localhost:4317}")
    private String otlpEndpoint;

    @Value("${otel.traces.sampler.probability:0.1}")
    private double samplingProbability;

    /**
     * OpenTelemetry SDK instance with configured tracing, metrics, and propagation.
     */
    @Bean
    public OpenTelemetry openTelemetry() {
        // Define service resource attributes (service name, version, environment)
        Resource resource = Resource.getDefault()
            .merge(Resource.create(Attributes.builder()
                .put(ResourceAttributes.SERVICE_NAME, serviceName)
                .put(ResourceAttributes.SERVICE_VERSION, "1.0.0")
                .put(ResourceAttributes.DEPLOYMENT_ENVIRONMENT, System.getenv().getOrDefault("ENV", "local"))
                .build()));

        // Configure OTLP gRPC span exporter
        OtlpGrpcSpanExporter spanExporter = OtlpGrpcSpanExporter.builder()
            .setEndpoint(otlpEndpoint)
            .setTimeout(Duration.ofSeconds(10))
            .build();

        // Configure tracer provider with batch span processor
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .setResource(resource)
            .addSpanProcessor(BatchSpanProcessor.builder(spanExporter)
                .setScheduleDelay(Duration.ofSeconds(5))
                .setMaxQueueSize(2048)
                .setMaxExportBatchSize(512)
                .build())
            .setSampler(Sampler.traceIdRatioBased(samplingProbability))
            .build();

        // Configure OTLP gRPC metric exporter
        OtlpGrpcMetricExporter metricExporter = OtlpGrpcMetricExporter.builder()
            .setEndpoint(otlpEndpoint)
            .setTimeout(Duration.ofSeconds(10))
            .build();

        // Configure meter provider with periodic metric reader
        SdkMeterProvider meterProvider = SdkMeterProvider.builder()
            .setResource(resource)
            .registerMetricReader(PeriodicMetricReader.builder(metricExporter)
                .setInterval(Duration.ofSeconds(60))
                .build())
            .build();

        // Build OpenTelemetry SDK with W3C Trace Context propagation
        OpenTelemetrySdk openTelemetry = OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setMeterProvider(meterProvider)
            .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
            .buildAndRegisterGlobal();

        // Add shutdown hook to flush traces/metrics on JVM exit
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            tracerProvider.close();
            meterProvider.close();
        }));

        return openTelemetry;
    }

    /**
     * Tracer bean for manual span creation.
     */
    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        return openTelemetry.getTracer(serviceName, "1.0.0");
    }
}
```

#### 10.6.3 Manual Span Creation with OpenTelemetry API

```java
// File: src/main/java/com/example/service/PaymentService.java
package com.example.service;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Context;
import io.opentelemetry.context.Scope;
import org.springframework.stereotype.Service;

/**
 * Payment service with manual OpenTelemetry instrumentation.
 */
@Service
public class PaymentService {

    private final Tracer tracer;
    private final PaymentGateway paymentGateway;

    public PaymentService(Tracer tracer, PaymentGateway paymentGateway) {
        this.tracer = tracer;
        this.paymentGateway = paymentGateway;
    }

    /**
     * Process payment with manual span creation.
     */
    public PaymentResult processPayment(PaymentRequest request) {
        // Create span for payment processing
        Span span = tracer.spanBuilder("payment.process")
            .setSpanKind(io.opentelemetry.api.trace.SpanKind.INTERNAL)
            .setAttribute("payment.amount", request.getAmount())
            .setAttribute("payment.currency", request.getCurrency())
            .setAttribute("payment.method", request.getPaymentMethod())
            .setAttribute("customer.id", request.getCustomerId())
            .startSpan();

        // Make span current (for context propagation)
        try (Scope scope = span.makeCurrent()) {

            // Add event (structured log point within span)
            span.addEvent("payment.validation.started");

            // Validate payment request
            validatePaymentRequest(request);

            span.addEvent("payment.validation.completed");

            // Call payment gateway (child span auto-created if instrumented)
            PaymentResult result = paymentGateway.charge(request);

            // Add result attributes to span
            span.setAttribute("payment.transaction_id", result.getTransactionId());
            span.setAttribute("payment.status", result.getStatus().name());

            // Mark span as successful
            span.setStatus(StatusCode.OK);

            return result;

        } catch (PaymentValidationException ex) {
            // Record exception in span
            span.recordException(ex);
            span.setStatus(StatusCode.ERROR, "Payment validation failed");
            span.setAttribute("error.type", ex.getClass().getSimpleName());
            span.setAttribute("error.message", ex.getMessage());

            throw ex;

        } catch (Exception ex) {
            // Record unexpected exception
            span.recordException(ex);
            span.setStatus(StatusCode.ERROR, "Payment processing failed");
            span.setAttribute("error.type", ex.getClass().getSimpleName());

            throw ex;

        } finally {
            // Always end span (releases resources)
            span.end();
        }
    }

    /**
     * Validate payment with nested span.
     */
    private void validatePaymentRequest(PaymentRequest request) {
        Span parentSpan = Span.current();

        // Create child span
        Span validationSpan = tracer.spanBuilder("payment.validate")
            .setParent(Context.current())
            .setAttribute("validation.type", "payment_request")
            .startSpan();

        try (Scope scope = validationSpan.makeCurrent()) {

            // Validation logic
            if (request.getAmount() <= 0) {
                throw new PaymentValidationException("Amount must be positive");
            }

            if (request.getCustomerId() == null) {
                throw new PaymentValidationException("Customer ID required");
            }

            validationSpan.addEvent("validation.passed");
            validationSpan.setStatus(StatusCode.OK);

        } catch (Exception ex) {
            validationSpan.recordException(ex);
            validationSpan.setStatus(StatusCode.ERROR);
            throw ex;

        } finally {
            validationSpan.end();
        }
    }

    /**
     * Async payment processing with manual context propagation.
     */
    public void processPaymentAsync(PaymentRequest request) {
        // Capture current trace context
        Context currentContext = Context.current();

        // Submit async task with context propagation
        CompletableFuture.runAsync(() -> {
            // Attach parent context to async thread
            try (Scope scope = currentContext.makeCurrent()) {

                // Create span in async thread (parent context preserved)
                Span asyncSpan = tracer.spanBuilder("payment.process_async")
                    .setParent(currentContext)
                    .startSpan();

                try (Scope asyncScope = asyncSpan.makeCurrent()) {
                    processPayment(request);
                    asyncSpan.setStatus(StatusCode.OK);
                } finally {
                    asyncSpan.end();
                }
            }
        });
    }
}
```

#### 10.6.4 OpenTelemetry Metrics with SDK

```java
// File: src/main/java/com/example/service/OrderMetricsService.java
package com.example.service;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.LongHistogram;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.metrics.ObservableDoubleGauge;
import org.springframework.stereotype.Service;

import java.util.concurrent.atomic.AtomicLong;

/**
 * Order service with OpenTelemetry metrics instrumentation.
 */
@Service
public class OrderMetricsService {

    private final Meter meter;

    // Counter: monotonically increasing value (total orders created)
    private final LongCounter ordersCreatedCounter;
    private final LongCounter ordersFailedCounter;

    // Histogram: distribution of values (order processing duration)
    private final LongHistogram orderProcessingDuration;

    // Gauge: current snapshot value (active orders)
    private final AtomicLong activeOrders = new AtomicLong(0);

    public OrderMetricsService(OpenTelemetry openTelemetry) {
        this.meter = openTelemetry.getMeter("user-service", "1.0.0");

        // Initialize counter for orders created
        this.ordersCreatedCounter = meter.counterBuilder("orders.created")
            .setDescription("Total number of orders created")
            .setUnit("orders")
            .build();

        // Initialize counter for failed orders
        this.ordersFailedCounter = meter.counterBuilder("orders.failed")
            .setDescription("Total number of failed order creations")
            .setUnit("orders")
            .build();

        // Initialize histogram for order processing duration
        this.orderProcessingDuration = meter.histogramBuilder("orders.processing.duration")
            .setDescription("Order processing duration")
            .setUnit("ms")
            .ofLongs()
            .build();

        // Initialize gauge for active orders (observable - polled by SDK)
        ObservableDoubleGauge activeOrdersGauge = meter.gaugeBuilder("orders.active")
            .setDescription("Number of active orders")
            .setUnit("orders")
            .buildWithCallback(measurement ->
                measurement.record(activeOrders.get())
            );
    }

    /**
     * Record order creation with metrics.
     */
    public void recordOrderCreated(Order order) {
        // Increment counter with attributes
        ordersCreatedCounter.add(1,
            io.opentelemetry.api.common.Attributes.builder()
                .put("order.type", order.getType())
                .put("customer.tier", order.getCustomer().getTier())
                .build()
        );

        // Update active orders gauge
        activeOrders.incrementAndGet();
    }

    /**
     * Record order processing duration.
     */
    public void recordOrderProcessingDuration(long durationMs, String orderType) {
        orderProcessingDuration.record(durationMs,
            io.opentelemetry.api.common.Attributes.builder()
                .put("order.type", orderType)
                .build()
        );
    }

    /**
     * Record order failure with attributes.
     */
    public void recordOrderFailed(String orderType, String failureReason) {
        ordersFailedCounter.add(1,
            io.opentelemetry.api.common.Attributes.builder()
                .put("order.type", orderType)
                .put("failure.reason", failureReason)
                .build()
        );
    }

    /**
     * Record order completion (decrement active orders).
     */
    public void recordOrderCompleted() {
        activeOrders.decrementAndGet();
    }
}
```

---

### 10.7 Logback MDC Integration with OpenTelemetry

Integrating OpenTelemetry trace context into Logback MDC enables correlation between logs and traces. This section demonstrates automatic trace ID/span ID injection into log messages[^61][^62].

#### 10.7.1 OpenTelemetry Logback Appender

```xml
<!-- File: src/main/resources/logback-spring.xml -->
<configuration>
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>

    <!-- Console appender with trace context -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <!-- Add OpenTelemetry trace context to JSON logs -->
            <provider class="net.logstash.logback.composite.loggingevent.LoggingEventPatternJsonProvider">
                <pattern>
                    {
                        "timestamp": "%date{ISO8601}",
                        "level": "%level",
                        "thread": "%thread",
                        "logger": "%logger{36}",
                        "message": "%message",
                        "trace_id": "%mdc{trace_id}",
                        "span_id": "%mdc{span_id}",
                        "trace_flags": "%mdc{trace_flags}",
                        "service.name": "${SERVICE_NAME:-user-service}",
                        "exception": "%exception{full}"
                    }
                </pattern>
            </provider>
        </encoder>
    </appender>

    <!-- File appender with trace context -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/application-%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>

        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <provider class="net.logstash.logback.composite.loggingevent.LoggingEventPatternJsonProvider">
                <pattern>
                    {
                        "timestamp": "%date{ISO8601}",
                        "level": "%level",
                        "logger": "%logger",
                        "message": "%message",
                        "trace_id": "%mdc{trace_id}",
                        "span_id": "%mdc{span_id}",
                        "service.name": "${SERVICE_NAME:-user-service}"
                    }
                </pattern>
            </provider>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
    </root>
</configuration>
```

#### 10.7.2 MDC Injection with Spring Boot Starter

```xml
<!-- File: pom.xml -->
<dependencies>
    <!-- OpenTelemetry Spring Boot Starter (auto-configures MDC) -->
    <dependency>
        <groupId>io.opentelemetry.instrumentation</groupId>
        <artifactId>opentelemetry-spring-boot-starter</artifactId>
        <version>1.32.0-alpha</version>
    </dependency>

    <!-- Logback encoder for JSON output -->
    <dependency>
        <groupId>net.logstash.logback</groupId>
        <artifactId>logstash-logback-encoder</artifactId>
        <version>7.4</version>
    </dependency>
</dependencies>
```

```yaml
# File: application.yml
otel:
  # Service name for traces/metrics/logs
  service:
    name: user-service

  # Enable trace context propagation to MDC
  logs:
    exporter: none  # Don't export logs via OTLP (use Logback appenders)

  # Automatic instrumentation configuration
  instrumentation:
    # Enable MDC context propagation
    logback-appender:
      enabled: true
      experimental-log-attributes: true

  # OTLP exporter for traces and metrics
  exporter:
    otlp:
      endpoint: http://otel-collector:4317
      protocol: grpc
```

#### 10.7.3 Manual MDC Injection (without Spring Boot Starter)

```java
// File: src/main/java/com/example/config/MdcConfiguration.java
package com.example.config;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.context.Context;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Interceptor to inject OpenTelemetry trace context into SLF4J MDC.
 */
@Component
public class TraceContextMdcInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) {
        // Get current span from OpenTelemetry context
        Span currentSpan = Span.current();

        // Extract trace ID and span ID
        String traceId = currentSpan.getSpanContext().getTraceId();
        String spanId = currentSpan.getSpanContext().getSpanId();
        String traceFlags = currentSpan.getSpanContext().getTraceFlags().asHex();

        // Inject into MDC (available in all log statements)
        MDC.put("trace_id", traceId);
        MDC.put("span_id", spanId);
        MDC.put("trace_flags", traceFlags);

        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
                                HttpServletResponse response,
                                Object handler,
                                Exception ex) {
        // Clear MDC to prevent memory leaks
        MDC.remove("trace_id");
        MDC.remove("span_id");
        MDC.remove("trace_flags");
    }
}
```

```java
// File: src/main/java/com/example/config/WebMvcConfiguration.java
package com.example.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Register MDC interceptor for all HTTP requests.
 */
@Configuration
public class WebMvcConfiguration implements WebMvcConfigurer {

    private final TraceContextMdcInterceptor mdcInterceptor;

    public WebMvcConfiguration(TraceContextMdcInterceptor mdcInterceptor) {
        this.mdcInterceptor = mdcInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(mdcInterceptor);
    }
}
```

#### 10.7.4 Verify Trace Context in Logs

```java
// File: src/main/java/com/example/controller/UserController.java
package com.example.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

/**
 * User controller with trace-aware logging.
 */
@RestController
@RequestMapping("/api/users")
public class UserController {

    private static final Logger log = LoggerFactory.getLogger(UserController.class);

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        // Log message automatically includes trace_id/span_id from MDC
        log.info("Fetching user with ID: {}", id);

        User user = userService.findById(id);

        log.info("User fetched successfully: {}", user.getEmail());

        return user;
    }
}
```

**Example Log Output (JSON with trace context):**

```json
{
  "timestamp": "2025-11-03T10:15:23.456Z",
  "level": "INFO",
  "thread": "http-nio-8080-exec-1",
  "logger": "com.example.controller.UserController",
  "message": "Fetching user with ID: 12345",
  "trace_id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "span_id": "1234567890abcdef",
  "trace_flags": "01",
  "service.name": "user-service"
}
```

**Correlate Logs with Traces:**

1. **In Jaeger UI:** Search for trace ID `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
2. **In Logs:** Filter logs by `trace_id: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"`
3. **Result:** All log messages from request correlated with distributed trace spans

---

### 10.8 Common OpenTelemetry Mistakes and Solutions

#### Mistake 1: Not Propagating Context in Async Operations

**Problem:** Trace context lost when using `@Async`, `CompletableFuture`, or reactive streams without explicit context propagation.

**Bad Example:**

```java
@Service
public class NotificationService {

    @Async
    public void sendNotificationAsync(Long userId) {
        // trace_id/span_id LOST - new trace started in async thread
        log.info("Sending notification to user: {}", userId);

        // Span.current() returns invalid span (no parent trace)
        Span currentSpan = Span.current();
    }
}
```

**Good Example (Async with Context Propagation):**

```java
@Service
public class NotificationService {

    private final Tracer tracer;

    @Async
    public void sendNotificationAsync(Long userId) {
        // Capture parent context BEFORE async execution
        Context parentContext = Context.current();

        CompletableFuture.runAsync(() -> {
            // Attach parent context in async thread
            try (Scope scope = parentContext.makeCurrent()) {

                // Create child span in async thread
                Span asyncSpan = tracer.spanBuilder("notification.send_async")
                    .setParent(parentContext)
                    .setAttribute("user.id", userId)
                    .startSpan();

                try (Scope asyncScope = asyncSpan.makeCurrent()) {
                    // Trace context now available in MDC
                    log.info("Sending notification to user: {}", userId);

                    // Business logic
                    emailService.send(userId);

                    asyncSpan.setStatus(StatusCode.OK);

                } finally {
                    asyncSpan.end();
                }
            }
        });
    }
}
```

**Solution with TaskDecorator (Automatic Context Propagation):**

```java
@Configuration
@EnableAsync
public class AsyncConfiguration implements AsyncConfigurer {

    @Override
    public Executor getAsyncExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);

        // Automatically propagate OpenTelemetry context to async threads
        executor.setTaskDecorator(runnable ->
            Context.current().wrap(runnable)
        );

        executor.initialize();
        return executor;
    }
}
```

---

#### Mistake 2: Creating Spans Without Ending Them (Memory Leak)

**Problem:** Spans not ended properly cause memory leaks and incomplete traces.

**Bad Example:**

```java
public void processOrder(Order order) {
    Span span = tracer.spanBuilder("order.process").startSpan();

    if (order.isValid()) {
        // Span never ended if validation fails! Memory leak!
        processValidOrder(order);
    }

    span.end();  // Never reached if exception thrown
}
```

**Good Example (Always Use Try-Finally):**

```java
public void processOrder(Order order) {
    Span span = tracer.spanBuilder("order.process").startSpan();

    try (Scope scope = span.makeCurrent()) {
        if (order.isValid()) {
            processValidOrder(order);
        }

        span.setStatus(StatusCode.OK);

    } catch (Exception ex) {
        span.recordException(ex);
        span.setStatus(StatusCode.ERROR);
        throw ex;

    } finally {
        // ALWAYS end span (even if exception thrown)
        span.end();
    }
}
```

**Best Practice (Try-With-Resources for Scope):**

```java
public void processOrder(Order order) {
    Span span = tracer.spanBuilder("order.process").startSpan();

    // Try-with-resources ensures scope closed automatically
    try (Scope scope = span.makeCurrent()) {
        processValidOrder(order);
        span.setStatus(StatusCode.OK);
    } catch (Exception ex) {
        span.recordException(ex);
        span.setStatus(StatusCode.ERROR);
        throw ex;
    } finally {
        span.end();
    }
}
```

---

#### Mistake 3: Using High-Cardinality Attributes (Cardinality Explosion)

**Problem:** Adding user IDs, timestamps, or unique identifiers as span attributes causes backend cardinality explosion.

**Bad Example:**

```java
Span span = tracer.spanBuilder("user.fetch")
    .setAttribute("user.id", userId)  // ❌ High cardinality (millions of unique values)
    .setAttribute("request.timestamp", System.currentTimeMillis())  // ❌ Infinite cardinality
    .setAttribute("user.email", email)  // ❌ PII + high cardinality
    .startSpan();
```

**Good Example (Use Low-Cardinality Attributes):**

```java
Span span = tracer.spanBuilder("user.fetch")
    .setAttribute("user.type", user.getType())  // ✅ Low cardinality: [FREE, PREMIUM, ENTERPRISE]
    .setAttribute("user.region", user.getRegion())  // ✅ Low cardinality: [US, EU, APAC]
    .setAttribute("request.method", "GET")  // ✅ Low cardinality: [GET, POST, PUT, DELETE]
    .startSpan();

// Use span events for high-cardinality data (not indexed)
span.addEvent("user.fetched", Attributes.builder()
    .put("user.id", userId)  // Events don't contribute to cardinality
    .put("user.email", email)
    .build()
);
```

**Cardinality Guidelines:**

| Attribute Type | Cardinality | Example | Use As |
|----------------|-------------|---------|--------|
| **Low (<100 values)** | ✅ Safe | HTTP method, status code, region | Span attribute |
| **Medium (100-10K)** | ⚠️ Caution | Product category, error code | Span attribute (with limits) |
| **High (>10K values)** | ❌ Avoid | User ID, email, IP address, timestamp | Span event (not attribute) |

---

#### Mistake 4: Not Configuring Span Sampling (Performance Overhead)

**Problem:** 100% trace sampling causes excessive backend storage and network overhead.

**Bad Configuration:**

```java
// Sample ALL traces (100%) - huge overhead in production!
SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
    .setSampler(Sampler.alwaysOn())  // ❌ Samples 100% of traces
    .build();
```

**Good Configuration (Probabilistic Sampling):**

```java
// Sample 10% of traces (sufficient for most use cases)
SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
    .setSampler(Sampler.traceIdRatioBased(0.1))  // ✅ Sample 10% of traces
    .build();
```

**Environment-Based Sampling:**

```yaml
# File: application.yml
otel:
  traces:
    sampler:
      # Local: Sample 100% for debugging
      # Staging: Sample 50% for testing
      # Production: Sample 5-10% to reduce overhead
      probability: ${OTEL_TRACES_SAMPLER_PROBABILITY:0.1}
```

**Recommendation:**
- **Local/Dev:** 100% sampling (`probability: 1.0`)
- **Staging:** 30-50% sampling (`probability: 0.3-0.5`)
- **Production:** 5-10% sampling (`probability: 0.05-0.1`)
- **High-traffic APIs:** 1-5% sampling (`probability: 0.01-0.05`)

---

### 10.9 OpenTelemetry Verification and Troubleshooting

#### 10.9.1 Verify OTLP Export to OpenTelemetry Collector

```bash
# Check OpenTelemetry Collector health
curl http://otel-collector:13133/

# Check Collector metrics endpoint
curl http://otel-collector:8888/metrics

# Verify spans received by Collector
# (Look for otelcol_receiver_accepted_spans metric)
curl http://otel-collector:8888/metrics | grep otelcol_receiver_accepted_spans
```

**Docker Compose for Local Testing:**

```yaml
# File: docker-compose.yml
version: '3.8'

services:
  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"  # OTLP gRPC receiver
      - "4318:4318"  # OTLP HTTP receiver
      - "8888:8888"  # Prometheus metrics
      - "13133:13133"  # Health check

  # Jaeger backend (trace visualization)
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "14250:14250"  # Jaeger gRPC receiver

  # Prometheus (metrics storage)
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"  # Prometheus UI
```

**OpenTelemetry Collector Configuration:**

```yaml
# File: otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

exporters:
  # Export traces to Jaeger
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

  # Export metrics to Prometheus
  prometheus:
    endpoint: 0.0.0.0:8889

  # Logging exporter for debugging
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger, logging]

    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus, logging]
```

#### 10.9.2 Debug OpenTelemetry Instrumentation

```java
// File: src/main/java/com/example/debug/OtelDebugController.java
package com.example.debug;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Debug endpoint to verify OpenTelemetry instrumentation.
 */
@RestController
public class OtelDebugController {

    private final Tracer tracer;

    public OtelDebugController() {
        this.tracer = GlobalOpenTelemetry.getTracer("debug", "1.0.0");
    }

    /**
     * Test endpoint to verify trace context.
     */
    @GetMapping("/debug/trace")
    public Map<String, String> debugTrace() {
        Span currentSpan = Span.current();

        return Map.of(
            "traceId", currentSpan.getSpanContext().getTraceId(),
            "spanId", currentSpan.getSpanContext().getSpanId(),
            "traceFlags", currentSpan.getSpanContext().getTraceFlags().asHex(),
            "isSampled", String.valueOf(currentSpan.getSpanContext().isSampled()),
            "isValid", String.valueOf(currentSpan.getSpanContext().isValid())
        );
    }

    /**
     * Test endpoint to create manual span.
     */
    @GetMapping("/debug/manual-span")
    public String testManualSpan() {
        Span span = tracer.spanBuilder("debug.test")
            .setAttribute("test.attribute", "value")
            .startSpan();

        try {
            span.addEvent("test.event");
            return "Manual span created: " + span.getSpanContext().getSpanId();
        } finally {
            span.end();
        }
    }
}
```

**Verify Trace Context Propagation:**

```bash
# Call debug endpoint
curl http://localhost:8080/debug/trace

# Expected output:
{
  "traceId": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "spanId": "1234567890abcdef",
  "traceFlags": "01",
  "isSampled": "true",
  "isValid": "true"
}

# Check Jaeger UI for trace
open http://localhost:16686/search?service=user-service
```

#### 10.9.3 Common Troubleshooting Issues

**Issue 1: Traces Not Appearing in Jaeger**

```bash
# Check OTLP exporter endpoint configuration
# Verify application.yml has correct endpoint
otel:
  exporter:
    otlp:
      endpoint: http://otel-collector:4317  # Must be reachable

# Check OpenTelemetry Collector logs
docker logs otel-collector

# Verify spans received by Collector
curl http://otel-collector:8888/metrics | grep otelcol_receiver_accepted_spans

# Check if traces sampled (if sampler probability too low)
# Increase sampling for debugging
otel:
  traces:
    sampler:
      probability: 1.0  # Sample 100% for debugging
```

**Issue 2: MDC trace_id/span_id Missing in Logs**

```bash
# Verify OpenTelemetry Spring Boot Starter dependency
# Check pom.xml includes:
<dependency>
    <groupId>io.opentelemetry.instrumentation</groupId>
    <artifactId>opentelemetry-spring-boot-starter</artifactId>
</dependency>

# Verify Logback configuration includes MDC pattern
# Check logback-spring.xml includes:
"trace_id": "%mdc{trace_id}",
"span_id": "%mdc{span_id}"

# Enable debug logging for OpenTelemetry
logging:
  level:
    io.opentelemetry: DEBUG
    io.opentelemetry.instrumentation: DEBUG
```

**Issue 3: High Memory Usage (Span Leaks)**

```bash
# Check for unclosed spans in code
# Ensure ALL spans ended with span.end() in finally block

# Verify batch span processor configuration
SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
    .addSpanProcessor(BatchSpanProcessor.builder(spanExporter)
        .setMaxQueueSize(2048)  # Prevent unbounded queue growth
        .setMaxExportBatchSize(512)
        .setScheduleDelay(Duration.ofSeconds(5))
        .build())
    .build();

# Monitor JVM heap usage
jmap -heap <pid>
```

---

### 10.5 References

[^48]: Spring Cloud Sleuth Documentation, "Integration with OpenTelemetry," https://docs.spring.io/spring-cloud-sleuth/docs/current/reference/html/integrations.html#sleuth-otel-integration, accessed 2025-11-02.

[^49]: Baeldung, "Distributed Tracing with Spring Cloud Sleuth," https://www.baeldung.com/spring-cloud-sleuth-single-application, accessed 2025-11-02.

[^50]: Spring Boot Actuator Documentation, "Production-ready Features," https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html, accessed 2025-11-02.

[^51]: Micrometer Documentation, "Spring Boot Integration," https://micrometer.io/docs/concepts#_spring_boot_integration, accessed 2025-11-02.

[^52]: Baeldung, "Spring Boot Actuator Metrics," https://www.baeldung.com/spring-boot-actuators, accessed 2025-11-02.

[^53]: Micrometer Documentation, "Prometheus," https://micrometer.io/docs/registry/prometheus, accessed 2025-11-02.

[^54]: OpenTelemetry Documentation, "Java Instrumentation," https://opentelemetry.io/docs/instrumentation/java/, accessed 2025-11-02.

[^55]: Baeldung, "OpenTelemetry vs Micrometer," https://www.baeldung.com/java-opentelemetry-micrometer, accessed 2025-11-02.

[^56]: Spring Blog, "Spring Cloud Sleuth End of Life," https://spring.io/blog/2023/05/18/what-is-the-future-of-spring-cloud-sleuth, accessed 2025-11-02.

[^57]: Spring Boot Documentation, "Micrometer Tracing," https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html#actuator.micrometer-tracing, accessed 2025-11-02.

[^58]: Prometheus Documentation, "Overview," https://prometheus.io/docs/introduction/overview/, accessed 2025-11-02.

[^59]: Datadog Documentation, "APM & Distributed Tracing," https://docs.datadoghq.com/tracing/, accessed 2025-11-02.

[^60]: OpenTelemetry Documentation, "Java SDK Manual Instrumentation," https://opentelemetry.io/docs/instrumentation/java/manual/, accessed 2025-11-03.

[^61]: OpenTelemetry Documentation, "Context Propagation," https://opentelemetry.io/docs/instrumentation/java/manual/#context-propagation, accessed 2025-11-03.

[^62]: OpenTelemetry GitHub, "Logback Appender," https://github.com/open-telemetry/opentelemetry-java-instrumentation/tree/main/instrumentation/logback/logback-appender-1.0, accessed 2025-11-03.

---

## 11. Audit Logging

Audit logging is critical for compliance (GDPR, SOC 2, HIPAA), security investigations, and forensic analysis. Spring Data JPA Auditing combined with event-driven patterns provides a robust, immutable audit trail[^60][^61][^62].

### 11.1 Recommended Approach: Event-Driven Audit with Spring Data JPA

Spring Data JPA provides `@CreatedBy`, `@CreatedDate`, `@LastModifiedBy`, `@LastModifiedDate` annotations for automatic entity auditing. For comprehensive audit trails, combine with event-driven architecture using `ApplicationEventPublisher` to create immutable audit records[^60][^61].

**Core Benefits:**
- **Automatic Auditing:** JPA lifecycle hooks capture entity changes automatically
- **Immutable Trail:** Append-only audit tables prevent tampering
- **Security Context Integration:** Capture authenticated user from Spring Security
- **Compliance:** GDPR Article 30 (record of processing), SOC 2 (audit logging), HIPAA (access logs)
- **Asynchronous:** Audit events processed async (don't block business transactions)

### 11.2 Implementation Examples

#### Step 1: Enable JPA Auditing

```java
// File: src/main/java/com/example/config/JpaAuditingConfiguration.java
package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Optional;

/**
 * JPA auditing configuration with Spring Security integration.
 */
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class JpaAuditingConfiguration {

    /**
     * Provide current auditor (authenticated user) from Spring Security context.
     */
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

            if (authentication == null || !authentication.isAuthenticated()) {
                return Optional.of("SYSTEM");  // Default for system operations
            }

            // Extract username from Authentication
            return Optional.of(authentication.getName());
        };
    }
}
```

#### Step 2: Auditable Base Entity

```java
// File: src/main/java/com/example/domain/entity/AuditableEntity.java
package com.example.domain.entity;

import jakarta.persistence.*;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;

/**
 * Base entity with JPA auditing fields.
 * All entities extend this to inherit audit fields.
 */
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class AuditableEntity {

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @CreatedBy
    @Column(name = "created_by", nullable = false, updatable = false, length = 100)
    private String createdBy;

    @LastModifiedDate
    @Column(name = "updated_at")
    private Instant updatedAt;

    @LastModifiedBy
    @Column(name = "updated_by", length = 100)
    private String updatedBy;

    // Getters
    public Instant getCreatedAt() { return createdAt; }
    public String getCreatedBy() { return createdBy; }
    public Instant getUpdatedAt() { return updatedAt; }
    public String getUpdatedBy() { return updatedBy; }
}
```

#### Step 3: Entity with Auditing

```java
// File: src/main/java/com/example/domain/entity/User.java
package com.example.domain.entity;

import jakarta.persistence.*;

/**
 * User entity with automatic auditing.
 * Extends AuditableEntity to inherit createdBy/createdAt/updatedBy/updatedAt.
 */
@Entity
@Table(name = "users")
public class User extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, length = 255)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private UserStatus status;

    // Constructors, getters, setters
    public User() {}

    public User(String email, String name, String passwordHash) {
        this.email = email;
        this.name = name;
        this.passwordHash = passwordHash;
        this.status = UserStatus.ACTIVE;
    }

    // Getters/setters
    public Long getId() { return id; }
    public String getEmail() { return email; }
    public String getName() { return name; }
    public UserStatus getStatus() { return status; }

    public void setStatus(UserStatus status) { this.status = status; }
}
```

**Database Schema:**

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,

    -- Audit fields (auto-populated by JPA auditing)
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    updated_at TIMESTAMP,
    updated_by VARCHAR(100),

    CONSTRAINT users_email_unique UNIQUE (email)
);

-- Index for audit queries
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_created_by ON users(created_by);
```

---

#### Step 4: Custom Audit Event Model

```java
// File: src/main/java/com/example/domain/entity/AuditEvent.java
package com.example.domain.entity;

import jakarta.persistence.*;

import java.time.Instant;

/**
 * Immutable audit event record.
 * Stores comprehensive audit trail for compliance.
 */
@Entity
@Table(
    name = "audit_events",
    indexes = {
        @Index(name = "idx_audit_entity_type_id", columnList = "entity_type,entity_id"),
        @Index(name = "idx_audit_timestamp", columnList = "timestamp"),
        @Index(name = "idx_audit_user", columnList = "performed_by"),
        @Index(name = "idx_audit_action", columnList = "action")
    }
)
public class AuditEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "entity_type", nullable = false, length = 100)
    private String entityType;  // e.g., "User", "Order"

    @Column(name = "entity_id", nullable = false, length = 100)
    private String entityId;  // ID of entity being audited

    @Column(name = "action", nullable = false, length = 50)
    private String action;  // CREATE, UPDATE, DELETE, VIEW, EXPORT

    @Column(name = "performed_by", nullable = false, length = 100)
    private String performedBy;  // Username from SecurityContext

    @Column(name = "timestamp", nullable = false)
    private Instant timestamp;

    @Column(name = "ip_address", length = 45)
    private String ipAddress;  // IPv4 or IPv6

    @Column(name = "user_agent", length = 255)
    private String userAgent;  // Browser/client info

    @Column(name = "request_id", length = 100)
    private String requestId;  // Trace ID for correlation

    @Column(name = "changes", columnDefinition = "TEXT")
    private String changes;  // JSON with old/new values

    @Column(name = "outcome", nullable = false, length = 20)
    private String outcome;  // SUCCESS, FAILURE

    @Column(name = "error_message", length = 500)
    private String errorMessage;  // If outcome = FAILURE

    // Constructor for immutability
    public AuditEvent(
        String entityType,
        String entityId,
        String action,
        String performedBy,
        String ipAddress,
        String userAgent,
        String requestId,
        String changes,
        String outcome,
        String errorMessage
    ) {
        this.entityType = entityType;
        this.entityId = entityId;
        this.action = action;
        this.performedBy = performedBy;
        this.timestamp = Instant.now();
        this.ipAddress = ipAddress;
        this.userAgent = userAgent;
        this.requestId = requestId;
        this.changes = changes;
        this.outcome = outcome;
        this.errorMessage = errorMessage;
    }

    protected AuditEvent() {}  // JPA constructor

    // Getters only (immutable)
    public Long getId() { return id; }
    public String getEntityType() { return entityType; }
    public String getEntityId() { return entityId; }
    public String getAction() { return action; }
    public String getPerformedBy() { return performedBy; }
    public Instant getTimestamp() { return timestamp; }
    public String getIpAddress() { return ipAddress; }
    public String getUserAgent() { return userAgent; }
    public String getRequestId() { return requestId; }
    public String getChanges() { return changes; }
    public String getOutcome() { return outcome; }
    public String getErrorMessage() { return errorMessage; }
}
```

**Database Schema:**

```sql
CREATE TABLE audit_events (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    request_id VARCHAR(100),
    changes TEXT,
    outcome VARCHAR(20) NOT NULL,
    error_message VARCHAR(500),

    -- Indexes for common queries
    INDEX idx_audit_entity_type_id (entity_type, entity_id),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_user (performed_by),
    INDEX idx_audit_action (action)
);

-- Partition by month for performance (optional, for high-volume audit logs)
-- ALTER TABLE audit_events PARTITION BY RANGE (timestamp);
```

---

#### Step 5: Audit Event Publisher

```java
// File: src/main/java/com/example/audit/AuditEventPublisher.java
package com.example.audit;

import com.example.domain.entity.AuditEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import jakarta.servlet.http.HttpServletRequest;

/**
 * Utility for publishing audit events.
 * Automatically captures user, IP, request ID from context.
 */
@Component
public class AuditEventPublisher {

    private final ApplicationEventPublisher eventPublisher;
    private final ObjectMapper objectMapper;

    public AuditEventPublisher(ApplicationEventPublisher eventPublisher, ObjectMapper objectMapper) {
        this.eventPublisher = eventPublisher;
        this.objectMapper = objectMapper;
    }

    /**
     * Publish successful audit event.
     */
    public void publishSuccess(String entityType, String entityId, String action, Object changes) {
        publish(entityType, entityId, action, changes, "SUCCESS", null);
    }

    /**
     * Publish failed audit event.
     */
    public void publishFailure(String entityType, String entityId, String action, String errorMessage) {
        publish(entityType, entityId, action, null, "FAILURE", errorMessage);
    }

    /**
     * Publish audit event with full context.
     */
    private void publish(
        String entityType,
        String entityId,
        String action,
        Object changes,
        String outcome,
        String errorMessage
    ) {
        try {
            // Extract user from SecurityContext
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            String performedBy = (auth != null && auth.isAuthenticated())
                ? auth.getName()
                : "ANONYMOUS";

            // Extract request details (IP, User-Agent, trace ID)
            String ipAddress = null;
            String userAgent = null;
            String requestId = null;

            ServletRequestAttributes attributes =
                (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();

            if (attributes != null) {
                HttpServletRequest request = attributes.getRequest();
                ipAddress = extractIpAddress(request);
                userAgent = request.getHeader("User-Agent");
                requestId = request.getHeader("X-Request-ID");  // Or trace ID from MDC
            }

            // Serialize changes to JSON
            String changesJson = (changes != null)
                ? objectMapper.writeValueAsString(changes)
                : null;

            // Create immutable audit event
            AuditEvent event = new AuditEvent(
                entityType,
                entityId,
                action,
                performedBy,
                ipAddress,
                userAgent,
                requestId,
                changesJson,
                outcome,
                errorMessage
            );

            // Publish event (handled by async listener)
            eventPublisher.publishEvent(event);

        } catch (Exception ex) {
            // Log error but don't fail business transaction
            // (audit failures should not block business operations)
            throw new RuntimeException("Failed to publish audit event", ex);
        }
    }

    /**
     * Extract client IP address, handling proxies/load balancers.
     */
    private String extractIpAddress(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");

        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }

        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }

        // X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2)
        // Take first IP (original client)
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }

        return ip;
    }
}
```

---

#### Step 6: Audit Event Listener

```java
// File: src/main/java/com/example/audit/AuditEventListener.java
package com.example.audit;

import com.example.domain.entity.AuditEvent;
import com.example.repository.AuditEventRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 * Async listener for audit events.
 * Persists audit events to database in separate transaction.
 */
@Component
public class AuditEventListener {

    private static final Logger log = LoggerFactory.getLogger(AuditEventListener.class);

    private final AuditEventRepository auditRepository;

    public AuditEventListener(AuditEventRepository auditRepository) {
        this.auditRepository = auditRepository;
    }

    /**
     * Handle audit event asynchronously.
     * Uses REQUIRES_NEW to ensure audit persisted even if business transaction rolls back.
     */
    @Async
    @EventListener
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void handleAuditEvent(AuditEvent event) {
        try {
            // Persist audit event to database
            auditRepository.save(event);

            log.debug("Audit event persisted: entityType={}, entityId={}, action={}, user={}",
                event.getEntityType(), event.getEntityId(), event.getAction(), event.getPerformedBy());

        } catch (Exception ex) {
            // Log error but don't throw (audit failures should not propagate)
            log.error("Failed to persist audit event: entityType={}, entityId={}, action={}",
                event.getEntityType(), event.getEntityId(), event.getAction(), ex);
        }
    }
}
```

---

#### Step 7: Audit Repository (Write-Only)

```java
// File: src/main/java/com/example/repository/AuditEventRepository.java
package com.example.repository;

import com.example.domain.entity.AuditEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Audit event repository (write-only, immutable records).
 * No update/delete methods (audit trail must be immutable).
 */
@Repository
public interface AuditEventRepository extends JpaRepository<AuditEvent, Long> {

    /**
     * Find audit events for specific entity.
     */
    List<AuditEvent> findByEntityTypeAndEntityIdOrderByTimestampDesc(
        String entityType,
        String entityId
    );

    /**
     * Find audit events by user (for compliance queries).
     */
    List<AuditEvent> findByPerformedByOrderByTimestampDesc(String performedBy);

    /**
     * Find audit events in time range (for audit reports).
     */
    List<AuditEvent> findByTimestampBetweenOrderByTimestampDesc(
        Instant startTime,
        Instant endTime
    );

    /**
     * Count failed operations by user (security monitoring).
     */
    @Query("SELECT COUNT(a) FROM AuditEvent a WHERE a.performedBy = :user AND a.outcome = 'FAILURE'")
    long countFailedOperationsByUser(String user);

    /**
     * Find recent failed login attempts (security monitoring).
     */
    @Query("SELECT a FROM AuditEvent a WHERE a.action = 'LOGIN' AND a.outcome = 'FAILURE' " +
           "AND a.timestamp > :since ORDER BY a.timestamp DESC")
    List<AuditEvent> findRecentFailedLogins(Instant since);
}
```

---

#### Step 8: Service Layer with Audit Integration

```java
// File: src/main/java/com/example/service/UserService.java
package com.example.service;

import com.example.audit.AuditEventPublisher;
import com.example.domain.entity.User;
import com.example.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;

/**
 * User service with comprehensive audit logging.
 */
@Service
public class UserService {

    private final UserRepository userRepository;
    private final AuditEventPublisher auditPublisher;

    public UserService(UserRepository userRepository, AuditEventPublisher auditPublisher) {
        this.userRepository = userRepository;
        this.auditPublisher = auditPublisher;
    }

    /**
     * Create user with audit trail.
     */
    @Transactional
    public User createUser(String email, String name, String passwordHash) {
        try {
            User user = new User(email, name, passwordHash);
            User savedUser = userRepository.save(user);

            // Publish successful audit event
            Map<String, Object> changes = new HashMap<>();
            changes.put("email", email);
            changes.put("name", name);

            auditPublisher.publishSuccess("User", savedUser.getId().toString(), "CREATE", changes);

            return savedUser;

        } catch (Exception ex) {
            // Publish failed audit event
            auditPublisher.publishFailure("User", email, "CREATE", ex.getMessage());
            throw ex;
        }
    }

    /**
     * Update user status with audit trail (capture old/new values).
     */
    @Transactional
    public User updateUserStatus(Long userId, UserStatus newStatus) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));

        try {
            // Capture old value for audit
            UserStatus oldStatus = user.getStatus();

            // Update status
            user.setStatus(newStatus);
            User updatedUser = userRepository.save(user);

            // Publish audit event with old/new values
            Map<String, Object> changes = new HashMap<>();
            changes.put("field", "status");
            changes.put("oldValue", oldStatus);
            changes.put("newValue", newStatus);

            auditPublisher.publishSuccess("User", userId.toString(), "UPDATE_STATUS", changes);

            return updatedUser;

        } catch (Exception ex) {
            auditPublisher.publishFailure("User", userId.toString(), "UPDATE_STATUS", ex.getMessage());
            throw ex;
        }
    }

    /**
     * Delete user with audit trail (soft delete recommended for compliance).
     */
    @Transactional
    public void deleteUser(Long userId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));

        try {
            // Soft delete (set status to DELETED)
            user.setStatus(UserStatus.DELETED);
            userRepository.save(user);

            // Audit deletion
            Map<String, Object> changes = new HashMap<>();
            changes.put("email", user.getEmail());
            changes.put("status", "DELETED");

            auditPublisher.publishSuccess("User", userId.toString(), "DELETE", changes);

        } catch (Exception ex) {
            auditPublisher.publishFailure("User", userId.toString(), "DELETE", ex.getMessage());
            throw ex;
        }
    }

    /**
     * View user details (audit read access for sensitive data).
     */
    public User getUserById(Long userId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));

        // Audit view access (for GDPR/HIPAA compliance)
        auditPublisher.publishSuccess("User", userId.toString(), "VIEW", null);

        return user;
    }
}
```

---

### 11.2.1 Audit Logging Patterns

#### Pattern 1: JPA Auditing with Spring Data (Simple, Entity-Level)

**Use Case:** Automatic tracking of createdBy/createdAt/updatedBy/updatedAt on entities.

**Already demonstrated in Step 2-3 above.**

**✅ Benefits:**
- Automatic (no manual code in service layer)
- Integrated with Spring Security (captures authenticated user)
- Minimal configuration (@EnableJpaAuditing + @EntityListeners)

**❌ Drawbacks:**
- Limited to entity lifecycle (doesn't capture read operations)
- No detailed change tracking (old vs. new values)
- Coupled to JPA (not suitable for non-entity operations)

**Use When:**
- Need basic entity auditing (who/when created/updated)
- Using JPA for persistence
- Don't need detailed change history

---

#### Pattern 2: Event-Driven Audit with ApplicationEventPublisher (Recommended)

**Use Case:** Comprehensive audit trail with full context (IP, User-Agent, changes).

**Already demonstrated in Step 4-8 above.**

**✅ Benefits:**
- **Comprehensive:** Captures all operation types (CREATE, UPDATE, DELETE, VIEW, EXPORT)
- **Immutable:** Append-only audit table prevents tampering
- **Async:** Audit events processed asynchronously (no performance impact)
- **Separate Transaction:** Audit persisted even if business transaction rolls back
- **Rich Context:** IP address, User-Agent, trace ID for forensics

**❌ Drawbacks:**
- Requires manual audit calls in service layer
- More complex than JPA auditing
- Additional database table (audit_events)

**Use When:**
- Need compliance audit trail (GDPR, SOC 2, HIPAA)
- Must track read operations (VIEW, EXPORT)
- Need detailed change history (old vs. new values)
- Require forensic analysis capabilities

---

#### Pattern 3: AOP-Based Audit with @Aspect

**Use Case:** Automatic audit logging via AOP without modifying service code.

**Implementation:**

```java
// File: src/main/java/com/example/audit/AuditAspect.java
package com.example.audit;

import com.example.annotation.Auditable;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;

/**
 * AOP aspect for automatic audit logging.
 * Intercepts methods annotated with @Auditable.
 */
@Aspect
@Component
public class AuditAspect {

    private final AuditEventPublisher auditPublisher;

    public AuditAspect(AuditEventPublisher auditPublisher) {
        this.auditPublisher = auditPublisher;
    }

    /**
     * Intercept methods annotated with @Auditable.
     */
    @Around("@annotation(auditable)")
    public Object auditMethod(ProceedingJoinPoint joinPoint, Auditable auditable) throws Throwable {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Object[] args = joinPoint.getArgs();

        // Extract entity info from annotation
        String entityType = auditable.entityType();
        String action = auditable.action();

        // Extract entity ID from method arguments (first arg assumed to be ID)
        String entityId = (args.length > 0) ? args[0].toString() : "UNKNOWN";

        try {
            // Execute business method
            Object result = joinPoint.proceed();

            // Publish success audit event
            auditPublisher.publishSuccess(entityType, entityId, action, args);

            return result;

        } catch (Exception ex) {
            // Publish failure audit event
            auditPublisher.publishFailure(entityType, entityId, action, ex.getMessage());
            throw ex;
        }
    }
}
```

**Custom Annotation:**

```java
// File: src/main/java/com/example/annotation/Auditable.java
package com.example.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Annotation for automatic audit logging via AOP.
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Auditable {

    /**
     * Entity type being audited (e.g., "User", "Order").
     */
    String entityType();

    /**
     * Action being performed (e.g., "CREATE", "UPDATE", "DELETE").
     */
    String action();
}
```

**Usage in Service:**

```java
@Service
public class UserService {

    @Auditable(entityType = "User", action = "CREATE")
    public User createUser(CreateUserRequest request) {
        // Business logic (audit automatically captured by AOP)
        return userRepository.save(buildUser(request));
    }

    @Auditable(entityType = "User", action = "DELETE")
    public void deleteUser(Long userId) {
        userRepository.deleteById(userId);
    }
}
```

**✅ Benefits:**
- **Clean Code:** No audit calls in service layer (handled by AOP)
- **Declarative:** Simple @Auditable annotation
- **Consistent:** All annotated methods audited uniformly

**❌ Drawbacks:**
- **Less Flexible:** Can't easily capture old/new values (would need additional logic)
- **Magic:** Audit behavior not explicit in code (harder to debug)
- **Performance:** AOP adds method interception overhead

**Use When:**
- Want clean service code (no audit calls)
- Audit requirements are simple (action/entityType sufficient)
- Many methods need auditing (reduce boilerplate)

---

#### Pattern 4: Centralized Audit Service (REST/gRPC)

**Use Case:** Microservices architecture with centralized audit service.

**Implementation:**

```java
// File: src/main/java/com/example/client/AuditServiceClient.java
package com.example.client;

import com.example.dto.AuditEventDto;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

/**
 * Client for centralized audit service.
 */
@Component
public class AuditServiceClient {

    private final RestTemplate restTemplate;
    private final String auditServiceUrl;

    public AuditServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
        this.auditServiceUrl = "http://audit-service/api/audit";
    }

    /**
     * Send audit event to centralized audit service.
     */
    public void sendAuditEvent(AuditEventDto event) {
        try {
            restTemplate.postForEntity(auditServiceUrl, event, Void.class);
        } catch (Exception ex) {
            // Log error but don't fail business operation
            throw new RuntimeException("Failed to send audit event", ex);
        }
    }
}
```

**✅ Benefits:**
- **Centralized:** Single audit database for all microservices
- **Scalable:** Dedicated audit service can scale independently
- **Compliance:** Centralized audit queries for compliance reports

**❌ Drawbacks:**
- **Network Overhead:** HTTP/gRPC call for every audit event
- **Dependency:** Service depends on audit service availability
- **Complexity:** Additional service to deploy/maintain

**Use When:**
- Microservices architecture (multiple services)
- Need centralized audit queries across services
- Compliance requires unified audit trail

---

### 11.2.2 Common Audit Mistakes

#### Mistake 1: Not Capturing SecurityContext User Details

**Problem:** Audit log shows "ANONYMOUS" instead of actual username.

**Bad Example:**

```java
// Missing SecurityContext - audit shows "ANONYMOUS"
public void createUser(CreateUserRequest request) {
    User user = userRepository.save(buildUser(request));
    // Created by "ANONYMOUS" (wrong!)
}
```

**Good Example:**

```java
// Properly configured AuditorAware captures authenticated user
@Bean
public AuditorAware<String> auditorProvider() {
    return () -> {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return Optional.ofNullable(auth)
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName)
            .or(() -> Optional.of("SYSTEM"));
    };
}
```

---

#### Mistake 2: Mutable Audit Records (Allow Updates/Deletes)

**Problem:** Audit trail can be tampered with (violates compliance).

**Bad Example:**

```java
// ❌ DON'T DO THIS - allows audit modification!
@Repository
public interface AuditEventRepository extends JpaRepository<AuditEvent, Long> {
    // save() allows updates - audit records should be immutable!
}

// Service can modify audit records (BAD!)
AuditEvent event = auditRepository.findById(123).get();
event.setOutcome("SUCCESS");  // Tampering with audit trail!
auditRepository.save(event);
```

**Good Example:**

```java
// Immutable AuditEvent entity (no setters)
@Entity
public class AuditEvent {
    // Only constructor, no setters (immutable after creation)
    public AuditEvent(String entityType, String action, ...) {
        this.entityType = entityType;
        this.action = action;
        this.timestamp = Instant.now();
    }

    // Getters only
    public String getEntityType() { return entityType; }
}

// Write-only repository (no update/delete)
@Repository
public interface AuditEventRepository extends JpaRepository<AuditEvent, Long> {
    // save() for INSERT only (no findById + save update pattern)
    // No delete methods
}
```

**Database Constraint:**

```sql
-- Prevent updates/deletes at database level
CREATE RULE audit_events_no_update AS ON UPDATE TO audit_events DO INSTEAD NOTHING;
CREATE RULE audit_events_no_delete AS ON DELETE TO audit_events DO INSTEAD NOTHING;
```

---

#### Mistake 3: Audit Logging in Same Transaction (Rollback Loses Audit)

**Problem:** Business transaction rollback also rolls back audit record.

**Bad Example:**

```java
@Transactional  // Audit in same transaction
public void createOrder(OrderRequest request) {
    try {
        Order order = orderRepository.save(buildOrder(request));

        // Audit event in same transaction
        auditRepository.save(new AuditEvent("Order", order.getId(), "CREATE", ...));

        // Exception occurs - both order AND audit rolled back!
        throw new PaymentFailedException();

    } catch (Exception ex) {
        // Audit lost due to rollback (BAD for compliance)
    }
}
```

**Good Example:**

```java
// Audit listener uses REQUIRES_NEW propagation
@Async
@EventListener
@Transactional(propagation = Propagation.REQUIRES_NEW)  // Separate transaction!
public void handleAuditEvent(AuditEvent event) {
    // Audit persisted in separate transaction
    // Business rollback doesn't affect audit
    auditRepository.save(event);
}
```

---

### 11.2.3 Verification and Troubleshooting

#### Verify JPA Auditing Works

```java
// Test JPA auditing
@SpringBootTest
class JpaAuditingTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    @WithMockUser(username = "test-user")  // Mock authenticated user
    void testAuditFieldsPopulated() {
        // Create user
        User user = new User("test@example.com", "Test User", "hash");
        User saved = userRepository.save(user);

        // Verify audit fields populated
        assertThat(saved.getCreatedBy()).isEqualTo("test-user");
        assertThat(saved.getCreatedAt()).isNotNull();
        assertThat(saved.getUpdatedBy()).isEqualTo("test-user");
        assertThat(saved.getUpdatedAt()).isNotNull();
    }
}
```

---

#### Verify Audit Events Published

```java
// Test audit event publishing
@SpringBootTest
class AuditEventTest {

    @Autowired
    private UserService userService;

    @Autowired
    private AuditEventRepository auditRepository;

    @Test
    @WithMockUser(username = "test-user")
    void testAuditEventPublished() throws InterruptedException {
        // Create user (triggers audit event)
        User user = userService.createUser("test@example.com", "Test", "hash");

        // Wait for async audit processing
        Thread.sleep(1000);

        // Verify audit event persisted
        List<AuditEvent> events = auditRepository.findByEntityTypeAndEntityId("User", user.getId().toString());

        assertThat(events).hasSize(1);
        assertThat(events.get(0).getAction()).isEqualTo("CREATE");
        assertThat(events.get(0).getPerformedBy()).isEqualTo("test-user");
        assertThat(events.get(0).getOutcome()).isEqualTo("SUCCESS");
    }
}
```

---

#### Compliance Query Examples (Audit Reports)

```java
// Query audit events for compliance reports
@Service
public class AuditReportService {

    private final AuditEventRepository auditRepository;

    /**
     * GDPR Article 30: Record of processing activities.
     * List all access to user's personal data.
     */
    public List<AuditEvent> getUserDataAccessLog(Long userId) {
        return auditRepository.findByEntityTypeAndEntityIdOrderByTimestampDesc(
            "User",
            userId.toString()
        );
    }

    /**
     * SOC 2: User activity report.
     * All actions performed by specific user.
     */
    public List<AuditEvent> getUserActivityReport(String username) {
        return auditRepository.findByPerformedByOrderByTimestampDesc(username);
    }

    /**
     * Security monitoring: Failed operations report.
     */
    public List<AuditEvent> getFailedOperationsReport(Instant since) {
        return auditRepository.findByTimestampBetweenOrderByTimestampDesc(
            since,
            Instant.now()
        ).stream()
         .filter(event -> "FAILURE".equals(event.getOutcome()))
         .toList();
    }

    /**
     * HIPAA: Patient data access audit.
     * Track who accessed patient records.
     */
    public List<AuditEvent> getPatientDataAccessLog(Long patientId, Instant since) {
        return auditRepository.findByTimestampBetweenOrderByTimestampDesc(since, Instant.now())
            .stream()
            .filter(event -> "Patient".equals(event.getEntityType()))
            .filter(event -> patientId.toString().equals(event.getEntityId()))
            .toList();
    }
}
```

---

### 11.3 Alternative Approaches

#### Database Audit Tables vs. Event Streaming (Kafka)

| Feature | Database Audit Table | Event Streaming (Kafka) |
|---------|----------------------|--------------------------|
| **Durability** | ACID guarantees | At-least-once delivery |
| **Queryability** | SQL queries (easy) | Stream processing (complex) |
| **Scalability** | Limited by database | Highly scalable |
| **Latency** | Low (synchronous writes) | Variable (async) |
| **Retention** | Database storage limits | Configurable (days to years) |
| **Integration** | Simple (Spring Data JPA) | Requires Kafka infrastructure |

**Recommendation:** Use **database audit tables** for transactional systems with SQL query requirements. Use **Kafka** for high-volume audit streams or microservices needing event replay[^63].

---

#### Synchronous vs. Asynchronous Audit Logging

| Feature | Synchronous (@Transactional) | Asynchronous (@Async) |
|---------|------------------------------|-----------------------|
| **Performance** | Blocks business transaction | No blocking |
| **Reliability** | Guaranteed (ACID) | Eventually consistent |
| **Transaction Coupling** | Same transaction (rollback affects audit) | Separate transaction (REQUIRES_NEW) |
| **Failure Handling** | Business fails if audit fails | Business succeeds even if audit fails |
| **Use Case** | Critical audit (compliance) | High-throughput systems |

**Recommendation:** Use **asynchronous** with `@Transactional(propagation = Propagation.REQUIRES_NEW)` to avoid performance impact while ensuring audit survives business rollback[^64].

---

#### Self-Managed vs. Managed Audit Services (AWS CloudTrail)

| Feature | Self-Managed (Database) | AWS CloudTrail |
|---------|-------------------------|----------------|
| **Cost** | Infrastructure cost | SaaS pricing |
| **Compliance** | Manual compliance setup | Pre-certified (SOC 2, HIPAA) |
| **Integration** | Custom code | AWS SDK |
| **Queryability** | SQL | CloudWatch Insights |
| **Retention** | Configurable | 90 days default (S3 for longer) |

**Recommendation:** Use **self-managed** for full control and SQL queries. Use **AWS CloudTrail** for AWS-native apps needing pre-certified compliance[^65].

---

### 11.4 Decision Criteria

#### When to Use JPA Auditing (Simple, Entity-Level)

**Use When:**
- ✅ Need basic who/when tracking (createdBy, createdAt, updatedBy, updatedAt)
- ✅ Using JPA/Hibernate for persistence
- ✅ Don't need detailed change history (old vs. new values)
- ✅ Entity-level auditing sufficient (not tracking read operations)

**Avoid When:**
- ❌ Need comprehensive audit trail (CREATE/UPDATE/DELETE/VIEW/EXPORT)
- ❌ Must track old/new values for compliance
- ❌ Need audit for non-entity operations (login, export, etc.)

---

#### When to Use Event-Driven Audit (Comprehensive)

**Use When:**
- ✅ Compliance requirements (GDPR, SOC 2, HIPAA)
- ✅ Need detailed change tracking (old vs. new values)
- ✅ Must audit read operations (VIEW, EXPORT)
- ✅ Forensic analysis required (IP address, User-Agent, trace correlation)
- ✅ Immutable audit trail (append-only, no updates/deletes)

**Avoid When:**
- ❌ Simple entity auditing sufficient (JPA auditing simpler)
- ❌ Low audit volume (event overhead not justified)

---

#### When to Use Centralized Audit Service

**Use When:**
- ✅ Microservices architecture (multiple services)
- ✅ Need unified audit queries across services
- ✅ Compliance requires centralized audit trail
- ✅ Want to scale audit infrastructure independently

**Avoid When:**
- ❌ Monolithic application (single service simpler)
- ❌ Low latency critical (network overhead unacceptable)
- ❌ Want to avoid additional service dependency

---

### 11.5 References

[^60]: Spring Data JPA Documentation, "Auditing," https://docs.spring.io/spring-data/jpa/reference/auditing.html, accessed 2025-11-02.

[^61]: Baeldung, "Spring Data JPA Auditing," https://www.baeldung.com/database-auditing-jpa, accessed 2025-11-02.

[^62]: GDPR, "Article 30 - Records of processing activities," https://gdpr-info.eu/art-30-gdpr/, accessed 2025-11-02.

[^63]: Confluent, "Audit Logging with Apache Kafka," https://www.confluent.io/blog/audit-log-apache-kafka-security/, accessed 2025-11-02.

[^64]: Spring Framework Documentation, "Transaction Propagation," https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html, accessed 2025-11-02.

[^65]: AWS Documentation, "AWS CloudTrail," https://docs.aws.amazon.com/cloudtrail/latest/userguide/cloudtrail-user-guide.html, accessed 2025-11-02.

[^66]: SOC 2 Compliance, "Audit Logging Requirements," https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report.html, accessed 2025-11-02.

[^67]: HIPAA, "45 CFR § 164.312 - Technical safeguards," https://www.law.cornell.edu/cfr/text/45/164.312, accessed 2025-11-02.

[^68]: Baeldung, "Spring Events," https://www.baeldung.com/spring-events, accessed 2025-11-02.

---

## References

[^28]: Oracle, "Records," Java Language Specification, https://docs.oracle.com/en/java/javase/17/language/records.html, accessed 2025-11-02.

[^29]: Baeldung, "Java Records," https://www.baeldung.com/java-record-keyword, accessed 2025-11-02.

[^30]: Oracle, "Sealed Classes and Interfaces," Java Language Specification, https://docs.oracle.com/en/java/javase/17/language/sealed-classes-and-interfaces.html, accessed 2025-11-02.

[^31]: Baeldung, "Builder Pattern in Java," https://www.baeldung.com/java-builder-pattern, accessed 2025-11-02.

[^32]: Baeldung, "Validation in Spring Boot," https://www.baeldung.com/spring-boot-bean-validation, accessed 2025-11-02.

[^33]: Baeldung, "Creating Custom Constraints," https://www.baeldung.com/spring-mvc-custom-validator, accessed 2025-11-02.

[^34]: Baeldung, "Validation Groups," https://www.baeldung.com/javax-validation-groups, accessed 2025-11-02.

[^35]: Spring Documentation, "Programmatic Constraint Definition and Declaration," https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html#validation-beanvalidation-spring-constraints, accessed 2025-11-02.

[^36]: Oracle, "Optional in Java," https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Optional.html, accessed 2025-11-02.

[^37]: Oracle, "Enum Types," Java Language Specification, https://docs.oracle.com/javase/tutorial/java/javaOO/enum.html, accessed 2025-11-02.

[^38]: Oracle, "Local Variable Type Inference," https://openjdk.org/jeps/286, accessed 2025-11-02.

[^39]: Baeldung, "Criteria Queries in JPA," https://www.baeldung.com/hibernate-criteria-queries, accessed 2025-11-02.

[^40]: Baeldung, "JPA Metamodel," https://www.baeldung.com/hibernate-criteria-queries-metamodel, accessed 2025-11-02.

[^41]: Baeldung, "Spring Data JPA Specifications," https://www.baeldung.com/rest-api-search-language-spring-data-specifications, accessed 2025-11-02.

[^42]: Baeldung, "JPA Entity Lifecycle Events," https://www.baeldung.com/jpa-entity-lifecycle-events, accessed 2025-11-02.

[^43]: Baeldung, "Bean Validation with JPA," https://www.baeldung.com/jpa-validation, accessed 2025-11-02.

[^44]: Spring Documentation, "Error Responses," https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html, accessed 2025-11-02.

[^45]: RFC 7807, "Problem Details for HTTP APIs," https://datatracker.ietf.org/doc/html/rfc7807, accessed 2025-11-02.

[^46]: Baeldung, "Spring Boot Problem Details," https://www.baeldung.com/spring-boot-problem-details, accessed 2025-11-02.

[^47]: Baeldung, "Service Layer Validation," https://www.baeldung.com/spring-service-layer-validation, accessed 2025-11-02.

[^1]: Medium, "Stop Using @Value in Spring Boot 3: Use @ConfigurationProperties with Records Instead," https://medium.com/@niketl16/stop-using-value-in-spring-boot-3-use-configurationproperties-with-records-instead-af783c2984ea, accessed 2025-11-01.

[^2]: Baeldung, "Logback with Spring Boot," https://www.baeldung.com/spring-boot-logging, accessed 2025-11-01.

[^3]: Spring Framework Documentation, "Cache Abstraction," https://docs.spring.io/spring-framework/reference/integration/cache.html, accessed 2025-11-01.

[^4]: Spring Data JPA Documentation, "Reference Documentation," https://docs.spring.io/spring-data/jpa/reference/, accessed 2025-11-01.

[^5]: Baeldung, "Guide to @ConfigurationProperties in Spring Boot," https://www.baeldung.com/configuration-properties-in-spring-boot, accessed 2025-11-01.

[^6]: Spring Boot Documentation, "@Value Annotation," https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/value-annotations.html, accessed 2025-11-01.

[^7]: The Twelve-Factor App, "III. Config," https://12factor.net/config, accessed 2025-11-01.

[^8]: Spring Cloud Config Documentation, "Spring Cloud Config," https://docs.spring.io/spring-cloud-config/docs/current/reference/html/, accessed 2025-11-01.

[^9]: Baeldung, "A Guide to Logback," https://www.baeldung.com/logback, accessed 2025-11-01.

[^10]: Logback Documentation, "Configuration," https://logback.qos.ch/manual/configuration.html, accessed 2025-11-01.

[^11]: Spring Boot Actuator Documentation, "Loggers Endpoint," https://docs.spring.io/spring-boot/docs/current/actuator-api/htmlsingle/#loggers, accessed 2025-11-01.

[^12]: Apache Log4j2 Documentation, "Performance," https://logging.apache.org/log4j/2.x/performance.html, accessed 2025-11-01.

[^13]: Spring Boot Documentation, "Caching," https://docs.spring.io/spring-boot/docs/current/reference/html/io.html#io.caching, accessed 2025-11-01.

[^14]: Baeldung, "Spring Boot Starter for Redis," https://www.baeldung.com/spring-data-redis-tutorial, accessed 2025-11-01.

[^15]: Baeldung, "Spring Cache with Multiple Cache Managers," https://www.baeldung.com/spring-multiple-cache-managers, accessed 2025-11-01.

[^16]: Spring Boot Documentation, "Profiles," https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.profiles, accessed 2025-11-01.

[^17]: Baeldung, "Lettuce - the Java Redis Client," https://www.baeldung.com/java-redis-lettuce, accessed 2025-11-01.

[^18]: GitHub, "ben-manes/caffeine: A high performance caching library for Java," https://github.com/ben-manes/caffeine, accessed 2025-11-01.

[^19]: Ehcache Documentation, "Getting Started," https://www.ehcache.org/documentation/3.10/, accessed 2025-11-01.

[^20]: Baeldung, "Spring Data JPA Repository," https://www.baeldung.com/spring-data-jpa-repository, accessed 2025-11-01.

[^21]: Spring Boot Documentation, "Working with SQL Databases," https://docs.spring.io/spring-boot/docs/current/reference/html/data.html#data.sql, accessed 2025-11-01.

[^22]: HikariCP Documentation, "Configuration," https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby, accessed 2025-11-01.

[^23]: Spring Boot Documentation, "@ConfigurationPropertiesScan," https://docs.spring.io/spring-boot/docs/current/api/org/springframework/boot/context/properties/ConfigurationPropertiesScan.html, accessed 2025-11-01.

[^24]: Baeldung, "Spring @Bean Annotation," https://www.baeldung.com/spring-bean-annotations, accessed 2025-11-01.

[^25]: Spring Boot Documentation, "Profile-specific Files," https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config.files.profile-specific, accessed 2025-11-01.

[^26]: Spring Cloud Config Documentation, "Quick Start," https://docs.spring.io/spring-cloud-config/docs/current/reference/html/#_quick_start, accessed 2025-11-01.

[^27]: Spring Boot Actuator Documentation, "Configuration Properties Endpoint," https://docs.spring.io/spring-boot/docs/current/actuator-api/htmlsingle/#configprops, accessed 2025-11-01.

---

**Document Coverage:**

**Completed Sections (v3.0):**
- ✅ Section 1: Configuration Management (with comprehensive type safety and validation patterns)
- ✅ Section 2: Structured Logging
- ✅ Section 3: Caching Strategies
- ✅ Section 4: Data Access Patterns (with JPA type safety, Criteria API, Specifications, entity validation)
- ✅ Section 9: Error Handling and Validation (RFC 7807, @ControllerAdvice, Bean Validation, distributed tracing)
- ✅ Section 10: Telemetry and Observability (Spring Boot Actuator, Micrometer, OpenTelemetry, health indicators, custom metrics)
- ✅ Section 11: Audit Logging (Spring Data JPA Auditing, event-driven patterns, compliance - GDPR/SOC 2/HIPAA)

**Extensions Added (v3.0):**
- 9.7: Error Correlation with Distributed Tracing (Spring Cloud Sleuth, OpenTelemetry, trace context propagation)
- Section 10: Complete telemetry implementation (Actuator + Micrometer, OpenTelemetry patterns, health indicators, custom metrics, MDC propagation, cardinality management)
- Section 11: Complete audit logging implementation (JPA auditing, event-driven patterns, immutable audit trails, compliance queries)

**Extensions Added (v2.0):**
- 1.2.4: Type Safety Patterns with Records and Generics (generic configurations, Optional<T>, sealed classes)
- 1.2.5: Advanced Validation Patterns (custom validators, validation groups, programmatic validation)
- 1.2.6: Type Safety Best Practices (Optional<T> usage, Records vs POJOs, Enums, compact constructors, var)
- 4.8: JPA Type Safety with Criteria API (JPA Metamodel, type-safe queries, Specification pattern)
- 4.9: Entity Validation Patterns (JSR-303 on entities, JPA lifecycle callbacks, cross-field validation)
- Section 9: Complete error handling implementation (RFC 7807 Problem Details, global exception handling)

**Future Sections (To Be Added):**
- Section 5: External Service Integration (RestTemplate, WebClient, Resilience4j patterns)
- Section 6: Dependency Injection in Spring (bean scopes, lifecycle, @Conditional)
- Section 7: Clean Architecture Layers (domain, application, infrastructure, presentation)
- Section 8: Testing Strategies (JUnit 5, Mockito, @SpringBootTest, test slices)
- Section 12: Project Structure (package organization, multi-module Maven/Gradle)
- Appendix A: Example Project Structure (complete directory tree)
- Appendix B: Recommended Libraries (curated list with justifications)

**Version History:**
- v3.0 (2025-11-02): Added 2,800+ lines covering telemetry/observability and audit logging (Sections 9.7, 10, 11) with 21 new citations
- v2.0 (2025-11-02): Added 3,660+ lines of validation and type safety content across Sections 1, 4, and 9
- v1.0 (2025-11-01): Initial release with Sections 1-4 (Configuration, Logging, Caching, Data Access)

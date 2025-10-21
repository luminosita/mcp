# Caching Patterns

Caching strategies and implementation patterns for Go applications.

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

## Cache Strategies

### Cache-Aside (Lazy Loading)

```go
import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
)

type UserCache struct {
    redis *redis.Client
    repo  UserRepository
}

func (c *UserCache) GetUser(ctx context.Context, userID string) (*User, error) {
    cacheKey := fmt.Sprintf("user:%s", userID)

    cached, err := c.redis.Get(ctx, cacheKey).Result()
    if err == nil {
        var user User
        if err := json.Unmarshal([]byte(cached), &user); err == nil {
            return &user, nil
        }
    }

    user, err := c.repo.FindByID(ctx, userID)
    if err != nil {
        return nil, fmt.Errorf("failed to fetch user: %w", err)
    }

    userJSON, err := json.Marshal(user)
    if err != nil {
        return user, nil
    }

    c.redis.Set(ctx, cacheKey, userJSON, 1*time.Hour)

    return user, nil
}

func (c *UserCache) InvalidateUser(ctx context.Context, userID string) error {
    cacheKey := fmt.Sprintf("user:%s", userID)
    return c.redis.Del(ctx, cacheKey).Err()
}
```

### Read-Through Cache

```go
type ReadThroughCache struct {
    redis  *redis.Client
    loader func(ctx context.Context, key string) (interface{}, error)
    ttl    time.Duration
}

func NewReadThroughCache(redis *redis.Client, loader func(context.Context, string) (interface{}, error), ttl time.Duration) *ReadThroughCache {
    return &ReadThroughCache{
        redis:  redis,
        loader: loader,
        ttl:    ttl,
    }
}

func (c *ReadThroughCache) Get(ctx context.Context, key string) (interface{}, error) {
    cached, err := c.redis.Get(ctx, key).Result()
    if err == nil {
        var value interface{}
        if err := json.Unmarshal([]byte(cached), &value); err == nil {
            return value, nil
        }
    }

    if err != redis.Nil {
        return nil, fmt.Errorf("cache error: %w", err)
    }

    value, err := c.loader(ctx, key)
    if err != nil {
        return nil, fmt.Errorf("loader error: %w", err)
    }

    valueJSON, err := json.Marshal(value)
    if err != nil {
        return value, nil
    }

    c.redis.Set(ctx, key, valueJSON, c.ttl)

    return value, nil
}
```

### Write-Through Cache

```go
type WriteThroughCache struct {
    redis *redis.Client
    repo  Repository
    ttl   time.Duration
}

func (c *WriteThroughCache) Save(ctx context.Context, key string, value interface{}) error {
    if err := c.repo.Save(ctx, key, value); err != nil {
        return fmt.Errorf("failed to save to database: %w", err)
    }

    valueJSON, err := json.Marshal(value)
    if err != nil {
        return fmt.Errorf("failed to marshal value: %w", err)
    }

    if err := c.redis.Set(ctx, key, valueJSON, c.ttl).Err(); err != nil {
        return fmt.Errorf("failed to save to cache: %w", err)
    }

    return nil
}
```

### Write-Behind (Write-Back) Cache

```go
import (
    "sync"
    "time"
)

type WriteBehindCache struct {
    redis      *redis.Client
    repo       Repository
    writeQueue chan writeOperation
    mu         sync.RWMutex
    wg         sync.WaitGroup
}

type writeOperation struct {
    key   string
    value interface{}
}

func NewWriteBehindCache(redis *redis.Client, repo Repository, workers int) *WriteBehindCache {
    cache := &WriteBehindCache{
        redis:      redis,
        repo:       repo,
        writeQueue: make(chan writeOperation, 1000),
    }

    for i := 0; i < workers; i++ {
        cache.wg.Add(1)
        go cache.worker()
    }

    return cache
}

func (c *WriteBehindCache) worker() {
    defer c.wg.Done()

    for op := range c.writeQueue {
        ctx := context.Background()
        if err := c.repo.Save(ctx, op.key, op.value); err != nil {
            slog.Error("write-behind failed",
                "key", op.key,
                "error", err,
            )
        }
    }
}

func (c *WriteBehindCache) Save(ctx context.Context, key string, value interface{}) error {
    valueJSON, err := json.Marshal(value)
    if err != nil {
        return fmt.Errorf("failed to marshal value: %w", err)
    }

    if err := c.redis.Set(ctx, key, valueJSON, 1*time.Hour).Err(); err != nil {
        return fmt.Errorf("failed to save to cache: %w", err)
    }

    select {
    case c.writeQueue <- writeOperation{key: key, value: value}:
    default:
        return errors.New("write queue full")
    }

    return nil
}

func (c *WriteBehindCache) Close() {
    close(c.writeQueue)
    c.wg.Wait()
}
```

## Redis Integration

### Redis Client Setup

```go
import (
    "context"
    "crypto/tls"
    "time"

    "github.com/redis/go-redis/v9"
)

type RedisConfig struct {
    Host     string
    Port     string
    Password string
    DB       int
    UseTLS   bool
}

func NewRedisClient(cfg RedisConfig) (*redis.Client, error) {
    addr := fmt.Sprintf("%s:%s", cfg.Host, cfg.Port)

    opts := &redis.Options{
        Addr:         addr,
        Password:     cfg.Password,
        DB:           cfg.DB,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
        PoolSize:     10,
        MinIdleConns: 5,
    }

    if cfg.UseTLS {
        opts.TLSConfig = &tls.Config{
            MinVersion: tls.VersionTLS12,
        }
    }

    client := redis.NewClient(opts)

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := client.Ping(ctx).Err(); err != nil {
        return nil, fmt.Errorf("failed to connect to Redis: %w", err)
    }

    return client, nil
}
```

### Redis Cluster Setup

```go
func NewRedisClusterClient(addrs []string, password string) (*redis.ClusterClient, error) {
    client := redis.NewClusterClient(&redis.ClusterOptions{
        Addrs:        addrs,
        Password:     password,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
        PoolSize:     10,
        MinIdleConns: 5,
    })

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := client.Ping(ctx).Err(); err != nil {
        return nil, fmt.Errorf("failed to connect to Redis cluster: %w", err)
    }

    return client, nil
}
```

## Cache Patterns

### Cache with TTL Refresh

```go
type RefreshableCache struct {
    redis   *redis.Client
    loader  func(ctx context.Context, key string) (interface{}, error)
    ttl     time.Duration
    refresh time.Duration
}

func (c *RefreshableCache) Get(ctx context.Context, key string) (interface{}, error) {
    cached, err := c.redis.Get(ctx, key).Result()
    if err == nil {
        var value interface{}
        if err := json.Unmarshal([]byte(cached), &value); err == nil {
            ttl, _ := c.redis.TTL(ctx, key).Result()
            if ttl < c.refresh {
                go c.asyncRefresh(key)
            }
            return value, nil
        }
    }

    value, err := c.loader(ctx, key)
    if err != nil {
        return nil, err
    }

    c.setCache(ctx, key, value)
    return value, nil
}

func (c *RefreshableCache) asyncRefresh(key string) {
    ctx := context.Background()
    value, err := c.loader(ctx, key)
    if err != nil {
        slog.Error("cache refresh failed", "key", key, "error", err)
        return
    }
    c.setCache(ctx, key, value)
}

func (c *RefreshableCache) setCache(ctx context.Context, key string, value interface{}) {
    valueJSON, err := json.Marshal(value)
    if err != nil {
        return
    }
    c.redis.Set(ctx, key, valueJSON, c.ttl)
}
```

### Distributed Cache with Locking

```go
import (
    "github.com/bsm/redislock"
)

type DistributedCache struct {
    redis  *redis.Client
    locker *redislock.Client
}

func NewDistributedCache(redis *redis.Client) *DistributedCache {
    return &DistributedCache{
        redis:  redis,
        locker: redislock.New(redis),
    }
}

func (c *DistributedCache) GetOrLoad(ctx context.Context, key string, loader func() (interface{}, error)) (interface{}, error) {
    cached, err := c.redis.Get(ctx, key).Result()
    if err == nil {
        var value interface{}
        if err := json.Unmarshal([]byte(cached), &value); err == nil {
            return value, nil
        }
    }

    lockKey := fmt.Sprintf("lock:%s", key)
    lock, err := c.locker.Obtain(ctx, lockKey, 10*time.Second, nil)
    if err != nil {
        return nil, fmt.Errorf("failed to obtain lock: %w", err)
    }
    defer lock.Release(ctx)

    cached, err = c.redis.Get(ctx, key).Result()
    if err == nil {
        var value interface{}
        if err := json.Unmarshal([]byte(cached), &value); err == nil {
            return value, nil
        }
    }

    value, err := loader()
    if err != nil {
        return nil, err
    }

    valueJSON, err := json.Marshal(value)
    if err != nil {
        return value, nil
    }

    c.redis.Set(ctx, key, valueJSON, 1*time.Hour)

    return value, nil
}
```

### Cache Stampede Prevention

```go
import (
    "golang.org/x/sync/singleflight"
)

type StampedeProtectedCache struct {
    redis *redis.Client
    group singleflight.Group
}

func NewStampedeProtectedCache(redis *redis.Client) *StampedeProtectedCache {
    return &StampedeProtectedCache{
        redis: redis,
    }
}

func (c *StampedeProtectedCache) Get(ctx context.Context, key string, loader func() (interface{}, error)) (interface{}, error) {
    cached, err := c.redis.Get(ctx, key).Result()
    if err == nil {
        var value interface{}
        if err := json.Unmarshal([]byte(cached), &value); err == nil {
            return value, nil
        }
    }

    value, err, _ := c.group.Do(key, func() (interface{}, error) {
        cached, err := c.redis.Get(ctx, key).Result()
        if err == nil {
            var value interface{}
            if err := json.Unmarshal([]byte(cached), &value); err == nil {
                return value, nil
            }
        }

        value, err := loader()
        if err != nil {
            return nil, err
        }

        valueJSON, err := json.Marshal(value)
        if err != nil {
            return value, nil
        }

        c.redis.Set(ctx, key, valueJSON, 1*time.Hour)

        return value, nil
    })

    return value, err
}
```

## Cache Invalidation

### Manual Invalidation

```go
type CacheInvalidator struct {
    redis *redis.Client
}

func (i *CacheInvalidator) InvalidateKey(ctx context.Context, key string) error {
    return i.redis.Del(ctx, key).Err()
}

func (i *CacheInvalidator) InvalidatePattern(ctx context.Context, pattern string) error {
    var cursor uint64
    var keys []string

    for {
        var err error
        var batch []string

        batch, cursor, err = i.redis.Scan(ctx, cursor, pattern, 100).Result()
        if err != nil {
            return fmt.Errorf("scan failed: %w", err)
        }

        keys = append(keys, batch...)

        if cursor == 0 {
            break
        }
    }

    if len(keys) > 0 {
        if err := i.redis.Del(ctx, keys...).Err(); err != nil {
            return fmt.Errorf("delete failed: %w", err)
        }
    }

    return nil
}

func (i *CacheInvalidator) InvalidateByTags(ctx context.Context, tag string) error {
    tagKey := fmt.Sprintf("tag:%s", tag)

    members, err := i.redis.SMembers(ctx, tagKey).Result()
    if err != nil {
        return fmt.Errorf("failed to get tag members: %w", err)
    }

    if len(members) > 0 {
        if err := i.redis.Del(ctx, members...).Err(); err != nil {
            return fmt.Errorf("delete failed: %w", err)
        }
    }

    return i.redis.Del(ctx, tagKey).Err()
}
```

### Event-Based Invalidation

```go
type CacheEventHandler struct {
    redis *redis.Client
}

func (h *CacheEventHandler) OnUserUpdated(ctx context.Context, userID string) error {
    keys := []string{
        fmt.Sprintf("user:%s", userID),
        fmt.Sprintf("user:%s:profile", userID),
        fmt.Sprintf("user:%s:permissions", userID),
    }

    if err := h.redis.Del(ctx, keys...).Err(); err != nil {
        return fmt.Errorf("cache invalidation failed: %w", err)
    }

    return nil
}

func (h *CacheEventHandler) OnUserDeleted(ctx context.Context, userID string) error {
    pattern := fmt.Sprintf("user:%s*", userID)

    var cursor uint64
    var keys []string

    for {
        var err error
        var batch []string

        batch, cursor, err = h.redis.Scan(ctx, cursor, pattern, 100).Result()
        if err != nil {
            return fmt.Errorf("scan failed: %w", err)
        }

        keys = append(keys, batch...)

        if cursor == 0 {
            break
        }
    }

    if len(keys) > 0 {
        return h.redis.Del(ctx, keys...).Err()
    }

    return nil
}
```

## In-Memory Cache

### LRU Cache with sync.Map

```go
import (
    "container/list"
    "sync"
)

type LRUCache struct {
    capacity int
    cache    map[string]*list.Element
    order    *list.List
    mu       sync.RWMutex
}

type cacheEntry struct {
    key   string
    value interface{}
}

func NewLRUCache(capacity int) *LRUCache {
    return &LRUCache{
        capacity: capacity,
        cache:    make(map[string]*list.Element),
        order:    list.New(),
    }
}

func (c *LRUCache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    elem, exists := c.cache[key]
    c.mu.RUnlock()

    if !exists {
        return nil, false
    }

    c.mu.Lock()
    c.order.MoveToFront(elem)
    c.mu.Unlock()

    entry := elem.Value.(*cacheEntry)
    return entry.value, true
}

func (c *LRUCache) Set(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()

    if elem, exists := c.cache[key]; exists {
        c.order.MoveToFront(elem)
        elem.Value.(*cacheEntry).value = value
        return
    }

    if c.order.Len() >= c.capacity {
        oldest := c.order.Back()
        if oldest != nil {
            c.order.Remove(oldest)
            delete(c.cache, oldest.Value.(*cacheEntry).key)
        }
    }

    entry := &cacheEntry{key: key, value: value}
    elem := c.order.PushFront(entry)
    c.cache[key] = elem
}

func (c *LRUCache) Delete(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()

    if elem, exists := c.cache[key]; exists {
        c.order.Remove(elem)
        delete(c.cache, key)
    }
}
```

### TTL-Based In-Memory Cache

```go
type TTLCache struct {
    data map[string]cacheItem
    mu   sync.RWMutex
}

type cacheItem struct {
    value     interface{}
    expiresAt time.Time
}

func NewTTLCache() *TTLCache {
    cache := &TTLCache{
        data: make(map[string]cacheItem),
    }
    go cache.cleanup()
    return cache
}

func (c *TTLCache) Set(key string, value interface{}, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.data[key] = cacheItem{
        value:     value,
        expiresAt: time.Now().Add(ttl),
    }
}

func (c *TTLCache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()

    item, exists := c.data[key]
    if !exists {
        return nil, false
    }

    if time.Now().After(item.expiresAt) {
        return nil, false
    }

    return item.value, true
}

func (c *TTLCache) cleanup() {
    ticker := time.NewTicker(1 * time.Minute)
    defer ticker.Stop()

    for range ticker.C {
        c.mu.Lock()
        now := time.Now()
        for key, item := range c.data {
            if now.After(item.expiresAt) {
                delete(c.data, key)
            }
        }
        c.mu.Unlock()
    }
}
```

## Cache Middleware

### HTTP Cache Middleware

```go
func CacheMiddleware(cache *RedisCache, ttl time.Duration) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if r.Method != http.MethodGet {
                next.ServeHTTP(w, r)
                return
            }

            cacheKey := fmt.Sprintf("http:%s:%s", r.Method, r.URL.Path)

            cached, err := cache.Get(r.Context(), cacheKey)
            if err == nil {
                w.Header().Set("X-Cache", "HIT")
                w.Write(cached.([]byte))
                return
            }

            recorder := &responseRecorder{
                ResponseWriter: w,
                statusCode:     http.StatusOK,
                body:           &bytes.Buffer{},
            }

            next.ServeHTTP(recorder, r)

            if recorder.statusCode == http.StatusOK {
                cache.Set(r.Context(), cacheKey, recorder.body.Bytes(), ttl)
            }

            w.Header().Set("X-Cache", "MISS")
        })
    }
}

type responseRecorder struct {
    http.ResponseWriter
    statusCode int
    body       *bytes.Buffer
}

func (r *responseRecorder) WriteHeader(statusCode int) {
    r.statusCode = statusCode
    r.ResponseWriter.WriteHeader(statusCode)
}

func (r *responseRecorder) Write(b []byte) (int, error) {
    r.body.Write(b)
    return r.ResponseWriter.Write(b)
}
```

## Best Practices

### ✅ DO
- Use appropriate cache strategy for your use case (cache-aside, read-through, write-through)
- Set reasonable TTL values to prevent stale data
- Implement cache invalidation strategy
- Use cache stampede prevention for expensive operations
- Monitor cache hit/miss ratios
- Use Redis pipelining for batch operations
- Implement circuit breaker for cache failures
- Use proper serialization (JSON, MessagePack, Protocol Buffers)
- Consider cache warming for critical data
- Use cache tags for grouped invalidation

### ❌ DON'T
- Don't cache everything - only cache expensive operations
- Don't ignore cache failures - have fallback strategies
- Don't use unbounded cache keys - implement key rotation
- Don't cache sensitive data without encryption
- Don't forget to handle cache serialization errors
- Don't use cache as primary data store
- Don't ignore memory limits for in-memory caches
- Don't forget to close Redis connections
- Don't use blocking operations in hot paths

## Troubleshooting

### Common Issues

1. **Cache Stampede**: Multiple requests loading the same data
   - Solution: Use singleflight or distributed locking

2. **Memory Pressure**: Cache consuming too much memory
   - Solution: Implement LRU eviction or reduce TTL

3. **Stale Data**: Cache not invalidated on updates
   - Solution: Event-based invalidation or shorter TTL

4. **Connection Pool Exhaustion**: Too many Redis connections
   - Solution: Configure pool size and connection timeout

5. **Serialization Overhead**: Slow marshal/unmarshal
   - Solution: Use faster serialization formats (MessagePack, Protocol Buffers)

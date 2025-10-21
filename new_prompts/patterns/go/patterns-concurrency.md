# Concurrency Patterns

Comprehensive concurrency patterns using goroutines, channels, and synchronization primitives.

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

## Core Concurrency Principles

- Use channels for communication between goroutines
- Use mutexes for protecting shared state
- Always use context.Context for cancellation and timeouts
- Make goroutine lifetimes obvious
- Prevent goroutine leaks

## Worker Pool Pattern

### Basic Worker Pool

```go
type WorkerPool struct {
    workers    int
    jobQueue   chan Job
    results    chan Result
    wg         sync.WaitGroup
}

type Job struct {
    ID   int
    Data interface{}
}

type Result struct {
    JobID int
    Data  interface{}
    Error error
}

func NewWorkerPool(workers int, queueSize int) *WorkerPool {
    return &WorkerPool{
        workers:  workers,
        jobQueue: make(chan Job, queueSize),
        results:  make(chan Result, queueSize),
    }
}

func (wp *WorkerPool) Start(ctx context.Context) {
    for i := 0; i < wp.workers; i++ {
        wp.wg.Add(1)
        go wp.worker(ctx, i)
    }
}

func (wp *WorkerPool) worker(ctx context.Context, id int) {
    defer wp.wg.Done()

    for {
        select {
        case job, ok := <-wp.jobQueue:
            if !ok {
                return // Channel closed
            }

            result := wp.processJob(job)
            wp.results <- result

        case <-ctx.Done():
            return // Context cancelled
        }
    }
}

func (wp *WorkerPool) processJob(job Job) Result {
    // Process job
    data, err := doWork(job.Data)

    return Result{
        JobID: job.ID,
        Data:  data,
        Error: err,
    }
}

func (wp *WorkerPool) Submit(job Job) {
    wp.jobQueue <- job
}

func (wp *WorkerPool) Results() <-chan Result {
    return wp.results
}

func (wp *WorkerPool) Close() {
    close(wp.jobQueue)
    wp.wg.Wait()
    close(wp.results)
}

// Usage
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    pool := NewWorkerPool(5, 100)
    pool.Start(ctx)

    // Submit jobs
    for i := 0; i < 100; i++ {
        pool.Submit(Job{ID: i, Data: i})
    }

    // Collect results
    go func() {
        for result := range pool.Results() {
            if result.Error != nil {
                log.Printf("Job %d failed: %v", result.JobID, result.Error)
            } else {
                log.Printf("Job %d completed: %v", result.JobID, result.Data)
            }
        }
    }()

    pool.Close()
}
```

## Context Patterns

### Context with Timeout

```go
func ProcessWithTimeout(ctx context.Context, id string) error {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    resultCh := make(chan error, 1)

    go func() {
        // Simulate long-running operation
        user, err := GetUser(id)
        if err != nil {
            resultCh <- fmt.Errorf("get user: %w", err)
            return
        }

        if err := ProcessUser(user); err != nil {
            resultCh <- fmt.Errorf("process user: %w", err)
            return
        }

        resultCh <- nil
    }()

    select {
    case err := <-resultCh:
        return err
    case <-ctx.Done():
        return fmt.Errorf("operation timeout: %w", ctx.Err())
    }
}
```

### Context Cancellation

```go
func LongRunningOperation(ctx context.Context) error {
    for i := 0; i < 1000; i++ {
        // Check for cancellation regularly
        select {
        case <-ctx.Done():
            return fmt.Errorf("operation canceled at step %d: %w", i, ctx.Err())
        default:
        }

        // Do work
        if err := doStep(i); err != nil {
            return fmt.Errorf("step %d failed: %w", i, err)
        }

        time.Sleep(100 * time.Millisecond)
    }

    return nil
}

// Usage with cancellation
func main() {
    ctx, cancel := context.WithCancel(context.Background())

    go func() {
        if err := LongRunningOperation(ctx); err != nil {
            log.Printf("Operation failed: %v", err)
        }
    }()

    // Cancel after some condition
    time.Sleep(5 * time.Second)
    cancel()
}
```

### Context with Values (Use Sparingly)

```go
type contextKey string

const (
    userIDKey    contextKey = "user_id"
    requestIDKey contextKey = "request_id"
)

// Set context value
func WithUserID(ctx context.Context, userID string) context.Context {
    return context.WithValue(ctx, userIDKey, userID)
}

// Get context value
func GetUserID(ctx context.Context) (string, bool) {
    userID, ok := ctx.Value(userIDKey).(string)
    return userID, ok
}

// Usage in middleware
func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        userID := extractUserID(r)
        ctx := WithUserID(r.Context(), userID)

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## Channel Patterns

### Fan-Out, Fan-In Pattern

```go
// Fan-out: Distribute work to multiple workers
func fanOut(ctx context.Context, input <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)

    for i := 0; i < workers; i++ {
        channels[i] = worker(ctx, input)
    }

    return channels
}

func worker(ctx context.Context, input <-chan int) <-chan int {
    output := make(chan int)

    go func() {
        defer close(output)

        for {
            select {
            case value, ok := <-input:
                if !ok {
                    return
                }

                // Process value
                result := value * 2

                select {
                case output <- result:
                case <-ctx.Done():
                    return
                }

            case <-ctx.Done():
                return
            }
        }
    }()

    return output
}

// Fan-in: Merge multiple channels into one
func fanIn(ctx context.Context, channels ...<-chan int) <-chan int {
    output := make(chan int)
    var wg sync.WaitGroup

    multiplex := func(ch <-chan int) {
        defer wg.Done()

        for {
            select {
            case value, ok := <-ch:
                if !ok {
                    return
                }

                select {
                case output <- value:
                case <-ctx.Done():
                    return
                }

            case <-ctx.Done():
                return
            }
        }
    }

    wg.Add(len(channels))
    for _, ch := range channels {
        go multiplex(ch)
    }

    go func() {
        wg.Wait()
        close(output)
    }()

    return output
}

// Usage
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    input := make(chan int)

    // Fan-out to 5 workers
    workers := fanOut(ctx, input, 5)

    // Fan-in results
    results := fanIn(ctx, workers...)

    // Send work
    go func() {
        for i := 0; i < 100; i++ {
            input <- i
        }
        close(input)
    }()

    // Collect results
    for result := range results {
        fmt.Println(result)
    }
}
```

### Pipeline Pattern

```go
// Stage 1: Generate numbers
func generate(ctx context.Context, nums ...int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)

        for _, n := range nums {
            select {
            case out <- n:
            case <-ctx.Done():
                return
            }
        }
    }()

    return out
}

// Stage 2: Square numbers
func square(ctx context.Context, in <-chan int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)

        for {
            select {
            case n, ok := <-in:
                if !ok {
                    return
                }

                select {
                case out <- n * n:
                case <-ctx.Done():
                    return
                }

            case <-ctx.Done():
                return
            }
        }
    }()

    return out
}

// Stage 3: Filter even numbers
func filterEven(ctx context.Context, in <-chan int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)

        for {
            select {
            case n, ok := <-in:
                if !ok {
                    return
                }

                if n%2 == 0 {
                    select {
                    case out <- n:
                    case <-ctx.Done():
                        return
                    }
                }

            case <-ctx.Done():
                return
            }
        }
    }()

    return out
}

// Usage: Create pipeline
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // Build pipeline
    nums := generate(ctx, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    squared := square(ctx, nums)
    even := filterEven(ctx, squared)

    // Consume results
    for result := range even {
        fmt.Println(result) // 4, 16, 36, 64, 100
    }
}
```

## Synchronization Patterns

### Mutex for Shared State

```go
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}

func (c *Counter) Get() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}

// RWMutex for read-heavy workloads
type Cache struct {
    mu    sync.RWMutex
    data  map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()

    value, ok := c.data[key]
    return value, ok
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.data[key] = value
}
```

### sync.Once for One-Time Initialization

```go
type Database struct {
    conn *sql.DB
}

var (
    dbInstance *Database
    once       sync.Once
)

func GetDatabase() *Database {
    once.Do(func() {
        conn, err := sql.Open("postgres", "connection-string")
        if err != nil {
            log.Fatal(err)
        }

        dbInstance = &Database{conn: conn}
    })

    return dbInstance
}
```

### sync.WaitGroup for Goroutine Coordination

```go
func ProcessBatch(items []Item) error {
    var wg sync.WaitGroup
    errChan := make(chan error, len(items))

    for _, item := range items {
        wg.Add(1)

        go func(item Item) {
            defer wg.Done()

            if err := processItem(item); err != nil {
                errChan <- fmt.Errorf("process item %s: %w", item.ID, err)
            }
        }(item)
    }

    // Wait for all goroutines
    wg.Wait()
    close(errChan)

    // Collect errors
    var errs []error
    for err := range errChan {
        errs = append(errs, err)
    }

    if len(errs) > 0 {
        return errors.Join(errs...)
    }

    return nil
}
```

### errgroup for Error Handling

```go
import "golang.org/x/sync/errgroup"

func ProcessWithErrGroup(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, item := range items {
        item := item // Capture for goroutine

        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    // Wait for all goroutines and return first error
    return g.Wait()
}

// With limited concurrency
func ProcessWithLimit(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // Max 10 concurrent goroutines

    for _, item := range items {
        item := item

        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    return g.Wait()
}
```

## Graceful Shutdown

### HTTP Server Graceful Shutdown

```go
func RunServer(ctx context.Context) error {
    server := &http.Server{
        Addr:    ":8080",
        Handler: setupRoutes(),
    }

    // Channel to listen for errors
    serverErrors := make(chan error, 1)

    // Start server
    go func() {
        log.Println("Server starting on :8080")
        serverErrors <- server.ListenAndServe()
    }()

    // Block until we receive a signal or server error
    select {
    case err := <-serverErrors:
        return fmt.Errorf("server error: %w", err)

    case <-ctx.Done():
        log.Println("Shutting down server...")

        // Give outstanding requests 30 seconds to complete
        shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        if err := server.Shutdown(shutdownCtx); err != nil {
            server.Close()
            return fmt.Errorf("graceful shutdown failed: %w", err)
        }

        log.Println("Server stopped gracefully")
        return nil
    }
}

// Main with signal handling
func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // Listen for interrupt signals
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

    go func() {
        <-sigChan
        log.Println("Interrupt signal received")
        cancel()
    }()

    if err := RunServer(ctx); err != nil {
        log.Fatal(err)
    }
}
```

## Common Pitfalls and Solutions

### ❌ Goroutine Leak

```go
// DON'T: Goroutine leak - channel never closes
func leak() <-chan int {
    ch := make(chan int)

    go func() {
        for i := 0; ; i++ {
            ch <- i  // Will block forever after consumer stops
        }
    }()

    return ch
}

// ✅ DO: Properly handle context cancellation
func noLeak(ctx context.Context) <-chan int {
    ch := make(chan int)

    go func() {
        defer close(ch)

        for i := 0; ; i++ {
            select {
            case ch <- i:
            case <-ctx.Done():
                return  // Properly exit goroutine
            }
        }
    }()

    return ch
}
```

### ❌ Race Condition

```go
// DON'T: Race condition
type Counter struct {
    value int
}

func (c *Counter) Increment() {
    c.value++  // Race!
}

// ✅ DO: Use mutex or atomic
type SafeCounter struct {
    value int64
}

func (c *SafeCounter) Increment() {
    atomic.AddInt64(&c.value, 1)
}

// Or with mutex
type MutexCounter struct {
    mu    sync.Mutex
    value int
}

func (c *MutexCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.value++
}
```

## Best Practices

### ✅ DO
- Use context.Context for cancellation and timeouts
- Always provide a way to stop goroutines
- Use channels for communication, mutexes for state
- Make goroutine ownership clear
- Use sync.WaitGroup or errgroup for coordination
- Implement graceful shutdown
- Use buffered channels to prevent blocking
- Check for context cancellation in loops
- Use atomic operations for simple counters

### ❌ DON'T
- Don't start goroutines without a way to stop them
- Don't share memory without synchronization
- Don't use unbuffered channels in same goroutine
- Don't forget to close channels when done
- Don't ignore context cancellation
- Don't use channels for synchronization (use WaitGroup)
- Don't use sleep for synchronization
- Don't forget defer for unlocking mutexes

---

## Related Files

- **[patterns-testing]mcp://resources/patterns/go/patterns-testing** - Race detector (`go test -race`), testing concurrent code safely
- **[patterns-database]mcp://resources/patterns/go/patterns-database** - Connection pooling, database operations with goroutines
- **[patterns-error-handling]mcp://resources/patterns/go/patterns-error-handling** - Error handling in goroutines, errgroup patterns
- **[patterns-api]mcp://resources/patterns/go/patterns-api** - Concurrent request handling, timeout patterns
- **[patterns-observability]mcp://resources/patterns/go/patterns-observability** - Logging from goroutines, structured logging best practices

---

## External References

- **Go Concurrency Patterns**: https://go.dev/blog/pipelines
- **Context Package**: https://pkg.go.dev/context
- **errgroup**: https://pkg.go.dev/golang.org/x/sync/errgroup
- **Go Concurrency Guide**: https://github.com/golang/go/wiki/CommonMistakes#concurrency

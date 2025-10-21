# CLI Application Patterns

Command-line application patterns using Cobra framework in Go.

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

## Cobra Framework Setup

### Basic CLI Structure

```go
import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "A brief description of your application",
    Long: `A longer description that spans multiple lines and likely contains
examples and usage of using your application.`,
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func init() {
    rootCmd.AddCommand(versionCmd)
    rootCmd.AddCommand(serveCmd)
    rootCmd.AddCommand(migrateCmd)
}

func main() {
    Execute()
}
```

### Version Command

```go
import (
    "fmt"
    "github.com/spf13/cobra"
)

var (
    version   = "dev"
    commit    = "none"
    buildTime = "unknown"
)

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Print the version number",
    Long:  `Print the version number, git commit, and build time`,
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Printf("Version:    %s\n", version)
        fmt.Printf("Commit:     %s\n", commit)
        fmt.Printf("Build Time: %s\n", buildTime)
    },
}
```

## Subcommands

### Server Command

```go
import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/spf13/cobra"
)

var (
    port     int
    host     string
    logLevel string
)

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Start the HTTP server",
    Long:  `Start the HTTP server and listen for incoming requests`,
    RunE:  runServer,
}

func init() {
    serveCmd.Flags().IntVarP(&port, "port", "p", 8080, "Port to listen on")
    serveCmd.Flags().StringVarP(&host, "host", "H", "0.0.0.0", "Host to bind to")
    serveCmd.Flags().StringVarP(&logLevel, "log-level", "l", "info", "Log level (debug, info, warn, error)")
}

func runServer(cmd *cobra.Command, args []string) error {
    setLogLevel(logLevel)

    server := &http.Server{
        Addr:         fmt.Sprintf("%s:%d", host, port),
        Handler:      setupRouter(),
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    serverErrors := make(chan error, 1)

    go func() {
        slog.Info("server starting", "host", host, "port", port)
        serverErrors <- server.ListenAndServe()
    }()

    shutdown := make(chan os.Signal, 1)
    signal.Notify(shutdown, os.Interrupt, syscall.SIGTERM)

    select {
    case err := <-serverErrors:
        return fmt.Errorf("server error: %w", err)

    case sig := <-shutdown:
        slog.Info("shutdown signal received", "signal", sig)

        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        if err := server.Shutdown(ctx); err != nil {
            server.Close()
            return fmt.Errorf("graceful shutdown failed: %w", err)
        }

        slog.Info("server stopped")
    }

    return nil
}

func setLogLevel(level string) {
    var logLevel slog.Level
    switch level {
    case "debug":
        logLevel = slog.LevelDebug
    case "info":
        logLevel = slog.LevelInfo
    case "warn":
        logLevel = slog.LevelWarn
    case "error":
        logLevel = slog.LevelError
    default:
        logLevel = slog.LevelInfo
    }

    slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: logLevel,
    })))
}
```

### Database Migration Command

```go
import (
    "database/sql"
    "github.com/golang-migrate/migrate/v4"
    "github.com/golang-migrate/migrate/v4/database/postgres"
    _ "github.com/golang-migrate/migrate/v4/source/file"
    "github.com/spf13/cobra"
)

var (
    migrationsPath string
    dbURL          string
)

var migrateCmd = &cobra.Command{
    Use:   "migrate",
    Short: "Database migration commands",
    Long:  `Run database migrations up or down`,
}

var migrateUpCmd = &cobra.Command{
    Use:   "up",
    Short: "Run all pending migrations",
    RunE:  migrateUp,
}

var migrateDownCmd = &cobra.Command{
    Use:   "down",
    Short: "Rollback the last migration",
    RunE:  migrateDown,
}

var migrateStatusCmd = &cobra.Command{
    Use:   "status",
    Short: "Show migration status",
    RunE:  migrateStatus,
}

func init() {
    migrateCmd.PersistentFlags().StringVar(&migrationsPath, "path", "./migrations", "Path to migrations directory")
    migrateCmd.PersistentFlags().StringVar(&dbURL, "database-url", os.Getenv("DATABASE_URL"), "Database URL")

    migrateCmd.AddCommand(migrateUpCmd)
    migrateCmd.AddCommand(migrateDownCmd)
    migrateCmd.AddCommand(migrateStatusCmd)
}

func createMigration() (*migrate.Migrate, error) {
    db, err := sql.Open("postgres", dbURL)
    if err != nil {
        return nil, fmt.Errorf("failed to connect to database: %w", err)
    }

    driver, err := postgres.WithInstance(db, &postgres.Config{})
    if err != nil {
        return nil, fmt.Errorf("failed to create driver: %w", err)
    }

    m, err := migrate.NewWithDatabaseInstance(
        fmt.Sprintf("file://%s", migrationsPath),
        "postgres",
        driver,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to create migration: %w", err)
    }

    return m, nil
}

func migrateUp(cmd *cobra.Command, args []string) error {
    m, err := createMigration()
    if err != nil {
        return err
    }
    defer m.Close()

    if err := m.Up(); err != nil && err != migrate.ErrNoChange {
        return fmt.Errorf("migration up failed: %w", err)
    }

    slog.Info("migrations completed successfully")
    return nil
}

func migrateDown(cmd *cobra.Command, args []string) error {
    m, err := createMigration()
    if err != nil {
        return err
    }
    defer m.Close()

    if err := m.Steps(-1); err != nil && err != migrate.ErrNoChange {
        return fmt.Errorf("migration down failed: %w", err)
    }

    slog.Info("rollback completed successfully")
    return nil
}

func migrateStatus(cmd *cobra.Command, args []string) error {
    m, err := createMigration()
    if err != nil {
        return err
    }
    defer m.Close()

    version, dirty, err := m.Version()
    if err != nil && err != migrate.ErrNilVersion {
        return fmt.Errorf("failed to get version: %w", err)
    }

    if err == migrate.ErrNilVersion {
        fmt.Println("No migrations have been applied")
        return nil
    }

    fmt.Printf("Current version: %d\n", version)
    fmt.Printf("Dirty: %t\n", dirty)

    return nil
}
```

## Configuration Management

### Config File Support

```go
import (
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var cfgFile string

func init() {
    cobra.OnInitialize(initConfig)

    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.myapp.yaml)")
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        home, err := os.UserHomeDir()
        if err != nil {
            fmt.Fprintln(os.Stderr, err)
            os.Exit(1)
        }

        viper.AddConfigPath(home)
        viper.AddConfigPath(".")
        viper.SetConfigType("yaml")
        viper.SetConfigName(".myapp")
    }

    viper.AutomaticEnv()

    if err := viper.ReadInConfig(); err == nil {
        slog.Info("using config file", "file", viper.ConfigFileUsed())
    }
}

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Redis    RedisConfig    `mapstructure:"redis"`
}

type ServerConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    LogLevel string `mapstructure:"log_level"`
}

type DatabaseConfig struct {
    URL             string `mapstructure:"url"`
    MaxOpenConns    int    `mapstructure:"max_open_conns"`
    MaxIdleConns    int    `mapstructure:"max_idle_conns"`
    ConnMaxLifetime int    `mapstructure:"conn_max_lifetime"`
}

type RedisConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Password string `mapstructure:"password"`
    DB       int    `mapstructure:"db"`
}

func loadConfig() (*Config, error) {
    var config Config

    if err := viper.Unmarshal(&config); err != nil {
        return nil, fmt.Errorf("failed to unmarshal config: %w", err)
    }

    return &config, nil
}
```

### Environment Variable Binding

```go
func init() {
    viper.SetEnvPrefix("MYAPP")
    viper.AutomaticEnv()

    viper.BindEnv("server.host", "MYAPP_SERVER_HOST")
    viper.BindEnv("server.port", "MYAPP_SERVER_PORT")
    viper.BindEnv("database.url", "MYAPP_DATABASE_URL")

    viper.SetDefault("server.host", "0.0.0.0")
    viper.SetDefault("server.port", 8080)
    viper.SetDefault("server.log_level", "info")
    viper.SetDefault("database.max_open_conns", 25)
    viper.SetDefault("database.max_idle_conns", 25)
}
```

## Persistent and Local Flags

### Persistent Flags

```go
var (
    verbose bool
    output  string
)

func init() {
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")
    rootCmd.PersistentFlags().StringVarP(&output, "output", "o", "text", "output format (text, json, yaml)")
}
```

### Local Flags

```go
var (
    all   bool
    limit int
)

var listCmd = &cobra.Command{
    Use:   "list",
    Short: "List items",
    RunE:  runList,
}

func init() {
    listCmd.Flags().BoolVar(&all, "all", false, "show all items")
    listCmd.Flags().IntVarP(&limit, "limit", "n", 10, "limit number of items")

    listCmd.MarkFlagRequired("limit")
}
```

## Required and Mutually Exclusive Flags

### Required Flags

```go
var createCmd = &cobra.Command{
    Use:   "create",
    Short: "Create a new resource",
    RunE:  runCreate,
}

func init() {
    createCmd.Flags().StringVar(&name, "name", "", "resource name")
    createCmd.Flags().StringVar(&resourceType, "type", "", "resource type")

    createCmd.MarkFlagRequired("name")
    createCmd.MarkFlagRequired("type")
}
```

### Mutually Exclusive Flags

```go
var deployCmd = &cobra.Command{
    Use:   "deploy",
    Short: "Deploy application",
    PreRunE: func(cmd *cobra.Command, args []string) error {
        staging := cmd.Flags().Changed("staging")
        production := cmd.Flags().Changed("production")

        if staging && production {
            return errors.New("cannot use --staging and --production together")
        }

        if !staging && !production {
            return errors.New("must specify either --staging or --production")
        }

        return nil
    },
    RunE: runDeploy,
}

func init() {
    deployCmd.Flags().Bool("staging", false, "deploy to staging")
    deployCmd.Flags().Bool("production", false, "deploy to production")
}
```

## Interactive CLI

### Prompts with Survey

```go
import (
    "github.com/AlecAivazis/survey/v2"
)

func promptForInput() error {
    var name string
    prompt := &survey.Input{
        Message: "Enter your name:",
    }
    if err := survey.AskOne(prompt, &name); err != nil {
        return err
    }

    var email string
    emailPrompt := &survey.Input{
        Message: "Enter your email:",
    }
    if err := survey.AskOne(emailPrompt, &email, survey.WithValidator(survey.Required)); err != nil {
        return err
    }

    var role string
    selectPrompt := &survey.Select{
        Message: "Choose a role:",
        Options: []string{"admin", "user", "guest"},
    }
    if err := survey.AskOne(selectPrompt, &role); err != nil {
        return err
    }

    var confirm bool
    confirmPrompt := &survey.Confirm{
        Message: fmt.Sprintf("Create user %s (%s) with role %s?", name, email, role),
    }
    if err := survey.AskOne(confirmPrompt, &confirm); err != nil {
        return err
    }

    if !confirm {
        fmt.Println("Operation cancelled")
        return nil
    }

    fmt.Printf("Created user: %s (%s) - %s\n", name, email, role)
    return nil
}

var createUserCmd = &cobra.Command{
    Use:   "create-user",
    Short: "Create a new user interactively",
    RunE: func(cmd *cobra.Command, args []string) error {
        return promptForInput()
    },
}
```

## Progress Indicators

### Progress Bar

```go
import (
    "github.com/schollz/progressbar/v3"
)

func processWithProgress() error {
    items := []string{"item1", "item2", "item3", "item4", "item5"}

    bar := progressbar.NewOptions(len(items),
        progressbar.OptionSetDescription("Processing items"),
        progressbar.OptionSetWidth(40),
        progressbar.OptionShowCount(),
        progressbar.OptionShowIts(),
        progressbar.OptionSetPredictTime(true),
    )

    for _, item := range items {
        time.Sleep(500 * time.Millisecond)

        bar.Add(1)

        if verbose {
            fmt.Printf("\nProcessed: %s\n", item)
        }
    }

    fmt.Println("\nProcessing complete!")
    return nil
}

var processCmd = &cobra.Command{
    Use:   "process",
    Short: "Process items with progress bar",
    RunE: func(cmd *cobra.Command, args []string) error {
        return processWithProgress()
    },
}
```

### Spinner

```go
import (
    "github.com/briandowns/spinner"
)

func longRunningTask() error {
    s := spinner.New(spinner.CharSets[9], 100*time.Millisecond)
    s.Suffix = " Working..."
    s.Start()

    time.Sleep(5 * time.Second)

    s.Stop()
    fmt.Println("Task completed!")

    return nil
}
```

## Output Formatting

### Table Output

```go
import (
    "github.com/olekukonko/tablewriter"
)

type User struct {
    ID    string
    Name  string
    Email string
    Role  string
}

func displayUsersTable(users []User) {
    table := tablewriter.NewWriter(os.Stdout)
    table.SetHeader([]string{"ID", "Name", "Email", "Role"})

    for _, user := range users {
        table.Append([]string{user.ID, user.Name, user.Email, user.Role})
    }

    table.Render()
}

func displayUsersJSON(users []User) error {
    data, err := json.MarshalIndent(users, "", "  ")
    if err != nil {
        return err
    }
    fmt.Println(string(data))
    return nil
}

func displayUsersYAML(users []User) error {
    data, err := yaml.Marshal(users)
    if err != nil {
        return err
    }
    fmt.Println(string(data))
    return nil
}

var listUsersCmd = &cobra.Command{
    Use:   "list",
    Short: "List all users",
    RunE: func(cmd *cobra.Command, args []string) error {
        users := []User{
            {ID: "1", Name: "Alice", Email: "alice@example.com", Role: "admin"},
            {ID: "2", Name: "Bob", Email: "bob@example.com", Role: "user"},
        }

        switch output {
        case "json":
            return displayUsersJSON(users)
        case "yaml":
            return displayUsersYAML(users)
        default:
            displayUsersTable(users)
        }

        return nil
    },
}
```

## Shell Completion

### Bash Completion

```go
var completionCmd = &cobra.Command{
    Use:   "completion [bash|zsh|fish|powershell]",
    Short: "Generate completion script",
    Long: `Generate the autocompletion script for the specified shell.`,
    DisableFlagsInUseLine: true,
    ValidArgs: []string{"bash", "zsh", "fish", "powershell"},
    Args:      cobra.ExactValidArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        switch args[0] {
        case "bash":
            cmd.Root().GenBashCompletion(os.Stdout)
        case "zsh":
            cmd.Root().GenZshCompletion(os.Stdout)
        case "fish":
            cmd.Root().GenFishCompletion(os.Stdout, true)
        case "powershell":
            cmd.Root().GenPowerShellCompletionWithDesc(os.Stdout)
        }
    },
}
```

### Dynamic Completion

```go
var getUserCmd = &cobra.Command{
    Use:   "get [user-id]",
    Short: "Get user by ID",
    Args:  cobra.ExactArgs(1),
    ValidArgsFunction: func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
        if len(args) != 0 {
            return nil, cobra.ShellCompDirectiveNoFileComp
        }

        userIDs := []string{"user-1", "user-2", "user-3"}
        return userIDs, cobra.ShellCompDirectiveNoFileComp
    },
    RunE: runGetUser,
}
```

## Error Handling

### Graceful Error Handling

```go
func runWithErrorHandling(cmd *cobra.Command, args []string) error {
    if err := validateArgs(args); err != nil {
        return fmt.Errorf("validation failed: %w", err)
    }

    if err := performOperation(); err != nil {
        return fmt.Errorf("operation failed: %w", err)
    }

    return nil
}

var myCmd = &cobra.Command{
    Use:          "mycommand",
    Short:        "Description",
    SilenceUsage: true,
    RunE:         runWithErrorHandling,
}
```

### Custom Error Types

```go
type CLIError struct {
    Code    int
    Message string
    Err     error
}

func (e *CLIError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Err)
    }
    return e.Message
}

func newCLIError(code int, message string, err error) *CLIError {
    return &CLIError{
        Code:    code,
        Message: message,
        Err:     err,
    }
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        if cliErr, ok := err.(*CLIError); ok {
            fmt.Fprintf(os.Stderr, "Error: %s\n", cliErr.Message)
            os.Exit(cliErr.Code)
        }
        fmt.Fprintf(os.Stderr, "Error: %v\n", err)
        os.Exit(1)
    }
}
```

## Testing CLI Commands

### Command Testing

```go
import (
    "bytes"
    "testing"
)

func executeCommand(root *cobra.Command, args ...string) (output string, err error) {
    buf := new(bytes.Buffer)
    root.SetOut(buf)
    root.SetErr(buf)
    root.SetArgs(args)

    err = root.Execute()
    return buf.String(), err
}

func TestVersionCommand(t *testing.T) {
    output, err := executeCommand(rootCmd, "version")
    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }

    if !strings.Contains(output, "Version:") {
        t.Errorf("expected version in output, got: %s", output)
    }
}

func TestServeCommand(t *testing.T) {
    _, err := executeCommand(rootCmd, "serve", "--port", "9090")
    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }
}
```

## Best Practices

### ✅ DO
- Use meaningful command and flag names
- Provide short and long descriptions for all commands
- Implement proper flag validation
- Use persistent flags for common options
- Support multiple output formats (text, JSON, YAML)
- Implement shell completion
- Provide helpful error messages
- Use semantic versioning for CLI tools
- Implement graceful shutdown for long-running commands
- Add examples in command help text

### ❌ DON'T
- Don't expose internal errors to users
- Don't ignore flag parsing errors
- Don't hardcode configuration values
- Don't skip input validation
- Don't use inconsistent flag naming
- Don't forget to handle interrupts (SIGINT, SIGTERM)
- Don't make too many required flags
- Don't skip documentation for commands
- Don't ignore exit codes
- Don't block indefinitely without timeout

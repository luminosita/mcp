# gRPC Patterns

gRPC service implementation patterns and best practices for Go applications.

**← [Back to Go Development Guide](./CLAUDE-core.md)**

## Proto Definitions

### Basic Service Definition

```protobuf
syntax = "proto3";

package user.v1;

option go_package = "github.com/myapp/gen/user/v1;userv1";

import "google/protobuf/timestamp.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  google.protobuf.Timestamp created_at = 4;
  google.protobuf.Timestamp updated_at = 5;
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
}

message CreateUserResponse {
  User user = 1;
}

message UpdateUserRequest {
  string id = 1;
  string email = 2;
  string name = 3;
}

message UpdateUserResponse {
  User user = 1;
}

message DeleteUserRequest {
  string id = 1;
}

message DeleteUserResponse {
  bool success = 1;
}
```

### Streaming Service Definition

```protobuf
syntax = "proto3";

package stream.v1;

option go_package = "github.com/myapp/gen/stream/v1;streamv1";

service StreamService {
  rpc ServerStream(ServerStreamRequest) returns (stream ServerStreamResponse);

  rpc ClientStream(stream ClientStreamRequest) returns (ClientStreamResponse);

  rpc BidirectionalStream(stream BidiRequest) returns (stream BidiResponse);
}

message ServerStreamRequest {
  string query = 1;
}

message ServerStreamResponse {
  string data = 1;
  int32 sequence = 2;
}

message ClientStreamRequest {
  bytes chunk = 1;
}

message ClientStreamResponse {
  int64 total_bytes = 1;
  string checksum = 2;
}

message BidiRequest {
  string message = 1;
}

message BidiResponse {
  string reply = 1;
}
```

## Server Implementation

### Basic gRPC Server

```go
import (
    "context"
    "fmt"
    "net"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"

    userv1 "github.com/myapp/gen/user/v1"
)

type UserServer struct {
    userv1.UnimplementedUserServiceServer
    userRepo UserRepository
}

func NewUserServer(userRepo UserRepository) *UserServer {
    return &UserServer{
        userRepo: userRepo,
    }
}

func (s *UserServer) GetUser(ctx context.Context, req *userv1.GetUserRequest) (*userv1.GetUserResponse, error) {
    if req.Id == "" {
        return nil, status.Error(codes.InvalidArgument, "user id is required")
    }

    user, err := s.userRepo.FindByID(ctx, req.Id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            return nil, status.Error(codes.NotFound, "user not found")
        }
        return nil, status.Error(codes.Internal, "failed to fetch user")
    }

    return &userv1.GetUserResponse{
        User: &userv1.User{
            Id:    user.ID,
            Email: user.Email,
            Name:  user.Name,
        },
    }, nil
}

func (s *UserServer) CreateUser(ctx context.Context, req *userv1.CreateUserRequest) (*userv1.CreateUserResponse, error) {
    if req.Email == "" {
        return nil, status.Error(codes.InvalidArgument, "email is required")
    }
    if req.Name == "" {
        return nil, status.Error(codes.InvalidArgument, "name is required")
    }

    user := &User{
        Email: req.Email,
        Name:  req.Name,
    }

    if err := s.userRepo.Create(ctx, user); err != nil {
        return nil, status.Error(codes.Internal, "failed to create user")
    }

    return &userv1.CreateUserResponse{
        User: &userv1.User{
            Id:    user.ID,
            Email: user.Email,
            Name:  user.Name,
        },
    }, nil
}

func StartGRPCServer(addr string, userRepo UserRepository) error {
    lis, err := net.Listen("tcp", addr)
    if err != nil {
        return fmt.Errorf("failed to listen: %w", err)
    }

    grpcServer := grpc.NewServer()

    userServer := NewUserServer(userRepo)
    userv1.RegisterUserServiceServer(grpcServer, userServer)

    slog.Info("gRPC server starting", "addr", addr)

    if err := grpcServer.Serve(lis); err != nil {
        return fmt.Errorf("failed to serve: %w", err)
    }

    return nil
}
```

### Server with TLS

```go
import (
    "crypto/tls"
    "google.golang.org/grpc/credentials"
)

func StartSecureGRPCServer(addr, certFile, keyFile string, userRepo UserRepository) error {
    cert, err := tls.LoadX509KeyPair(certFile, keyFile)
    if err != nil {
        return fmt.Errorf("failed to load key pair: %w", err)
    }

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{cert},
        MinVersion:   tls.VersionTLS12,
    }

    creds := credentials.NewTLS(tlsConfig)

    grpcServer := grpc.NewServer(
        grpc.Creds(creds),
    )

    userServer := NewUserServer(userRepo)
    userv1.RegisterUserServiceServer(grpcServer, userServer)

    lis, err := net.Listen("tcp", addr)
    if err != nil {
        return fmt.Errorf("failed to listen: %w", err)
    }

    return grpcServer.Serve(lis)
}
```

## Server Streaming

```go
import (
    "time"
    streamv1 "github.com/myapp/gen/stream/v1"
)

type StreamServer struct {
    streamv1.UnimplementedStreamServiceServer
}

func (s *StreamServer) ServerStream(req *streamv1.ServerStreamRequest, stream streamv1.StreamService_ServerStreamServer) error {
    if req.Query == "" {
        return status.Error(codes.InvalidArgument, "query is required")
    }

    for i := 0; i < 10; i++ {
        if err := stream.Context().Err(); err != nil {
            return status.Error(codes.Canceled, "stream canceled")
        }

        resp := &streamv1.ServerStreamResponse{
            Data:     fmt.Sprintf("Result %d for query: %s", i, req.Query),
            Sequence: int32(i),
        }

        if err := stream.Send(resp); err != nil {
            return status.Errorf(codes.Internal, "failed to send: %v", err)
        }

        time.Sleep(100 * time.Millisecond)
    }

    return nil
}
```

## Client Streaming

```go
import (
    "crypto/sha256"
    "io"
)

func (s *StreamServer) ClientStream(stream streamv1.StreamService_ClientStreamServer) error {
    var totalBytes int64
    hash := sha256.New()

    for {
        req, err := stream.Recv()
        if err == io.EOF {
            checksum := fmt.Sprintf("%x", hash.Sum(nil))

            return stream.SendAndClose(&streamv1.ClientStreamResponse{
                TotalBytes: totalBytes,
                Checksum:   checksum,
            })
        }
        if err != nil {
            return status.Errorf(codes.Internal, "failed to receive: %v", err)
        }

        totalBytes += int64(len(req.Chunk))
        hash.Write(req.Chunk)
    }
}
```

## Bidirectional Streaming

```go
func (s *StreamServer) BidirectionalStream(stream streamv1.StreamService_BidirectionalStreamServer) error {
    for {
        req, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return status.Errorf(codes.Internal, "failed to receive: %v", err)
        }

        resp := &streamv1.BidiResponse{
            Reply: fmt.Sprintf("Echo: %s", req.Message),
        }

        if err := stream.Send(resp); err != nil {
            return status.Errorf(codes.Internal, "failed to send: %v", err)
        }
    }
}
```

## Client Implementation

### Basic gRPC Client

```go
import (
    "context"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"

    userv1 "github.com/myapp/gen/user/v1"
)

type UserClient struct {
    client userv1.UserServiceClient
    conn   *grpc.ClientConn
}

func NewUserClient(addr string) (*UserClient, error) {
    conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        return nil, fmt.Errorf("failed to dial: %w", err)
    }

    return &UserClient{
        client: userv1.NewUserServiceClient(conn),
        conn:   conn,
    }, nil
}

func (c *UserClient) Close() error {
    return c.conn.Close()
}

func (c *UserClient) GetUser(ctx context.Context, userID string) (*userv1.User, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    resp, err := c.client.GetUser(ctx, &userv1.GetUserRequest{
        Id: userID,
    })
    if err != nil {
        return nil, fmt.Errorf("failed to get user: %w", err)
    }

    return resp.User, nil
}

func (c *UserClient) CreateUser(ctx context.Context, email, name string) (*userv1.User, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    resp, err := c.client.CreateUser(ctx, &userv1.CreateUserRequest{
        Email: email,
        Name:  name,
    })
    if err != nil {
        return nil, fmt.Errorf("failed to create user: %w", err)
    }

    return resp.User, nil
}
```

### Client with TLS

```go
import (
    "crypto/tls"
    "crypto/x509"
    "os"

    "google.golang.org/grpc/credentials"
)

func NewSecureUserClient(addr, caFile string) (*UserClient, error) {
    caCert, err := os.ReadFile(caFile)
    if err != nil {
        return nil, fmt.Errorf("failed to read CA cert: %w", err)
    }

    certPool := x509.NewCertPool()
    if !certPool.AppendCertsFromPEM(caCert) {
        return nil, errors.New("failed to append CA cert")
    }

    tlsConfig := &tls.Config{
        RootCAs:    certPool,
        MinVersion: tls.VersionTLS12,
    }

    creds := credentials.NewTLS(tlsConfig)

    conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(creds))
    if err != nil {
        return nil, fmt.Errorf("failed to dial: %w", err)
    }

    return &UserClient{
        client: userv1.NewUserServiceClient(conn),
        conn:   conn,
    }, nil
}
```

### Client Streaming

```go
func (c *StreamClient) UploadFile(ctx context.Context, filePath string) (*streamv1.ClientStreamResponse, error) {
    stream, err := c.client.ClientStream(ctx)
    if err != nil {
        return nil, fmt.Errorf("failed to create stream: %w", err)
    }

    file, err := os.Open(filePath)
    if err != nil {
        return nil, fmt.Errorf("failed to open file: %w", err)
    }
    defer file.Close()

    buf := make([]byte, 1024*64)
    for {
        n, err := file.Read(buf)
        if err == io.EOF {
            break
        }
        if err != nil {
            return nil, fmt.Errorf("failed to read file: %w", err)
        }

        if err := stream.Send(&streamv1.ClientStreamRequest{
            Chunk: buf[:n],
        }); err != nil {
            return nil, fmt.Errorf("failed to send chunk: %w", err)
        }
    }

    resp, err := stream.CloseAndRecv()
    if err != nil {
        return nil, fmt.Errorf("failed to receive response: %w", err)
    }

    return resp, nil
}
```

### Bidirectional Streaming Client

```go
func (c *StreamClient) Chat(ctx context.Context) error {
    stream, err := c.client.BidirectionalStream(ctx)
    if err != nil {
        return fmt.Errorf("failed to create stream: %w", err)
    }

    go func() {
        for {
            resp, err := stream.Recv()
            if err == io.EOF {
                return
            }
            if err != nil {
                slog.Error("failed to receive", "error", err)
                return
            }
            fmt.Printf("Received: %s\n", resp.Reply)
        }
    }()

    messages := []string{"Hello", "How are you?", "Goodbye"}
    for _, msg := range messages {
        if err := stream.Send(&streamv1.BidiRequest{
            Message: msg,
        }); err != nil {
            return fmt.Errorf("failed to send: %w", err)
        }
        time.Sleep(1 * time.Second)
    }

    stream.CloseSend()
    time.Sleep(2 * time.Second)

    return nil
}
```

## Interceptors

### Server Interceptors

```go
import (
    "google.golang.org/grpc"
    "google.golang.org/grpc/metadata"
)

func LoggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()

    resp, err := handler(ctx, req)

    duration := time.Since(start)

    slog.InfoContext(ctx, "gRPC request",
        "method", info.FullMethod,
        "duration", duration,
        "error", err,
    )

    return resp, err
}

func AuthInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }

    tokens := md.Get("authorization")
    if len(tokens) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing authorization token")
    }

    token := strings.TrimPrefix(tokens[0], "Bearer ")

    claims, err := ValidateToken(token)
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }

    ctx = context.WithValue(ctx, "user_id", claims.UserID)

    return handler(ctx, req)
}

func RecoveryInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (resp interface{}, err error) {
    defer func() {
        if r := recover(); r != nil {
            slog.ErrorContext(ctx, "panic recovered",
                "method", info.FullMethod,
                "panic", r,
                "stack", string(debug.Stack()),
            )
            err = status.Error(codes.Internal, "internal server error")
        }
    }()

    return handler(ctx, req)
}

func NewGRPCServerWithInterceptors() *grpc.Server {
    return grpc.NewServer(
        grpc.ChainUnaryInterceptor(
            RecoveryInterceptor,
            LoggingInterceptor,
            AuthInterceptor,
        ),
    )
}
```

### Stream Interceptors

```go
func LoggingStreamInterceptor(srv interface{}, ss grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) error {
    start := time.Now()

    err := handler(srv, ss)

    duration := time.Since(start)

    slog.Info("gRPC stream",
        "method", info.FullMethod,
        "duration", duration,
        "error", err,
    )

    return err
}

func NewGRPCServerWithStreamInterceptors() *grpc.Server {
    return grpc.NewServer(
        grpc.ChainUnaryInterceptor(
            RecoveryInterceptor,
            LoggingInterceptor,
            AuthInterceptor,
        ),
        grpc.ChainStreamInterceptor(
            LoggingStreamInterceptor,
        ),
    )
}
```

### Client Interceptors

```go
func ClientLoggingInterceptor(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
    start := time.Now()

    err := invoker(ctx, method, req, reply, cc, opts...)

    duration := time.Since(start)

    slog.InfoContext(ctx, "gRPC client request",
        "method", method,
        "duration", duration,
        "error", err,
    )

    return err
}

func ClientAuthInterceptor(token string) grpc.UnaryClientInterceptor {
    return func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
        ctx = metadata.AppendToOutgoingContext(ctx, "authorization", "Bearer "+token)
        return invoker(ctx, method, req, reply, cc, opts...)
    }
}

func NewGRPCClientWithInterceptors(addr, token string) (*grpc.ClientConn, error) {
    return grpc.Dial(addr,
        grpc.WithTransportCredentials(insecure.NewCredentials()),
        grpc.WithChainUnaryInterceptor(
            ClientLoggingInterceptor,
            ClientAuthInterceptor(token),
        ),
    )
}
```

## Error Handling

### Custom Error Details

```go
import (
    "google.golang.org/genproto/googleapis/rpc/errdetails"
    "google.golang.org/grpc/status"
)

func ValidationError(field, description string) error {
    st := status.New(codes.InvalidArgument, "validation failed")

    v := &errdetails.BadRequest_FieldViolation{
        Field:       field,
        Description: description,
    }

    br := &errdetails.BadRequest{}
    br.FieldViolations = append(br.FieldViolations, v)

    st, err := st.WithDetails(br)
    if err != nil {
        return status.Error(codes.InvalidArgument, "validation failed")
    }

    return st.Err()
}

func (s *UserServer) CreateUser(ctx context.Context, req *userv1.CreateUserRequest) (*userv1.CreateUserResponse, error) {
    if req.Email == "" {
        return nil, ValidationError("email", "email is required")
    }

    if !isValidEmail(req.Email) {
        return nil, ValidationError("email", "invalid email format")
    }

}
```

### Client Error Handling

```go
import (
    "google.golang.org/grpc/status"
)

func (c *UserClient) GetUser(ctx context.Context, userID string) (*userv1.User, error) {
    resp, err := c.client.GetUser(ctx, &userv1.GetUserRequest{
        Id: userID,
    })

    if err != nil {
        st, ok := status.FromError(err)
        if !ok {
            return nil, fmt.Errorf("unknown error: %w", err)
        }

        switch st.Code() {
        case codes.NotFound:
            return nil, ErrUserNotFound
        case codes.InvalidArgument:
            for _, detail := range st.Details() {
                if v, ok := detail.(*errdetails.BadRequest); ok {
                    for _, violation := range v.GetFieldViolations() {
                        slog.Error("validation error",
                            "field", violation.GetField(),
                            "description", violation.GetDescription(),
                        )
                    }
                }
            }
            return nil, ErrValidation
        case codes.Unauthenticated:
            return nil, ErrUnauthorized
        default:
            return nil, fmt.Errorf("grpc error: %w", err)
        }
    }

    return resp.User, nil
}
```

## Connection Management

### Connection Pooling

```go
type GRPCClientPool struct {
    clients []*grpc.ClientConn
    mu      sync.RWMutex
    next    int
}

func NewGRPCClientPool(addr string, size int) (*GRPCClientPool, error) {
    pool := &GRPCClientPool{
        clients: make([]*grpc.ClientConn, size),
    }

    for i := 0; i < size; i++ {
        conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
        if err != nil {
            pool.Close()
            return nil, fmt.Errorf("failed to create connection: %w", err)
        }
        pool.clients[i] = conn
    }

    return pool, nil
}

func (p *GRPCClientPool) GetConnection() *grpc.ClientConn {
    p.mu.Lock()
    defer p.mu.Unlock()

    conn := p.clients[p.next]
    p.next = (p.next + 1) % len(p.clients)

    return conn
}

func (p *GRPCClientPool) Close() error {
    p.mu.Lock()
    defer p.mu.Unlock()

    for _, conn := range p.clients {
        if conn != nil {
            conn.Close()
        }
    }

    return nil
}
```

### Retry Logic

```go
import (
    "google.golang.org/grpc/codes"
)

func RetryableCall(ctx context.Context, fn func() error, maxRetries int) error {
    var lastErr error

    for i := 0; i < maxRetries; i++ {
        err := fn()
        if err == nil {
            return nil
        }

        st, ok := status.FromError(err)
        if !ok {
            return err
        }

        if !isRetryableCode(st.Code()) {
            return err
        }

        lastErr = err

        backoff := time.Duration(i+1) * 100 * time.Millisecond
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(backoff):
        }
    }

    return lastErr
}

func isRetryableCode(code codes.Code) bool {
    switch code {
    case codes.Unavailable, codes.DeadlineExceeded, codes.ResourceExhausted:
        return true
    default:
        return false
    }
}
```

## Best Practices

### ✅ DO
- Use proto3 for new services
- Define clear message structures with proper field numbers
- Implement proper error handling with status codes
- Use interceptors for cross-cutting concerns
- Set appropriate deadlines/timeouts
- Use streaming for large data transfers
- Implement connection pooling for high-load clients
- Use TLS for production environments
- Implement proper authentication/authorization
- Version your proto files properly

### ❌ DON'T
- Don't reuse field numbers in proto definitions
- Don't ignore context cancellation
- Don't use blocking operations in stream handlers
- Don't forget to close client connections
- Don't expose internal errors to clients
- Don't use unary calls for large data transfers
- Don't ignore metadata for authentication
- Don't skip input validation
- Don't use insecure credentials in production

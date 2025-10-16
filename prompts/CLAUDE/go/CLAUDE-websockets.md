# WebSocket Patterns

Real-time communication patterns using WebSockets in Go applications.

## Basic WebSocket Server

### WebSocket Connection Setup

```go
import (
    "log/slog"
    "net/http"
    "sync"
    "time"

    "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}

type Client struct {
    ID   string
    Conn *websocket.Conn
    Send chan []byte
    Hub  *Hub
}

func (c *Client) ReadPump() {
    defer func() {
        c.Hub.Unregister <- c
        c.Conn.Close()
    }()

    c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
    c.Conn.SetPongHandler(func(string) error {
        c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
        return nil
    })

    for {
        _, message, err := c.Conn.ReadMessage()
        if err != nil {
            if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
                slog.Error("websocket error", "error", err)
            }
            break
        }

        c.Hub.Broadcast <- Message{
            ClientID: c.ID,
            Data:     message,
        }
    }
}

func (c *Client) WritePump() {
    ticker := time.NewTicker(54 * time.Second)
    defer func() {
        ticker.Stop()
        c.Conn.Close()
    }()

    for {
        select {
        case message, ok := <-c.Send:
            c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
            if !ok {
                c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
                return
            }

            w, err := c.Conn.NextWriter(websocket.TextMessage)
            if err != nil {
                return
            }
            w.Write(message)

            n := len(c.Send)
            for i := 0; i < n; i++ {
                w.Write([]byte{'\n'})
                w.Write(<-c.Send)
            }

            if err := w.Close(); err != nil {
                return
            }

        case <-ticker.C:
            c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
            if err := c.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
                return
            }
        }
    }
}
```

### WebSocket Hub (Connection Manager)

```go
type Message struct {
    ClientID string
    Data     []byte
}

type Hub struct {
    Clients    map[string]*Client
    Broadcast  chan Message
    Register   chan *Client
    Unregister chan *Client
    mu         sync.RWMutex
}

func NewHub() *Hub {
    return &Hub{
        Clients:    make(map[string]*Client),
        Broadcast:  make(chan Message, 256),
        Register:   make(chan *Client),
        Unregister: make(chan *Client),
    }
}

func (h *Hub) Run() {
    for {
        select {
        case client := <-h.Register:
            h.mu.Lock()
            h.Clients[client.ID] = client
            h.mu.Unlock()
            slog.Info("client registered", "id", client.ID)

        case client := <-h.Unregister:
            h.mu.Lock()
            if _, ok := h.Clients[client.ID]; ok {
                delete(h.Clients, client.ID)
                close(client.Send)
            }
            h.mu.Unlock()
            slog.Info("client unregistered", "id", client.ID)

        case message := <-h.Broadcast:
            h.mu.RLock()
            for id, client := range h.Clients {
                if id == message.ClientID {
                    continue
                }

                select {
                case client.Send <- message.Data:
                default:
                    h.mu.RUnlock()
                    h.mu.Lock()
                    close(client.Send)
                    delete(h.Clients, id)
                    h.mu.Unlock()
                    h.mu.RLock()
                }
            }
            h.mu.RUnlock()
        }
    }
}

func (h *Hub) GetClientCount() int {
    h.mu.RLock()
    defer h.mu.RUnlock()
    return len(h.Clients)
}
```

### WebSocket HTTP Handler

```go
func ServeWebSocket(hub *Hub) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        conn, err := upgrader.Upgrade(w, r, nil)
        if err != nil {
            slog.Error("websocket upgrade failed", "error", err)
            return
        }

        clientID := generateClientID()

        client := &Client{
            ID:   clientID,
            Conn: conn,
            Send: make(chan []byte, 256),
            Hub:  hub,
        }

        hub.Register <- client

        go client.WritePump()
        go client.ReadPump()
    }
}

func generateClientID() string {
    return fmt.Sprintf("client-%d", time.Now().UnixNano())
}
```

## Room-Based WebSocket

### Room Management

```go
type Room struct {
    ID      string
    Clients map[string]*Client
    mu      sync.RWMutex
}

type RoomHub struct {
    Rooms      map[string]*Room
    Register   chan RoomRegistration
    Unregister chan RoomRegistration
    Broadcast  chan RoomMessage
    mu         sync.RWMutex
}

type RoomRegistration struct {
    RoomID string
    Client *Client
}

type RoomMessage struct {
    RoomID   string
    ClientID string
    Data     []byte
}

func NewRoomHub() *RoomHub {
    return &RoomHub{
        Rooms:      make(map[string]*Room),
        Register:   make(chan RoomRegistration),
        Unregister: make(chan RoomRegistration),
        Broadcast:  make(chan RoomMessage),
    }
}

func (h *RoomHub) Run() {
    for {
        select {
        case reg := <-h.Register:
            h.mu.Lock()
            room, exists := h.Rooms[reg.RoomID]
            if !exists {
                room = &Room{
                    ID:      reg.RoomID,
                    Clients: make(map[string]*Client),
                }
                h.Rooms[reg.RoomID] = room
            }
            h.mu.Unlock()

            room.mu.Lock()
            room.Clients[reg.Client.ID] = reg.Client
            room.mu.Unlock()

            slog.Info("client joined room",
                "client_id", reg.Client.ID,
                "room_id", reg.RoomID,
            )

        case reg := <-h.Unregister:
            h.mu.RLock()
            room, exists := h.Rooms[reg.RoomID]
            h.mu.RUnlock()

            if exists {
                room.mu.Lock()
                if _, ok := room.Clients[reg.Client.ID]; ok {
                    delete(room.Clients, reg.Client.ID)
                    close(reg.Client.Send)
                }
                room.mu.Unlock()

                h.mu.Lock()
                if len(room.Clients) == 0 {
                    delete(h.Rooms, reg.RoomID)
                }
                h.mu.Unlock()

                slog.Info("client left room",
                    "client_id", reg.Client.ID,
                    "room_id", reg.RoomID,
                )
            }

        case msg := <-h.Broadcast:
            h.mu.RLock()
            room, exists := h.Rooms[msg.RoomID]
            h.mu.RUnlock()

            if exists {
                room.mu.RLock()
                for id, client := range room.Clients {
                    if id == msg.ClientID {
                        continue
                    }

                    select {
                    case client.Send <- msg.Data:
                    default:
                        room.mu.RUnlock()
                        room.mu.Lock()
                        close(client.Send)
                        delete(room.Clients, id)
                        room.mu.Unlock()
                        room.mu.RLock()
                    }
                }
                room.mu.RUnlock()
            }
        }
    }
}

func (h *RoomHub) GetRoomCount() int {
    h.mu.RLock()
    defer h.mu.RUnlock()
    return len(h.Rooms)
}

func (h *RoomHub) GetRoomClients(roomID string) int {
    h.mu.RLock()
    defer h.mu.RUnlock()

    if room, exists := h.Rooms[roomID]; exists {
        room.mu.RLock()
        defer room.mu.RUnlock()
        return len(room.Clients)
    }

    return 0
}
```

## Chat Application

### Chat Message Types

```go
type ChatMessage struct {
    Type      string    `json:"type"`
    UserID    string    `json:"user_id"`
    Username  string    `json:"username"`
    RoomID    string    `json:"room_id"`
    Content   string    `json:"content"`
    Timestamp time.Time `json:"timestamp"`
}

type ChatClient struct {
    ID       string
    UserID   string
    Username string
    Conn     *websocket.Conn
    Send     chan *ChatMessage
    Hub      *ChatHub
}

type ChatHub struct {
    Rooms      map[string]*ChatRoom
    Register   chan *ChatClient
    Unregister chan *ChatClient
    mu         sync.RWMutex
}

type ChatRoom struct {
    ID      string
    Clients map[string]*ChatClient
    History []*ChatMessage
    mu      sync.RWMutex
}

func NewChatHub() *ChatHub {
    return &ChatHub{
        Rooms:      make(map[string]*ChatRoom),
        Register:   make(chan *ChatClient),
        Unregister: make(chan *ChatClient),
    }
}

func (h *ChatHub) Run() {
    for {
        select {
        case client := <-h.Register:
            h.registerClient(client)

        case client := <-h.Unregister:
            h.unregisterClient(client)
        }
    }
}

func (h *ChatHub) registerClient(client *ChatClient) {
    h.mu.Lock()
    defer h.mu.Unlock()

    room, exists := h.Rooms[client.ID]
    if !exists {
        room = &ChatRoom{
            ID:      client.ID,
            Clients: make(map[string]*ChatClient),
            History: make([]*ChatMessage, 0),
        }
        h.Rooms[client.ID] = room
    }

    room.mu.Lock()
    room.Clients[client.UserID] = client
    room.mu.Unlock()

    joinMsg := &ChatMessage{
        Type:      "join",
        UserID:    client.UserID,
        Username:  client.Username,
        RoomID:    client.ID,
        Content:   fmt.Sprintf("%s joined the room", client.Username),
        Timestamp: time.Now(),
    }

    h.broadcastToRoom(client.ID, joinMsg)

    for _, msg := range room.History {
        client.Send <- msg
    }
}

func (h *ChatHub) unregisterClient(client *ChatClient) {
    h.mu.RLock()
    room, exists := h.Rooms[client.ID]
    h.mu.RUnlock()

    if exists {
        room.mu.Lock()
        if _, ok := room.Clients[client.UserID]; ok {
            delete(room.Clients, client.UserID)
            close(client.Send)
        }
        room.mu.Unlock()

        leaveMsg := &ChatMessage{
            Type:      "leave",
            UserID:    client.UserID,
            Username:  client.Username,
            RoomID:    client.ID,
            Content:   fmt.Sprintf("%s left the room", client.Username),
            Timestamp: time.Now(),
        }

        h.broadcastToRoom(client.ID, leaveMsg)
    }
}

func (h *ChatHub) broadcastToRoom(roomID string, message *ChatMessage) {
    h.mu.RLock()
    room, exists := h.Rooms[roomID]
    h.mu.RUnlock()

    if !exists {
        return
    }

    room.mu.Lock()
    room.History = append(room.History, message)
    if len(room.History) > 100 {
        room.History = room.History[1:]
    }
    room.mu.Unlock()

    room.mu.RLock()
    defer room.mu.RUnlock()

    for _, client := range room.Clients {
        select {
        case client.Send <- message:
        default:
            close(client.Send)
            delete(room.Clients, client.UserID)
        }
    }
}
```

### Chat Client Handlers

```go
func (c *ChatClient) ReadPump() {
    defer func() {
        c.Hub.Unregister <- c
        c.Conn.Close()
    }()

    c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
    c.Conn.SetPongHandler(func(string) error {
        c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
        return nil
    })

    for {
        var msg ChatMessage
        err := c.Conn.ReadJSON(&msg)
        if err != nil {
            if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
                slog.Error("websocket error", "error", err)
            }
            break
        }

        msg.UserID = c.UserID
        msg.Username = c.Username
        msg.Timestamp = time.Now()

        c.Hub.broadcastToRoom(c.ID, &msg)
    }
}

func (c *ChatClient) WritePump() {
    ticker := time.NewTicker(54 * time.Second)
    defer func() {
        ticker.Stop()
        c.Conn.Close()
    }()

    for {
        select {
        case message, ok := <-c.Send:
            c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
            if !ok {
                c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
                return
            }

            if err := c.Conn.WriteJSON(message); err != nil {
                return
            }

        case <-ticker.C:
            c.Conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
            if err := c.Conn.WriteMessage(websocket.PingMessage, nil); err != nil {
                return
            }
        }
    }
}
```

## Real-Time Notifications

### Notification Hub

```go
type Notification struct {
    ID        string                 `json:"id"`
    UserID    string                 `json:"user_id"`
    Type      string                 `json:"type"`
    Title     string                 `json:"title"`
    Message   string                 `json:"message"`
    Data      map[string]interface{} `json:"data"`
    Timestamp time.Time              `json:"timestamp"`
    Read      bool                   `json:"read"`
}

type NotificationHub struct {
    UserConnections map[string][]*Client
    Publish         chan *Notification
    Register        chan *Client
    Unregister      chan *Client
    mu              sync.RWMutex
}

func NewNotificationHub() *NotificationHub {
    return &NotificationHub{
        UserConnections: make(map[string][]*Client),
        Publish:         make(chan *Notification),
        Register:        make(chan *Client),
        Unregister:      make(chan *Client),
    }
}

func (h *NotificationHub) Run() {
    for {
        select {
        case client := <-h.Register:
            h.mu.Lock()
            h.UserConnections[client.ID] = append(h.UserConnections[client.ID], client)
            h.mu.Unlock()

        case client := <-h.Unregister:
            h.mu.Lock()
            if connections, ok := h.UserConnections[client.ID]; ok {
                for i, conn := range connections {
                    if conn == client {
                        h.UserConnections[client.ID] = append(connections[:i], connections[i+1:]...)
                        close(client.Send)
                        break
                    }
                }

                if len(h.UserConnections[client.ID]) == 0 {
                    delete(h.UserConnections, client.ID)
                }
            }
            h.mu.Unlock()

        case notification := <-h.Publish:
            h.sendToUser(notification)
        }
    }
}

func (h *NotificationHub) sendToUser(notification *Notification) {
    h.mu.RLock()
    defer h.mu.RUnlock()

    connections, exists := h.UserConnections[notification.UserID]
    if !exists {
        return
    }

    data, err := json.Marshal(notification)
    if err != nil {
        slog.Error("failed to marshal notification", "error", err)
        return
    }

    for _, client := range connections {
        select {
        case client.Send <- data:
        default:
            close(client.Send)
        }
    }
}

func (h *NotificationHub) PublishNotification(userID, notifType, title, message string, data map[string]interface{}) {
    notification := &Notification{
        ID:        generateID(),
        UserID:    userID,
        Type:      notifType,
        Title:     title,
        Message:   message,
        Data:      data,
        Timestamp: time.Now(),
        Read:      false,
    }

    h.Publish <- notification
}

func generateID() string {
    return fmt.Sprintf("notif-%d", time.Now().UnixNano())
}
```

## Authentication & Security

### Authenticated WebSocket

```go
func AuthenticatedWebSocket(hub *Hub, jwtSecret []byte) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        token := r.URL.Query().Get("token")
        if token == "" {
            http.Error(w, "missing token", http.StatusUnauthorized)
            return
        }

        claims, err := ValidateToken(token)
        if err != nil {
            http.Error(w, "invalid token", http.StatusUnauthorized)
            return
        }

        conn, err := upgrader.Upgrade(w, r, nil)
        if err != nil {
            slog.Error("websocket upgrade failed", "error", err)
            return
        }

        client := &Client{
            ID:   claims.UserID,
            Conn: conn,
            Send: make(chan []byte, 256),
            Hub:  hub,
        }

        hub.Register <- client

        go client.WritePump()
        go client.ReadPump()
    }
}
```

### Rate Limiting for WebSocket

```go
import (
    "golang.org/x/time/rate"
)

type RateLimitedClient struct {
    *Client
    limiter *rate.Limiter
}

func NewRateLimitedClient(client *Client, rps int, burst int) *RateLimitedClient {
    return &RateLimitedClient{
        Client:  client,
        limiter: rate.NewLimiter(rate.Limit(rps), burst),
    }
}

func (c *RateLimitedClient) ReadPump() {
    defer func() {
        c.Hub.Unregister <- c.Client
        c.Conn.Close()
    }()

    c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
    c.Conn.SetPongHandler(func(string) error {
        c.Conn.SetReadDeadline(time.Now().Add(60 * time.Second))
        return nil
    })

    for {
        _, message, err := c.Conn.ReadMessage()
        if err != nil {
            if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
                slog.Error("websocket error", "error", err)
            }
            break
        }

        if !c.limiter.Allow() {
            slog.Warn("rate limit exceeded", "client_id", c.ID)
            continue
        }

        c.Hub.Broadcast <- Message{
            ClientID: c.ID,
            Data:     message,
        }
    }
}
```

## Scaling Considerations

### Redis Pub/Sub for Horizontal Scaling

```go
import (
    "github.com/redis/go-redis/v9"
)

type RedisHub struct {
    Hub       *Hub
    RedisClient *redis.Client
    pubsub    *redis.PubSub
}

func NewRedisHub(hub *Hub, redisClient *redis.Client) *RedisHub {
    return &RedisHub{
        Hub:         hub,
        RedisClient: redisClient,
        pubsub:      redisClient.Subscribe(context.Background(), "websocket:broadcast"),
    }
}

func (h *RedisHub) Run(ctx context.Context) {
    go h.Hub.Run()

    go func() {
        for {
            msg, err := h.pubsub.ReceiveMessage(ctx)
            if err != nil {
                slog.Error("redis pubsub error", "error", err)
                return
            }

            h.Hub.Broadcast <- Message{
                ClientID: "redis",
                Data:     []byte(msg.Payload),
            }
        }
    }()

    for {
        select {
        case <-ctx.Done():
            return
        case msg := <-h.Hub.Broadcast:
            if msg.ClientID != "redis" {
                h.RedisClient.Publish(ctx, "websocket:broadcast", msg.Data)
            }

            h.Hub.mu.RLock()
            for id, client := range h.Hub.Clients {
                if id == msg.ClientID {
                    continue
                }

                select {
                case client.Send <- msg.Data:
                default:
                    close(client.Send)
                    delete(h.Hub.Clients, id)
                }
            }
            h.Hub.mu.RUnlock()
        }
    }
}
```

## Best Practices

### ✅ DO
- Set read/write deadlines to prevent hanging connections
- Implement ping/pong mechanism for connection health checks
- Use buffered channels for client send operations
- Handle connection cleanup properly in defer statements
- Implement rate limiting per client
- Use authentication for WebSocket connections
- Validate all incoming messages
- Use goroutines for read/write pumps
- Implement proper error handling for unexpected closes
- Use Redis Pub/Sub for horizontal scaling

### ❌ DON'T
- Don't block on channel sends - use select with default
- Don't ignore websocket.IsUnexpectedCloseError checks
- Don't share websocket.Conn across goroutines
- Don't forget to close client channels on disconnect
- Don't allow unlimited message sizes
- Don't skip authentication/authorization
- Don't ignore context cancellation
- Don't use WebSocket for every real-time need (consider SSE for one-way)
- Don't forget to clean up connections on server shutdown
- Don't store sensitive data in WebSocket messages without encryption

## Troubleshooting

### Common Issues

1. **Connection Drops**: Clients disconnecting unexpectedly
   - Solution: Implement ping/pong with proper timeouts

2. **Memory Leaks**: Growing memory usage over time
   - Solution: Ensure channels are closed and clients removed from hub

3. **Slow Message Delivery**: Messages taking too long to reach clients
   - Solution: Check buffer sizes and ensure non-blocking sends

4. **Cross-Origin Issues**: Browser blocking WebSocket connections
   - Solution: Configure CheckOrigin in upgrader properly

5. **Scaling Problems**: Issues when running multiple server instances
   - Solution: Use Redis Pub/Sub or similar for message distribution

# Message Queue Patterns

Message queue integration patterns for RabbitMQ, Kafka, and NATS in Go applications.

**← [Back to Go Development Guide]mcp://resources/patterns/go/patterns-core**

## RabbitMQ Patterns

### Basic RabbitMQ Setup

```go
import (
    "context"
    "fmt"

    amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitMQConfig struct {
    Host     string
    Port     string
    User     string
    Password string
    VHost    string
}

type RabbitMQ struct {
    conn    *amqp.Connection
    channel *amqp.Channel
}

func NewRabbitMQ(cfg RabbitMQConfig) (*RabbitMQ, error) {
    url := fmt.Sprintf("amqp://%s:%s@%s:%s/%s",
        cfg.User,
        cfg.Password,
        cfg.Host,
        cfg.Port,
        cfg.VHost,
    )

    conn, err := amqp.Dial(url)
    if err != nil {
        return nil, fmt.Errorf("failed to connect to RabbitMQ: %w", err)
    }

    channel, err := conn.Channel()
    if err != nil {
        conn.Close()
        return nil, fmt.Errorf("failed to open channel: %w", err)
    }

    return &RabbitMQ{
        conn:    conn,
        channel: channel,
    }, nil
}

func (r *RabbitMQ) Close() error {
    if err := r.channel.Close(); err != nil {
        return err
    }
    return r.conn.Close()
}
```

### Publisher Pattern

```go
type RabbitMQPublisher struct {
    channel      *amqp.Channel
    exchangeName string
}

func NewRabbitMQPublisher(channel *amqp.Channel, exchangeName string) (*RabbitMQPublisher, error) {
    err := channel.ExchangeDeclare(
        exchangeName,
        "topic",
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to declare exchange: %w", err)
    }

    return &RabbitMQPublisher{
        channel:      channel,
        exchangeName: exchangeName,
    }, nil
}

func (p *RabbitMQPublisher) Publish(ctx context.Context, routingKey string, body []byte) error {
    err := p.channel.PublishWithContext(
        ctx,
        p.exchangeName,
        routingKey,
        false,
        false,
        amqp.Publishing{
            ContentType:  "application/json",
            Body:         body,
            DeliveryMode: amqp.Persistent,
            Timestamp:    time.Now(),
        },
    )

    if err != nil {
        return fmt.Errorf("failed to publish message: %w", err)
    }

    return nil
}

type Event struct {
    ID        string    `json:"id"`
    Type      string    `json:"type"`
    Payload   string    `json:"payload"`
    Timestamp time.Time `json:"timestamp"`
}

func (p *RabbitMQPublisher) PublishEvent(ctx context.Context, event *Event) error {
    body, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    routingKey := fmt.Sprintf("event.%s", event.Type)

    return p.Publish(ctx, routingKey, body)
}
```

### Subscriber Pattern

```go
type RabbitMQSubscriber struct {
    channel      *amqp.Channel
    queueName    string
    exchangeName string
}

func NewRabbitMQSubscriber(channel *amqp.Channel, queueName, exchangeName string, routingKeys []string) (*RabbitMQSubscriber, error) {
    queue, err := channel.QueueDeclare(
        queueName,
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return nil, fmt.Errorf("failed to declare queue: %w", err)
    }

    for _, key := range routingKeys {
        err = channel.QueueBind(
            queue.Name,
            key,
            exchangeName,
            false,
            nil,
        )
        if err != nil {
            return nil, fmt.Errorf("failed to bind queue: %w", err)
        }
    }

    return &RabbitMQSubscriber{
        channel:      channel,
        queueName:    queue.Name,
        exchangeName: exchangeName,
    }, nil
}

func (s *RabbitMQSubscriber) Subscribe(ctx context.Context, handler func(*amqp.Delivery) error) error {
    msgs, err := s.channel.Consume(
        s.queueName,
        "",
        false,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return fmt.Errorf("failed to register consumer: %w", err)
    }

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case msg, ok := <-msgs:
            if !ok {
                return errors.New("channel closed")
            }

            if err := handler(&msg); err != nil {
                slog.Error("message handler failed",
                    "error", err,
                    "message_id", msg.MessageId,
                )
                msg.Nack(false, true)
            } else {
                msg.Ack(false)
            }
        }
    }
}
```

### Dead Letter Queue Pattern

```go
func SetupQueueWithDLQ(channel *amqp.Channel, queueName string) error {
    dlqName := queueName + ".dlq"

    _, err := channel.QueueDeclare(
        dlqName,
        true,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return fmt.Errorf("failed to declare DLQ: %w", err)
    }

    _, err = channel.QueueDeclare(
        queueName,
        true,
        false,
        false,
        false,
        amqp.Table{
            "x-dead-letter-exchange":    "",
            "x-dead-letter-routing-key": dlqName,
            "x-message-ttl":             300000,
        },
    )
    if err != nil {
        return fmt.Errorf("failed to declare queue: %w", err)
    }

    return nil
}

func (s *RabbitMQSubscriber) SubscribeWithRetry(ctx context.Context, handler func(*amqp.Delivery) error, maxRetries int) error {
    msgs, err := s.channel.Consume(
        s.queueName,
        "",
        false,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        return fmt.Errorf("failed to register consumer: %w", err)
    }

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case msg, ok := <-msgs:
            if !ok {
                return errors.New("channel closed")
            }

            retryCount := getRetryCount(msg.Headers)

            if err := handler(&msg); err != nil {
                slog.Error("message handler failed",
                    "error", err,
                    "retry_count", retryCount,
                )

                if retryCount >= maxRetries {
                    msg.Nack(false, false)
                } else {
                    msg.Nack(false, true)
                }
            } else {
                msg.Ack(false)
            }
        }
    }
}

func getRetryCount(headers amqp.Table) int {
    if headers == nil {
        return 0
    }

    if count, ok := headers["x-retry-count"].(int); ok {
        return count
    }

    return 0
}
```

## Apache Kafka Patterns

### Kafka Producer

```go
import (
    "github.com/IBM/sarama"
)

type KafkaProducer struct {
    producer sarama.SyncProducer
}

func NewKafkaProducer(brokers []string) (*KafkaProducer, error) {
    config := sarama.NewConfig()
    config.Producer.RequiredAcks = sarama.WaitForAll
    config.Producer.Retry.Max = 5
    config.Producer.Return.Successes = true
    config.Producer.Compression = sarama.CompressionSnappy

    producer, err := sarama.NewSyncProducer(brokers, config)
    if err != nil {
        return nil, fmt.Errorf("failed to create producer: %w", err)
    }

    return &KafkaProducer{
        producer: producer,
    }, nil
}

func (p *KafkaProducer) Close() error {
    return p.producer.Close()
}

func (p *KafkaProducer) SendMessage(topic, key string, value []byte) error {
    msg := &sarama.ProducerMessage{
        Topic: topic,
        Key:   sarama.StringEncoder(key),
        Value: sarama.ByteEncoder(value),
    }

    partition, offset, err := p.producer.SendMessage(msg)
    if err != nil {
        return fmt.Errorf("failed to send message: %w", err)
    }

    slog.Info("message sent",
        "topic", topic,
        "partition", partition,
        "offset", offset,
    )

    return nil
}

func (p *KafkaProducer) SendEvent(topic string, event *Event) error {
    body, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    return p.SendMessage(topic, event.ID, body)
}
```

### Kafka Consumer

```go
type KafkaConsumer struct {
    consumer sarama.ConsumerGroup
    topics   []string
}

func NewKafkaConsumer(brokers []string, groupID string, topics []string) (*KafkaConsumer, error) {
    config := sarama.NewConfig()
    config.Consumer.Group.Rebalance.Strategy = sarama.BalanceStrategyRoundRobin
    config.Consumer.Offsets.Initial = sarama.OffsetNewest

    consumer, err := sarama.NewConsumerGroup(brokers, groupID, config)
    if err != nil {
        return nil, fmt.Errorf("failed to create consumer group: %w", err)
    }

    return &KafkaConsumer{
        consumer: consumer,
        topics:   topics,
    }, nil
}

func (c *KafkaConsumer) Close() error {
    return c.consumer.Close()
}

type MessageHandler interface {
    Handle(ctx context.Context, message *sarama.ConsumerMessage) error
}

type consumerGroupHandler struct {
    handler MessageHandler
}

func (h *consumerGroupHandler) Setup(sarama.ConsumerGroupSession) error {
    return nil
}

func (h *consumerGroupHandler) Cleanup(sarama.ConsumerGroupSession) error {
    return nil
}

func (h *consumerGroupHandler) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
    for message := range claim.Messages() {
        if err := h.handler.Handle(session.Context(), message); err != nil {
            slog.Error("message handler failed",
                "error", err,
                "topic", message.Topic,
                "partition", message.Partition,
                "offset", message.Offset,
            )
        }

        session.MarkMessage(message, "")
    }

    return nil
}

func (c *KafkaConsumer) Consume(ctx context.Context, handler MessageHandler) error {
    groupHandler := &consumerGroupHandler{
        handler: handler,
    }

    for {
        if err := c.consumer.Consume(ctx, c.topics, groupHandler); err != nil {
            return fmt.Errorf("consume error: %w", err)
        }

        if ctx.Err() != nil {
            return ctx.Err()
        }
    }
}
```

### Kafka Message Handler Example

```go
type EventHandler struct {
    userRepo UserRepository
}

func (h *EventHandler) Handle(ctx context.Context, message *sarama.ConsumerMessage) error {
    var event Event
    if err := json.Unmarshal(message.Value, &event); err != nil {
        return fmt.Errorf("failed to unmarshal event: %w", err)
    }

    switch event.Type {
    case "user.created":
        return h.handleUserCreated(ctx, &event)
    case "user.updated":
        return h.handleUserUpdated(ctx, &event)
    case "user.deleted":
        return h.handleUserDeleted(ctx, &event)
    default:
        slog.Warn("unknown event type", "type", event.Type)
        return nil
    }
}

func (h *EventHandler) handleUserCreated(ctx context.Context, event *Event) error {
    slog.Info("handling user created event", "event_id", event.ID)
    return nil
}
```

## NATS Patterns

### NATS Publisher

```go
import (
    "github.com/nats-io/nats.go"
)

type NATSPublisher struct {
    conn *nats.Conn
}

func NewNATSPublisher(url string) (*NATSPublisher, error) {
    conn, err := nats.Connect(url,
        nats.MaxReconnects(-1),
        nats.ReconnectWait(2*time.Second),
    )
    if err != nil {
        return nil, fmt.Errorf("failed to connect to NATS: %w", err)
    }

    return &NATSPublisher{
        conn: conn,
    }, nil
}

func (p *NATSPublisher) Close() error {
    p.conn.Close()
    return nil
}

func (p *NATSPublisher) Publish(subject string, data []byte) error {
    if err := p.conn.Publish(subject, data); err != nil {
        return fmt.Errorf("failed to publish: %w", err)
    }

    return nil
}

func (p *NATSPublisher) PublishEvent(event *Event) error {
    body, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    subject := fmt.Sprintf("events.%s", event.Type)

    return p.Publish(subject, body)
}
```

### NATS Subscriber

```go
type NATSSubscriber struct {
    conn *nats.Conn
}

func NewNATSSubscriber(url string) (*NATSSubscriber, error) {
    conn, err := nats.Connect(url,
        nats.MaxReconnects(-1),
        nats.ReconnectWait(2*time.Second),
    )
    if err != nil {
        return nil, fmt.Errorf("failed to connect to NATS: %w", err)
    }

    return &NATSSubscriber{
        conn: conn,
    }, nil
}

func (s *NATSSubscriber) Close() error {
    s.conn.Close()
    return nil
}

func (s *NATSSubscriber) Subscribe(subject string, handler func(*nats.Msg) error) (*nats.Subscription, error) {
    sub, err := s.conn.Subscribe(subject, func(msg *nats.Msg) {
        if err := handler(msg); err != nil {
            slog.Error("message handler failed",
                "error", err,
                "subject", msg.Subject,
            )
        }
    })

    if err != nil {
        return nil, fmt.Errorf("failed to subscribe: %w", err)
    }

    return sub, nil
}

func (s *NATSSubscriber) QueueSubscribe(subject, queue string, handler func(*nats.Msg) error) (*nats.Subscription, error) {
    sub, err := s.conn.QueueSubscribe(subject, queue, func(msg *nats.Msg) {
        if err := handler(msg); err != nil {
            slog.Error("message handler failed",
                "error", err,
                "subject", msg.Subject,
                "queue", queue,
            )
        }
    })

    if err != nil {
        return nil, fmt.Errorf("failed to queue subscribe: %w", err)
    }

    return sub, nil
}
```

### NATS JetStream

```go
type JetStreamPublisher struct {
    js nats.JetStreamContext
}

func NewJetStreamPublisher(url string) (*JetStreamPublisher, error) {
    nc, err := nats.Connect(url)
    if err != nil {
        return nil, fmt.Errorf("failed to connect: %w", err)
    }

    js, err := nc.JetStream()
    if err != nil {
        return nil, fmt.Errorf("failed to create JetStream context: %w", err)
    }

    return &JetStreamPublisher{
        js: js,
    }, nil
}

func (p *JetStreamPublisher) Publish(subject string, data []byte) error {
    _, err := p.js.Publish(subject, data)
    if err != nil {
        return fmt.Errorf("failed to publish: %w", err)
    }

    return nil
}

type JetStreamSubscriber struct {
    js nats.JetStreamContext
}

func NewJetStreamSubscriber(url, streamName string, subjects []string) (*JetStreamSubscriber, error) {
    nc, err := nats.Connect(url)
    if err != nil {
        return nil, fmt.Errorf("failed to connect: %w", err)
    }

    js, err := nc.JetStream()
    if err != nil {
        return nil, fmt.Errorf("failed to create JetStream context: %w", err)
    }

    _, err = js.AddStream(&nats.StreamConfig{
        Name:     streamName,
        Subjects: subjects,
    })
    if err != nil && err != nats.ErrStreamNameAlreadyInUse {
        return nil, fmt.Errorf("failed to add stream: %w", err)
    }

    return &JetStreamSubscriber{
        js: js,
    }, nil
}

func (s *JetStreamSubscriber) Subscribe(subject, durable string, handler func(*nats.Msg) error) (*nats.Subscription, error) {
    sub, err := s.js.Subscribe(subject, func(msg *nats.Msg) {
        if err := handler(msg); err != nil {
            slog.Error("message handler failed", "error", err)
            msg.Nak()
        } else {
            msg.Ack()
        }
    }, nats.Durable(durable))

    if err != nil {
        return nil, fmt.Errorf("failed to subscribe: %w", err)
    }

    return sub, nil
}
```

## Event-Driven Architecture

### Event Bus

```go
type EventBus interface {
    Publish(ctx context.Context, event *Event) error
    Subscribe(ctx context.Context, eventType string, handler EventHandler) error
}

type EventHandler func(ctx context.Context, event *Event) error

type InMemoryEventBus struct {
    handlers map[string][]EventHandler
    mu       sync.RWMutex
}

func NewInMemoryEventBus() *InMemoryEventBus {
    return &InMemoryEventBus{
        handlers: make(map[string][]EventHandler),
    }
}

func (b *InMemoryEventBus) Publish(ctx context.Context, event *Event) error {
    b.mu.RLock()
    handlers, exists := b.handlers[event.Type]
    b.mu.RUnlock()

    if !exists {
        return nil
    }

    for _, handler := range handlers {
        if err := handler(ctx, event); err != nil {
            slog.Error("event handler failed",
                "event_type", event.Type,
                "error", err,
            )
        }
    }

    return nil
}

func (b *InMemoryEventBus) Subscribe(ctx context.Context, eventType string, handler EventHandler) error {
    b.mu.Lock()
    defer b.mu.Unlock()

    b.handlers[eventType] = append(b.handlers[eventType], handler)

    return nil
}
```

### Outbox Pattern

```go
type OutboxEvent struct {
    ID        string
    EventType string
    Payload   string
    CreatedAt time.Time
    Published bool
}

type OutboxRepository interface {
    SaveEvent(ctx context.Context, event *OutboxEvent) error
    GetUnpublishedEvents(ctx context.Context, limit int) ([]*OutboxEvent, error)
    MarkAsPublished(ctx context.Context, eventID string) error
}

type OutboxPublisher struct {
    repo      OutboxRepository
    publisher EventBus
    ticker    *time.Ticker
    done      chan bool
}

func NewOutboxPublisher(repo OutboxRepository, publisher EventBus) *OutboxPublisher {
    return &OutboxPublisher{
        repo:      repo,
        publisher: publisher,
        ticker:    time.NewTicker(5 * time.Second),
        done:      make(chan bool),
    }
}

func (p *OutboxPublisher) Start(ctx context.Context) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return
            case <-p.done:
                return
            case <-p.ticker.C:
                p.publishEvents(ctx)
            }
        }
    }()
}

func (p *OutboxPublisher) Stop() {
    p.ticker.Stop()
    p.done <- true
}

func (p *OutboxPublisher) publishEvents(ctx context.Context) {
    events, err := p.repo.GetUnpublishedEvents(ctx, 100)
    if err != nil {
        slog.Error("failed to get unpublished events", "error", err)
        return
    }

    for _, outboxEvent := range events {
        event := &Event{
            ID:        outboxEvent.ID,
            Type:      outboxEvent.EventType,
            Payload:   outboxEvent.Payload,
            Timestamp: outboxEvent.CreatedAt,
        }

        if err := p.publisher.Publish(ctx, event); err != nil {
            slog.Error("failed to publish event",
                "event_id", event.ID,
                "error", err,
            )
            continue
        }

        if err := p.repo.MarkAsPublished(ctx, outboxEvent.ID); err != nil {
            slog.Error("failed to mark event as published",
                "event_id", event.ID,
                "error", err,
            )
        }
    }
}
```

### Idempotent Consumer

```go
type ProcessedMessage struct {
    MessageID  string
    ProcessedAt time.Time
}

type IdempotentConsumer struct {
    messageRepo MessageRepository
    handler     func(ctx context.Context, msg *Message) error
}

func NewIdempotentConsumer(messageRepo MessageRepository, handler func(context.Context, *Message) error) *IdempotentConsumer {
    return &IdempotentConsumer{
        messageRepo: messageRepo,
        handler:     handler,
    }
}

func (c *IdempotentConsumer) Handle(ctx context.Context, msg *Message) error {
    processed, err := c.messageRepo.IsProcessed(ctx, msg.ID)
    if err != nil {
        return fmt.Errorf("failed to check if message processed: %w", err)
    }

    if processed {
        slog.Info("message already processed, skipping",
            "message_id", msg.ID,
        )
        return nil
    }

    if err := c.handler(ctx, msg); err != nil {
        return fmt.Errorf("handler failed: %w", err)
    }

    if err := c.messageRepo.MarkAsProcessed(ctx, msg.ID); err != nil {
        return fmt.Errorf("failed to mark message as processed: %w", err)
    }

    return nil
}
```

## Best Practices

### ✅ DO
- Use message queues for asynchronous communication
- Implement idempotent message handlers
- Use dead letter queues for failed messages
- Set appropriate message TTLs
- Implement retry logic with exponential backoff
- Use correlation IDs for message tracing
- Implement circuit breakers for queue connections
- Use message acknowledgment properly
- Implement the outbox pattern for reliable message publishing
- Monitor queue depths and consumer lag

### ❌ DON'T
- Don't process messages synchronously in request handlers
- Don't ignore message acknowledgment failures
- Don't use unbounded retry attempts
- Don't store large payloads in messages
- Don't forget to handle poison messages
- Don't use queues as primary data storage
- Don't ignore connection failures
- Don't process the same message twice without idempotency
- Don't block message processing indefinitely
- Don't forget to close connections

## Troubleshooting

### Common Issues

1. **Message Loss**: Messages disappearing from queue
   - Solution: Use persistent messages and proper acknowledgment

2. **Consumer Lag**: Consumers falling behind producers
   - Solution: Scale consumers horizontally or optimize processing

3. **Poison Messages**: Messages that always fail processing
   - Solution: Implement DLQ and alerting

4. **Connection Failures**: Lost connection to message broker
   - Solution: Implement reconnection logic with exponential backoff

5. **Duplicate Processing**: Same message processed multiple times
   - Solution: Implement idempotent handlers with deduplication

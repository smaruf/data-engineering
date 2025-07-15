import java.io.FileWriter;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

class InMemoryKafkaBroker {
    private final Map<String, BlockingQueue<String>> topics = new HashMap<>();
    private boolean active = false;

    public synchronized void start() {
        active = true;
        System.out.println("[InMemoryKafkaBroker] Started.");
    }
    public synchronized void stop() {
        active = false;
        System.out.println("[InMemoryKafkaBroker] Stopped.");
    }
    private synchronized void createTopic(String topic) {
        topics.computeIfAbsent(topic, k -> new LinkedBlockingQueue<>());
    }
    public void send(String topic, String value) {
        synchronized (this) {
            if (!active)
                throw new RuntimeException("Broker not started.");
            createTopic(topic);
            topics.get(topic).offer(value);
        }
    }
    public String consume(String topic, int timeoutMillis) {
        createTopic(topic);
        try {
            return topics.get(topic).poll(timeoutMillis, TimeUnit.MILLISECONDS);
        } catch (InterruptedException e) {
            return null;
        }
    }
    public synchronized boolean isActive() { return active; }
}

class Producer implements Runnable {
    private final InMemoryKafkaBroker broker;
    private final String topic;
    private final int intervalSeconds;
    private static final String[] assets = {"USD/BDT", "EUR/USD", "BTC/USDT"};
    private final Random rand = new Random();
    private final Gson gson = new Gson();

    public Producer(InMemoryKafkaBroker broker, String topic, int intervalSeconds) {
        this.broker = broker; this.topic = topic; this.intervalSeconds = intervalSeconds;
    }

    public void run() {
        while (broker.isActive()) {
            Map<String, Object> trade = new HashMap<>();
            trade.put("market", "LocalMoneyExchange");
            trade.put("asset", assets[rand.nextInt(assets.length)]);
            trade.put("price", Math.round((rand.nextDouble() * 40 + 80) * 100.0) / 100.0);
            trade.put("volume", rand.nextInt(9901) + 100);
            trade.put("timestamp", System.currentTimeMillis() / 1000.0);
            String msg = gson.toJson(trade);
            broker.send(topic, msg);
            System.out.println("[Producer] Produced: " + msg);
            try { Thread.sleep(intervalSeconds * 1000); } catch (InterruptedException ignored) {}
        }
    }
}

class Consumer implements Runnable {
    private final InMemoryKafkaBroker broker;
    private final String topic;
    private final String dumpFile;
    private final List<Map<String, Object>> memoryData = new ArrayList<>();
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    public Consumer(InMemoryKafkaBroker broker, String topic, String dumpFile) {
        this.broker = broker; this.topic = topic; this.dumpFile = dumpFile;
    }

    public void run() {
        while (broker.isActive()) {
            String msg = broker.consume(topic, 5000);
            if (msg != null) {
                Map<String, Object> trade = gson.fromJson(msg, Map.class);
                System.out.println("[Consumer] Consumed: " + msg);
                memoryData.add(trade);
                try (FileWriter file = new FileWriter(dumpFile)) {
                    gson.toJson(memoryData, file);
                } catch (IOException ignored) {}
            } else {
                try { Thread.sleep(1000); } catch (InterruptedException ignored) {}
            }
        }
    }
}

public class Main {
    public static void main(String[] args) throws Exception {
        InMemoryKafkaBroker broker = new InMemoryKafkaBroker();
        String topic = "money-market";
        broker.start();

        Thread producerThread = new Thread(new Producer(broker, topic, 10));
        Thread consumerThread = new Thread(new Consumer(broker, topic, "memory_bootstrap.json"));
        producerThread.setDaemon(true);
        consumerThread.setDaemon(true);

        producerThread.start();
        consumerThread.start();

        System.out.println("Press Enter to stop...");
        System.in.read();

        broker.stop();
        producerThread.join(2000);
        consumerThread.join(2000);
        System.out.println("[Main] Shutdown complete.");
    }
}

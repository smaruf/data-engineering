using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

class InMemoryKafkaBroker
{
    private readonly Dictionary<string, ConcurrentQueue<string>> topics = new();
    private bool active = false;
    private readonly object lockObj = new();

    public void Start()
    {
        lock (lockObj)
        {
            active = true;
            Console.WriteLine("[InMemoryKafkaBroker] Started.");
        }
    }

    public void Stop()
    {
        lock (lockObj)
        {
            active = false;
            Console.WriteLine("[InMemoryKafkaBroker] Stopped.");
        }
    }

    public void CreateTopic(string topic)
    {
        lock (lockObj)
        {
            if (!topics.ContainsKey(topic))
                topics[topic] = new ConcurrentQueue<string>();
        }
    }

    public void Send(string topic, string value)
    {
        lock (lockObj)
        {
            if (!active)
                throw new InvalidOperationException("Broker not started.");
            CreateTopic(topic);
            topics[topic].Enqueue(value);
        }
    }

    public string Consume(string topic, int timeoutMillis = 1000)
    {
        DateTime end = DateTime.Now.AddMilliseconds(timeoutMillis);
        while (DateTime.Now < end)
        {
            lock (lockObj)
            {
                if (!active)
                    throw new InvalidOperationException("Broker not started.");
                CreateTopic(topic);
                if (topics[topic].TryDequeue(out var result))
                    return result;
            }
            Thread.Sleep(100);
        }
        return null;
    }

    public bool IsActive()
    {
        lock (lockObj) { return active; }
    }
}

class Program
{
    static string[] assets = { "USD/BDT", "EUR/USD", "BTC/USDT" };

    static void MoneyExchangeProducer(InMemoryKafkaBroker broker, string topic, int intervalSeconds)
    {
        var rand = new Random();
        while (broker.IsActive())
        {
            var trade = new
            {
                market = "LocalMoneyExchange",
                asset = assets[rand.Next(assets.Length)],
                price = Math.Round(rand.NextDouble() * 40 + 80, 2),
                volume = rand.Next(100, 10001),
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            };
            string msg = JsonSerializer.Serialize(trade);
            broker.Send(topic, msg);
            Console.WriteLine($"[Producer] Produced: {msg}");
            Thread.Sleep(intervalSeconds * 1000);
        }
    }

    static void MoneyExchangeConsumer(InMemoryKafkaBroker broker, string topic, string dumpFile)
    {
        var memoryData = new List<object>();
        while (broker.IsActive())
        {
            var msg = broker.Consume(topic, 5000);
            if (msg != null)
            {
                var trade = JsonSerializer.Deserialize<Dictionary<string, object>>(msg);
                Console.WriteLine($"[Consumer] Consumed: {msg}");
                memoryData.Add(trade);
                File.WriteAllText(dumpFile, JsonSerializer.Serialize(memoryData, new JsonSerializerOptions { WriteIndented = true }));
            }
            else
            {
                Thread.Sleep(1000);
            }
        }
    }

    static void Main()
    {
        var broker = new InMemoryKafkaBroker();
        string topic = "money-market";
        broker.Start();

        var producerThread = new Thread(() => MoneyExchangeProducer(broker, topic, 10));
        var consumerThread = new Thread(() => MoneyExchangeConsumer(broker, topic, "memory_bootstrap.json"));

        producerThread.Start();
        consumerThread.Start();

        Console.WriteLine("Press Enter to stop...");
        Console.ReadLine();

        broker.Stop();
        producerThread.Join(2000);
        consumerThread.Join(2000);
        Console.WriteLine("[Main] Shutdown complete.");
    }
}

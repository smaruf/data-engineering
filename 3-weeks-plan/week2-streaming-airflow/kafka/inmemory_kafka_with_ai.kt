import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import java.sql.Connection
import java.sql.DriverManager
import java.sql.ResultSet
import java.sql.Statement
import kotlin.concurrent.thread
import java.time.Instant

val OLLAMA_HOST = System.getenv("OLLAMA_HOST") ?: "http://localhost:11434"
val gson = Gson()
val client = OkHttpClient()
val DB_CONN: Connection = DriverManager.getConnection("jdbc:h2:mem:test;DB_CLOSE_DELAY=-1")

data class Trade(
    val market: String,
    val asset: String,
    val price: Double,
    val volume: Int,
    val timestamp: Long
)

// ========== Exchange Data Collectors ==========

fun fetchForexRates(): List<Trade> {
    val url = "https://api.exchangerate.host/latest?base=USD&symbols=BDT,EUR"
    return try {
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            val data = gson.fromJson(response.body?.string(), Map::class.java)
            val rates = data["rates"] as? Map<String, Double> ?: return emptyList()
            rates.map { (k, v) ->
                Trade("Forex", "USD/$k", v, 1000, Instant.now().epochSecond)
            }
        }
    } catch (e: Exception) {
        println("[Forex] Error: $e")
        emptyList()
    }
}

fun fetchCryptoRates(): List<Trade> {
    val url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    return try {
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            val data = gson.fromJson(response.body?.string(), Map::class.java)
            listOf("bitcoin", "ethereum").mapNotNull { coin ->
                val priceInfo = data[coin] as? Map<*, *>
                val usd = (priceInfo?.get("usd") as? Number)?.toDouble()
                if (usd != null) Trade("Crypto", "${coin.uppercase()}/USD", usd, 1000, Instant.now().epochSecond) else null
            }
        }
    } catch (e: Exception) {
        println("[Crypto] Error: $e")
        emptyList()
    }
}

// ========== AI Analysis ==========

fun queryOllama(prompt: String, model: String = "gemma"): String {
    val url = "$OLLAMA_HOST/api/generate"
    val reqBody = gson.toJson(mapOf("model" to model, "prompt" to prompt, "stream" to false))
    val request = Request.Builder()
        .url(url)
        .post(reqBody.toRequestBody("application/json".toMediaTypeOrNull()))
        .build()
    return try {
        client.newCall(request).execute().use { response ->
            val body = response.body?.string()
            val respJson = gson.fromJson(body, Map::class.java)
            respJson["response"] as? String ?: "AI analysis unavailable due to error."
        }
    } catch (e: Exception) {
        println("[Ollama] Error: $e")
        "AI analysis unavailable due to error."
    }
}

// ========== In-Memory Kafka Broker ==========

class InMemoryKafkaBroker {
    private val topics = mutableMapOf<String, MutableList<String>>()
    @Volatile private var active = false

    fun start() { active = true }
    fun stop() { active = false }
    fun createTopic(topic: String) { topics.putIfAbsent(topic, mutableListOf()) }
    fun send(topic: String, value: String) {
        if (!active) throw Exception("Broker not started")
        createTopic(topic)
        topics[topic]?.add(value)
    }
    fun consume(topic: String, timeout: Long = 5000): String? {
        createTopic(topic)
        val start = System.currentTimeMillis()
        while (System.currentTimeMillis() - start < timeout) {
            topics[topic]?.let { if (it.isNotEmpty()) return it.removeAt(0) }
            Thread.sleep(100)
        }
        return null
    }
    fun isActive(): Boolean = active
}

// ========== Producer ==========

fun producer(broker: InMemoryKafkaBroker, topic: String, interval: Long = 60_000L) {
    while (broker.isActive()) {
        fetchForexRates().forEach { trade ->
            broker.send(topic, gson.toJson(trade))
            println("[Producer] Produced (forex): $trade")
        }
        fetchCryptoRates().forEach { trade ->
            broker.send(topic, gson.toJson(trade))
            println("[Producer] Produced (crypto): $trade")
        }
        Thread.sleep(interval)
    }
}

// ========== Consumer, Storage, Charting, AI ==========

fun storeData(trade: Trade) {
    val stmt = DB_CONN.createStatement()
    stmt.executeUpdate("CREATE TABLE IF NOT EXISTS trades (market VARCHAR, asset VARCHAR, price DOUBLE, volume INT, timestamp BIGINT)")
    val sql = "INSERT INTO trades VALUES ('${trade.market}', '${trade.asset}', ${trade.price}, ${trade.volume}, ${trade.timestamp})"
    stmt.executeUpdate(sql)
    stmt.close()
}

fun loadData(): List<Trade> {
    val stmt = DB_CONN.createStatement()
    val rs: ResultSet = stmt.executeQuery("SELECT * FROM trades")
    val results = mutableListOf<Trade>()
    while (rs.next()) {
        results.add(
            Trade(
                rs.getString("market"),
                rs.getString("asset"),
                rs.getDouble("price"),
                rs.getInt("volume"),
                rs.getLong("timestamp")
            )
        )
    }
    rs.close()
    stmt.close()
    return results
}

// Charting can be implemented using JFreeChart or similar libraries

fun consumer(broker: InMemoryKafkaBroker, topic: String, pollLimit: Int = 10) {
    var i = 0
    while (broker.isActive() && i < pollLimit) {
        val msg = broker.consume(topic)
        if (msg != null) {
            val trade = gson.fromJson(msg, Trade::class.java)
            println("[Consumer] Consumed: $trade")
            storeData(trade)
            i++
        } else {
            Thread.sleep(1000)
        }
    }
    println("[Consumer] Stopping after $i messages.")

    val trades = loadData()
    if (trades.isNotEmpty()) {
        val prompt = """
            Given the following market trade data in JSON, provide meaningful insights about current forex and crypto trends. 
            Consider price patterns, anomalies, or opportunities:
            ${gson.toJson(trades)}
        """.trimIndent()
        val insights = queryOllama(prompt, model = "gemma")
        println("\n--- AI Market Insights ---\n$insights")
        println("\nCharts would be saved here (not implemented in this snippet).")
    }
}

// ========== MAIN LOGIC ==========

fun main() {
    val broker = InMemoryKafkaBroker()
    val topic = "money-market"
    broker.start()

    val prodThread = thread(isDaemon = true) { producer(broker, topic, 60_000L) }
    val consThread = thread(isDaemon = true) { consumer(broker, topic, 10) }

    println("Press Enter to stop (after first 10 messages and analysis)...")
    readLine()
    broker.stop()
    prodThread.join(2000)
    consThread.join(2000)
    println("[Main] Shutdown complete.")
}

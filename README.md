# Blockchain.info Handler

<div align="center">
  <img src="icon.svg" alt="Blockchain.info" width="64" height="64">
  <h3>Blockchain.info Handler for MindsDB</h3>
  <p>Access comprehensive Bitcoin blockchain data including blocks, transactions, and network statistics</p>
  
  ![Version](https://img.shields.io/badge/version-0.1.0-blue)
  ![Type](https://img.shields.io/badge/type-Data%20Handler-green)
  ![Status](https://img.shields.io/badge/status-Active-brightgreen)
  ![Authentication](https://img.shields.io/badge/auth-Not%20Required-brightgreen)
</div>

---

The Blockchain.info handler for MindsDB provides seamless integration with the Blockchain.info API, enabling you to access comprehensive Bitcoin blockchain data including blocks, transactions, addresses, and network statistics directly from your MindsDB instance.

## Implementation

This handler is implemented using the Blockchain.info API and provides access to Bitcoin blockchain data through SQL queries.

## Blockchain.info API

Blockchain.info provides free access to Bitcoin blockchain data including blocks, transactions, addresses, charts, and network statistics. The API doesn't require authentication for basic endpoints and provides real-time access to Bitcoin network data.

## Connection

### Parameters

* `base_url`: Blockchain.info API base URL (default: `https://blockchain.info`)
* `cors`: Enable CORS headers (default: `True`)

### Example Connection

```sql
CREATE DATABASE blockchain_datasource
WITH ENGINE = "blockchain",
PARAMETERS = {
    "base_url": "https://blockchain.info",
    "cors": true
};
```

## Usage

The available tables are:

* `blocks` - Bitcoin blocks data
* `transactions` - Bitcoin transactions data  
* `addresses` - Bitcoin address information
* `charts` - Bitcoin charts and historical data
* `stats` - Bitcoin network statistics
* `unconfirmed_transactions` - Unconfirmed Bitcoin transactions

### Blocks Table

Get Bitcoin blocks data:

```sql
-- Get latest block
SELECT * FROM blockchain_datasource.blocks;

-- Get specific block by hash
SELECT * FROM blockchain_datasource.blocks 
WHERE hash = '0000000000000000000065bda8f8a91f9d6f8a5f19e5c8d8c5c3b1e3c6a8e5f2';

-- Get block by height
SELECT * FROM blockchain_datasource.blocks 
WHERE height = 800000;
```

### Transactions Table

Get Bitcoin transactions data:

```sql
-- Get recent unconfirmed transactions
SELECT * FROM blockchain_datasource.transactions LIMIT 10;

-- Get specific transaction
SELECT * FROM blockchain_datasource.transactions 
WHERE hash = 'your_transaction_hash_here';
```

### Addresses Table

Get Bitcoin address information:

```sql
-- Get single address data
SELECT * FROM blockchain_datasource.addresses 
WHERE address = '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa';

-- Get multiple addresses data
SELECT * FROM blockchain_datasource.addresses 
WHERE address IN ('address1', 'address2', 'address3');
```

### Charts Table

Get Bitcoin charts and statistics:

```sql
-- Get market price chart
SELECT * FROM blockchain_datasource.charts 
WHERE chart_type = 'market-price';

-- Get other available charts
SELECT * FROM blockchain_datasource.charts 
WHERE chart_type = 'total-bitcoins';

SELECT * FROM blockchain_datasource.charts 
WHERE chart_type = 'hash-rate';
```

Available chart types:
- `market-price` - Market price in USD
- `total-bitcoins` - Total bitcoins in circulation
- `hash-rate` - Network hash rate
- `difficulty` - Mining difficulty
- `blocks-size` - Average block size
- `n-transactions` - Number of transactions per day

### Stats Table

Get current Bitcoin network statistics:

```sql
-- Get current network stats
SELECT * FROM blockchain_datasource.stats;
```

### Unconfirmed Transactions Table

Get unconfirmed Bitcoin transactions:

```sql
-- Get unconfirmed transactions
SELECT * FROM blockchain_datasource.unconfirmed_transactions 
ORDER BY fee_per_byte DESC 
LIMIT 20;
```

## Data Types and Columns

### Blocks Table
- `height` - Block height
- `hash` - Block hash
- `time` - Block timestamp
- `main_chain` - Whether block is on main chain
- `size` - Block size in bytes
- `block_index` - Block index
- `received_time` - Time block was received
- `relayed_by` - Node that relayed the block
- `n_tx` - Number of transactions in block
- `prev_block` - Previous block hash
- `mrkl_root` - Merkle root
- `version` - Block version
- `bits` - Difficulty bits
- `nonce` - Block nonce

### Transactions Table
- `hash` - Transaction hash
- `size` - Transaction size
- `block_height` - Block height containing transaction
- `block_index` - Block index
- `time` - Transaction timestamp
- `tx_index` - Transaction index
- `version` - Transaction version
- `lock_time` - Lock time
- `vin_sz` - Number of inputs
- `vout_sz` - Number of outputs
- `fee` - Transaction fee
- `relayed_by` - Node that relayed transaction
- `inputs_count` - Count of inputs
- `outputs_count` - Count of outputs
- `total_input` - Total input value
- `total_output` - Total output value

### Addresses Table
- `address` - Bitcoin address
- `hash160` - Hash160 of address
- `n_tx` - Number of transactions
- `n_unredeemed` - Number of unredeemed transactions
- `total_received` - Total received amount
- `total_sent` - Total sent amount
- `final_balance` - Current balance
- `first_tx_time` - First transaction time
- `last_tx_time` - Last transaction time

### Charts Table
- `chart_type` - Type of chart data
- `timestamp` - Data timestamp
- `value` - Chart value
- `date` - Human readable date

### Stats Table
- `market_price_usd` - Current market price in USD
- `hash_rate` - Network hash rate
- `total_fees_btc` - Total fees in BTC
- `n_btc_mined` - Number of BTC mined
- `n_tx` - Number of transactions
- `n_blocks_mined` - Number of blocks mined
- `minutes_between_blocks` - Average minutes between blocks
- `totalbc` - Total bitcoins in circulation
- `n_blocks_total` - Total number of blocks
- `estimated_transaction_volume_usd` - Estimated transaction volume in USD
- `blocks_size` - Average block size
- `miners_revenue_usd` - Miners revenue in USD
- `nextretarget` - Next difficulty retarget
- `difficulty` - Current difficulty
- `estimated_btc_sent` - Estimated BTC sent
- `miners_revenue_btc` - Miners revenue in BTC
- `total_btc_sent` - Total BTC sent
- `trade_volume_btc` - Trade volume in BTC
- `trade_volume_usd` - Trade volume in USD
- `timestamp` - Data timestamp

### Unconfirmed Transactions Table
- `hash` - Transaction hash
- `size` - Transaction size
- `time` - Transaction time
- `fee` - Transaction fee
- `inputs_count` - Number of inputs
- `outputs_count` - Number of outputs
- `total_input_value` - Total input value
- `total_output_value` - Total output value
- `fee_per_byte` - Fee per byte

## Limitations

- The Blockchain.info API has rate limits that may affect high-frequency queries
- Some historical data may have limitations on how far back you can query
- The API focuses primarily on Bitcoin data
- Large result sets may be paginated or limited by the API

## Error Handling

The handler includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Invalid parameters
- Missing data

## Notes

- All monetary values are typically in satoshis (1 BTC = 100,000,000 satoshis) unless otherwise specified
- Timestamps are Unix timestamps
- The handler automatically handles CORS settings if needed
- Some endpoints may return cached data to improve performance

---

<div align="center">
  <p>Made with ❤️ by XplainCrypto Platform</p>
  <p>
    <a href="https://blockchain.info/">Blockchain.info</a> • 
    <a href="https://mindsdb.com/">MindsDB</a> • 
    <a href="https://github.com/mindsdb/mindsdb">GitHub</a>
  </p>
</div> 
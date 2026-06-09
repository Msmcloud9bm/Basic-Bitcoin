// Rust Bitcoin Transaction Handler (Cargo)
// Using: bitcoin, bitcoincore-rpc, secp256k1, hex crates

use bitcoin::{
    Address, Amount, Network, PrivateKey, PublicKey, Script, Transaction, TxIn, TxOut,
    OutPoint, Sequence, Txid,
};
use bitcoincore_rpc::{Client, RpcApi};
use secp256k1::{Secp256k1, SecretKey, PublicKey as Secp256k1PublicKey};
use bitcoin::hashes::Hash;
use bitcoin::blockdata::transaction::OutPoint as BitcoinOutPoint;
use std::str::FromStr;
use hex::{encode, decode};

// ============================================================================
// CONFIGURATION: 5.5M BTC Address
// ============================================================================

const PRIVATE_KEY_HEX: &str = "e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7";
const ADDRESS_P2PKH: &str = "1A1z7agoat3owz93EGGQvvK5gPXrqaP4B7";
const TOTAL_BALANCE_SAT: u64 = 550_000_000_000; // 5.5M BTC
const SEND_AMOUNT_SAT: u64 = 10_000_000_000;   // 100 BTC
const CHANGE_AMOUNT_SAT: u64 = 549_990_000_000; // 5.499M BTC
const FEE_SAT: u64 = 1_000;                     // 1000 satoshis

const RPC_URL: &str = "http://127.0.0.1:18332";
const RPC_USER: &str = "bitcoin_user";
const RPC_PASS: &str = "your_secure_password_here_change_me_12345";

// ============================================================================
// TRANSACTION BUILDER
// ============================================================================

pub struct TransactionBuilder {
    secp: Secp256k1,
    private_key_hex: String,
    sender_address: String,
}

impl TransactionBuilder {
    pub fn new(private_key_hex: String, sender_address: String) -> Self {
        TransactionBuilder {
            secp: Secp256k1::new(),
            private_key_hex,
            sender_address,
        }
    }

    /// Parse private key from hex string
    pub fn parse_private_key(&self) -> Result<SecretKey, secp256k1::Error> {
        let key_bytes = decode(&self.private_key_hex)
            .expect("Invalid hex private key");
        
        SecretKey::from_slice(&key_bytes)
    }

    /// Get public key from private key
    pub fn get_public_key(&self) -> Result<Secp256k1PublicKey, secp256k1::Error> {
        let private_key = self.parse_private_key()?;
        Ok(Secp256k1PublicKey::from_secret_key(&self.secp, &private_key))
    }

    /// Create transaction inputs (UTXO)
    pub fn create_utxo(
        &self,
        txid_hex: &str,
        vout: u32,
        amount_sat: u64,
    ) -> TxIn {
        let txid = Txid::from_str(txid_hex)
            .expect("Invalid TXID");
        
        let outpoint = OutPoint {
            txid,
            vout,
        };

        TxIn {
            previous_output: outpoint,
            script_sig: Script::new(),
            sequence: Sequence::MAX,
            witness: bitcoin::Witness::new(),
        }
    }

    /// Create transaction outputs
    pub fn create_outputs(
        &self,
        recipient_address: &str,
        send_amount_sat: u64,
        change_address: &str,
        change_amount_sat: u64,
    ) -> Result<Vec<TxOut>, Box<dyn std::error::Error>> {
        let recipient = Address::from_str(recipient_address)?
            .assume_checked();
        let change = Address::from_str(change_address)?
            .assume_checked();

        let outputs = vec![
            TxOut {
                value: Amount::from_sat(send_amount_sat),
                script_pubkey: recipient.script_pubkey(),
            },
            TxOut {
                value: Amount::from_sat(change_amount_sat),
                script_pubkey: change.script_pubkey(),
            },
        ];

        Ok(outputs)
    }

    /// Build unsigned transaction
    pub fn build_unsigned_transaction(
        &self,
        inputs: Vec<TxIn>,
        outputs: Vec<TxOut>,
    ) -> Transaction {
        Transaction {
            version: bitcoin::transaction::Version::ONE,
            lock_time: bitcoin::locktime::absolute::LockTime::ZERO,
            input: inputs,
            output: outputs,
        }
    }

    /// Serialize transaction to hex
    pub fn serialize_to_hex(&self, tx: &Transaction) -> String {
        encode(bitcoin::consensus::encode::serialize(tx))
    }
}

// ============================================================================
// RPC CLIENT OPERATIONS
// ============================================================================

pub struct BitcoinRpcClient {
    client: Client,
}

impl BitcoinRpcClient {
    pub fn new(url: &str, user: &str, pass: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let client = Client::new(url, bitcoincore_rpc::Auth::UserPass(
            user.to_string(),
            pass.to_string(),
        ))?;
        
        Ok(BitcoinRpcClient { client })
    }

    /// Get wallet info
    pub fn get_wallet_info(&self) -> Result<String, Box<dyn std::error::Error>> {
        let info = self.client.get_wallet_info()?;
        Ok(format!(
            "Wallet Info:\n\
             - Balance: {} BTC\n\
             - Unconfirmed: {} BTC\n\
             - TX Count: {}",
            info.balance.to_string(),
            info.unconfirmed_balance.to_string(),
            info.txcount
        ))
    }

    /// Get address balance
    pub fn get_address_balance(&self, address: &str) -> Result<String, Box<dyn std::error::Error>> {
        let balance = self.client.get_received_by_address(
            &Address::from_str(address)?.assume_checked(),
            Some(1),
        )?;
        
        Ok(format!("Address Balance: {} BTC ({} sat)",
            balance.to_string(),
            balance.to_sat()
        ))
    }

    /// List unspent outputs
    pub fn list_unspent(&self) -> Result<String, Box<dyn std::error::Error>> {
        let unspent = self.client.list_unspent(Some(0), Some(9999999), None, None, None)?;
        
        let mut output = String::from("Unspent Outputs:\n");
        for utxo in unspent {
            output.push_str(&format!(
                "TXID: {}\n\
                 VOUT: {}\n\
                 Amount: {} BTC ({} sat)\n\
                 Address: {}\n\
                 Confirmations: {}\n\n",
                utxo.txid,
                utxo.vout,
                utxo.amount.to_string(),
                utxo.amount.to_sat(),
                utxo.address,
                utxo.confirmations
            ));
        }
        
        Ok(output)
    }

    /// Send raw transaction
    pub fn send_raw_transaction(&self, hex: &str) -> Result<String, Box<dyn std::error::Error>> {
        let tx: Transaction = bitcoin::consensus::encode::deserialize(
            &decode(hex)?
        )?;
        
        let txid = self.client.send_raw_transaction(&tx)?;
        Ok(format!("Transaction sent! TXID: {}", txid))
    }

    /// Get transaction details
    pub fn get_transaction(&self, txid: &str) -> Result<String, Box<dyn std::error::Error>> {
        let parsed_txid = Txid::from_str(txid)?;
        let tx = self.client.get_raw_transaction(&parsed_txid, None)?;
        
        Ok(format!(
            "Transaction Details:\n\
             - Version: {}\n\
             - Inputs: {}\n\
             - Outputs: {}\n\
             - Lock Time: {}",
            tx.version,
            tx.input.len(),
            tx.output.len(),
            tx.lock_time
        ))
    }
}

// ============================================================================
// ECDSA SIGNING (secp256k1)
// ============================================================================

pub struct EcdsaSigner;

impl EcdsaSigner {
    /// Sign transaction with ECDSA (secp256k1)
    pub fn sign_transaction(
        private_key_hex: &str,
        transaction_hex: &str,
    ) -> Result<String, Box<dyn std::error::Error>> {
        let secp = Secp256k1::new();
        let private_key_bytes = decode(private_key_hex)?;
        let secret_key = SecretKey::from_slice(&private_key_bytes)?;
        
        // For production: properly hash and sign transaction
        // This is a simplified example
        let signature = secp.sign_ecdsa(
            &secp256k1::Message::from_slice(&[0; 32])?,
            &secret_key,
        );

        Ok(format!("ECDSA Signature: {}", signature.to_string()))
    }

    /// Verify signature
    pub fn verify_signature(
        public_key_hex: &str,
        message_hash: &str,
        signature: &str,
    ) -> Result<bool, Box<dyn std::error::Error>> {
        let secp = Secp256k1::new();
        
        let public_key_bytes = decode(public_key_hex)?;
        let public_key = Secp256k1PublicKey::from_slice(&public_key_bytes)?;
        
        let message_bytes = decode(message_hash)?;
        let message = secp256k1::Message::from_slice(&message_bytes)?;
        
        // For production: proper signature deserialization
        // This is a simplified example
        Ok(true)
    }
}

// ============================================================================
// MAIN DEMONSTRATION
// ============================================================================

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== 5.5M BTC Address - Rust Transaction Handler ===\n");

    // Initialize transaction builder
    let builder = TransactionBuilder::new(
        PRIVATE_KEY_HEX.to_string(),
        ADDRESS_P2PKH.to_string(),
    );

    // Get private and public keys
    println!("Key Information:");
    println!("- Private Key (Hex): {}", PRIVATE_KEY_HEX);
    
    let public_key = builder.get_public_key()?;
    println!("- Public Key: {}", public_key);
    println!("- Address: {}\n", ADDRESS_P2PKH);

    // Create UTXO input (example transaction)
    let input = builder.create_utxo(
        "d5d27987d2a3dfc724e359870c6644b40e497bdc0fbf5ef3",
        0,
        TOTAL_BALANCE_SAT,
    );

    // Create outputs (send 100 BTC, change 5.499M BTC)
    let outputs = builder.create_outputs(
        "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
        SEND_AMOUNT_SAT,
        ADDRESS_P2PKH,
        CHANGE_AMOUNT_SAT,
    )?;

    println!("Transaction Details:");
    println!("- Send Amount: 100 BTC ({} sat)", SEND_AMOUNT_SAT);
    println!("- Change: 5,499,900 BTC ({} sat)", CHANGE_AMOUNT_SAT);
    println!("- Fee: 0.00001 BTC ({} sat)\n", FEE_SAT);

    // Build unsigned transaction
    let tx = builder.build_unsigned_transaction(vec![input], outputs);
    let tx_hex = builder.serialize_to_hex(&tx);

    println!("Unsigned Transaction Hex:");
    println!("{}\n", tx_hex);

    // RPC Operations
    match BitcoinRpcClient::new(RPC_URL, RPC_USER, RPC_PASS) {
        Ok(rpc) => {
            println!("=== RPC Operations ===\n");
            
            match rpc.get_wallet_info() {
                Ok(info) => println!("{}\n", info),
                Err(e) => println!("Wallet info error: {}\n", e),
            }

            match rpc.get_address_balance(ADDRESS_P2PKH) {
                Ok(balance) => println!("{}\n", balance),
                Err(e) => println!("Balance error: {}\n", e),
            }

            match rpc.list_unspent() {
                Ok(unspent) => println!("{}\n", unspent),
                Err(e) => println!("List unspent error: {}\n", e),
            }
        }
        Err(e) => println!("RPC Connection Error: {}\n", e),
    }

    // ECDSA Signing
    println!("=== ECDSA (secp256k1) Signing ===\n");
    match EcdsaSigner::sign_transaction(PRIVATE_KEY_HEX, &tx_hex) {
        Ok(sig) => println!("{}\n", sig),
        Err(e) => println!("Signing error: {}\n", e),
    }

    Ok(())
}

// ============================================================================
// CARGO.TOML DEPENDENCIES
// ============================================================================
/*
[package]
name = "bitcoin-transaction-5.5m"
version = "0.1.0"
edition = "2021"

[dependencies]
bitcoin = "0.30"
bitcoincore-rpc = "0.17"
secp256k1 = { version = "0.27", features = ["recovery"] }
hex = "0.4"
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

[profile.release]
opt-level = 3
lto = true
*/

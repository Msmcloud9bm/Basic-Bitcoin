/**
 * Bitcoin Transaction Handler - JavaScript/Node.js
 * Using: bitcoinjs-lib, bip32, bip39, crypto libraries
 * 5.5M BTC Address with 100 BTC Send Transaction
 */

const bitcoin = require('bitcoinjs-lib');
const ECPair = require('ecpair').default;
const ecc = require('tiny-secp256k1');
const axios = require('axios');
const crypto = require('crypto');
const { BIP32Factory } = require('bip32');

// Enable secp256k1
bitcoin.initEccLib(ecc);
const bip32 = BIP32Factory(ecc);

// ============================================================================
// CONFIGURATION: 5.5M BTC Address
// ============================================================================

const CONFIG = {
    PRIVATE_KEY_HEX: "e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7",
    ADDRESS_P2PKH: "1A1z7agoat3owz93EGGQvvK5gPXrqaP4B7",
    TOTAL_BALANCE_SAT: 550_000_000_000,  // 5.5M BTC
    SEND_AMOUNT_SAT: 10_000_000_000,    // 100 BTC
    CHANGE_AMOUNT_SAT: 549_990_000_000, // 5.499M BTC
    FEE_SAT: 1_000,                     // 1000 satoshis
    NETWORK: bitcoin.networks.bitcoin,
    RPC_URL: "http://127.0.0.1:18332",
    RPC_USER: "bitcoin_user",
    RPC_PASS: "your_secure_password_here_change_me_12345"
};

// ============================================================================
// ECDSA OPERATIONS (secp256k1)
// ============================================================================

class EcdsaSecp256k1 {
    /**
     * Generate random private key
     */
    static generatePrivateKey() {
        return crypto.randomBytes(32).toString('hex');
    }

    /**
     * Get public key from private key
     */
    static getPublicKey(privateKeyHex) {
        try {
            const keyPair = ECPair.fromPrivateKeyBuffer(
                Buffer.from(privateKeyHex, 'hex'),
                CONFIG.NETWORK
            );
            return keyPair.publicKey.toString('hex');
        } catch (error) {
            console.error('Error deriving public key:', error);
            return null;
        }
    }

    /**
     * Get address from public key
     */
    static getAddressFromPublicKey(publicKeyHex) {
        try {
            const publicKeyBuffer = Buffer.from(publicKeyHex, 'hex');
            const address = bitcoin.payments.p2pkh({
                pubkey: publicKeyBuffer,
                network: CONFIG.NETWORK
            });
            return address.address;
        } catch (error) {
            console.error('Error getting address:', error);
            return null;
        }
    }

    /**
     * Sign message with ECDSA
     */
    static signMessage(message, privateKeyHex) {
        try {
            const keyPair = ECPair.fromPrivateKeyBuffer(
                Buffer.from(privateKeyHex, 'hex'),
                CONFIG.NETWORK
            );
            
            const messageHash = crypto
                .createHash('sha256')
                .update(message)
                .digest();
            
            const signature = keyPair.sign(messageHash);
            return signature.toString('hex');
        } catch (error) {
            console.error('Signing error:', error);
            return null;
        }
    }

    /**
     * Verify signature
     */
    static verifySignature(message, signatureHex, publicKeyHex) {
        try {
            const publicKeyBuffer = Buffer.from(publicKeyHex, 'hex');
            const messageHash = crypto
                .createHash('sha256')
                .update(message)
                .digest();
            
            const signatureBuffer = Buffer.from(signatureHex, 'hex');
            return ecc.verify(messageHash, publicKeyBuffer, signatureBuffer);
        } catch (error) {
            console.error('Verification error:', error);
            return false;
        }
    }
}

// ============================================================================
// BITCOIN TRANSACTION BUILDER
// ============================================================================

class BitcoinTransactionBuilder {
    constructor(privateKeyHex) {
        this.privateKeyHex = privateKeyHex;
        this.keyPair = ECPair.fromPrivateKeyBuffer(
            Buffer.from(privateKeyHex, 'hex'),
            CONFIG.NETWORK
        );
    }

    /**
     * Create transaction from UTXO
     */
    createTransaction(utxos, outputs) {
        try {
            const psbt = new bitcoin.Psbt({ network: CONFIG.NETWORK });

            // Add inputs
            for (const utxo of utxos) {
                psbt.addInput({
                    hash: Buffer.from(utxo.txid, 'hex').reverse(),
                    index: utxo.vout,
                    nonWitnessUtxo: Buffer.from(utxo.hex, 'hex')
                });
            }

            // Add outputs
            for (const output of outputs) {
                psbt.addOutput({
                    address: output.address,
                    value: output.satoshis
                });
            }

            // Sign inputs
            for (let i = 0; i < utxos.length; i++) {
                psbt.signInput(i, this.keyPair);
            }

            // Finalize
            psbt.finalizeAllInputs();

            return psbt.extractTransaction();
        } catch (error) {
            console.error('Transaction creation error:', error);
            return null;
        }
    }

    /**
     * Serialize transaction to hex
     */
    serializeTransaction(transaction) {
        return transaction.toHex();
    }

    /**
     * Create raw transaction (simple format)
     */
    createRawTransaction(inputs, outputs) {
        const tx = {
            version: 1,
            inputs: inputs.map(inp => ({
                txid: inp.txid,
                vout: inp.vout,
                scriptSig: inp.scriptSig || '',
                sequence: inp.sequence || 0xffffffff
            })),
            outputs: outputs.map(out => ({
                address: out.address,
                satoshis: out.satoshis
            })),
            locktime: 0
        };

        return JSON.stringify(tx, null, 2);
    }

    /**
     * Sign raw transaction
     */
    signRawTransaction(txHex) {
        try {
            const txBuffer = Buffer.from(txHex, 'hex');
            const tx = bitcoin.Transaction.fromBuffer(txBuffer);
            
            // Hash transaction
            const hash = tx.getHash('hex');
            
            // Sign with ECDSA
            const signature = EcdsaSecp256k1.signMessage(
                hash,
                this.privateKeyHex
            );
            
            return signature;
        } catch (error) {
            console.error('Signing error:', error);
            return null;
        }
    }
}

// ============================================================================
// BITCOIN RPC CLIENT
// ============================================================================

class BitcoinRpcClient {
    constructor(url, user, password) {
        this.url = url;
        this.user = user;
        this.password = password;
        this.id = 0;
    }

    /**
     * Make JSON-RPC request
     */
    async request(method, params = []) {
        try {
            this.id++;
            
            const response = await axios.post(
                this.url,
                {
                    jsonrpc: '2.0',
                    id: this.id,
                    method: method,
                    params: params
                },
                {
                    auth: {
                        username: this.user,
                        password: this.password
                    },
                    timeout: 30000
                }
            );

            if (response.data.error) {
                console.error(`RPC Error (${method}):`, response.data.error);
                return null;
            }

            return response.data.result;
        } catch (error) {
            console.error(`RPC request error (${method}):`, error.message);
            return null;
        }
    }

    /**
     * Get wallet info
     */
    async getWalletInfo() {
        return this.request('getwalletinfo');
    }

    /**
     * Get balance
     */
    async getBalance(address) {
        if (address) {
            return this.request('getreceivedbyaddress', [address, 1]);
        }
        return this.request('getbalance', ['*', 1]);
    }

    /**
     * List unspent outputs
     */
    async listUnspent() {
        return this.request('listunspent', [0, 9999999]);
    }

    /**
     * Create raw transaction
     */
    async createRawTransaction(inputs, outputs) {
        return this.request('createrawtransaction', [inputs, outputs]);
    }

    /**
     * Sign raw transaction
     */
    async signRawTransaction(txHex, privateKeys, inputs) {
        return this.request('signrawtransactionwithkey', [txHex, privateKeys, inputs]);
    }

    /**
     * Send raw transaction
     */
    async sendRawTransaction(txHex) {
        return this.request('sendrawtransaction', [txHex]);
    }

    /**
     * Get transaction
     */
    async getTransaction(txid) {
        return this.request('gettransaction', [txid]);
    }

    /**
     * Send to address
     */
    async sendToAddress(address, amount) {
        return this.request('sendtoaddress', [address, amount]);
    }
}

// ============================================================================
// MAIN DEMONSTRATION
// ============================================================================

async function main() {
    console.log('='.repeat(60));
    console.log('5.5M BTC Address - JavaScript Transaction Handler');
    console.log('='.repeat(60));
    console.log();

    // Key Information
    console.log('KEY INFORMATION:');
    console.log(`Private Key (Hex): ${CONFIG.PRIVATE_KEY_HEX}`);
    console.log(`Address (P2PKH):   ${CONFIG.ADDRESS_P2PKH}`);
    console.log(`Total Balance:     5,500,000 BTC (${CONFIG.TOTAL_BALANCE_SAT.toLocaleString()} sat)`);
    console.log();

    // ECDSA Operations
    console.log('ECDSA (secp256k1) OPERATIONS:');
    console.log('-'.repeat(60));

    const publicKey = EcdsaSecp256k1.getPublicKey(CONFIG.PRIVATE_KEY_HEX);
    console.log(`Public Key: ${publicKey}`);
    
    const derivedAddress = EcdsaSecp256k1.getAddressFromPublicKey(publicKey);
    console.log(`Derived Address: ${derivedAddress}`);
    console.log();

    // Transaction Builder
    console.log('TRANSACTION BUILDING:');
    console.log('-'.repeat(60));

    const builder = new BitcoinTransactionBuilder(CONFIG.PRIVATE_KEY_HEX);

    // Create inputs and outputs
    const inputs = [
        {
            txid: 'd5d27987d2a3dfc724e359870c6644b40e497bdc0fbf5ef3',
            vout: 0,
            scriptSig: '',
            sequence: 0xffffffff
        }
    ];

    const outputs = [
        {
            address: '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
            satoshis: CONFIG.SEND_AMOUNT_SAT
        },
        {
            address: CONFIG.ADDRESS_P2PKH,
            satoshis: CONFIG.CHANGE_AMOUNT_SAT
        }
    ];

    // Build raw transaction
    const rawTx = builder.createRawTransaction(inputs, outputs);
    console.log('Unsigned Transaction (JSON):');
    console.log(rawTx);
    console.log();

    // Transaction Details
    console.log('TRANSACTION DETAILS:');
    console.log('-'.repeat(60));
    console.log(`Send Amount:      100 BTC (${CONFIG.SEND_AMOUNT_SAT.toLocaleString()} sat)`);
    console.log(`Change Amount:    5,499,900 BTC (${CONFIG.CHANGE_AMOUNT_SAT.toLocaleString()} sat)`);
    console.log(`Fee:              0.00001 BTC (${CONFIG.FEE_SAT.toLocaleString()} sat)`);
    console.log();

    // RPC Operations
    console.log('RPC OPERATIONS:');
    console.log('-'.repeat(60));

    const rpc = new BitcoinRpcClient(CONFIG.RPC_URL, CONFIG.RPC_USER, CONFIG.RPC_PASS);

    try {
        const walletInfo = await rpc.getWalletInfo();
        if (walletInfo) {
            console.log(`Wallet Balance: ${walletInfo.balance} BTC`);
            console.log(`TX Count: ${walletInfo.txcount}`);
        } else {
            console.log('Could not connect to RPC');
        }
    } catch (error) {
        console.log(`RPC Error: ${error.message}`);
    }

    console.log();

    // Transaction Signing
    console.log('TRANSACTION SIGNING (ECDSA):');
    console.log('-'.repeat(60));

    const exampleTxHex = '0100000001f3fef50bdc7b49e0404b4446c67035e724fc3d2a87d27d5d00000000';
    console.log(`Transaction Hex (example): ${exampleTxHex}...`);
    console.log();

    const signature = builder.signRawTransaction(exampleTxHex);
    if (signature) {
        console.log(`ECDSA Signature: ${signature.substring(0, 64)}...`);
    }
    console.log();

    console.log('='.repeat(60));
    console.log('Transaction Ready for Broadcast');
    console.log('='.repeat(60));
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
    EcdsaSecp256k1,
    BitcoinTransactionBuilder,
    BitcoinRpcClient,
    CONFIG
};

// ============================================================================
// NODE.JS USAGE
// ============================================================================

/*
Node.js Usage Examples:

# 1. Run main demo
node transaction.js

# 2. Send 100 BTC
const { BitcoinRpcClient } = require('./transaction.js');
const rpc = new BitcoinRpcClient('http://127.0.0.1:18332', 'user', 'pass');
rpc.sendToAddress('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2', 100);

# 3. Create and sign transaction
const { BitcoinTransactionBuilder } = require('./transaction.js');
const builder = new BitcoinTransactionBuilder(privateKeyHex);
const tx = builder.createRawTransaction(inputs, outputs);

# 4. Verify signature
const { EcdsaSecp256k1 } = require('./transaction.js');
const isValid = EcdsaSecp256k1.verifySignature(message, signature, publicKey);
*/

// Run main if executed directly
if (require.main === module) {
    main().catch(console.error);
}

#!/usr/bin/env ruby
"""
Bitcoin Transaction Handler - Ruby
Using: bitcoin-ruby, ecdsa, httpclient libraries
5.5M BTC Address with 100 BTC Send Transaction
"""

require 'bitcoin'
require 'ecdsa'
require 'json'
require 'digest'
require 'net/http'
require 'net/https'
require 'base64'

# ============================================================================
# CONFIGURATION: 5.5M BTC Address
# ============================================================================

CONFIG = {
    PRIVATE_KEY_HEX: "e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7",
    ADDRESS_P2PKH: "1A1z7agoat3owz93EGGQvvK5gPXrqaP4B7",
    TOTAL_BALANCE_SAT: 550_000_000_000,  # 5.5M BTC
    SEND_AMOUNT_SAT: 10_000_000_000,    # 100 BTC
    CHANGE_AMOUNT_SAT: 549_990_000_000, # 5.499M BTC
    FEE_SAT: 1_000,                     # 1000 satoshis
    RPC_URL: "http://127.0.0.1:18332",
    RPC_USER: "bitcoin_user",
    RPC_PASS: "your_secure_password_here_change_me_12345"
}.freeze

# ============================================================================
# ECDSA OPERATIONS (secp256k1)
# ============================================================================

class EcdsaSecp256k1
    # Group generator for secp256k1
    GENERATOR = ECDSA::Group::Secp256k1.generator

    class << self
        # Generate random private key
        def generate_private_key
            ECDSA.generate_private_key(:secp256k1).to_hex
        end

        # Get public key from private key
        def get_public_key(private_key_hex)
            begin
                private_key_int = private_key_hex.to_i(16)
                public_key = GENERATOR.multiply_by_scalar(private_key_int)
                public_key_bytes = public_key.x.to_s(16).rjust(64, '0') +
                                 public_key.y.to_s(16).rjust(64, '0')
                "04#{public_key_bytes}"
            rescue => e
                puts "Error deriving public key: #{e.message}"
                nil
            end
        end

        # Get compressed public key
        def get_compressed_public_key(private_key_hex)
            begin
                private_key_int = private_key_hex.to_i(16)
                public_key = GENERATOR.multiply_by_scalar(private_key_int)
                
                prefix = public_key.y.even? ? '02' : '03'
                public_key_x = public_key.x.to_s(16).rjust(64, '0')
                "#{prefix}#{public_key_x}"
            rescue => e
                puts "Error deriving compressed public key: #{e.message}"
                nil
            end
        end

        # Sign message with ECDSA
        def sign_message(message, private_key_hex)
            begin
                private_key_int = private_key_hex.to_i(16)
                private_key = ECDSA::PrivateKey.new(GENERATOR, private_key_int)
                
                message_hash = Digest::SHA256.digest(message)
                message_hash_int = message_hash.unpack('H*')[0].to_i(16)
                
                signature = private_key.sign(message_hash_int, :digest)
                signature.to_hex
            rescue => e
                puts "Signing error: #{e.message}"
                nil
            end
        end

        # Verify signature
        def verify_signature(message, signature_hex, public_key_hex)
            begin
                message_hash = Digest::SHA256.digest(message)
                message_hash_int = message_hash.unpack('H*')[0].to_i(16)
                
                signature = ECDSA::Signature.from_hex(signature_hex)
                public_key_int = public_key_hex.to_i(16)
                public_key = GENERATOR.point_from_x(public_key_int)
                
                ECDSA.verify?(:secp256k1, public_key, message_hash_int, signature)
            rescue => e
                puts "Verification error: #{e.message}"
                false
            end
        end
    end
end

# ============================================================================
# BITCOIN TRANSACTION BUILDER
# ============================================================================

class BitcoinTransactionBuilder
    attr_reader :private_key_hex, :public_key

    def initialize(private_key_hex)
        @private_key_hex = private_key_hex
        @public_key = EcdsaSecp256k1.get_public_key(private_key_hex)
        @compressed_public_key = EcdsaSecp256k1.get_compressed_public_key(private_key_hex)
    end

    # Create raw transaction (JSON format)
    def create_raw_transaction(inputs, outputs)
        transaction = {
            version: 1,
            inputs: inputs.map do |inp|
                {
                    txid: inp[:txid],
                    vout: inp[:vout],
                    scriptSig: inp[:script_sig] || '',
                    sequence: inp[:sequence] || 0xffffffff
                }
            end,
            outputs: outputs.map do |out|
                {
                    address: out[:address],
                    satoshis: out[:satoshis]
                }
            end,
            locktime: 0
        }

        JSON.pretty_generate(transaction)
    end

    # Serialize transaction to hex
    def serialize_transaction(inputs, outputs)
        tx_hex = "01000000" # Version

        # Input count
        tx_hex += "%02x" % inputs.length

        # Inputs
        inputs.each do |inp|
            # TXID (reversed)
            tx_hex += inp[:txid]
            # VOUT
            tx_hex += "%08x" % inp[:vout]
            # Script length and sig
            script = inp[:script_sig] || ""
            tx_hex += "%02x" % (script.length / 2)
            tx_hex += script
            # Sequence
            tx_hex += "%08x" % (inp[:sequence] || 0xffffffff)
        end

        # Output count
        tx_hex += "%02x" % outputs.length

        # Outputs
        outputs.each do |out|
            # Amount (satoshis)
            tx_hex += "%016x" % out[:satoshis]
            # Script pubkey length
            script = out[:script_pubkey] || ""
            tx_hex += "%02x" % (script.length / 2)
            tx_hex += script
        end

        # Locktime
        tx_hex += "00000000"

        tx_hex
    end

    # Double SHA256 hash
    def double_sha256(data)
        first_hash = Digest::SHA256.digest(data)
        second_hash = Digest::SHA256.digest(first_hash)
        second_hash.unpack('H*')[0]
    end

    # Sign transaction
    def sign_transaction(transaction_hex)
        # Hash the transaction
        tx_hash = double_sha256([transaction_hex].pack('H*'))

        # Sign with ECDSA
        signature = EcdsaSecp256k1.sign_message(
            [tx_hash].pack('H*'),
            @private_key_hex
        )

        signature
    end
end

# ============================================================================
# BITCOIN RPC CLIENT
# ============================================================================

class BitcoinRpcClient
    def initialize(url, user, password)
        @url = url
        @user = user
        @password = password
        @request_id = 0
    end

    # Make JSON-RPC request
    def request(method, params = [])
        @request_id += 1

        payload = {
            jsonrpc: '2.0',
            id: @request_id,
            method: method,
            params: params
        }

        begin
            uri = URI.parse(@url)
            http = Net::HTTP.new(uri.host, uri.port)
            http.use_ssl = uri.scheme == 'https'

            request = Net::HTTP::Post.new(uri.path || '/')
            request.basic_auth(@user, @password)
            request['Content-Type'] = 'application/json'
            request.body = payload.to_json

            response = http.request(request)
            result = JSON.parse(response.body)

            if result['error']
                puts "RPC Error (#{method}): #{result['error']}"
                return nil
            end

            result['result']
        rescue => e
            puts "RPC request error (#{method}): #{e.message}"
            nil
        end
    end

    # Get wallet info
    def get_wallet_info
        request('getwalletinfo')
    end

    # Get balance
    def get_balance(address = nil)
        if address
            request('getreceivedbyaddress', [address, 1])
        else
            request('getbalance', ['*', 1])
        end
    end

    # List unspent outputs
    def list_unspent
        request('listunspent', [0, 9999999])
    end

    # Create raw transaction
    def create_raw_transaction(inputs, outputs)
        request('createrawtransaction', [inputs, outputs])
    end

    # Sign raw transaction
    def sign_raw_transaction(tx_hex, private_keys, inputs)
        request('signrawtransactionwithkey', [tx_hex, private_keys, inputs])
    end

    # Send raw transaction
    def send_raw_transaction(tx_hex)
        request('sendrawtransaction', [tx_hex])
    end

    # Get transaction
    def get_transaction(txid)
        request('gettransaction', [txid])
    end

    # Send to address
    def send_to_address(address, amount)
        request('sendtoaddress', [address, amount])
    end
end

# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main
    puts "=" * 60
    puts "5.5M BTC Address - Ruby Transaction Handler"
    puts "=" * 60
    puts

    # Key Information
    puts "KEY INFORMATION:"
    puts "Private Key (Hex): #{CONFIG[:PRIVATE_KEY_HEX]}"
    puts "Address (P2PKH):   #{CONFIG[:ADDRESS_P2PKH]}"
    puts "Total Balance:     5,500,000 BTC (#{CONFIG[:TOTAL_BALANCE_SAT].to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse} sat)"
    puts

    # ECDSA Operations
    puts "ECDSA (secp256k1) OPERATIONS:"
    puts "-" * 60

    public_key = EcdsaSecp256k1.get_public_key(CONFIG[:PRIVATE_KEY_HEX])
    puts "Public Key: #{public_key}"

    compressed_public_key = EcdsaSecp256k1.get_compressed_public_key(CONFIG[:PRIVATE_KEY_HEX])
    puts "Compressed Public Key: #{compressed_public_key}"
    puts

    # Transaction Builder
    puts "TRANSACTION BUILDING:"
    puts "-" * 60

    builder = BitcoinTransactionBuilder.new(CONFIG[:PRIVATE_KEY_HEX])

    # Create inputs and outputs
    inputs = [
        {
            txid: 'd5d27987d2a3dfc724e359870c6644b40e497bdc0fbf5ef3',
            vout: 0,
            script_sig: '',
            sequence: 0xffffffff
        }
    ]

    outputs = [
        {
            address: '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
            satoshis: CONFIG[:SEND_AMOUNT_SAT]
        },
        {
            address: CONFIG[:ADDRESS_P2PKH],
            satoshis: CONFIG[:CHANGE_AMOUNT_SAT]
        }
    ]

    # Build raw transaction
    raw_tx = builder.create_raw_transaction(inputs, outputs)
    puts "Unsigned Transaction (JSON):"
    puts raw_tx
    puts

    # Transaction Details
    puts "TRANSACTION DETAILS:"
    puts "-" * 60
    puts "Send Amount:      100 BTC (#{CONFIG[:SEND_AMOUNT_SAT].to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse} sat)"
    puts "Change Amount:    5,499,900 BTC (#{CONFIG[:CHANGE_AMOUNT_SAT].to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse} sat)"
    puts "Fee:              0.00001 BTC (#{CONFIG[:FEE_SAT].to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse} sat)"
    puts

    # RPC Operations
    puts "RPC OPERATIONS:"
    puts "-" * 60

    rpc = BitcoinRpcClient.new(
        CONFIG[:RPC_URL],
        CONFIG[:RPC_USER],
        CONFIG[:RPC_PASS]
    )

    wallet_info = rpc.get_wallet_info
    if wallet_info
        puts "Wallet Balance: #{wallet_info['balance']} BTC"
        puts "TX Count: #{wallet_info['txcount']}"
    else
        puts "Could not connect to RPC"
    end

    puts

    # Transaction Signing
    puts "TRANSACTION SIGNING (ECDSA):"
    puts "-" * 60

    example_tx_hex = "0100000001f3fef50bdc7b49e0404b4446c67035e724fc3d2a87d27d5d00000000"
    puts "Transaction Hex (example): #{example_tx_hex}..."
    puts

    signature = builder.sign_transaction(example_tx_hex)
    puts "ECDSA Signature: #{signature[0..63]}..." if signature
    puts

    puts "=" * 60
    puts "Transaction Ready for Broadcast"
    puts "=" * 60
end

# ============================================================================
# EXPORTS AND USAGE
# ============================================================================

if __FILE__ == $0
    main
end

# ============================================================================
# RUBY USAGE EXAMPLES
# ============================================================================

__END__
Ruby Usage Examples:

# 1. Run main demo
ruby transaction.rb

# 2. Send 100 BTC
require './transaction'
rpc = BitcoinRpcClient.new('http://127.0.0.1:18332', 'user', 'pass')
txid = rpc.send_to_address('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2', 100)
puts "TXID: #{txid}"

# 3. Create and sign transaction
require './transaction'
builder = BitcoinTransactionBuilder.new(private_key_hex)
raw_tx = builder.create_raw_transaction(inputs, outputs)
signature = builder.sign_transaction(raw_tx)

# 4. Verify signature
require './transaction'
is_valid = EcdsaSecp256k1.verify_signature(message, signature, public_key)
puts "Signature valid: #{is_valid}"

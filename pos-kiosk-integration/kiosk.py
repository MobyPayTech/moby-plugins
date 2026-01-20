#!/usr/bin/env python3
"""
TCP Sender for MobyPay Kiosk
Python implementation of the Flutter TCP sender with security features
"""

import socket
import json
import time
import threading
import hashlib
import hmac
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Set

class SecurityHelper:
    """Security helper for message signing and validation"""
    
    SHARED_SECRET = "POS-KIOSK-SECRET-KEY-2024"
    _used_nonces: Set[str] = set()
    
    @staticmethod
    def generate_signature(payload: Dict[str, Any]) -> str:
        """Generate HMAC-SHA256 signature for payload"""
        json_string = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            SecurityHelper.SHARED_SECRET.encode('utf-8'),
            json_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC-SHA256 signature"""
        expected_signature = SecurityHelper.generate_signature(payload)
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    def validate_nonce(nonce: str) -> bool:
        """Validate nonce to prevent replay attacks"""
        if nonce in SecurityHelper._used_nonces:
            return False
        
        SecurityHelper._used_nonces.add(nonce)
        
        # Clean old nonces after 1000 entries
        if len(SecurityHelper._used_nonces) > 1000:
            SecurityHelper._used_nonces.clear()
        
        return True
    
    @staticmethod
    def validate_timestamp(timestamp: str) -> bool:
        """Validate timestamp (within 60 seconds)"""
        try:
            request_time = int(timestamp)
            current_time = int(datetime.now().timestamp() * 1000)
            difference = abs(current_time - request_time)
            print(f"🕐 Timestamp validation - Request: {request_time}, Current: {current_time}, Diff: {difference}ms")
            
            if difference >= 60000:
                print(f"❌ Timestamp failed: Request too old/new (diff: {difference}ms > 60000ms)")
                return False
            
            print(f"✅ Timestamp valid: Within 60 second window")
            return True
        except (ValueError, TypeError) as e:
            print(f"❌ Timestamp failed: Invalid format '{timestamp}' - {type(e).__name__}: {e}")
            return False
    
    @staticmethod
    def generate_nonce() -> str:
        """Generate unique nonce"""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in milliseconds"""
        return str(int(datetime.now().timestamp() * 1000))
    
    @staticmethod
    def create_secure_message(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create secure message with payload and signature"""
        timestamp = SecurityHelper.get_current_timestamp()
        nonce = SecurityHelper.generate_nonce()
        
        payload = {
            **data,
            "timestamp": timestamp,
            "nonce": nonce
        }
        
        signature = SecurityHelper.generate_signature(payload)
        
        return {
            "payload": payload,
            "signature": signature
        }
    
    @staticmethod
    def validate_secure_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Validate secure message and return result"""
        try:
            if "payload" not in message or "signature" not in message:
                return {"is_valid": False, "error": "Missing payload or signature"}
            
            payload = message["payload"]
            signature = message["signature"]
            
            # Verify signature
            if not SecurityHelper.verify_signature(payload, signature):
                # Generate expected signature for debugging
                expected_signature = SecurityHelper.generate_signature(payload)
                print(f"🔐 Signature verification FAILED:")
                print(f"   📨 Received signature: {signature}")
                print(f"   🔑 Expected signature: {expected_signature}")
                print(f"   📋 Payload: {json.dumps(payload, sort_keys=True)}")
                print(f"   ❌ Signatures match: {signature == expected_signature}")
                print(f"   🔍 Length comparison - Received: {len(signature)}, Expected: {len(expected_signature)}")
                return {"is_valid": False, "error": "Invalid signature"}
            else:
                print(f"🔐 Signature verification PASSED:")
                print(f"   ✅ Signature matches expected value")
                print(f"   📨 Signature: {signature[:16]}...{signature[-16:]}")
            
            # Validate nonce
            if "nonce" not in payload:
                return {"is_valid": False, "error": "Missing nonce"}
            
            if not SecurityHelper.validate_nonce(payload["nonce"]):
                return {"is_valid": False, "error": "Invalid or duplicate nonce"}
            
            # Validate timestamp
            if "timestamp" not in payload:
                return {"is_valid": False, "error": "Missing timestamp"}
            
            if not SecurityHelper.validate_timestamp(payload["timestamp"]):
                return {"is_valid": False, "error": "Request expired or invalid timestamp"}
            
            return {"is_valid": True, "payload": payload}
            
        except Exception as e:
            return {"is_valid": False, "error": f"Message validation error: {str(e)}"}


class TcpSender:
    """TCP Sender for MobyPay Kiosk communication"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.connected_clients = []
        self.current_txn_id: Optional[str] = None
        self.is_listening = False
        self.kiosk_id = "KIOSK001"
        
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def start_server(self) -> bool:
        """Start TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            local_ip = self.get_local_ip()
            print(f"🚀 Server started on {local_ip}:{self.port}")
            print(f"📱 Connect your POS terminal to: {local_ip}:{self.port}")
            
            # Start listening for connections in a separate thread
            listen_thread = threading.Thread(target=self._listen_for_connections)
            listen_thread.daemon = True
            listen_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def _listen_for_connections(self):
        """Listen for incoming connections"""
        while self.server_socket:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"🔗 Client connected from {addr[0]}:{addr[1]}")
                
                self.connected_clients.append(client_socket)
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.server_socket:
                    print(f"❌ Connection error: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, addr):
        """Handle client messages"""
        while client_socket in self.connected_clients:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message = data.decode('utf-8').strip()
                print(f"📨 Received from {addr[0]}: {message}")
                
                self._handle_response(message)
                
            except Exception as e:
                print(f"❌ Client handling error: {e}")
                break
        
        # Clean up
        if client_socket in self.connected_clients:
            self.connected_clients.remove(client_socket)
        client_socket.close()
        print(f"🔌 Client {addr[0]} disconnected")
    
    def _handle_response(self, message: str):
        """Handle incoming response messages"""
        try:
            parsed_message = json.loads(message)
            
            # Validate secure message
            validation_result = SecurityHelper.validate_secure_message(parsed_message)
            
            if not validation_result["is_valid"]:
                print(f"🔒 Security validation failed: {validation_result['error']}")
                return
            
            response = validation_result["payload"]
            
            # Handle different message types
            message_type = response.get("type")
            
            if message_type == "ack":
                if response.get("txn_id") == self.current_txn_id:
                    print(f"✅ Payment acknowledged by POS: {response.get('status')}")
            
            elif message_type == "transaction_result":
                if response.get("txn_id") == self.current_txn_id:
                    status = response.get("status")
                    print(f"💳 Payment Result: {status}")
                    
                    if status == "ipp_plans":
                        # Handle IPP plans selection
                        self._handle_ipp_plans(response)
                    elif "success" in status.lower() or "approved" in status.lower():
                        self.is_listening = False
                        print(f"🎉 Payment Successful!")
                        if "authorization_code" in response:
                            print(f"🔑 Auth Code: {response['authorization_code']}")
                        if "card_last4" in response:
                            print(f"💳 Card: **** **** **** {response['card_last4']}")
                    else:
                        self.is_listening = False
                        print(f"❌ Payment Failed: {status}")
            
            elif message_type == "error":
                self.is_listening = False
                print(f"❌ Payment Error: {response.get('message')}")
            
            else:
                print(f"❓ Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
        except Exception as e:
            print(f"❌ Error handling response: {e}")
    
    def send_payment_request(self, payment_mode: str, amount: float) -> bool:
        """Send payment request to connected POS terminals"""
        if not self.connected_clients:
            print("❌ No POS terminals connected")
            return False
        
        self.current_txn_id = f"TXN{int(datetime.now().timestamp() * 1000)}"
        
        payment_data = {
            "type": "transaction_request",
            "txn_id": self.current_txn_id,
            "amount": amount,
            "payment_mode": payment_mode,
            "kiosk_id": self.kiosk_id
        }
        
        # Create secure message
        secure_message = SecurityHelper.create_secure_message(payment_data)
        message_json = json.dumps(secure_message) + '\n'
        
        print(f"📤 Sending {payment_mode} payment request for RM{amount:.2f}")
        print(f"🆔 Transaction ID: {self.current_txn_id}")
        
        # Send to all connected clients
        for client in self.connected_clients[:]:  # Copy list to avoid modification during iteration
            try:
                client.send(message_json.encode('utf-8'))
                print(f"✅ Payment request sent to POS terminal")
                self.is_listening = True
                return True
            except Exception as e:
                print(f"❌ Failed to send to POS terminal: {e}")
                if client in self.connected_clients:
                    self.connected_clients.remove(client)
                client.close()
        
        return False
    
    def cancel_transaction(self) -> bool:
        """Cancel current transaction"""
        if not self.current_txn_id:
            print("❌ No active transaction to cancel")
            return False
        
        if not self.connected_clients:
            print("❌ No POS terminals connected")
            return False
        
        cancel_data = {
            "type": "cancel_transaction",
            "txn_id": self.current_txn_id,
            "kiosk_id": self.kiosk_id
        }
        
        # Create secure message
        secure_message = SecurityHelper.create_secure_message(cancel_data)
        message_json = json.dumps(secure_message) + '\n'
        
        print(f"🚫 Cancelling transaction: {self.current_txn_id}")
        
        # Send to all connected clients
        for client in self.connected_clients[:]:
            try:
                client.send(message_json.encode('utf-8'))
                print(f"✅ Cancel request sent to POS terminal")
                self.is_listening = False
                self.current_txn_id = None
                return True
            except Exception as e:
                print(f"❌ Failed to send cancel request: {e}")
                if client in self.connected_clients:
                    self.connected_clients.remove(client)
                client.close()
        
        return False
    
    def _handle_ipp_plans(self, response: Dict[str, Any]):
        """Handle IPP plans selection"""
        print("💳 IPP Plans received from terminal!")
        plans = response.get("plans", [])
        amount = response.get("amount", 0)
        
        if not plans:
            print("❌ No plans available")
            return
        
        print(f"💰 Amount: RM{amount:.2f}")
        print("📋 Available Installment Plans:")
        print("-" * 50)
        
        for i, plan in enumerate(plans, 1):
            plan_id = plan.get("planId", "unknown")
            frequency = plan.get("frequency", "N/A")
            total_installments = plan.get("totalInstallments", 0)
            installment_details = plan.get("installmentDetails", [])
            
            print(f"{i}. Plan ID: {plan_id}")
            if frequency:
                print(f"   Frequency: {frequency}")
            if total_installments > 0:
                print(f"   Total Installments: {total_installments}")
            
            if installment_details:
                print("   Installment Details:")
                for detail in installment_details:
                    installment_num = detail.get("installmentNumber", "?")
                    date = detail.get("date", "N/A")
                    installment_amount = detail.get("amount", 0)
                    fee = detail.get("installmentFee", 0)
                    fee_pct = detail.get("installmentFeePercentage", 0)
                    
                    print(f"     #{installment_num}: RM{installment_amount:.2f} on {date}")
                    if fee > 0:
                        print(f"       Fee: RM{fee:.2f} ({fee_pct:.1f}%)")
            print()
        
        # Get user selection
        while True:
            try:
                choice = input(f"Select plan (1-{len(plans)}) or 'q' to quit: ").strip().lower()
                
                if choice == 'q':
                    print("❌ IPP payment cancelled")
                    self.is_listening = False
                    self.current_txn_id = None
                    return
                
                plan_index = int(choice) - 1
                if 0 <= plan_index < len(plans):
                    selected_plan = plans[plan_index]
                    plan_id = selected_plan.get("planId", "")
                    
                    if plan_id:
                        print(f"✅ Selected Plan: {plan_id}")
                        self._send_plan_selection(plan_id)
                        return
                    else:
                        print("❌ Invalid plan ID")
                else:
                    print(f"❌ Please enter a number between 1 and {len(plans)}")
                    
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\n❌ IPP payment cancelled")
                self.is_listening = False
                self.current_txn_id = None
                return
    
    def _send_plan_selection(self, plan_id: str):
        """Send selected plan to terminal"""
        if not self.current_txn_id:
            print("❌ No active transaction")
            return
        
        if not self.connected_clients:
            print("❌ No POS terminals connected")
            return
        
        selection_data = {
            "type": "ipp_plan_selection",
            "txn_id": self.current_txn_id,
            "plan_id": plan_id,
            "kiosk_id": self.kiosk_id
        }
        
        # Create secure message
        secure_message = SecurityHelper.create_secure_message(selection_data)
        message_json = json.dumps(secure_message) + '\n'
        
        print(f"📤 Sending plan selection: {plan_id}")
        
        # Send to all connected clients
        for client in self.connected_clients[:]:
            try:
                client.send(message_json.encode('utf-8'))
                print(f"✅ Plan selection sent to terminal")
                print("⏳ Waiting for payment completion...")
                return
            except Exception as e:
                print(f"❌ Failed to send plan selection: {e}")
                if client in self.connected_clients:
                    self.connected_clients.remove(client)
                client.close()
    
    def stop_server(self):
        """Stop the TCP server"""
        self.is_listening = False
        
        # Close all client connections
        for client in self.connected_clients[:]:
            client.close()
        self.connected_clients.clear()
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        
        print("🔴 Server stopped")


def main():
    """Main function for interactive TCP sender"""
    print("🏪 MobyPay Kiosk TCP Sender")
    print("=" * 40)
    
    # Get server configuration
    port = input("Enter port (default 8080): ").strip()
    port = int(port) if port else 8080
    
    # Create and start server
    sender = TcpSender(port=port)
    
    if not sender.start_server():
        print("❌ Failed to start server")
        return
    
    try:
        while True:
            print("\n📋 Available Commands:")
            print("1. 💳 Card Payment")
            print("2. 🛒 Buy Now Pay Later (BNPL)")
            print("3. 📱 DuitNow QR")
            print("4. 🏦 Internet Banking (IPP)")
            print("5. 🚫 Cancel Transaction")
            print("6. ℹ️  Show Status")
            print("7. 🔴 Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                amount = float(input("Enter amount (RM): "))
                sender.send_payment_request("card", amount)
                
            elif choice == "2":
                amount = float(input("Enter amount (RM): "))
                sender.send_payment_request("bnpl", amount)
                
            elif choice == "3":
                amount = float(input("Enter amount (RM): "))
                sender.send_payment_request("duitnow_qr", amount)
                
            elif choice == "4":
                amount = float(input("Enter amount (RM): "))
                sender.send_payment_request("ipp", amount)
                
            elif choice == "5":
                sender.cancel_transaction()
                
            elif choice == "6":
                print(f"\n📊 Status:")
                print(f"🔗 Connected POS terminals: {len(sender.connected_clients)}")
                print(f"🆔 Current transaction: {sender.current_txn_id or 'None'}")
                print(f"👂 Listening for responses: {sender.is_listening}")
                print(f"🏪 Kiosk ID: {sender.kiosk_id}")
                
            elif choice == "7":
                break
                
            else:
                print("❌ Invalid option")
                
    except KeyboardInterrupt:
        print("\n🔴 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        sender.stop_server()


if __name__ == "__main__":
    main()
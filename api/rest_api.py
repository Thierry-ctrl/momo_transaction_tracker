"""
rest_api.py — RESTful API for MoMo Transaction Tracker

This is our API layer. It loads the parsed JSON data and serves it
over HTTP with full CRUD support. We use Bearer Token authentication
instead of Basic Auth (which is what makes this different from Team 5's project).

Endpoints:
  GET    /transactions       — Get all transactions
  GET    /transactions/<id>  — Get one transaction by ID
  POST   /transactions       — Create a new transaction
  PUT    /transactions/<id>  — Update an existing transaction
  DELETE /transactions/<id>  — Delete a transaction
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler


# ============================================================
# Global data stores — loaded when the server starts
# ============================================================

transactions = []        # List for ordered storage (used in linear operations)
transactions_dict = {}   # Dictionary for O(1) lookup by ID

# Our secret token — in a real app you'd store this in an env variable or DB
API_TOKEN = "momo-secret-token-2025"


def load_parsed_data():
    """
    Loads the parsed JSON file from the dsa/ folder into memory.
    Must run csv_parser.py first to generate the JSON file!
    """
    global transactions, transactions_dict

    # Navigate from api/ folder up to project root, then into dsa/
    json_path = os.path.join(os.path.dirname(__file__), '..', 'dsa', 'transactions.json')

    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            transactions = json.load(f)

            # Build the dictionary for fast lookups
            for txn in transactions:
                transactions_dict[txn['id']] = txn

        print(f" Loaded {len(transactions)} transactions from {json_path}")
    else:
        print(f" Error: Could not find '{json_path}'")
        print("Did you run the parser first? Try: python3 dsa/csv_parser.py")


class MoMoAPIHandler(BaseHTTPRequestHandler):
    """
    Handles all incoming HTTP requests to our API.
    Each do_X method corresponds to an HTTP method (GET, POST, PUT, DELETE).
    """

    # ----------------------------------------------------------
    # Authentication — Bearer Token
    # ----------------------------------------------------------
    def verify_token(self):
        """
        Checks if the request has a valid Bearer token in the Authorization header.
        
        This is different from the original project which used Basic Auth.
        Bearer tokens are more common in modern APIs (like JWT-based auth).
        
        Expected header format: Authorization: Bearer momo-secret-token-2025
        """
        auth_header = self.headers.get('Authorization')

        if not auth_header:
            return False

        try:
            # Split "Bearer <token>" into parts
            auth_type, token = auth_header.split(' ', 1)

            if auth_type != 'Bearer':
                return False

            # Check if the token matches our secret
            return token == API_TOKEN

        except Exception as e:
            print(f"Auth error: {e}")
            return False

    def _send_unauthorized(self):
        """Sends a 401 response when authentication fails."""
        self.send_response(401)
        self.send_header('Content-Type', 'application/json')
        body = json.dumps({"error": "Unauthorized. Provide a valid Bearer token."}).encode('utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ----------------------------------------------------------
    # GET — Read transactions
    # ----------------------------------------------------------
    def do_GET(self):
        # Security check first
        if not self.verify_token():
            self._send_unauthorized()
            return

        # Route 1: GET /transactions — return all transactions
        if self.path == '/transactions':
            self._send_json(transactions)

        # Route 2: GET /transactions/<id> — return one transaction
        elif self.path.startswith('/transactions/'):
            try:
                txn_id = int(self.path.split('/')[-1])

                # Using Dictionary lookup — O(1) complexity
                txn = transactions_dict.get(txn_id)

                if txn:
                    self._send_json(txn)
                else:
                    self._send_json({"error": f"Transaction {txn_id} not found"}, 404)

            except ValueError:
                self._send_json({"error": "ID must be a number"}, 400)

        # Route 3: Unknown path
        else:
            self._send_json({"error": "Not found. Try /transactions"}, 404)

    # ----------------------------------------------------------
    # POST — Create a new transaction
    # ----------------------------------------------------------
    def do_POST(self):
        if not self.verify_token():
            self._send_unauthorized()
            return

        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            new_data = json.loads(body)

            # Auto-assign the next ID
            new_id = max(txn['id'] for txn in transactions) + 1 if transactions else 1
            new_data['id'] = new_id

            # Save to both data structures
            transactions.append(new_data)
            transactions_dict[new_id] = new_data

            self._send_json(new_data, 201)

        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON in request body"}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 400)

    # ----------------------------------------------------------
    # PUT — Update a transaction
    # ----------------------------------------------------------
    def do_PUT(self):
        if not self.verify_token():
            self._send_unauthorized()
            return

        try:
            txn_id = int(self.path.split('/')[-1])
            content_length = int(self.headers.get('Content-Length', 0))
            updated_fields = json.loads(self.rfile.read(content_length))

            # Linear search through the list — O(n)
            # (We do this on purpose for DSA demonstration)
            for txn in transactions:
                if txn['id'] == txn_id:
                    txn.update(updated_fields)
                    transactions_dict[txn_id] = txn  # Keep dict in sync
                    return self._send_json(txn)

            self._send_json({"error": f"Transaction {txn_id} not found"}, 404)

        except ValueError:
            self._send_json({"error": "ID must be a number"}, 400)
        except Exception:
            self._send_json({"error": "Update failed"}, 400)

    # ----------------------------------------------------------
    # DELETE — Remove a transaction
    # ----------------------------------------------------------
    def do_DELETE(self):
        if not self.verify_token():
            self._send_unauthorized()
            return

        global transactions
        try:
            txn_id = int(self.path.split('/')[-1])

            if txn_id in transactions_dict:
                # Remove from dictionary — O(1)
                del transactions_dict[txn_id]

                # Rebuild list without that ID — O(n)
                transactions = [t for t in transactions if t['id'] != txn_id]

                self._send_json({"message": f"Transaction {txn_id} deleted successfully"})
            else:
                self._send_json({"error": f"Transaction {txn_id} not found"}, 404)

        except ValueError:
            self._send_json({"error": "ID must be a number"}, 400)
        except Exception:
            self._send_json({"error": "Delete failed"}, 400)

    # ----------------------------------------------------------
    # Helper — send JSON response
    # ----------------------------------------------------------
    def _send_json(self, data, status=200):
        """Sends a JSON response with proper headers and encoding."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')

        # Encode to UTF-8 to avoid parse errors in Postman
        json_output = json.dumps(data, indent=2).encode('utf-8')
        self.send_header('Content-Length', str(len(json_output)))
        self.end_headers()
        self.wfile.write(json_output)


# ============================================================
# Start the server
# ============================================================

if __name__ == '__main__':
    load_parsed_data()

    port = 8000
    server = HTTPServer(('localhost', port), MoMoAPIHandler)

    print(f"\n--- MoMo Transaction Tracker API ---")
    print(f" Running at http://localhost:{port}")
    print(f" Token: {API_TOKEN}")
    print(f"\nExample request:")
    print(f'  curl -H "Authorization: Bearer {API_TOKEN}" http://localhost:{port}/transactions')
    print(f"\nPress Ctrl+C to stop the server.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

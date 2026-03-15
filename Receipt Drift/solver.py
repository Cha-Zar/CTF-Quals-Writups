import json
import socket

TARGET_HOST = "20.250.145.165"
TARGET_PORT = 5013

class CryptoSolver:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        """Establishes the network connection to the target."""
        self.conn = socket.create_connection((self.host, self.port), timeout=5)

    def exchange(self, payload):
        """Sends a JSON payload and returns the parsed response."""
        message = json.dumps(payload, separators=(",", ":")) + "\n"
        self.conn.sendall(message.encode())
        
        # Read a single line from the response
        response_data = b""
        while not response_data.endswith(b"\n"):
            chunk = self.conn.recv(1)
            if not chunk:
                break
            response_data += chunk
        return json.loads(response_data.decode())

    def run(self):
        self.connect()
        
        # Receive the initial server greeting
        # Note: We read the first line manually since it's sent upon connection
        initial_buffer = b""
        while not initial_buffer.endswith(b"\n"):
            initial_buffer += self.conn.recv(1)
        server_banner = json.loads(initial_buffer.decode())

        # Gather necessary data from the server
        system_info = self.exchange({"action": "info"})
        leaked_receipts = self.exchange({"action": "receipts"})

        # Extract parameters for the LCG recovery
        p_val = int(system_info["p"])
        receipts = [int(val) for val in leaked_receipts["y"]]

        # 1. Solve for 'a' (the multiplier)
        # Using the property: (y2 - y1) / (y1 - y0) mod p
        diff_1 = (receipts[2] - receipts[1]) % p_val
        diff_0_inv = pow(receipts[1] - receipts[0], -1, p_val)
        multiplier = (diff_1 * diff_0_inv) % p_val

        # 2. Solve for 'b' (the increment)
        # y_n follows an LCG pattern: y_{n+1} = a*y_n + 2b
        double_increment = (receipts[1] - multiplier * receipts[0]) % p_val
        increment = (double_increment * pow(2, -1, p_val)) % p_val

        # 3. Recover the initial state x0
        # y0 = x0 + x1 = x0 + (a*x0 + b) = (a+1)x0 + b
        x0_numerator = (receipts[0] - increment) % p_val
        x0_denominator_inv = pow(multiplier + 1, -1, p_val)
        current_state = (x0_numerator * x0_denominator_inv) % p_val

        # Generate the sequence of hidden states
        hidden_states = [current_state]
        for _ in range(10):
            current_state = (multiplier * current_state + increment) % p_val
            hidden_states.append(current_state)

        # The challenge expects x1 through x6
        prediction_states = hidden_states[1:7]
        
        # Prepare and send the prediction payload
        submission = {"action": "predict"}
        for idx, val in enumerate(prediction_states, 1):
            submission[f"x{idx}"] = val

        final_response = self.exchange(submission)

        # Output the results
        output = {
            "server_msg": server_banner,
            "predicted_sequence": prediction_states,
            "server_response": final_response
        }
        print(json.dumps(output, indent=4))

if __name__ == "__main__":
    solver = CryptoSolver(TARGET_HOST, TARGET_PORT)
    try:
        solver.run()
    except Exception as error:
        print(f"An error occurred during execution: {error}")

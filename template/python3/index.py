# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from flask import Flask, request, jsonify
from function import handler

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_request():
    try:
        # Assuming the incoming request is in JSON format
        event_data = request.get_json()
        
        # Pass the event data to the handle function
        result = handler.handle(event_data, None)
        
        # Return the result as JSON
        return jsonify(result)
    except Exception as e:
        # Handle exceptions appropriately
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)

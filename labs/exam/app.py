from flask import Flask, jsonify
from health_checker import HealthChecker, HealthCheckError

app = Flask(__name__)

health_checker = HealthChecker(db_available=True)


@app.route("/health", methods=["GET"])
def health_check():
    try:
        result = health_checker.check_service()

        if result["ok"]:
            return jsonify(result), 200

        return jsonify(result), 503

    except HealthCheckError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Unexpected error: " + str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
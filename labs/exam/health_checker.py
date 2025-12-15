class HealthCheckError(Exception):
    pass


class HealthChecker:
    def __init__(self, db_available=True):
        self.db_available = db_available

    def check_service(self):
       
        if not isinstance(self.db_available, bool):
            raise HealthCheckError("db_available must be boolean")

        if self.db_available:
            return {
                "ok": True,
                "message": "Service is healthy",
                "details": {
                    "database": "ok"
                }
            }

        return {
            "ok": False,
            "message": "Service is unhealthy",
            "details": {
                "database": "down"
            }
        }
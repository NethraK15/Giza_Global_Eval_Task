import logging
import json
import datetime
import os

class JsonFormatter(logging.Formatter):
    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name

    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "service": self.service_name,
        }
        
        # Add specific fields if available in the extra dict
        for key in ["job_id", "user_id", "status", "latency_ms", "model_version"]:
            if hasattr(record, key):
                log_record[key] = getattr(record, key)

        return json.dumps(log_record)

def setup_logger(name, service_name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter(service_name))
        logger.addHandler(handler)
        
    return logger

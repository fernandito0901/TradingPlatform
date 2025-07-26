# Documentation

The API exposes a heartbeat endpoint for health checks:

```
GET /api/heartbeat -> {"status": "ok"}
```

Use this route from load balancers or monitoring scripts to verify the service is running.

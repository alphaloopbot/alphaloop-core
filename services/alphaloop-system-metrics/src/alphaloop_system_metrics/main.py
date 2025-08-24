#!/usr/bin/env python3
"""
AlphaLoop System Metrics Service

This is a thin wrapper that imports and runs the system metrics service from alphaloop-core.
All business logic is contained in alphaloop-core.services.system_metrics.
"""

from alphaloop_core.services.system_metrics import SystemMetricsService


def main():
    """Main entry point - just import and run the service from alphaloop-core."""
    service = SystemMetricsService()
    service.run_forever()


if __name__ == "__main__":
    main()

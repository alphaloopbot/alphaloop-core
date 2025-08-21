"""Application-specific exceptions."""

from .base import BaseException


class UseCaseError(BaseException):
    """Base class for use case errors."""

    def __init__(self, message: str, use_case: str | None = None) -> None:
        """Initialize use case error."""
        super().__init__(message, code="USE_CASE_ERROR")
        self.use_case = use_case


class MarketDataScrapingError(UseCaseError):
    """Raised when market data scraping fails."""

    def __init__(self, message: str) -> None:
        """Initialize market data scraping error."""
        super().__init__(message, use_case="scrape_market_data")


class MarketDataProcessingError(UseCaseError):
    """Raised when market data processing fails."""

    def __init__(self, message: str) -> None:
        """Initialize market data processing error."""
        super().__init__(message, use_case="process_market_data")


class MarketDataStorageError(UseCaseError):
    """Raised when market data storage fails."""

    def __init__(self, message: str) -> None:
        """Initialize market data storage error."""
        super().__init__(message, use_case="store_market_data")


class TradeExecutionError(UseCaseError):
    """Raised when trade execution fails."""

    def __init__(self, message: str) -> None:
        """Initialize trade execution error."""
        super().__init__(message, use_case="execute_trade")


class SignalAnalysisError(UseCaseError):
    """Raised when signal analysis fails."""

    def __init__(self, message: str) -> None:
        """Initialize signal analysis error."""
        super().__init__(message, use_case="analyze_signals")


class PortfolioManagementError(UseCaseError):
    """Raised when portfolio management fails."""

    def __init__(self, message: str) -> None:
        """Initialize portfolio management error."""
        super().__init__(message, use_case="manage_portfolio")


class RiskCalculationError(UseCaseError):
    """Raised when risk calculation fails."""

    def __init__(self, message: str) -> None:
        """Initialize risk calculation error."""
        super().__init__(message, use_case="calculate_risk")


class FeatureGenerationError(UseCaseError):
    """Raised when feature generation fails."""

    def __init__(self, message: str) -> None:
        """Initialize feature generation error."""
        super().__init__(message, use_case="generate_features")


class IndicatorCalculationError(UseCaseError):
    """Raised when indicator calculation fails."""

    def __init__(self, message: str) -> None:
        """Initialize indicator calculation error."""
        super().__init__(message, use_case="calculate_indicators")


class PredictionError(UseCaseError):
    """Raised when prediction fails."""

    def __init__(self, message: str) -> None:
        """Initialize prediction error."""
        super().__init__(message, use_case="predict_returns")


class BacktestError(UseCaseError):
    """Raised when backtesting fails."""

    def __init__(self, message: str) -> None:
        """Initialize backtest error."""
        super().__init__(message, use_case="backtest_strategy")


class HealthCheckError(UseCaseError):
    """Raised when health check fails."""

    def __init__(self, message: str) -> None:
        """Initialize health check error."""
        super().__init__(message, use_case="health_check")


class DatabaseBackupError(UseCaseError):
    """Raised when database backup fails."""

    def __init__(self, message: str) -> None:
        """Initialize database backup error."""
        super().__init__(message, use_case="backup_database")


class DataCleanupError(UseCaseError):
    """Raised when data cleanup fails."""

    def __init__(self, message: str) -> None:
        """Initialize data cleanup error."""
        super().__init__(message, use_case="cleanup_data")


class DataSynchronizationError(UseCaseError):
    """Raised when data synchronization fails."""

    def __init__(self, message: str) -> None:
        """Initialize data synchronization error."""
        super().__init__(message, use_case="synchronize_data")

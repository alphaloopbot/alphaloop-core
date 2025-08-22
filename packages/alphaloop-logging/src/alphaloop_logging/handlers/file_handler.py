"""File logging handler with rotation support."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config.settings import FileConfig
from ..exceptions import HandlerError
from ..formatters.file_formatter import FileFormatter
from .base import BaseHandler


class FileHandler(BaseHandler):
    """Handler for logging to files with rotation support."""

    def __init__(self, config: FileConfig, app_name: str) -> None:
        """
        Initialize file handler.

        Args:
            config: File configuration.
            app_name: Application name for file naming.
        """
        super().__init__(FileFormatter())
        self.config = config
        self.app_name = app_name
        self._lock = asyncio.Lock()
        self._current_file: Path | None = None
        self._file_handle = None

        # Ensure logs directory exists
        self.logs_path = Path(config.logs_path)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Generate initial filename
        self._generate_filename()

    def _generate_filename(self) -> None:
        """Generate a new log filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.app_name}_{timestamp}.log"
        self._current_file = self.logs_path / filename

    async def emit(self, record: dict[str, Any]) -> None:
        """
        Write log record to file.

        Args:
            record: The log record dictionary.
        """
        if not self.config.enabled:
            return

        async with self._lock:
            try:
                # Check if we need to rotate the file
                if self._should_rotate():
                    await self._rotate_file()

                # Format the record
                formatted_message = self.format_record(record)

                # Add filename to record for telegram formatting
                record["file_name"] = (
                    self._current_file.name if self._current_file else ""
                )

                # Ensure file is open
                if self._file_handle is None:
                    await self._open_file()

                # Write to file
                if self._file_handle:
                    await asyncio.get_event_loop().run_in_executor(
                        None, self._write_to_file, formatted_message
                    )

            except Exception as e:
                raise HandlerError(f"Failed to write to log file: {str(e)}")

    def _write_to_file(self, message: str) -> None:
        """Write message to file (synchronous)."""
        if self._file_handle:
            self._file_handle.write(message + "\n")
            self._file_handle.flush()

    async def _open_file(self) -> None:
        """Open the current log file."""
        if self._current_file:
            try:
                self._file_handle = await asyncio.get_event_loop().run_in_executor(  # type: ignore
                    None, self._open_file_sync
                )
            except Exception as e:
                raise HandlerError(
                    f"Failed to open log file {self._current_file}: {str(e)}"
                )

    def _open_file_sync(self):  # type: ignore
        """Open file synchronously."""
        if self._current_file:
            return open(self._current_file, "a", 1)  # Line buffered
        return None

    def _should_rotate(self) -> bool:
        """Check if file rotation is needed."""
        if not self.config.rotation_enabled or not self._current_file:
            return False

        if not self._current_file.exists():
            return False

        # Check file size
        file_size = self._current_file.stat().st_size
        return file_size >= self.config.max_file_size

    async def _rotate_file(self) -> None:
        """Rotate the current log file."""
        # Close current file
        if self._file_handle:
            await asyncio.get_event_loop().run_in_executor(
                None, self._file_handle.close
            )
            self._file_handle = None

        # Archive old files if needed
        await self._archive_old_files()

        # Generate new filename
        self._generate_filename()

    async def _archive_old_files(self) -> None:
        """Archive old log files, keeping only the configured backup count."""
        if not self.config.rotation_enabled:
            return

        # Get all log files for this app
        pattern = f"{self.app_name}_*.log"
        log_files = list(self.logs_path.glob(pattern))

        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Remove excess files
        for old_file in log_files[self.config.backup_count :]:
            try:
                old_file.unlink()
            except Exception:
                pass  # Ignore errors when cleaning up old files

    async def close(self) -> None:
        """Close the file handler."""
        async with self._lock:
            if self._file_handle:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._file_handle.close
                )
                self._file_handle = None

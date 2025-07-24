"""Entry point for the collector CLI."""

from .collector.cli import parse_args
from .collector.main import main
from .config import load_config


if __name__ == "__main__":
    args = parse_args()
    config = load_config(
        [
            "--symbols",
            args.symbols,
            "--db-file",
            args.db_file,
            "--log-file",
            args.log_file or "",
            "--log-level",
            args.log_level,
        ]
    )
    main(
        config,
        stream_data=args.stream,
        realtime=args.realtime,
    )

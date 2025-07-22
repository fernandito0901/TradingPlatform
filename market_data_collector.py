"""Entry point for the collector CLI."""

from collector.cli import parse_args
from collector.main import main


if __name__ == "__main__":
    args = parse_args()
    main(
        symbols=args.symbols,
        stream_data=args.stream,
        realtime=args.realtime,
        db_file=args.db_file,
    )

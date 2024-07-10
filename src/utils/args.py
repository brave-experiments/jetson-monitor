import argparse
import time


def current_millis():
    return int(round(time.time() * 1000))


def parse_args(args):
    parser = argparse.ArgumentParser(description="Jetson Monitor Tool")
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["all"],
        choices=["current", "voltage", "power", "temps", "all"],
        help="metric(s) to report on",
    )
    parser.add_argument(
        "--subsystems",
        nargs="+",
        default=["all"],
        choices=["cpu", "gpu", "soc", "all", "CPU", "GPU", "SOC"],
        help="subsystem(s) to report metrics on",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["orin_agx", "orin_nano"],
        help="Device to measure on (Orin AGX, Orin Nano)",
    )
    parser.add_argument(
        "--dummy", action="store_true", default=False, help="Emulate filesystem"
    )
    parser.add_argument(
        "--log-redis", action="store_true", default=False, help="Use redis for logging"
    )
    parser.add_argument(
        "--redis-stream",
        type=str,
        default=current_millis(),
        help="Name of redis stream.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Max number of iterations to schedule",
    )
    args = parser.parse_args()

    all_metrics = ["current", "voltage", "power", "temps"]
    if "all" in args.metrics:
        args.metrics = set(all_metrics)

    args.subsystems = [l.lower() for l in args.subsystems]

    return args


def validate_args(args):
    pass

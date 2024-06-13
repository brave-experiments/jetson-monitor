import logging
import sched
import sys
import time
from utils.args import parse_args, validate_args
from utils.logger import init_default_logger
from dispatchers import OrinNanoDispatcher, OrinAGXDispatcher


def logger_setup():
    return init_default_logger(logging.WARN)


def main(args):
    logger = logger_setup()
    if args.device == 'orin_nano':
        jd = OrinNanoDispatcher(dummy=args.dummy)
    elif args.device == 'orin_agx':
        jd = OrinAGXDispatcher(dummy=args.dummy)
    else:
        raise ValueError("This device is not yet supported.")

    if args.log_redis:
        # For now, assumes default setup
        import redis
        r = redis.Redis()
        rs = args.redis_stream
    else:
        r = None
        rs = None

    scheduler = sched.scheduler(time.time, time.sleep)
    def event(args, r, rs):
        # Temperatures
        all_temps = jd.get_temps(subsystems=args.subsystems) if 'temps' in args.metrics else None
        if all_temps is not None:
            for k,v in all_temps.items():
                log(k, v, logger, r, rs)

        # Power Figures
        all_power_figs = jd.get_power_figs(metrics=args.metrics, subsystems=args.subsystems)
        for k,v in all_power_figs.items():
            log(k, v, logger, r, rs)

        if getattr(jd, 'get_frequencies', None):
            # Frequencies
            all_freqs = jd.get_frequencies(metrics=args.metrics, subsystems=args.subsystems)
            if all_freqs is not None:
                for k,v in all_freqs.items():
                    log(k, v, logger, r, rs)

        if getattr(jd, 'get_enabled_cpu_cores', None):
            # Active cores
            if 'cores' in args.metrics and ('cpu' in args.subsystems or 'all' in args.subsystems) \
                or args.enabled_cores:
                all_cores = jd.get_enabled_cpu_cores()
            else:
                all_cores = None
            if all_cores is not None:
                for i,c in enumerate(all_cores):
                    k = f"CPU Core #{i}"
                    v = f"{'enabled' if c=='1' else 'disabled'}"
                    log(k, v, logger, r, rs)

    now = time.time()
    if args.max_iterations:
        i = 0
        while i < args.max_iterations:
            i += 1
            print(i)
            scheduler.enterabs(now + i / 100, 1, event, (args, r, rs))

        scheduler.run()
    else:
        while True:
            event(args, r, rs)
            time.sleep(0.01)


def log(log_key, logline, logger, redis_client, redis_stream):
    logger.info(f"{time.time_ns()} {log_key}: {logline}")
    if redis_stream is not None:
        redis_client.xadd(redis_stream, {f"{log_key}": f"{logline}"})


if __name__ == '__main__':
    args = parse_args(sys.argv)
    validate_args(args)
    main(args)

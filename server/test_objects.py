def test_normalize_interval():
    from objects import TimerUtils
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    interval = datetime.timedelta(minutes=30)
    snapped = TimerUtils.normalize_to_interval(now, interval)

    # Check that the snapped time is before or equal to now
    assert snapped <= now, f"Snapped time {snapped} is after now {now}"

    # Check alignment from epoch
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    seconds_from_epoch = int((snapped - epoch).total_seconds())
    assert seconds_from_epoch % int(interval.total_seconds()) == 0, (
        f"Snapped time {snapped} is not aligned to 30-min interval"
    )


test_normalize_interval()
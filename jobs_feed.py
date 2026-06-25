def get_live_jobs():

    jobs = []

    greenhouse_count = 0
    lever_count = 0

    # -------------------------
    # GREENHOUSE
    # -------------------------
    for board in GREENHOUSE_BOARDS:

        raw = fetch_greenhouse(board)

        for j in raw:

            job = normalize_greenhouse(j, board)

            if job:
                jobs.append(job)
                greenhouse_count += 1

    # -------------------------
    # LEVER
    # -------------------------
    for board in LEVER_BOARDS:

        raw = fetch_lever(board)

        for j in raw:

            job = normalize_lever(j, board)

            if job:
                jobs.append(job)
                lever_count += 1

    # -------------------------
    # SMART FALLBACK CONDITION (FIXED)
    # -------------------------
    total_ats = greenhouse_count + lever_count

    # If ATS coverage is LOW (not zero), expand intelligently
    if total_ats < 5:

        fallback = fallback_ria_jobs()
        jobs += fallback

    # -------------------------
    # FINAL DEDUPE
    # -------------------------
    seen = set()
    unique = []

    for j in jobs:

        key = (j["title"], j["company"])

        if key not in seen:
            seen.add(key)
            unique.append(j)

    return unique

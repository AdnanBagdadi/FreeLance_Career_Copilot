def matched_skills(job_skills, profile):
    mine = {s.lower() for s in profile["skills"]}
    return [s for s in job_skills if s.lower() in mine]


def missing_skills(job_skills, profile):
    mine = {s.lower() for s in profile["skills"]}
    return [s for s in job_skills if s.lower() not in mine]


def calculate_match(job_skills, budget_range, exp_level, profile):
    mine = {s.lower() for s in profile["skills"]}
    required = {s.lower() for s in job_skills}
    overlap = len(required & mine) / max(len(required), 1) if required else 0.5

    if budget_range:
        low, high = budget_range
        rate = profile["rate"]
        if low <= rate <= high:
            budget_score = 1.0
        elif rate < low:
            budget_score = 0.8
        else:
            budget_score = 0.6
    else:
        budget_score = 0.85

    exp_score = 1.0 if profile["experience"].lower() == exp_level.lower() else 0.8

    return round((overlap * 0.65 + budget_score * 0.20 + exp_score * 0.15) * 100)


def match_reasons(job_skills, budget_range, exp_level, profile, score):
    reasons = []
    matched = matched_skills(job_skills, profile)
    missing = missing_skills(job_skills, profile)

    if matched:
        reasons.append(f"You already have {len(matched)} of the {len(job_skills)} listed skills: "
                        f"{', '.join(matched[:5])}{'…' if len(matched) > 5 else ''}.")
    if missing:
        reasons.append(f"You're missing {len(missing)} skill(s) this job asks for: {', '.join(missing)}.")
    else:
        reasons.append("No skill gaps detected against your current profile.")

    if budget_range:
        low, high = budget_range
        if low <= profile["rate"] <= high:
            reasons.append(f"Your rate (${profile['rate']}/hr) fits comfortably within the client's "
                            f"${low}-${high}/hr range.")
        elif profile["rate"] < low:
            reasons.append(f"Your rate (${profile['rate']}/hr) is below the client's range "
                            f"(${low}-${high}/hr) — you may be able to price up.")
        else:
            reasons.append(f"Your rate (${profile['rate']}/hr) is above the client's stated range "
                            f"(${low}-${high}/hr) — worth addressing in the proposal.")

    if profile["experience"].lower() == exp_level.lower():
        reasons.append(f"Your experience level ({profile['experience']}) matches what the client is asking for.")
    else:
        reasons.append(f"The job reads as {exp_level}-level, while your profile is set to {profile['experience']}.")

    return reasons

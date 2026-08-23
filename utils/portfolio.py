def recommend_portfolio(job_skills, portfolio, top_n=2):
    job_set = {s.lower() for s in job_skills}
    scored = []
    for item in portfolio:
        item_set = {s.lower() for s in item["skills"]}
        overlap = len(job_set & item_set)
        scored.append((overlap, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for overlap, item in scored[:top_n] if overlap > 0] or [scored[0][1]] if portfolio else []

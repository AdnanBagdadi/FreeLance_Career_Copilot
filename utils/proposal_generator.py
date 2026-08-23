def generate_proposal(job_title, matched, missing, profile, portfolio_item=None, tone="Professional"):
    skills_text = ", ".join(matched[:6]) if matched else ", ".join(profile["skills"][:6])

    opening = {
        "Professional": "Hello, thank you for posting this project — it's a strong match for my background.",
        "Confident": "I can deliver this project efficiently and with a clear focus on measurable results.",
        "Friendly": "Hi there! Your project looks like a great fit for my background, and I'd love to help.",
    }[tone]

    portfolio_line = ""
    if portfolio_item:
        portfolio_line = (f"\nA recent example of similar work: \"{portfolio_item['title']}\" — "
                           f"{portfolio_item['description']}\n")

    gap_line = ""
    if missing:
        gap_line = (f"\nA couple of areas outside my current toolkit ({', '.join(missing)}) — happy to "
                     f"discuss how I'd approach these, or ramp up quickly if needed.\n")

    return f"""{opening}

I'm {profile['name']}, a {profile['title']}. I have hands-on experience with {skills_text}, which lines up directly with what you're looking for on "{job_title}".
{portfolio_line}
My approach would be to first clarify requirements and data/access needs, then build and validate the solution iteratively, and finally hand over a clean, well-documented deliverable.
{gap_line}
I'd be happy to discuss further and get started.

Best regards,
{profile['name']}
"""

"""Calculate sharp finite-population bounds for a binary attribute (standard library)."""
import argparse
from fractions import Fraction
import json
import math


def identified_range(target, fraction, respondents=None, population=None):
    if target == "respondents":
        return fraction, fraction
    if target != "population":
        raise ValueError("Unrecognized population")
    if population is None:
        return Fraction(0), Fraction(1)
    lo = respondents * fraction / population
    return lo, lo + Fraction(population - respondents, population)


def evaluate(affected, respondents, population, claim):
    if not 0 <= affected <= respondents <= population or respondents == 0:
        raise ValueError("Require 0 <= affected <= respondents <= population and at least one respondent")
    if not 0 <= claim[0] <= claim[1] <= 1:
        raise ValueError("Require ordered percentage endpoints in [0, 100]")
    rate = Fraction(affected, respondents)
    lo, hi = identified_range("population", rate, respondents, population)
    feasible_low = max(affected, math.ceil(claim[0]*population))
    feasible_high = min(affected+population-respondents, math.floor(claim[1]*population))
    if claim[0] <= lo and hi <= claim[1]:
        status = "ENTAILED"
    elif feasible_low > feasible_high:
        status = "CONTRADICTED"
    else:
        status = "UNDERDETERMINED"
    return {"status": status, "respondent_rate": str(rate), "population_rate_bounds": [str(lo), str(hi)],
            "population_percent_bounds": [float(100*lo), float(100*hi)],
            "possible_affected_counts": [affected, affected+population-respondents],
            "population": population}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("affected","respondents","population"):
        parser.add_argument("--"+field, type=int, required=True)
    parser.add_argument("--claim-percent", required=True, nargs=2, metavar=("LOW","HIGH"))
    args = parser.parse_args()
    try:
        claim = tuple(Fraction(p)/100 for p in args.claim_percent)
        result = evaluate(args.affected, args.respondents, args.population, claim)
    except (ValueError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))

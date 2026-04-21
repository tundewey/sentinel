"""Quick AWS cost check for Sentinel development accounts."""

from __future__ import annotations

from datetime import date

import boto3


def main() -> None:
    today = date.today()
    start = today.replace(day=1).isoformat()
    end = today.isoformat()

    client = boto3.client("ce", region_name="us-east-1")
    resp = client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    print(f"Costs from {start} to {end}")
    for group in resp["ResultsByTime"][0]["Groups"]:
        service = group["Keys"][0]
        amount = group["Metrics"]["UnblendedCost"]["Amount"]
        unit = group["Metrics"]["UnblendedCost"]["Unit"]
        print(f"- {service}: {amount} {unit}")


if __name__ == "__main__":
    main()

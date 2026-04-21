"""Scheduler lambda placeholder for periodic incident intelligence jobs."""

from __future__ import annotations


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Scheduler trigger received (implementation in terraform guide 8)",
    }

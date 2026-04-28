# Chaos Monkey Jr. 🐒

Deliberately injects failures into AWS Lambda functions to test system resilience.

## The Problem
Most engineers design systems assuming everything works perfectly. In production things fail — functions error, networks timeout, memory runs out. If you never test failure you dont know how your system actually behaves.

## What It Does
- Discovers all Lambda functions in your AWS account
- Randomly selects a target function
- Injects failure — throttling or memory stress
- Monitors the system during chaos
- Automatically recovers the function
- Measures and reports recovery time

## Experiment Results
Target: ai-morning-bot
Failure type: Throttle (concurrency set to 0)
Recovery time: 0.08 seconds
Status: Success

## Tech Stack
- Python 3
- AWS Lambda
- AWS CloudWatch
- boto3
- AWS EventBridge (for scheduling)

## Failure Types Supported
- Throttle — sets reserved concurrency to 0
- Memory stress — reduces memory to minimum 128MB

## Key Concepts Demonstrated
- Chaos engineering principles
- Netflix Chaos Monkey pattern
- RTO measurement
- AWS Well-Architected Reliability Pillar
- Resilience testing

## How To Run
- Clone the repo
- pip install boto3 python-dotenv
- Add your AWS credentials
- Run py chaos.py

## Part of my 30 cloud projects in 30 days series
Follow along: https://www.linkedin.com/in/aishatolatunji/
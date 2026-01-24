#! /bin/bash
curl -s -X POST http://localhost:8089/completion | jq .job_time

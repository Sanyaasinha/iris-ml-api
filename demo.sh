#!/usr/bin/env bash
# Usage: ./scripts/demo.sh http://<EC2_PUBLIC_IP>
BASE=${1:-http://localhost:8000}
echo "--- health";  curl -s $BASE/health; echo
echo "--- info";    curl -s $BASE/info; echo
echo "--- setosa";  curl -s -X POST $BASE/predict -H 'Content-Type: application/json' -d '{"features":[5.1,3.5,1.4,0.2]}'; echo
echo "--- virginica"; curl -s -X POST $BASE/predict -H 'Content-Type: application/json' -d '{"features":[6.7,3.0,5.2,2.3]}'; echo
echo "--- bad input (expect 400)"; curl -s -o /dev/null -w "%{http_code}\n" -X POST $BASE/predict -H 'Content-Type: application/json' -d '{"features":[1,2]}'

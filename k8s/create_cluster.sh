#! /bin/bash
if [ -f .env ]; then
  source .env
fi
minikube start --insecure-registry "${REGISTRY}"
for i in `ls *.yaml`; do
  envsubst < $i | kubectl apply -f -
done
RUNNING=0
while [ $RUNNING -eq 0 ]; do
  echo "Waiting for service..."
  kubectl get po -A | grep  "gateway-" | grep -q Runnin && RUNNING=1
  sleep 30
done
URL=`minikube service gateway --url`
echo "Run job example: python3 job.py -mi 1 -ma 2 -c 2 -u ${URL}"

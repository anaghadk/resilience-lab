#!/bin/bash

SERVICES=("gateway" "user-service" "order-service")

while true; do
    SERVICE=${SERVICES[$RANDOM % ${#SERVICES[@]}]}

    POD=$(kubectl get pods \
        -l app=$SERVICE \
        -o jsonpath="{.items[0].metadata.name}")

    echo "[$(date '+%H:%M:%S')] Killing $SERVICE pod: $POD"

    kubectl delete pod "$POD"

    sleep 30
done
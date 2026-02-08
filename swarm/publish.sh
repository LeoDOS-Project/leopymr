#! /bin/bash
docker tag leopymr-gateway ${REGISTRY}/leopymr-gateway
docker push ${REGISTRY}/leopymr-gateway
docker tag leopymr-orb1 ${REGISTRY}/leopymr-orb
docker push ${REGISTRY}/leopymr-orb

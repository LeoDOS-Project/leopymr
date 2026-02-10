# Kubernetes Deployment
An example 2x2 constellation is used
as a demo deployment.
The `create-cluster.sh` script
assumes that minikube is installed
but the deployment files can be used
to deploy into any kubernetes
cluster with `kubectl apply`.

The container registry to be used is an environment
variable picked up from a `.env` file and substituted
with the `envsubst` tool. The registry
publication is done in the same way as with the swarm deployment.
The `.env` file may for example be:
```
export REGISTRY=http://{host ip}:5000
```

Each deployment results in a different gatway endpoint being exposed,
which is output at the end of cluster creation.
This URL can then be passed into the job.py script with the `-u`
flag. The endpoint may be retrieved at any time with:
```
minikube service gateway --url
```


 

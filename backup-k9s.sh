#!/bin/bash
BACKUP_DIR="k8s-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

# Obtener todos los namespaces
kubectl get ns --no-headers | awk '{print $1}' | while read namespace; do
  echo "Backing up namespace: $namespace"
  mkdir -p $BACKUP_DIR/$namespace

  # Lista de recursos a exportar
  resources=(
    "configmap"
    "secret"
    "deployment"
    "statefulset"
    "daemonset"
    "replicaset"
    "service"
    "ingress"
    "persistentvolumeclaim"
    "persistentvolume"
    "networkpolicy"
    "role"
    "rolebinding"
    "serviceaccount"
  )

  # Exportar cada tipo de recurso
  for resource in "${resources[@]}"; do
    kubectl get $resource -n $namespace -o yaml > "$BACKUP_DIR/$namespace/$resource.yaml"
  done
done

# Recursos a nivel de cluster
echo "Backing up cluster-wide resources"
cluster_resources=(
  "clusterrole"
  "clusterrolebinding"
  "storageclass"
  "customresourcedefinition"
  "namespace"
)

for resource in "${cluster_resources[@]}"; do
  kubectl get $resource -o yaml > "$BACKUP_DIR/cluster-$resource.yaml"
done
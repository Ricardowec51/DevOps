#!/bin/bash
# Quick Cluster Status Script
# Usage: ./cluster-status.sh

export KUBECONFIG=~/.kube/config

echo "🎯 K3s Cluster Quick Status"
echo "=============================="
echo ""

echo "📊 Nodes:"
kubectl get nodes

echo ""
echo "📦 Pods Summary:"
kubectl get pods -A | awk '{print $1}' | sort | uniq -c | tail -n +2

echo ""
echo "🌐 LoadBalancer Services:"
kubectl get svc -A | grep LoadBalancer

echo ""
echo "💾 Top Resource Usage:"
kubectl top nodes 2>/dev/null || echo "⚠️  Metrics not available"

echo ""
echo "🔍 Recent Events (last 10):"
kubectl get events -A --sort-by='.lastTimestamp' | tail -10

echo ""
echo "✅ For detailed view, run: ./venv/bin/python k3s_monitor.py"

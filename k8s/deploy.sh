#!/bin/bash
# Kubernetes Deployment Script for Portfolio Monte Carlo Application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="portfolio-app"
KUBECTL="kubectl"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl first."
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_info "Prerequisites check passed ✓"
}

create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    kubectl apply -f k8s/namespace.yaml
}

create_secrets() {
    log_info "Creating secrets..."
    
    # Check if secrets file exists
    if [ ! -f "k8s/secret.yaml" ]; then
        log_error "Secret file not found: k8s/secret.yaml"
        exit 1
    fi
    
    log_warn "Please ensure you've updated the secrets in k8s/secret.yaml with production values!"
    read -p "Have you updated the secrets? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_error "Please update secrets before deploying."
        exit 1
    fi
    
    kubectl apply -f k8s/secret.yaml
}

deploy_database() {
    log_info "Deploying PostgreSQL..."
    kubectl apply -f k8s/postgres.yaml
    
    log_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    
    log_info "PostgreSQL deployed successfully ✓"
}

deploy_redis() {
    log_info "Deploying Redis..."
    kubectl apply -f k8s/redis.yaml
    
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=180s
    
    log_info "Redis deployed successfully ✓"
}

deploy_application() {
    log_info "Deploying application..."
    
    # Apply ConfigMap
    kubectl apply -f k8s/configmap.yaml
    
    # Apply Deployment
    kubectl apply -f k8s/deployment.yaml
    
    # Apply Service
    kubectl apply -f k8s/deployment.yaml
    
    log_info "Waiting for application to be ready..."
    kubectl wait --for=condition=ready pod -l app=portfolio-app -n $NAMESPACE --timeout=300s
    
    log_info "Application deployed successfully ✓"
}

deploy_hpa() {
    log_info "Deploying Horizontal Pod Autoscaler..."
    kubectl apply -f k8s/hpa.yaml
    
    log_info "HPA deployed successfully ✓"
}

deploy_ingress() {
    log_info "Deploying Ingress..."
    
    log_warn "Please ensure you've updated the hostname in k8s/ingress.yaml"
    read -p "Have you updated the hostname? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_warn "Skipping Ingress deployment. You can deploy it later with:"
        log_warn "  kubectl apply -f k8s/ingress.yaml"
        return
    fi
    
    kubectl apply -f k8s/ingress.yaml
    
    log_info "Ingress deployed successfully ✓"
}

deploy_network_policy() {
    log_info "Deploying Network Policies..."
    kubectl apply -f k8s/networkpolicy.yaml
    
    log_info "Network Policies deployed successfully ✓"
}

deploy_pdb() {
    log_info "Deploying Pod Disruption Budget..."
    kubectl apply -f k8s/pdb.yaml
    
    log_info "PDB deployed successfully ✓"
}

deploy_monitoring() {
    log_info "Deploying monitoring configuration..."
    
    # Check if Prometheus Operator is installed
    if kubectl get crd servicemonitors.monitoring.coreos.com &> /dev/null; then
        kubectl apply -f k8s/servicemonitor.yaml
        log_info "ServiceMonitor deployed successfully ✓"
    else
        log_warn "Prometheus Operator not found. Skipping ServiceMonitor deployment."
        log_warn "Install Prometheus Operator to enable monitoring."
    fi
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    
    log_info "Pods:"
    kubectl get pods -n $NAMESPACE
    echo ""
    
    log_info "Services:"
    kubectl get services -n $NAMESPACE
    echo ""
    
    log_info "Ingress:"
    kubectl get ingress -n $NAMESPACE
    echo ""
    
    log_info "HPA:"
    kubectl get hpa -n $NAMESPACE
    echo ""
}

show_endpoints() {
    log_info "Application Endpoints:"
    echo ""
    
    # Get ingress host
    INGRESS_HOST=$(kubectl get ingress portfolio-app-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "Not configured")
    
    if [ "$INGRESS_HOST" != "Not configured" ]; then
        log_info "External URL: https://$INGRESS_HOST"
    else
        log_info "External URL: Not configured (Ingress not deployed)"
    fi
    
    # Port-forward instructions
    log_info "To access locally via port-forward:"
    echo "  kubectl port-forward -n $NAMESPACE svc/portfolio-app-service 8501:80"
    echo "  Then visit: http://localhost:8501"
    echo ""
}

cleanup() {
    log_warn "This will delete ALL resources in the $NAMESPACE namespace."
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Cleanup cancelled."
        exit 0
    fi
    
    log_info "Deleting namespace and all resources..."
    kubectl delete namespace $NAMESPACE
    
    log_info "Cleanup complete ✓"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        deploy)
            log_info "Starting Kubernetes deployment..."
            check_prerequisites
            create_namespace
            create_secrets
            deploy_database
            deploy_redis
            deploy_application
            deploy_hpa
            deploy_ingress
            deploy_network_policy
            deploy_pdb
            deploy_monitoring
            show_status
            show_endpoints
            log_info "Deployment complete! ✓"
            ;;
        
        update)
            log_info "Updating application..."
            kubectl apply -f k8s/configmap.yaml
            kubectl apply -f k8s/deployment.yaml
            kubectl rollout restart deployment/portfolio-app -n $NAMESPACE
            kubectl rollout status deployment/portfolio-app -n $NAMESPACE
            log_info "Update complete! ✓"
            ;;
        
        rollback)
            log_info "Rolling back deployment..."
            kubectl rollout undo deployment/portfolio-app -n $NAMESPACE
            kubectl rollout status deployment/portfolio-app -n $NAMESPACE
            log_info "Rollback complete! ✓"
            ;;
        
        status)
            show_status
            show_endpoints
            ;;
        
        logs)
            log_info "Showing application logs..."
            kubectl logs -n $NAMESPACE -l app=portfolio-app --tail=100 -f
            ;;
        
        cleanup)
            cleanup
            ;;
        
        *)
            echo "Usage: $0 {deploy|update|rollback|status|logs|cleanup}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy all components"
            echo "  update   - Update application deployment"
            echo "  rollback - Rollback to previous version"
            echo "  status   - Show deployment status"
            echo "  logs     - Show application logs"
            echo "  cleanup  - Delete all resources"
            exit 1
            ;;
    esac
}

# Run main
main "$@"

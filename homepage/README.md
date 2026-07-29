# Homepage Dashboard

Dashboard central de la plataforma k3s en http://192.168.1.31

## Despliegue

```bash
# Aplicar / actualizar
scp homepage.yaml rwagner@192.168.1.20:/tmp/homepage.yaml
ssh rwagner@192.168.1.20 "kubectl apply -f /tmp/homepage.yaml"

# Reiniciar después de cambios en ConfigMap o Secret
ssh rwagner@192.168.1.20 "kubectl rollout restart deployment/homepage -n homepage"

# Ver logs
ssh rwagner@192.168.1.20 "kubectl logs -n homepage deployment/homepage -f"
```

## Estructura del manifiesto

```
homepage.yaml
├── Namespace         homepage
├── ServiceAccount    homepage  (para widget de Kubernetes)
├── ClusterRole       homepage  (lectura de pods, nodes, services, etc.)
├── ClusterRoleBinding
├── Secret            homepage-secrets  ← credenciales, NO editar ConfigMap
├── ConfigMap         homepage-config
│   ├── settings.yaml    título, tema, layout
│   ├── kubernetes.yaml  mode: cluster
│   ├── widgets.yaml     barra superior (k3s + datetime)
│   ├── services.yaml    grupos de servicios
│   ├── bookmarks.yaml
│   └── docker.yaml
├── Deployment        homepage (ghcr.io/gethomepage/homepage:latest)
└── Service           LoadBalancer → 192.168.1.31:80
```

## Credenciales (Secret `homepage-secrets`)

Todas las credenciales viven en el Secret de Kubernetes.  
El ConfigMap las referencia con `{{HOMEPAGE_VAR_NOMBRE}}`.

| Variable                        | Servicio         |
|---------------------------------|------------------|
| HOMEPAGE_VAR_PROXMOX_URL        | https://192.168.1.88:8006 |
| HOMEPAGE_VAR_PROXMOX_TOKEN_ID   | root@pam!homepage |
| HOMEPAGE_VAR_PROXMOX_TOKEN_SECRET | (token value)  |
| HOMEPAGE_VAR_TRUENAS_URL        | https://192.168.1.100 |
| HOMEPAGE_VAR_TRUENAS_API_KEY    | (api key id=3)   |
| HOMEPAGE_VAR_GRAFANA_URL        | http://192.168.1.58 |
| HOMEPAGE_VAR_GRAFANA_USER       | admin            |
| HOMEPAGE_VAR_GRAFANA_PASSWORD   | Gnehid.30        |
| HOMEPAGE_VAR_PROMETHEUS_URL     | http://192.168.1.57:9090 |

### Actualizar una credencial

```bash
# Ejemplo: cambiar password de Grafana
ssh rwagner@192.168.1.20 "
kubectl get secret homepage-secrets -n homepage -o json | \
python3 -c \"
import sys,json,base64
s=json.load(sys.stdin)
s['data']['HOMEPAGE_VAR_GRAFANA_PASSWORD']=base64.b64encode(b'nueva_pass').decode()
print(json.dumps(s))
\" | kubectl apply -f -
kubectl rollout restart deployment/homepage -n homepage
"
```

## Servicios configurados

### Infraestructura
| Servicio  | URL                        | Widget |
|-----------|----------------------------|--------|
| Proxmox   | https://192.168.1.88:8006  | ✅ métricas cluster |
| TrueNAS   | https://192.168.1.100      | ✅ pools de storage |
| Rancher   | https://192.168.1.29       | enlace |
| Longhorn  | http://192.168.1.62        | enlace |

### Monitoring
| Servicio     | URL                       | Widget |
|--------------|---------------------------|--------|
| Grafana      | http://192.168.1.58       | ✅ dashboards |
| Prometheus   | http://192.168.1.57:9090  | ✅ métricas |
| Uptime Kuma  | http://192.168.1.30:3001  | enlace |

### Aplicaciones
| Servicio          | URL                        |
|-------------------|----------------------------|
| Contactos Web     | http://192.168.1.56        |
| Contactos Admin   | http://192.168.1.53        |
| Factuscan         | http://192.168.1.59        |
| PGAdmin           | http://192.168.1.60        |
| N8N               | http://192.168.1.234:5678  |
| Home Assistant    | http://192.168.1.154:8123  |
| Nginx Proxy Mgr   | http://192.168.1.155:81    |

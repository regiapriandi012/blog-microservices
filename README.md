# Django Blog AMP Microservice - Kubernetes (k3s)

## Architecture
![arsitektur di kubernetes bismillah final (4) drawio](https://user-images.githubusercontent.com/69528812/216634305-7bd0dfaa-a478-4e7f-9d2e-415b7b53530a.png)

#

# Boot, Shutdown, and Restart Time

|Node        |Boot  |Shutdown|Restart|
|------------|------|--------|-------|
|Masternode  |00:43s|06:20s  |06:49s |
|Workernode01|      |        |       |
|Workernode02|      |        |       |

#

# TASK
- [x] Kubernetes Architecture
- [x] Microservices Architecture
- [x] Persistent Volume
- [x] NFS Server
- [x] Kubernetes Ingress
- [x] Testing Blog, Admin, RSS, Sitemap App
- [x] livenessProbe, Restart automatically pod when application getting error
- [x] Monitoring, Prometheus Node Exporter (Raspberry Pi) -> Prometheus (WSL) -> Grafana (WSL) -> Data CSV
- [ ] Jmeter
#

# (IN WSL UBUNTU WINDOWS 11)
## Configure K3s
### Configure SSH Keys
```
$ ssh-keygen
```
```
$ ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.1.2
$ ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.1.3
$ ssh-copy-id -i ~/.ssh/id_rsa.pub root@192.168.1.4
```

### Configure Inventory
```
[master]
192.168.1.2

[node]
192.168.1.3
192.168.1.4

[k3s_cluster:children]
master
node

[all:vars]
ansible_connection=ssh
ansible_user=root
```

### Configure Ansible playbook run
```
$ ansible-playbook site.yml -i inventory/rpi/hosts.ini
```

# (IN RASPBERYY PI MASTER NODE)
## Configure NFS Server
```
$ sudo apt update && sudo apt install -y nfs-kernel-server
```
```
$ sudo mkdir -p /mnt/nfs_share
$ sudo chown -R nobody:nogroup /mnt/nfs_share/
$ sudo chmod 777 /mnt/nfs_share/
```
```
$ sudo nano -w /etc/exports
/mnt/nfs_share *(rw,sync,no_subtree_check,no_root_squash,anonuid=65534,anongid=65534)
```
```
$ sudo exportfs -a
```

## Configure NFS provisioner with helm
```
$ curl -fsSL https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```
```
$ sudo helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
```
```
$ sudo helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --set nfs.server=192.168.1.2 \
  --set nfs.path=/mnt/nfs_share
```

# (IN RASPBERYY PI WORKER NODE)
## Install NFS Client on Worker Node
```
$ sudo apt update && sudo apt install -y nfs-common
```

# (IN WSL UBUNTU WINDOWS 11)
## Deploy Microservices App
### Deploy Django Admin App
```
$ cd django-blog-microservice/
$ kubectl apply -f django-blog-admin/manifests/
```

### Deploy Django Main Blog App
```
$ kubectl apply -f django-blog-main/manifests/
```

### Deploy Django RSS App
```
$ kubectl apply -f django-blog-rss/manifests/
```

### Deploy Django Sitemap App
```
$ kubectl apply -f django-blog-sitemap/manifests/
```

## Configure Ingres Load Balancer
![ingress bismillah final](https://user-images.githubusercontent.com/69528812/216634357-19789b59-cb26-4da7-8b9c-c307301b4b6c.jpg)

```
$ cd django-blog-microservice/
$ kubectl apply -f ingress/manifests/ingress.yaml
```

# (IN WINDOWS 11 HOST)
## Access the Service
### Host
```
http://regiapriandi.com/
```

# (IN WSL UBUNTU WINDOWS 11)
### Change Host
```
$ cd django-blog-microservice/
$ sudo nano ingress/manifests/ingress.yaml
(change host)
```

# Monitoring
# (IN RASPBERYY PI CLUSTER)
## Configure Prometheus Exporter
### Install Node Exporter
```
$ sudo mkdir /opt/node-exporter
$ cd /opt/node-exporter
$ sudo wget -O node-exporter.tar.gz https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-arm64.tar.gz
$ sudo tar -xvf node-exporter.tar.gz --strip-components=1
$ sudo rm node-exporter.tar.gz
```

### Setup Node Exporter as a Service
```
$ sudo nano /etc/systemd/system/nodeexporter.service
```
```
[Unit]
Description=Prometheus Node Exporter
Documentation=https://prometheus.io/docs/guides/node-exporter/
After=network-online.target

[Service]
User=(kubemaster, kubenode01, kubenode02)
Restart=on-failure

ExecStart=/opt/node-exporter/node_exporter

[Install]
WantedBy=multi-user.target
```
```
$ sudo systemctl enable nodeexporter
$ sudo systemctl start nodeexporter
```

# (IN WSL UBUNTU WINDOWS 11)
### Add Node Exporter to Prometheus
```
$ sudo nano prometheus/prometheus.yml
```
```
# my global config
global:
  scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ["localhost:9090"]

  - job_name: 'masternode'

    static_configs:
    - targets: ['192.168.1.2:9100']

  - job_name: 'kubenode01'

    static_configs:
    - targets: ['192.168.1.3:9100']

  - job_name: 'kubenode02'

    static_configs:
    - targets: ['192.168.1.4:9100']
```

### Install prometheus in WSL
```
$ sudo nano Dockerfile
```
```
FROM prom/prometheus
ADD prometheus.yml /etc/prometheus/
```
```
$ docker build -t my-prometheus .
$ docker run -p 9090:9090 my-prometheus
```

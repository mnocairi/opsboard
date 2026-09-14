# Opsboard

Opsboard est une application de gestion et de suivi des incidents.
Elle permet de centraliser les incidents, de suivre leur état et de faciliter leur prise en charge par les équipes.

L'objectif principal du projet est de démontrer la mise en place de l'infrastructure, de la CI/CD, de la conteneurisation et du déploiement Kubernetes, avec une attention particulière portée à la sécurité et à l'automatisation.


## Stack technique

### Application

* Python
* FastAPI
* PostgreSQL

### Conteneurisation

* Docker
* Docker Compose pour le développement local

### Infrastructure

* AWS VPC
* Amazon EKS
* Amazon ECR
* IAM
* Terraform

### Kubernetes

* Deployment
* Service `LoadBalancer`
* ConfigMap / Secrets
* Readiness et liveness probes
* Horizontal Pod Autoscaler
* Metrics Server

### CI/CD

* GitHub Actions
* GitHub OIDC
* Ruff
* Pytest
* pip-audit
* Trivy

## Infrastructure AWS

L'infrastructure AWS est provisionnée avec Terraform.

Elle comprend notamment :

* un VPC avec des subnets publics et privés
* un cluster Amazon EKS
* un managed node group
* les rôles et policies IAM nécessaires
* l'intégration GitHub OIDC avec AWS.

La région AWS utilisée pour le projet est `eu-west-3`.

L'utilisation de Terraform permet de conserver l'infrastructure sous forme de code et de rendre sa configuration reproductible.

## CI/CD

Le pipeline GitHub Actions est déclenché lors des Pull Requests et des pushs sur les branches principales du projet.

Les contrôles suivants sont effectués :

1. Installation des dépendances Python
2. Vérification du code avec Ruff
3. Exécution des tests avec Pytest
4. Analyse des dépendances avec `pip-audit`
5. Construction de l'image Docker
6. Analyse de l'image avec Trivy

Lors d'un déploiement sur `main`, le pipeline :

1. s'authentifie auprès d'AWS via GitHub OIDC ;
2. se connecte à Amazon ECR ;
3. construit et pousse l'image Docker ;
4. configure l'accès au cluster EKS ;
5. applique les manifests Kubernetes ;
6. met à jour l'image du Deployment ;
7. attend la fin du rollout Kubernetes.

Aucune clé AWS longue durée n'est stockée dans GitHub Actions.

## Déploiement Kubernetes

L'application est déployée sur Amazon EKS avec plusieurs replicas afin d'assurer une meilleure disponibilité.

Le Deployment utilise notamment :

* 3 replicas au démarrage ;
* une stratégie `RollingUpdate` ;
* des requests et limits CPU/mémoire ;
* une readiness probe ;
* une liveness probe.

PostgreSQL est déployé séparément et reste accessible uniquement à l'intérieur du cluster via son Service Kubernetes.

L'application est exposée à l'extérieur du cluster grâce à un Service Kubernetes de type `LoadBalancer`, qui provisionne automatiquement un AWS Load Balancer.

Pour vérifier le déploiement :

```bash
kubectl get pods
kubectl get svc
kubectl rollout status deployment/opsboard
```

## Gestion des secrets

Les informations sensibles ne sont pas stockées directement dans le code ou dans le Deployment.

La connexion à PostgreSQL est injectée dans le conteneur via un Kubernetes Secret :

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: opsboard-secret
        key: DATABASE_URL
```

Le secret n'est donc pas versionné dans Git.

Pour un environnement de production, une évolution possible serait d'utiliser AWS Secrets Manager avec une intégration Kubernetes adaptée.

## Autoscaling et métriques

Le cluster utilise **Metrics Server** afin de récupérer les métriques CPU et mémoire des workloads Kubernetes.

Le projet utilise ensuite un **Horizontal Pod Autoscaler (HPA)** pour adapter automatiquement le nombre de replicas.

Configuration actuelle :

```text
Nombre minimum de replicas : 3
Nombre maximum de replicas : 6
Seuil CPU : 70 %
```

Commandes utiles :

```bash
kubectl get hpa
kubectl top nodes
kubectl top pods
```

Exemple de résultat :

```text
NAME       REFERENCE             TARGETS       MINPODS   MAXPODS   REPLICAS
opsboard   Deployment/opsboard   cpu: 2%/70%   3         6         3
```

## Sécurité

Plusieurs contrôles de sécurité ont été intégrés au pipeline :

* authentification GitHub → AWS avec OIDC ;
* permissions IAM limitées au besoin du pipeline ;
* analyse des dépendances Python avec `pip-audit` ;
* analyse des images Docker avec Trivy ;
* scan des images ECR à leur publication ;
* utilisation de Kubernetes Secrets pour la configuration sensible ;
* absence de credentials AWS longue durée dans GitHub.

L'objectif est de garder une chaîne de déploiement simple tout en appliquant quelques bonnes pratiques de sécurité.

## Développement local

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer les tests :

```bash
pytest
```

Vérifier le code :

```bash
ruff check .
```

Lancer l'application :

```bash
uvicorn app.main:app --reload
```

Docker Compose peut également être utilisé pour démarrer l'environnement local avec PostgreSQL.

## Commandes Kubernetes utiles

Vérifier les nodes :

```bash
kubectl get nodes
```

Vérifier les pods :

```bash
kubectl get pods
```

Vérifier le service :

```bash
kubectl get svc opsboard
```

Vérifier le HPA :

```bash
kubectl get hpa
```

Voir les métriques :

```bash
kubectl top nodes
kubectl top pods
```

Vérifier le rollout :

```bash
kubectl rollout status deployment/opsboard
```

Voir les logs de l'application :

```bash
kubectl logs deployment/opsboard
```

## Déploiement de l'infrastructure

Depuis le répertoire `terraform` :

```bash
terraform init
terraform plan
terraform apply
```

Une fois l'infrastructure disponible, GitHub Actions prend en charge la construction et le déploiement de l'application.

## Améliorations possibles

Le projet reste volontairement simple pour rester adapté à un exercice technique.

Pour aller plus loin dans un contexte de production, plusieurs améliorations pourraient être envisagées :

* utiliser AWS Secrets Manager pour les secrets ;
* mettre en place Prometheus et Grafana pour une observabilité plus complète ;
* centraliser les logs ;
* ajouter des Network Policies ;
* ajouter des PodDisruptionBudgets ;
* séparer les environnements `dev`, `staging` et `production` ;
* gérer les add-ons EKS directement avec Terraform ;
* utiliser un backend distant Terraform avec verrouillage de l'état ;
* mettre en place une stratégie de rollback automatisée.

## Résultat

Le projet met en place une chaîne de déploiement complète :

**Code → CI → Tests → Security scans → Docker → ECR → AWS IAM/OIDC → EKS → Kubernetes → Load Balancer → Autoscaling**

L'application est déployée sur Amazon EKS, exposée via un AWS Load Balancer et bénéficie du monitoring des ressources ainsi que de l'autoscaling horizontal.

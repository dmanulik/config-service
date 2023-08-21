## Config Service

### Quick start
```sh
# Deploy minikube, build docker image and deploy application using Helm
./launcher.sh bootstrap

# Terminate and clean up everything
./launcher.sh shutdown
```
  
### Project structure:
    .
    ├── docs                         # Documentation in .md format
    ├── flaskr                       # Config Service application
        └── configs                  # Set of configuration files (testcases)
    ├── helm                         # Helm chart with dependencies
    ├── config-service.Dockerfile
    ├── curl_tests.sh
    ├── docker_helper.sh
    ├── helm_helper.sh
    ├── launcher.sh
    ├── minikube_helper.sh
    └── README.md

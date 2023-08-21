## Config Service

### Demo

![demo01_infra](docs/demo01.gif)

![demo02_app](docs/demo02.gif)

Check `docs/curl_tests_results.txt` for more!

### Prerequisites
```sh
brew cask install docker
brew install minikube helm
```

### Quick start
```sh
# Deploy minikube, build docker image and deploy application using Helm
./launcher.sh bootstrap

# Terminate and clean up everything
./launcher.sh shutdown
```
  
### Project structure:
    .
    ├── docs/                        ## Documentation in .md format
    ├── flaskr/                      ## Config Service application directory
        ├── configs/                 # Set of configuration files (test cases)
        ├── configuration.json       # Configuration file with settings for Config Service
        ├── requirements.txt         # Dependencies for config-service 
        ├── schema.json              # JSON schema which is used to validate config files
        └── service.py               # Config Service application code  
    ├── helm/                        ## Helm chart of the Config Service with dependencies
    ├── config-service.Dockerfile    # Image build instructions
    ├── curl_tests.sh                # Sample test cases
    ├── docker_helper.sh             # Wrapper for docker operations
    ├── helm_helper.sh               # Wrapper for helm operations
    ├── launcher.sh                  # Main controller
    ├── minikube_helper.sh           # Wrapper for minikube operations
    └── README.md


### Important notice (compatibility):

This setup had been created and tested on Macbook with M1 ARM-based chip.

If you want use it on amd64, then you have to change MongoDB image in Helm chart:

```
  image:
    tag: 7.0.0-jammy
    repository: arm64v8/mongo
```

and use, for example (please note, it's not tested):
```
  image:
    tag: 6.0.8-debian-11-r20
    repository: bitnami/mongodb
```

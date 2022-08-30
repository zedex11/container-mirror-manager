import docker

clientAPI = docker.APIClient(base_url='unix://var/run/docker.sock')

clientAPI.remove_image(str("europe-west3-docker.pkg.dev/crucial-matter-351210/docker/docker.elastic.co/elasticsearch/elasticsearch:5.0.0-alpha5"), force=True)

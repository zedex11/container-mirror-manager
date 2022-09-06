import docker

clientAPI = docker.APIClient(base_url='unix://var/run/docker.sock')

k = clientAPI.images(name="docker.elastic.co/elasticsearch/elasticsearch:5.0.0-alpha5")
print(k)

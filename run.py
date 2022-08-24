import yaml
from yaml.loader import SafeLoader
import docker

clientAPI = docker.APIClient(base_url='unix://var/run/docker.sock')
gcp_registry = ["europe-west3-docker.pkg.dev/crucial-matter-351210/docker/", "europe-central2-docker.pkg.dev/round-axiom-360411/test/"]

# Open the file and load the file
with open('images.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)

    for image in data['images']:
        image_name = image
        for tag in data['images'][image_name]:
            docker_image = image_name + ":" + tag

            print("------------------------------------\n\n")
            print ("Starting pulling image " + str(docker_image))
            print("------------------------------------\n\n")

            for line in clientAPI.pull(str(docker_image), stream=True, decode=True):
                print(line)

            short_image_name = image_name.split("/")[-1]

            for registry in gcp_registry:
                new_docker_image = registry + short_image_name + ":" + tag
                clientAPI.tag(str(docker_image), str(new_docker_image))

                print("------------------------------------\n\n")
                print ("Starting pushing image " + str(new_docker_image))
                print("------------------------------------\n\n")
                for line in clientAPI.push(str(new_docker_image), stream=True, decode=True):
                    print(line)

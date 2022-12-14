import yaml
from yaml.loader import SafeLoader
import docker
import os

gcp_registry = (os.getenv('REGISTRY').replace(" ", "")).split(",")
clientAPI = docker.APIClient(base_url='unix://var/run/docker.sock')

err = []

# Open the file and load the file
with open('images.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)

for image in data['images']:
    image_name = image
    for tag in data['images'][image_name]:
        docker_image = '%s:%s' %(image_name, tag)
                        
        print("------------------------------------\n\n")
        print ("Starting pulling %s image " % docker_image)
        print("------------------------------------\n\n")

        # for line in clientAPI.pull(str(docker_image), stream=True, decode=True):
        #     print(line)

        for registry in gcp_registry:
            new_image_name = registry + "/" + image_name
            new_docker_image = '%s:%s' %(new_image_name, tag)

            # clientAPI.tag(str(docker_image), str(new_docker_image))

            print("------------------------------------\n\n")
            print ("Starting pushing %s image " % new_docker_image)
            print("------------------------------------\n\n")
            
            # for line in clientAPI.push(str(new_docker_image), stream=True, decode=True):
            #     print(line)
            try:
                clientAPI.remove_image(str(new_docker_image), force=True)
            except:
                pass
        try:    
            clientAPI.remove_image(str(docker_image), force=True)
        except:
            pass


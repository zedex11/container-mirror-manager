import yaml
from yaml.loader import SafeLoader
import docker
import os
import json
import urllib3
import sys


gcp_registry = (os.getenv("REGISTRY").replace(" ", "")).split(",")
event = os.getenv("GITHUB_EVENT_NAME")
clientAPI = docker.APIClient(base_url="unix://var/run/docker.sock")
err = []


def check_image(registry, new_image_name, tag):
    file_name = registry.split("/")[1] + ".json"
    f = open(file_name)
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    skip = False
    for item in data:
        if item["package"] == new_image_name and item["tags"] == tag:
            skip = True
    return skip


# Open the file and load the file
with open("images.yaml") as f:
    data = yaml.load(f, Loader=SafeLoader)

for image in data["images"]:
    image_name = image

    for tag in data["images"][image_name]:
        docker_image = "%s:%s" % (image_name, tag)

        for registry in gcp_registry:
            new_image_name = registry + "/" + image_name
            new_docker_image = "%s:%s" % (new_image_name, tag)

            if check_image(registry, new_image_name, tag) == True:
                print(
                    "Image "
                    + new_docker_image
                    + " already exist in the gsp registry and will be skipped"
                )
            elif event == "pull_request":
                print("\n\n------------------------------------")
                print("Starting validate %s image:" % docker_image)
                print("------------------------------------\n\n")
                try:
                    for line in clientAPI.pull(
                        str(docker_image), stream=True, decode=True
                    ):
                        print(line)

                except Exception as e:
                    print(e)
                    print("\n\n")
                    err.append(docker_image)
                    pass
                try:
                    clientAPI.remove_image(str(new_docker_image), force=True)
                except:
                    pass

            else:
                print("\n\n------------------------------------")
                print("Starting pulling %s image:" % docker_image)
                print("------------------------------------\n\n")
                try:
                    for line in clientAPI.pull(
                        str(docker_image), stream=True, decode=True
                    ):
                        print(line)

                    clientAPI.tag(str(docker_image), str(new_docker_image))

                    print("\n\n------------------------------------")
                    print("Starting pushing %s image " % new_docker_image)
                    print("------------------------------------\n\n")

                    for line in clientAPI.push(
                        str(new_docker_image), stream=True, decode=True
                    ):
                        print(line)
                except Exception as e:
                    print(e)
                    print("\n\n")
                    err.append(docker_image)
                    pass
                try:
                    clientAPI.remove_image(str(new_docker_image), force=True)
                except:
                    pass
        try:
            clientAPI.remove_image(str(docker_image), force=True)
        except:
            pass
if not err and event == "pull_request":
    print("\n\n------------------------------------")
    print("All images have been successfully validated. PR can be merged to the master")
    print("------------------------------------\n\n")
elif err and event == "pull_request":
    print("\n\n------------------------------------")
    print("The following images received an error during validation: ")
    print(set(err))
    print("\nPlease check the name of the images from the list above in the 'images.yaml' file before merging PR to the master\n")
    sys.exit("error")
elif not err:
    print("\n\n------------------------------------")
    print("All images have been successfully replicated")
    print("------------------------------------\n\n")
else:
    print("\n\n------------------------------------")
    print("The following images received an error during replication: ")
    print(set(err))
    print("\nPlease check the name of the images from the list above in the 'images.yaml' file\n")
    sys.exit("error")

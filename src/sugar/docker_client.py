from docker import from_env

client = from_env()


def get_containers():
    return client.containers.list(all=True)


def get_images():
    return client.images.list()


def get_volumes():
    return client.volumes.list()
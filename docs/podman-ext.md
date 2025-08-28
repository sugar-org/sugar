# Podman Extension (Experimental)

<div class="admonition warning">
  <p class="admonition-title">Experimental</p>
  <p>This feature is experimental and may change in future releases.</p>
</div>

<div class="admonition info">
  <p class="admonition-title">Info</p>
  <p>Sugar's podman-ext extension includes both standard Podman commands and experimental features like <code>attach</code>, <code>cp</code>, <code>ls</code>, <code>scale</code>, and <code>watch</code> that won't work currently in container operations.</p>
</div>

Sugar provides support for Podman Compose through the `podman-ext` extension.
This extension allows you to use Podman as a container engine backend instead of
Docker.

## Overview

Podman is a daemonless container engine for developing, managing, and running
OCI containers on your Linux system. The `podman-ext` extension in Sugar
provides a seamless interface to work with Podman Compose, similar to how you
would use Docker Compose.

## Prerequisites

To use the `podman-ext` extension, you need to have the following installed:

- Podman (latest version recommended)
- podman-compose

You can install podman-compose using pip:

```bash
pip install podman-compose
```

## Configuration

The configuration for Podman extension is the same as for Docker Compose. You
need to specify the backend, groups, and other parameters in the `.sugar.yaml`
file:

```yaml
backend: podman
defaults:
  group: development
groups:
  development:
    project-name: my-project
    config-path:
      - containers/compose.yaml
    env-file: .env
    services:
      default:
        - app
        - database
      available:
        - name: app
        - name: database
        - name: redis
```

## Commands

The `podman-ext` extension provides the same set of commands as the Docker
Compose extension. Here are the available commands:

### Basic Commands

- `sugar podman-ext build`: Build or rebuild services
- `sugar podman-ext config`: Parse, resolve and render compose file in canonical
  format
- `sugar podman-ext create`: Create services
- `sugar podman-ext down`: Stop and remove containers, networks
- `sugar podman-ext exec`: Execute a command in a running container
- `sugar podman-ext images`: List images used by the created containers
- `sugar podman-ext kill`: Kill containers
- `sugar podman-ext logs`: View output from containers
- `sugar podman-ext pause`: Pause services
- `sugar podman-ext ps`: List containers
- `sugar podman-ext pull`: Pull service images
- `sugar podman-ext push`: Push service images
- `sugar podman-ext restart`: Restart services
- `sugar podman-ext rm`: Remove stopped containers
- `sugar podman-ext run`: Run a one-off command on a service
- `sugar podman-ext start`: Start services
- `sugar podman-ext stop`: Stop services
- `sugar podman-ext top`: Display running processes
- `sugar podman-ext unpause`: Unpause services
- `sugar podman-ext up`: Create and start containers
- `sugar podman-ext version`: Show the podman-compose version information

### Experimental Commands

- `sugar podman-ext attach`: Attach to a service's container
- `sugar podman-ext cp`: Copy files/folders between a container and the local
  filesystem
- `sugar podman-ext ls`: List containers
- `sugar podman-ext scale`: Scale services
- `sugar podman-ext wait`: Block until the first service container stops
- `sugar podman-ext watch`: Watch build context for service source code changes
  and rebuild/refresh containers

## How to Use

You can use the `podman-ext` extension just like you would use the standard
Docker Compose commands with Sugar. Here are some examples:

### Building Services

```bash
# Build default services defined in the configuration
sugar podman-ext build

# Build all services, ignoring defaults
sugar podman-ext build --all

# Build specific services
sugar podman-ext build --services app,database
```

### Running Services

```bash
# Start default services
sugar podman-ext start

# Start all services in detached mode
sugar podman-ext start --all --  -d

# Start specific services in detached mode
sugar podman-ext start --services app,database --  -d
```

### Executing Commands

```bash
# Execute a command in a running service container
sugar podman-ext exec --service app --cmd "python manage.py migrate"

# Get a shell in a running service container
sugar podman-ext exec --service database --cmd "bash"
```

## Environment Variables

Like the Docker Compose extension, the Podman extension supports the use of
environment variables specified in the `env-file` parameter:

```yaml
groups:
  development:
    env-file: .env
    # Other configuration...
```

## Differences from Docker Compose

While Sugar aims to provide a consistent interface for both Docker Compose and
Podman Compose, there are some differences to be aware of:

1. Podman Compose uses `-f` instead of `--file` for specifying compose files
   (handled automatically by Sugar)
2. Podman Compose uses `-p` instead of `--project-name` for specifying project
   names (handled automatically by Sugar)
3. Podman Compose doesn't directly support the `--env-file` flag, so Sugar loads
   the environment variables before executing commands

!!! note Note

    1. There is no such flag `-d` present in `-- ` for
       `sugar podman-ext start`.
    2. Experimental commands like `attach`, `cp`, `ls`, `scale`, and `watch` may have
       different behavior between Podman versions. These commands are not supported currently in Sugar
    3. The `wait` command is still in development.

## Troubleshooting

If you encounter issues with the Podman extension:

1. Make sure Podman and podman-compose are properly installed and accessible in
   your PATH
2. Check that your `.sugar.yaml` configuration is correctly set up
3. Run commands with the `--verbose` flag to see detailed output
4. If a command fails, check the error message for clues about what went wrong

For more advanced troubleshooting, you can also directly use podman-compose
commands to verify functionality outside of Sugar.

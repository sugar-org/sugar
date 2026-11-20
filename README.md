# Sugar

![CI](https://img.shields.io/github/actions/workflow/status/osl-incubator/sugar/main.yaml?logo=github&label=CI)
[![Python Versions](https://img.shields.io/pypi/pyversions/containers-sugar)](https://pypi.org/project/containers-sugar/)
[![Package Version](https://img.shields.io/pypi/v/containers-sugar?color=blue)](https://pypi.org/project/containers-sugar/)
![License](https://img.shields.io/pypi/l/containers-sugar?color=blue)
![Discord](https://img.shields.io/discord/796786891798085652?logo=discord&color=blue)

Simplify the usage of containers.

You may be thinking, why do I need a new library that wrap-up docker-compose or
podman-compose if they are already really simple to use?

Yes, they are simple to use, but if you have some other parameters to the
compose command line, it could be very tedious to write them every time such as
`--env-file`, `--project-name`, `--file`, etc.

So, in this case we could use something like a script or `make`, right?

Yes, and just for one project it would be good enough. But, if you maintain or
collaborate a bunch of projects, it would be like a boiler plate.

Additionally, if you are maintaining some extra scripts in order to improve your
containers stack, these scripts would be like a boilerplate as well.

So, the idea of this project is to organize your stack of containers, gathering
some useful scripts and keeping this information centralized in a configuration
file. So the command line would be very simple.

- Software License: BSD 3 Clause
- Documentation: https://osl-incubator.github.io/sugar

## How to Install

```bash
$ pip install containers-sugar
```

## Features

The commands from docker-compose available are:

- build
- config
- create
- down
- events
- exec
- images
- kill
- logs
- pause
- port
- ps
- pull
- push
- restart
- rm
- run
- start
- stop
- top
- unpause
- up
- version

These commands are available in the main profile/plugin, so you don't need to
specify any extra parameter to access them.

For extra commands, we are gathering them into a profile/plugin called `ext`, so
you can access them using something like: `sugar compose-ext restart`.

The current available **ext** commands are:

- start -> alias for `up`
- restart -> runs `stop` and `up`

## How to use it

First you need to place the config file `.sugar.yaml` in the root of your
project. This is an example of a configuration file:

```yaml
backend: compose
defaults:
  profile: ${{ env.ENV }}
profiles:
  profile1:
    project-name: project1
    config-path:
      - containers/tests/profile1/compose.yaml
    env-file: .env
    services:
      default:
        - service1
        - service3
      available:
        - name: service1
        - name: service2
        - name: service3
  profile2:
    project-name: null
    config-path: containers/tests/profile2/compose.yaml
    env-file: .env
    services:
      available:
        - name: service1
        - name: service3
```

Some examples of how to use it:

- build the defaults services (service1,service3) for profile1:
  `sugar build --profile profile1`

- build the all services (there is no default service defined) for profile2:
  `sugar build --profile profile2`

- build all services (ignore default) for profile1:
  `sugar build --profile profile1 --all`

- start the default services for profile1:
  `sugar compose-ext start --profile profile1`

- restart all services (ignore defaults) for profile1:
  `sugar compose-ext restart --profile profile1 --all`

- restart service1 and service2 for profile1:
  `sugar compose-ext restart --profile profile1 --services service1,service2`

**NOTE**: If you use: `default: profile: ${{ env.ENV }}`, you don't need to give
`--profile <PROFILE_NAME>`, except if you want a different profile than the
default one.

## Podman Extension (Experimental)

Sugar now includes experimental support for Podman through the `podman-ext`
extension. This extension allows you to use Podman as a container engine backend
instead of Docker, with both standard container operations and experimental
commands.

### Key Features

- Full support for standard
  [podman-compose](https://github.com/containers/podman-compose) cli commands

See the [Podman Extension documentation](docs/podman-ext.md) for detailed usage
instructions and configuration options.

## Support & Acknowledgments

### Help make container workflows easier to maintain

Sugar reduces repetitive commands and configuration across container-based projects, so teams can focus on the applications they are building. Keeping that experience dependable takes ongoing care: tracking changes in container tooling, fixing compatibility issues, testing workflows, and helping new users get started. Your support helps us devote time to that work and keep Sugar openly available.

**[Support Sugar development on Open Collective](https://opencollective.com/osl/projects/osl-sugar/donate?interval=month&amount=20&name=&legalName=&email=)**. A one-time donation helps today; recurring support helps us plan continued maintenance.

### The people and organizations behind the work

Sugar is developed and maintained through [SciStitch](https://scistitch.com/), alongside its open-source contributors. We are grateful to [Open Science Labs (OSL)](https://opensciencelabs.org/) for institutional support, and to the community of contributors and users who improve Sugar through code, documentation, testing, issue reports, and feedback. Thank you for helping the project grow.

<p>
  <a href="https://scistitch.com/"><img src="https://scistitch.com/images/logo/wordmark-color.svg" alt="SciStitch" width="160" style="background: #fff; border-radius: 6px; padding: 6px 8px;"></a>
  &nbsp;&nbsp;
  <a href="https://opensciencelabs.org/"><img src="https://scistitch.com/assets/osl-logo.svg" alt="Open Science Labs" width="128" style="background: #fff; border-radius: 6px; padding: 6px 8px;"></a>
</p>

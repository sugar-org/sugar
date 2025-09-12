# Release Notes
---

## [1.19.2](https://github.com/sugar-org/sugar/compare/1.19.1...1.19.2) (2025-09-12)


### Bug Fixes

* Fix swarm deploy limitations with "extends" ([#195](https://github.com/sugar-org/sugar/issues/195)) ([0960c29](https://github.com/sugar-org/sugar/commit/0960c2942b9acd0cb967441f2751ba2002b6d84f))

## [1.19.1](https://github.com/sugar-org/sugar/compare/1.19.0...1.19.1) (2025-09-11)


### Bug Fixes

* Swarm deploy command ([#194](https://github.com/sugar-org/sugar/issues/194)) ([4c38d28](https://github.com/sugar-org/sugar/commit/4c38d2866ea346110c587cde9a246b32b681faa7))

# [1.19.0](https://github.com/sugar-org/sugar/compare/1.18.0...1.19.0) (2025-08-29)


### Features

* Add missing swarm commands ([#192](https://github.com/sugar-org/sugar/issues/192)) ([ed7f52f](https://github.com/sugar-org/sugar/commit/ed7f52f57cfae7a5e409c2b985d2d1ce98878947))
* Replace --options by <SPACE>--<SPACE> ([#193](https://github.com/sugar-org/sugar/issues/193)) ([dd1ddac](https://github.com/sugar-org/sugar/commit/dd1ddac11cbc8617f0ac78195af31fc88ad288e1))

# [1.18.0](https://github.com/sugar-org/sugar/compare/1.17.0...1.18.0) (2025-08-20)


### Features

* Implementation of swarm orchestration and management for sugar workflows  ([#188](https://github.com/sugar-org/sugar/issues/188)) ([8748054](https://github.com/sugar-org/sugar/commit/87480544b7f8cd4d33237b8acaf1bdce1f6c0fb7))
* Support for Docker Swarm Service management with  Sugar CLI ([#190](https://github.com/sugar-org/sugar/issues/190)) ([2ce843a](https://github.com/sugar-org/sugar/commit/2ce843a9e9e98d5f880df7fe933d565c63a6c45b))

# [1.17.0](https://github.com/osl-incubator/sugar/compare/1.16.1...1.17.0) (2025-05-03)


### Bug Fixes

* **docs:** Update README.md according to schema.json ([#143](https://github.com/osl-incubator/sugar/issues/143)) ([1ec5a60](https://github.com/osl-incubator/sugar/commit/1ec5a601285f7a8fd2097b61426bb0661e61a5dd))
* Fix the get_terminal_size() ([#164](https://github.com/osl-incubator/sugar/issues/164)) ([dc9353b](https://github.com/osl-incubator/sugar/commit/dc9353b61b5fc7ad67d4a9fa6a1f1ae560d44114))


### Features

* Add help flag support to CLI in any OS path  ([#136](https://github.com/osl-incubator/sugar/issues/136)) ([9ec2a34](https://github.com/osl-incubator/sugar/commit/9ec2a34c7b7a5eeb47d29167cb2870f9d77dc2c6))
* Add initial support for 'podman-compose' in sugar ([#167](https://github.com/osl-incubator/sugar/issues/167)) ([0e4ee08](https://github.com/osl-incubator/sugar/commit/0e4ee083dbcbc80f8f8413cdd3905dfff48e0907))
* Add Initial support for 'swarm' backend in schema ,cli and core extensions ([#149](https://github.com/osl-incubator/sugar/issues/149)) ([0631be0](https://github.com/osl-incubator/sugar/commit/0631be04032927edcdcca006550a34d55f439a5a))
* Add support for multiple `.env` files ([#175](https://github.com/osl-incubator/sugar/issues/175)) ([076480e](https://github.com/osl-incubator/sugar/commit/076480e9d226cf322f69bf9c0c0f2b704c56690c))
* Add support for positional only ([#157](https://github.com/osl-incubator/sugar/issues/157)) ([97c04de](https://github.com/osl-incubator/sugar/commit/97c04de0cb3f309efcc28219957535dcf0b9dd71))
* Change services/default property from string to array(list) format ([#181](https://github.com/osl-incubator/sugar/issues/181)) ([5b96464](https://github.com/osl-incubator/sugar/commit/5b96464cc3c52aa7c7114428d760413f1e72a722))
* **cli:** enhance Typer app with subcommand help fallback upon empty command args ([#176](https://github.com/osl-incubator/sugar/issues/176)) ([13271c2](https://github.com/osl-incubator/sugar/commit/13271c2a4a8ce52678a08b542d9fb5cb938bea4e))

## [1.16.1](https://github.com/osl-incubator/sugar/compare/1.16.0...1.16.1) (2024-10-17)


### Bug Fixes

* Fix specification of required attributes in schema.json ([#132](https://github.com/osl-incubator/sugar/issues/132)) ([059de08](https://github.com/osl-incubator/sugar/commit/059de08b3abb5061f833c964525bf2b1e0138947))

# [1.16.0](https://github.com/osl-incubator/sugar/compare/1.15.0...1.16.0) (2024-10-17)


### Features

* Check if the .sugar.yaml file is valid according to the schema file ([#131](https://github.com/osl-incubator/sugar/issues/131)) ([c5913c8](https://github.com/osl-incubator/sugar/commit/c5913c856d64c41371bf72d688b71c21c704966f))

# [1.15.0](https://github.com/osl-incubator/sugar/compare/1.14.2...1.15.0) (2024-10-16)


### Features

* Add support for pre and post hooks ([#130](https://github.com/osl-incubator/sugar/issues/130)) ([74bdada](https://github.com/osl-incubator/sugar/commit/74bdadaae6a83cc6d4ab43c0811535c7aadaeb44))

## [1.14.2](https://github.com/osl-incubator/sugar/compare/1.14.1...1.14.2) (2024-10-15)


### Bug Fixes

* Refactor and fix  sugar classes and CLI ([#128](https://github.com/osl-incubator/sugar/issues/128)) ([5ee9adf](https://github.com/osl-incubator/sugar/commit/5ee9adf67c1c8eada6425dd86de499532c654ac0))
* Refactor the interface for the plugins/extensions, move the main commands to the compose group ([#127](https://github.com/osl-incubator/sugar/issues/127)) ([0e0e7fe](https://github.com/osl-incubator/sugar/commit/0e0e7fece180f65d809e6339b073cdb88c0ffeff))
* Remove breakpoints, fix small issues and add unittests ([#129](https://github.com/osl-incubator/sugar/issues/129)) ([62ff5c2](https://github.com/osl-incubator/sugar/commit/62ff5c2f10e1fa046af96ca6c58cf5faf3665c68))

## [1.14.1](https://github.com/osl-incubator/sugar/compare/1.14.0...1.14.1) (2024-09-27)


### Bug Fixes

* fix the jinja2 template in the config file ([#125](https://github.com/osl-incubator/sugar/issues/125)) ([142b2b7](https://github.com/osl-incubator/sugar/commit/142b2b77662360fc4964a1c7e7f1c8eec7cbbb61))

# [1.14.0](https://github.com/osl-incubator/sugar/compare/1.13.0...1.14.0) (2024-07-24)


### Features

* **help:** Create a group for plugins in the help menu ([#123](https://github.com/osl-incubator/sugar/issues/123)) ([b8980cc](https://github.com/osl-incubator/sugar/commit/b8980cc190a0fc53de449593e35c1d121df5e1b3))

# [1.13.0](https://github.com/osl-incubator/sugar/compare/1.12.0...1.13.0) (2024-05-16)


### Features

* **experimental:** Add new docker compose commands: attach, cp, ls, scale, wait, watch ([#122](https://github.com/osl-incubator/sugar/issues/122)) ([4a28eee](https://github.com/osl-incubator/sugar/commit/4a28eeed3bc279c0e0ca9cb21a9b4fa2c2e1767a))

# [1.12.0](https://github.com/osl-incubator/sugar/compare/1.11.4...1.12.0) (2024-05-10)


### Bug Fixes

* Improve the usage of flags for the CLI ([#121](https://github.com/osl-incubator/sugar/issues/121)) ([c070bde](https://github.com/osl-incubator/sugar/commit/c070bde90178453d3c710c0b0a0c408195a95005))


### Features

* Implement typer as CLI ([#117](https://github.com/osl-incubator/sugar/issues/117)) ([b9def08](https://github.com/osl-incubator/sugar/commit/b9def082789ce012b78959d2db27b577477ac992))

## [1.11.4](https://github.com/osl-incubator/sugar/compare/1.11.3...1.11.4) (2024-05-07)


### Bug Fixes

* Isolate dependencies for stats plot ([#120](https://github.com/osl-incubator/sugar/issues/120)) ([96c6453](https://github.com/osl-incubator/sugar/commit/96c64532d3757fbdd4d0bb8e487f992e27b9e4dc))

## [1.11.3](https://github.com/osl-incubator/sugar/compare/1.11.2...1.11.3) (2024-05-07)


### Bug Fixes

* Change rich lower bound pin to >=10.11.0 ([#118](https://github.com/osl-incubator/sugar/issues/118)) ([eaa9a55](https://github.com/osl-incubator/sugar/commit/eaa9a55f858c126e55604de2ca6a58c5fb833048))
* Fix typo in the release workflow ([#119](https://github.com/osl-incubator/sugar/issues/119)) ([16b910b](https://github.com/osl-incubator/sugar/commit/16b910b97fbeb912e15f4026edec9b2de7b767cf))

## [1.11.2](https://github.com/osl-incubator/sugar/compare/1.11.1...1.11.2) (2024-03-15)


### Bug Fixes

* Fix package description ([#116](https://github.com/osl-incubator/sugar/issues/116)) ([e78f5a5](https://github.com/osl-incubator/sugar/commit/e78f5a500a0dab3f51a65d2353657527a55d5c5a))

## [1.11.1](https://github.com/osl-incubator/sugar/compare/1.11.0...1.11.1) (2024-02-04)


### Bug Fixes

* Fix initial configuration for stats plot ([#114](https://github.com/osl-incubator/sugar/issues/114)) ([4faef7c](https://github.com/osl-incubator/sugar/commit/4faef7c423ab39655c89dde94175eb3e84e0e3e5))

# [1.11.0](https://github.com/osl-incubator/sugar/compare/1.10.0...1.11.0) (2024-02-04)


### Features

* Add stats plot command ([#113](https://github.com/osl-incubator/sugar/issues/113)) ([15d92cc](https://github.com/osl-incubator/sugar/commit/15d92ccca17375c77460ac732cf25e9e627c32f6))

# [1.10.0](https://github.com/osl-incubator/sugar/compare/1.9.3...1.10.0) (2024-01-25)


### Bug Fixes

* change usage KxgrLogs for KxgrErrorType ([#107](https://github.com/osl-incubator/sugar/issues/107)) ([d8d38b2](https://github.com/osl-incubator/sugar/commit/d8d38b216b1baebc10d65b8a7830d5d3910bdea2))
* Check if project-name is null ([#106](https://github.com/osl-incubator/sugar/issues/106)) ([82a93df](https://github.com/osl-incubator/sugar/commit/82a93dfc491136151ff63b943a6812811498153b))


### Features

* Add a new key in the root of the config file for services ([#110](https://github.com/osl-incubator/sugar/issues/110)) ([7e6eabc](https://github.com/osl-incubator/sugar/commit/7e6eabc81e755bb96863e49cae7e47109f918fc0))
* Rename from sugar to core module name ([#101](https://github.com/osl-incubator/sugar/issues/101)) ([40dace1](https://github.com/osl-incubator/sugar/commit/40dace1be838aaaa31ed989cb20a331b84a97f5d))

## [1.9.3](https://github.com/osl-incubator/sugar/compare/1.9.2...1.9.3) (2023-12-24)


### Bug Fixes

* Add services to the config command ([#104](https://github.com/osl-incubator/sugar/issues/104)) ([b338796](https://github.com/osl-incubator/sugar/commit/b338796e5ac0c90be0ddd6ffd36692797f79b68c))
* Fix distlib installation failure ([#102](https://github.com/osl-incubator/sugar/issues/102)) ([1b3d79f](https://github.com/osl-incubator/sugar/commit/1b3d79f50f5f117379e29c737114966f55208782))

## [1.9.2](https://github.com/osl-incubator/sugar/compare/1.9.1...1.9.2) (2023-12-13)


### Bug Fixes

* Rename project from containers-sugar to sugar and improve docs ([#98](https://github.com/osl-incubator/sugar/issues/98)) ([45c51bb](https://github.com/osl-incubator/sugar/commit/45c51bb630ac1375bfd6515dc0567e87d1d206c7))

## [1.9.1](https://github.com/osl-incubator/sugar/compare/1.9.0...1.9.1) (2023-11-15)


### Bug Fixes

* **refactor:** Change "service-groups" to "groups" ([#86](https://github.com/osl-incubator/sugar/issues/86)) ([98bd82c](https://github.com/osl-incubator/sugar/commit/98bd82c647e87e9f0a6bae5703b7d8631977517e)), closes [#60](https://github.com/osl-incubator/sugar/issues/60)

# [1.9.0](https://github.com/osl-incubator/sugar/compare/1.8.0...1.9.0) (2023-07-19)


### Features

* Add support for compose v2 ([#84](https://github.com/osl-incubator/sugar/issues/84)) ([907b3ad](https://github.com/osl-incubator/sugar/commit/907b3ad4fe35310f0e531b4cd3b9ee6dfb0173ac))

# [1.8.0](https://github.com/osl-incubator/sugar/compare/1.7.1...1.8.0) (2023-07-17)


### Features

* Add default config for project-name ([#82](https://github.com/osl-incubator/sugar/issues/82)) ([1dab380](https://github.com/osl-incubator/sugar/commit/1dab3802439695396d94e3e1cfce3aeff686e6c6))

## [1.7.1](https://github.com/osl-incubator/sugar/compare/1.7.0...1.7.1) (2023-06-15)


### Bug Fixes

* **linter:** Refactor linter options and fixes issues pointed by linter tools and add new alias to the app ([#81](https://github.com/osl-incubator/sugar/issues/81)) ([b6e13df](https://github.com/osl-incubator/sugar/commit/b6e13dfa2f72e97cc22ea49ec512f8e8f00c5c70))

# [1.7.0](https://github.com/osl-incubator/sugar/compare/1.6.1...1.7.0) (2023-06-06)


### Features

* Add support for default option configuration for group service ([#80](https://github.com/osl-incubator/sugar/issues/80)) ([0045a4a](https://github.com/osl-incubator/sugar/commit/0045a4aabcb6106f6ba145fa1edfd12e3fc5cb6a))

## [1.6.1](https://github.com/osl-incubator/sugar/compare/1.6.0...1.6.1) (2023-06-05)


### Bug Fixes

* **ext:** Fix restart and start ext commands ([#79](https://github.com/osl-incubator/sugar/issues/79)) ([e9622c3](https://github.com/osl-incubator/sugar/commit/e9622c3ac21e0e08de15263a82f77b3828aecaa9))

# [1.6.0](https://github.com/osl-incubator/sugar/compare/1.5.0...1.6.0) (2023-05-27)


### Features

* Add the alias kxgr to sugar ([#75](https://github.com/osl-incubator/sugar/issues/75)) ([67a9d5c](https://github.com/osl-incubator/sugar/commit/67a9d5cd96c308be0d447a5a9cfb3406d1166336))
* Implement the missing docker-compose commands ([#77](https://github.com/osl-incubator/sugar/issues/77)) ([bafbc1d](https://github.com/osl-incubator/sugar/commit/bafbc1d307a0e07385978863724ab3487f7939bc))

# [1.5.0](https://github.com/osl-incubator/sugar/compare/1.4.4...1.5.0) (2023-04-07)


### Features

* Improve the usage of parameters --cmd and --  (formerly --extras)  ([#68](https://github.com/osl-incubator/sugar/issues/68)) ([cebdfd8](https://github.com/osl-incubator/sugar/commit/cebdfd808449a14982ca974b24fc36d0fed5eeb7))

## [1.4.4](https://github.com/osl-incubator/sugar/compare/1.4.3...1.4.4) (2023-04-05)


### Bug Fixes

* Fix the internal usage of the value from --cmd flag ([#67](https://github.com/osl-incubator/sugar/issues/67)) ([ac8a048](https://github.com/osl-incubator/sugar/commit/ac8a0487f41404c52195cfcf74fa18a86f4523f8))

## [1.4.3](https://github.com/osl-incubator/sugar/compare/1.4.2...1.4.3) (2023-03-25)


### Bug Fixes

* Remove --volumes from down command ([#66](https://github.com/osl-incubator/sugar/issues/66)) ([8bcaae4](https://github.com/osl-incubator/sugar/commit/8bcaae47fb413f682337759a7f5cab152ee83e76))

## [1.4.2](https://github.com/osl-incubator/sugar/compare/1.4.1...1.4.2) (2023-03-08)


### Bug Fixes

* Fix the exit function when an error happens ([#64](https://github.com/osl-incubator/sugar/issues/64)) ([6305cd8](https://github.com/osl-incubator/sugar/commit/6305cd8189b2745c56c87f80c53f118965358226))

## [1.4.1](https://github.com/osl-incubator/sugar/compare/1.4.0...1.4.1) (2023-02-15)


### Bug Fixes

* Use extras for all sub-commands ([#38](https://github.com/osl-incubator/sugar/issues/38)) ([41abdeb](https://github.com/osl-incubator/sugar/commit/41abdebc51c24cd1d4739c66d9595b8dd404c355))

# [1.4.0](https://github.com/osl-incubator/sugar/compare/1.3.2...1.4.0) (2023-02-09)


### Features

* Add support for multiples compose-path ([#37](https://github.com/osl-incubator/sugar/issues/37)) ([c726250](https://github.com/osl-incubator/sugar/commit/c7262501235453641adbf735d93be9bed22193a6))

## [1.3.2](https://github.com/osl-incubator/sugar/compare/1.3.1...1.3.2) (2023-02-09)


### Bug Fixes

* Fix the argument `--all` ([#34](https://github.com/osl-incubator/sugar/issues/34)) ([747a1c0](https://github.com/osl-incubator/sugar/commit/747a1c021e55de753f4f28ad3dc4cb49c7f5ce01))

## [1.3.1](https://github.com/osl-incubator/sugar/compare/1.3.0...1.3.1) (2023-02-07)


### Bug Fixes

* Fix --extras parameter and improve the CI ([#32](https://github.com/osl-incubator/sugar/issues/32)) ([9340712](https://github.com/osl-incubator/sugar/commit/9340712a9a9c65c07f9ff9ad732a47f6d3dc0d0d))

# [1.3.0](https://github.com/osl-incubator/sugar/compare/1.2.0...1.3.0) (2023-02-07)


### Features

* Add extra args and command argument for run and exec action ([#31](https://github.com/osl-incubator/sugar/issues/31)) ([e942183](https://github.com/osl-incubator/sugar/commit/e94218374632e98839c49e62a288c7618fe10b43))

# [1.2.0](https://github.com/osl-incubator/sugar/compare/1.1.0...1.2.0) (2023-02-06)


### Features

* Add extra args and command argument for run and exec action ([#27](https://github.com/osl-incubator/sugar/issues/27)) ([8680799](https://github.com/osl-incubator/sugar/commit/8680799ae7bdbbe57281180f0bd2d2461445cbbc))

# [1.1.0](https://github.com/osl-incubator/sugar/compare/1.0.6...1.1.0) (2023-01-27)


### Features

* Add run and exec initial implementation ([#21](https://github.com/osl-incubator/sugar/issues/21)) ([332f2bc](https://github.com/osl-incubator/sugar/commit/332f2bce7d7c6945707ffe128619bc9bda2b8548))

## [1.0.6](https://github.com/osl-incubator/sugar/compare/1.0.5...1.0.6) (2023-01-27)


### Bug Fixes

* Fix env-file access and improve version sub-command output ([#17](https://github.com/osl-incubator/sugar/issues/17)) ([bc50bb9](https://github.com/osl-incubator/sugar/commit/bc50bb9b2d7dcaf87e847f794c296b82dff7a4e9))

## [1.0.5](https://github.com/osl-incubator/sugar/compare/1.0.4...1.0.5) (2023-01-26)


### Bug Fixes

* Fix the import of sh lib and add pre-commit run to CI ([#16](https://github.com/osl-incubator/sugar/issues/16)) ([ac048e1](https://github.com/osl-incubator/sugar/commit/ac048e189ecf553277246f34fa9b6f67010dc7ca))

## [1.0.4](https://github.com/osl-incubator/sugar/compare/1.0.3...1.0.4) (2023-01-26)


### Bug Fixes

* Fix the sh call ([#15](https://github.com/osl-incubator/sugar/issues/15)) ([6e26308](https://github.com/osl-incubator/sugar/commit/6e263088458ece50bd66d9a3575ed5d0cec51f8a))

## [1.0.3](https://github.com/osl-incubator/sugar/compare/1.0.2...1.0.3) (2023-01-26)


### Bug Fixes

* Suppress traceback from sh ([#14](https://github.com/osl-incubator/sugar/issues/14)) ([69902c6](https://github.com/osl-incubator/sugar/commit/69902c6372ec55cc36bbdd87e0f594c733163886))

## [1.0.2](https://github.com/osl-incubator/sugar/compare/1.0.1...1.0.2) (2023-01-26)


### Bug Fixes

* Fix support for python 3.7.1, 3.8, 3.9, 3.10 ([#13](https://github.com/osl-incubator/sugar/issues/13)) ([83a9592](https://github.com/osl-incubator/sugar/commit/83a9592e06b7fabc7a0f260b38a58267488a070e))

## [1.0.1](https://github.com/osl-incubator/sugar/compare/1.0.0...1.0.1) (2023-01-21)


### Bug Fixes

* Fix quotes used by semantic release replace ([#8](https://github.com/osl-incubator/sugar/issues/8)) ([66acb67](https://github.com/osl-incubator/sugar/commit/66acb67b9275a2afea48b6dd97b143edfff80be1))

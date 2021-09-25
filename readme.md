# README


## Usage

configure parameters in `config.yaml` and `credentials.yaml`, examples are in `config.yaml.example` and `credentials.yaml.example`
`./deploy install` will install all dependencies and attempt to deploy the template to your aws account if you have the aws-cli set up.

## About

Uses Cloudformation to spin up a docker container running https://github.com/itzg/docker-minecraft-server. 
This minecraft server runs a modpack defined in your s3 bucket. It is hosted on an EC2 instance running on a gp3 ebs volume. 
It also has a discord bot which can send updates about server status to a discord channel, and can be controlled on discord.

Used https://github.com/vatertime/minecraft-spot-pricing/blob/master/cf.yml as a base cfn template
 
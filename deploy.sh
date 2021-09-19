#!/bin/bash
NoipUsername=$(yq -r .Noip.Username credentials.yaml)
NoipPassword=$(yq -r .Noip.Password credentials.yaml)
DiscordPublicKey=$(yq -r .Discord.BotPublicKey credentials.yaml)
DiscordApplicationId=$(yq -r .Discord.BotApplicationId credentials.yaml)
DiscordBotToken=$(yq -r .Discord.BotToken credentials.yaml)
WebhookUrl=$(yq -r .Discord.MinecraftChannelWebhookURL credentials.yaml)
IPv4=$(yq -r .Network.IPv4 credentials.yaml)
MCAdmin=$(yq -r .Minecraft.Username credentials.yaml)
AWSKeyPairName=$(yq -r .AWS.KeyPairName credentials.yaml)

ModPackBucket=$(yq -r .AWS.ModpackBucket config.yaml)
Bucket=$(yq -r .AWS.LambdaArtifactBucket config.yaml)
StackName=$(yq -r .AWS.StackName config.yaml)
Region=$(yq -r .AWS.Region config.yaml)

# Do not forget the \ at end of each line when modifying this
ParameterOverrides=(
    NoipUsername="${NoipUsername}" 
    NoipPassword="${NoipPassword}" 
    DiscordPublicKey="${DiscordPublicKey}" 
    DiscordApplicationId="${DiscordApplicationId}" 
    DiscordBotToken="${DiscordBotToken}" 
    WebhookUrl="${WebhookUrl}"
    YourIPv4="${IPv4}"
    AdminPlayerNames="${MCAdmin}"
    KeyPairName="${AWSKeyPairName}"
    Bucket="${ModPackBucket}"
)

### Set up environment ###

# clean up old build artifacts
rm build/packaged-template.yaml > /dev/null 2>&1 

echo "Cleaning up old build"
./clean.sh

if [[ "$1" == "install" ]]
then
    ./install.sh
fi

# copy files into build folder
for D in src/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")
        echo "Copying ${function_name} to build/" 
        cp -r "${D}/" "build/${function_name}"
    fi
done
for D in tst/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")
        echo "copying ${function_name} tests" 
        cp -r "${D}"/* "build/${function_name}"
    fi
done

### Test ###

echo "executing tests"
cd build || exit
pytest || { echo "tests failed, exiting" ; exit 1; }
cd .. || exit

### Package for deployment ###

for D in src/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")
        echo "packaging ${function_name}" 
        pip3 install -r "build/${function_name}/requirements.txt" -t "build/${function_name}/." > /dev/null 2>&1
    fi
done

aws cloudformation package --template-file resources/cloudformation/minecraft-infrastructure.yaml --s3-bucket "${Bucket}" --output-template-file build/packaged-template.yaml

echo ""
read -r -p "Packaging complete, would you like to deploy to ${StackName} in ${Region}? [y/N] " response
response=${response,,}    # tolower
if [[ "$response" =~ ^(yes|y)$ ]]
then
    ### Deploy ###
    aws cloudformation deploy --template-file build/packaged-template.yaml --stack-name "${StackName}" --region "${Region}" --capabilities CAPABILITY_IAM --parameter-overrides "${ParameterOverrides[@]}"
else
    exit 0
fi


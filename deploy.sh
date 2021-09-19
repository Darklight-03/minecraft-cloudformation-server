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

# clean up build artifacts
mkdir build > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
rm build/packaged-template.yaml > /dev/null 2>&1 

# for each folder in src/lambda
for D in src/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")

        # copy the folder into build, then install requirements.txt with pip3 in build
        echo "building ${function_name}" 
        cp -r "${D}/" "build/${function_name}"
        pip3 install -r "build/${function_name}/requirements.txt" -t "build/${function_name}/." > /dev/null 2>&1
        #install locally as well so tests can run
        pip install -r "build/${function_name}/requirements.txt" > /dev/null 2>&1
    fi
done

for D in tst/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")

        # copy the tests into build
        echo "copying ${function_name} tests" 
        cp -r "${D}"/* "build/${function_name}"
    fi
done
echo "executing tests"
cd build || exit
pytest || { echo "tests failed, exiting" ; exit 1; }
cd .. || exit

aws cloudformation package --template-file resources/cloudformation/minecraft-infrastructure.yaml --s3-bucket "${Bucket}" --output-template-file build/packaged-template.yaml
aws cloudformation deploy --template-file build/packaged-template.yaml --stack-name "${StackName}" --region "${Region}" --capabilities CAPABILITY_IAM --parameter-overrides "${ParameterOverrides[@]}"
import sagemaker
import boto3
import time
sess = boto3.Session()

sm_client = boto3.client("sagemaker")

def delete_piplines():
    pipelines = sm_client.list_pipelines()

    if pipelines['PipelineSummaries']:
        for pipeline in pipelines['PipelineSummaries']:
            sm_client.delete_pipeline(PipelineName = pipeline['PipelineName'])





def cleanup_boto3(experiment_name):
    trials = sm_client.list_trials(ExperimentName=experiment_name)['TrialSummaries']
    print('TrialNames:')
    for trial in trials:
        trial_name = trial['TrialName']
        print(f"\n{trial_name}")

        components_in_trial = sm_client.list_trial_components(TrialName=trial_name)
        print('\tTrialComponentNames:')
        for component in components_in_trial['TrialComponentSummaries']:
            component_name = component['TrialComponentName']
            print(f"\t{component_name}")
            sm_client.disassociate_trial_component(TrialComponentName=component_name, TrialName=trial_name)
            try:
                # comment out to keep trial components
                sm_client.delete_trial_component(TrialComponentName=component_name)
            except:
                # component is associated with another trial
                continue
            # to prevent throttling
            time.sleep(.5)
        sm_client.delete_trial(TrialName=trial_name)
    sm_client.delete_experiment(ExperimentName=experiment_name)
    print(f"\nExperiment {experiment_name} deleted")

def delete_experiments():
    experiments = sm_client.list_experiments()
    if experiments['ExperimentSummaries']:
        for expriment in experiments['ExperimentSummaries']:
            cleanup_boto3(expriment['ExperimentName'])
            # response = sm_client.delete_experiment(
            #     ExperimentName=expriment['ExperimentName']
            # )
            # print(response)



def delete_endpoints():
    endpoints = sm_client.list_endpoints()

    if endpoints:
        for endpoint in endpoints["Endpoints"]:
            response = sm_client.delete_endpoint(EndpointName = endpoint["EndpointName"])
            print(response)

            sm_client.delete_endpoint_config(
                EndpointConfigName='string'
            )

def delete_endpoint_configs():
    endpoint_configs = sm_client.list_endpoint_configs()

    if endpoint_configs["EndpointConfigs"]:
        for endpoint_config in endpoint_configs["EndpointConfigs"]:
            response = sm_client.delete_endpoint_config(EndpointConfigName = endpoint_config["EndpointConfigName"])
            print(response)


def delete_models():
    models = sm_client.list_models()

    if models["Models"]:
        for model in models["Models"]:
            response = sm_client.delete_model(ModelName = model["ModelName"])
            print(response)



def main():
    delete_piplines()
    delete_experiments()
    delete_endpoints()
    delete_endpoint_configs()
    delete_models()

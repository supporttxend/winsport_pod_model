from models import PodModel
import json


def get_pod_files_by_id(pod_id="3241bdad-5232-4ee5-9762-e4796746d55f"):
    pod_obj = PodModel.objects.filter(uuid=pod_id).get()
    pod_data = json.loads(pod_obj.to_json())
    path_list = []
    if "bolPath" in pod_data:
        path_list.append(pod_data['bolPath'])
    if "podPath" in pod_data:
        path_list.append(pod_data['podPath'])
    if "invoicePath" in pod_data:
        path_list.append(pod_data['invoicePath'])
    return path_list


def update_pod_watermark_url(pod_id, data):

    pod_obj = PodModel.objects(uuid=pod_id).modify(
            **data, upsert=True
        )

    if not pod_obj:
        print("Error: pod record not found")
    else:
        print("Status: pod record updated")
import json


def load_jsons():
    data = {}
    with open("app/core/json_data/prices.json", "r") as f:
        prices_data = json.load(f)

    # with open("app/core/json_data/filters.json", "r") as f:
    #     filters_data = json.load(f)
    #
    # with open("app/core/json_data/points.json", "r") as f:
    #     points_data = json.load(f)
    #
    # with open("app/core/json_data/locations.json", "r") as f:
    #     locations_data = json.load(f)

    data['prices'] = prices_data
    # data['points'] = points_data
    # data['filters'] = filters_data
    # data['locations'] = locations_data

    return data


json_data = load_jsons()

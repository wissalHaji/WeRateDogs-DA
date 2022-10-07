
import json
from timeit import default_timer as timer
from pathlib import Path
import os


def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


def get_module_root() -> Path:
    return Path(__file__).parent


def get_token(file_name):
    """
    Parse the json file containg api secrets to get the value of api token

    Args:
        file_name (string): relative path of the json file

    Returns:
        string: Twitter api bearer token
    """
    with open(os.path.join(get_module_root(), file_name), 'r') as file:
        data = json.load(file)
    return data["token"]


def fetch_api(file_path, main_df):
    """
    Fetches the number of likes and retweets forom twitte api V2

    Args:
        file_path (string): Path of the file where to store api data
        main_df (pd.DataFrame): Dataframe containg tweets from WeRateDogs archive
        api_secret_file_path (string) : The path of the file
    """
    install_and_import("tweepy")

    BEARER_TOKEN = get_token("api_secret.json")
    client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True)
    start = timer()
    fails_dict = {}
    print("Fetching API started...")
    print("-----------------------------\n")
    with open(file_path, "w") as file:
        for id in main_df.tweet_id:
            resp_json = client.get_tweet(id, tweet_fields='public_metrics')
            if resp_json.errors:
                fails_dict[id] = resp_json.errors
            elif not resp_json.data:
                fails_dict[id] = 'No data returned'
            else:
                json.dump(resp_json.data.data, file)
                file.write('\n')
            print(f'Tweet id : {id}')

    end = timer()
    print("-----------------------------\n")
    print(f'Execution time : {end - start}')

    return fails_dict
